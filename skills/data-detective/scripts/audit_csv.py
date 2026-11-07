#!/usr/bin/env python3
"""Read-only CSV data quality audit. No third-party packages required."""
import argparse
import csv
import json
from collections import Counter
from datetime import date, datetime
from pathlib import Path


def guess_type(value):
    s = value.strip()
    if not s:
        return 'missing'
    low = s.lower()
    if low in ('true', 'false'):
        return 'boolean'
    try:
        int(s)
        return 'integer'
    except ValueError:
        pass
    try:
        float(s)
        return 'number'
    except ValueError:
        pass
    try:
        date.fromisoformat(s)
        return 'date'
    except ValueError:
        pass
    try:
        datetime.fromisoformat(s)
        return 'datetime'
    except ValueError:
        return 'text'


def audit(path):
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            raise ValueError('The CSV file is empty.')
        if not header or any(not h.strip() for h in header):
            raise ValueError('Header names must not be empty.')
        if len(set(header)) != len(header):
            raise ValueError('Duplicate header names are not supported.')
        counts = {h: Counter() for h in header}
        missing = Counter()
        whitespace = Counter()
        examples = {h: [] for h in header}
        seen = set()
        duplicate_rows = 0
        invalid_width_rows = []
        rows = 0
        for row_number, row in enumerate(reader, start=2):
            rows += 1
            if len(row) != len(header):
                invalid_width_rows.append({'line': row_number, 'fields': len(row)})
                continue
            key = tuple(row)
            if key in seen:
                duplicate_rows += 1
            else:
                seen.add(key)
            for h, raw in zip(header, row):
                if not raw.strip():
                    missing[h] += 1
                    continue
                if raw != raw.strip():
                    whitespace[h] += 1
                typ = guess_type(raw)
                counts[h][typ] += 1
                if len(examples[h]) < 3 and raw not in examples[h]:
                    examples[h].append(raw[:120])
    columns = []
    for h in header:
        distinct_types = list(counts[h])
        # integer+number is a common numeric family, not a type inconsistency
        normalized = set('number' if t in ('integer', 'number') else t for t in distinct_types)
        columns.append({
            'name': h, 'missing_count': missing[h],
            'missing_pct': round(missing[h] * 100 / rows, 2) if rows else 0,
            'leading_or_trailing_whitespace_count': whitespace[h],
            'observed_types': dict(counts[h]),
            'potential_mixed_types': len(normalized) > 1,
            'sample_values': examples[h],
        })
    return {
        'source_file': path.name, 'row_count': rows, 'column_count': len(header),
        'duplicate_row_count': duplicate_rows,
        'malformed_row_count': len(invalid_width_rows),
        'malformed_rows': invalid_width_rows[:25],
        'columns': columns,
        'notes': [
            'Missing means empty or whitespace-only; strings such as NA and null are not treated as missing.',
            'Duplicates are exact full-row matches only and may be legitimate.',
            'Type detection is heuristic; identifiers and categorical codes may look numeric.',
            'Only the first 25 malformed row locations are included in the report.'
        ],
    }


def make_markdown(result):
    lines = [f"# CSV Data Quality Audit: {result['source_file']}", '',
             f"- Rows: {result['row_count']}",
             f"- Columns: {result['column_count']}",
             f"- Exact duplicate rows: {result['duplicate_row_count']}",
             f"- Malformed rows (wrong field count): {result['malformed_row_count']}", '',
             '| Column | Missing | Missing % | Whitespace | Mixed types? | Observed types |',
             '|---|---:|---:|---:|---|---|']
    for col in result['columns']:
        types = ', '.join(f'{k}: {v}' for k, v in col['observed_types'].items()) or 'none'
        name = col['name'].replace('|', '\\|').replace('\n', ' ')
        lines.append(f"| {name} | {col['missing_count']} | {col['missing_pct']}% | {col['leading_or_trailing_whitespace_count']} | {'Yes' if col['potential_mixed_types'] else 'No'} | {types} |")
    lines.extend(['', '## Interpretation notes', ''])
    lines.extend(f'- {note}' for note in result['notes'])
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description='Read-only CSV quality audit')
    parser.add_argument('input', type=Path)
    parser.add_argument('--output-dir', type=Path, default=Path('audit-output'))
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error('Input CSV not found')
    try:
        result = audit(args.input)
    except (UnicodeError, csv.Error, ValueError) as exc:
        parser.error(str(exc))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / 'report.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (args.output_dir / 'report.md').write_text(make_markdown(result), encoding='utf-8')
    print(f"Audit complete: {args.output_dir / 'report.md'}")

if __name__ == '__main__':
    main()
