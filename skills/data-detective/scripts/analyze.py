#!/usr/bin/env python3
"""Integrated read-only CSV data quality and exploratory analysis (stdlib only)."""
import argparse
import csv
import html
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from audit_csv import audit

MAX_SAMPLE = 5000
MAX_COLUMNS = 60
MAX_CHARTS = 8


def numeric_value(raw):
    raw = raw.strip()
    if not raw or raw.lower() in {'na', 'null', 'n/a', 'nan', 'inf', '-inf', 'infinity'}:
        return None
    try:
        value = float(raw)
        return value if math.isfinite(value) else None
    except ValueError:
        return None


def sample_csv(path, max_rows):
    sample = []
    valid_count = 0
    with path.open('r', encoding='utf-8-sig', newline='') as source:
        reader = csv.reader(source)
        headers = next(reader)
        for row in reader:
            if len(row) != len(headers):
                continue
            valid_count += 1
            # Deterministic bounded systematic sample: retain first max_rows; explicitly reported.
            if len(sample) < max_rows:
                sample.append(row)
    return headers, sample, valid_count


def profile_columns(headers, rows, valid_count):
    output = []
    for idx, name in enumerate(headers[:MAX_COLUMNS]):
        values = [row[idx].strip() for row in rows]
        nonempty = [v for v in values if v]
        parsed = [numeric_value(v) for v in nonempty]
        all_numeric = bool(nonempty) and all(v is not None for v in parsed)
        profile = {'name': name, 'sampled_nonmissing_count': len(nonempty)}
        if all_numeric:
            nums = [float(v) for v in parsed]
            ordered = sorted(nums)
            def percentile(p):
                position = (len(ordered) - 1) * p
                low = math.floor(position)
                high = math.ceil(position)
                return ordered[low] + (ordered[high] - ordered[low]) * (position - low)
            profile.update({
                'kind': 'numeric', 'min': min(nums), 'max': max(nums),
                'mean': round(statistics.fmean(nums), 5),
                'median': round(statistics.median(nums), 5),
                'std_dev': round(statistics.stdev(nums), 5) if len(nums) > 1 else None,
                'q1': round(percentile(.25), 5), 'q3': round(percentile(.75), 5),
            })
        else:
            counts = Counter(nonempty)
            profile.update({'kind': 'categorical_or_text', 'distinct_in_sample': len(counts),
                            'top_values': [{'value': val[:60], 'count': freq}
                                           for val, freq in counts.most_common(5)]})
        output.append(profile)
    return output


def make_svg_bars(labels, counts, title, x_label='Count'):
    width, height = 760, 310
    left, top, chart_w, chart_h = 205, 55, 495, 185
    maximum = max(counts) if counts else 1
    bars = []
    for index, (label, count) in enumerate(zip(labels, counts)):
        y = top + index * (chart_h / max(len(labels), 1))
        row_h = chart_h / max(len(labels), 1)
        bar_width = chart_w * (count / maximum) if maximum else 0
        safe = html.escape(str(label)[:29], quote=True)
        bars.append(f'<text x="{left-10}" y="{y+row_h*.6:.1f}" text-anchor="end" font-size="12">{safe}</text>'
                    f'<rect x="{left}" y="{y+3:.1f}" width="{bar_width:.1f}" height="{max(row_h-8,3):.1f}" fill="#2563eb" />'
                    f'<text x="{min(left+bar_width+5,width-20):.1f}" y="{y+row_h*.6:.1f}" font-size="11">{count}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">'
            f'<rect width="100%" height="100%" fill="#fff"/>'
            f'<text x="25" y="30" font-family="Arial,sans-serif" font-size="18" font-weight="bold">{html.escape(title[:72])}</text>'
            f'<g font-family="Arial,sans-serif" fill="#111827">{"".join(bars)}</g>'
            f'<text x="{left}" y="275" fill="#4b5563" font-family="Arial,sans-serif" font-size="12">{html.escape(x_label)}</text></svg>')


def make_numeric_histogram(rows, index, name):
    vals = [numeric_value(row[index]) for row in rows if row[index].strip()]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    lo, hi = min(vals), max(vals)
    bins = [0] * 8
    for val in vals:
        pos = min(int(8 * (val - lo) / (hi - lo)), 7) if hi > lo else 0
        bins[pos] += 1
    labels = [f'{lo + (hi-lo)*i/8:.3g}–{lo+(hi-lo)*(i+1)/8:.3g}' for i in range(8)] if hi > lo else [f'{lo:.3g}']
    return make_svg_bars(labels, bins if hi > lo else [len(vals)], f'Histogram: {name}', 'Sampled records per bin')


def derive_findings(quality, profiles, sample_size):
    """Evidence-backed, deterministic observations; never assert causation."""
    findings = []
    total = quality['row_count']
    malformed = quality['malformed_row_count']
    if malformed:
        findings.append({'severity': 'warning', 'code': 'malformed_rows',
                         'message': f'{malformed} of {total} CSV records have an unexpected field count; excluded from EDA.',
                         'evidence': {'malformed_rows': malformed, 'total_rows': total}})
    duplicates = quality['duplicate_row_count']
    if duplicates:
        findings.append({'severity': 'review', 'code': 'exact_duplicates',
                         'message': f'{duplicates} exact duplicate records detected; verify whether repeated records are expected.',
                         'evidence': {'duplicate_rows': duplicates}})
    valid = total - malformed
    for col in quality['columns']:
        if col['missing_count']:
            findings.append({'severity': 'review', 'code': 'missing_values', 'column': col['name'],
                             'message': f'{col["name"]}: {col["missing_count"]} empty values among {valid} structurally valid rows.',
                             'evidence': {'missing_count': col['missing_count'], 'valid_rows': valid}})
        if col['potential_mixed_types']:
            findings.append({'severity': 'review', 'code': 'mixed_types', 'column': col['name'],
                             'message': f'{col["name"]}: multiple inferred value types; confirm intended schema.',
                             'evidence': {'observed_types': col['observed_types']}})
    if total > sample_size:
        findings.append({'severity': 'info', 'code': 'sampling_limit',
                         'message': f'EDA uses only the first {sample_size} well-formed rows; check for ordering bias.',
                         'evidence': {'sampled_rows': sample_size, 'total_rows': total}})
    return findings


def run(path, output_dir, max_rows=MAX_SAMPLE, charts=True):
    if max_rows < 1 or max_rows > MAX_SAMPLE:
        raise ValueError(f'--max-rows must be between 1 and {MAX_SAMPLE}')
    path = path.resolve()
    output_dir = output_dir.resolve()
    if path in (output_dir / 'report.md', output_dir / 'report.json'):
        raise ValueError('Output path would overwrite input; choose a different output directory.')
    quality = audit(path)
    headers, rows, valid_count = sample_csv(path, max_rows)
    profiles = profile_columns(headers, rows, valid_count)
    report = {
        'source_file': path.name,
        'quality': quality,
        'eda': {
            'sampled_rows': len(rows),
            'valid_rows': valid_count,
            'sampling_method': 'first N valid rows (not random; order bias possible)',
            'columns_profiled': len(profiles),
            'columns_skipped': max(0, len(headers)-MAX_COLUMNS),
            'columns': profiles,
        },
        'findings': derive_findings(quality, profiles, len(rows)),
        'warnings': [
            'All statistics and charts are descriptive and not causal evidence.',
            'EDA uses only the first N well-formed rows; results may be biased by row order.',
            'Numeric-looking identifiers can be classified as numbers; confirm column meaning.',
            'Reports and charts can expose data values. Review before sharing publicly.',
            'Input is read-only; no cleaning or imputation is applied.',
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    chart_files = []
    if charts:
        chart_dir = output_dir / 'charts'
        chart_dir.mkdir(exist_ok=True)
        for index, profile in enumerate(profiles):
            if len(chart_files) >= MAX_CHARTS:
                break
            if profile['kind'] == 'numeric':
                svg = make_numeric_histogram(rows, index, profile['name'])
            else:
                top = profile['top_values']
                svg = make_svg_bars([x['value'] for x in top], [x['count'] for x in top],
                                    f'Top values: {profile["name"]}') if top else None
            if svg:
                filename = f'column-{index+1:02d}.svg'
                (chart_dir / filename).write_text(svg, encoding='utf-8')
                chart_files.append(f'charts/{filename}')
    report['eda']['charts'] = chart_files
    (output_dir / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')
    lines = [f'# Data Detective Report: {path.name}', '', '## Quality overview', '',
             f'- Total rows: **{quality["row_count"]}**',
             f'- Malformed rows: **{quality["malformed_row_count"]}**',
             f'- Exact duplicates: **{quality["duplicate_row_count"]}**', '',
             '| Column | Missing | Missing % | Mixed types? |', '|---|---:|---:|---|']
    for col in quality['columns']:
        name = col['name'].replace('|','\\|').replace('\n',' ')
        lines.append(f'| {name} | {col["missing_count"]} | {col["missing_pct"]}% | {"Yes" if col["potential_mixed_types"] else "No"} |')
    lines += ['', '## Evidence-backed findings', '']
    lines += [f'- **{finding["severity"].upper()}**: {finding["message"]}' for finding in report['findings']] or ['- No predefined quality flags detected; this does not guarantee the dataset is clean.']
    lines += ['', '## Exploratory data analysis', '',
              f'EDA sample: **{len(rows)} / {valid_count}** valid rows (first rows, not random).', '']
    for profile in profiles:
        lines.append(f'### {profile["name"]}')
        if profile['kind'] == 'numeric':
            lines.append(f'- Numeric: mean **{profile["mean"]}**, median **{profile["median"]}**, min **{profile["min"]}**, max **{profile["max"]}**, Q1 **{profile["q1"]}**, Q3 **{profile["q3"]}**')
        else:
            lines.append(f'- Categorical/text: **{profile["distinct_in_sample"]}** distinct sampled values')
        lines.append('')
    lines += ['## Questions to confirm before interpreting', '', '- What does each numeric column represent, particularly identifiers and codes?', '- Are blank cells expected, or should they be treated as missing?', '- Are exact duplicate records legitimate business events?', '- Is the dataset ordered by date, group, or priority (which could bias first-row EDA)?', '']
    if chart_files:
        lines += ['## Charts', ''] + [f'![Chart]({file})' for file in chart_files] + ['']
    lines += ['## Important limitations', ''] + [f'- {w}' for w in report['warnings']]
    (output_dir / 'report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description='Integrated CSV quality audit + auto-EDA (no API key or dependencies)')
    parser.add_argument('input', type=Path)
    parser.add_argument('--output-dir', type=Path, default=Path('data-detective-output'))
    parser.add_argument('--max-rows', type=int, default=MAX_SAMPLE)
    parser.add_argument('--no-charts', action='store_true')
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error('Input CSV not found')
    try:
        run(args.input, args.output_dir, args.max_rows, not args.no_charts)
    except (UnicodeError, csv.Error, ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f'Report created: {args.output_dir / "report.md"}')


if __name__ == '__main__':
    main()
