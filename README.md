# Data Detective 🔎📊

**Open-source, offline Agent Skill for CSV quality auditing and exploratory data analysis.** Agent instructions are in [`skills/data-detective/SKILL.md`](skills/data-detective/SKILL.md); the analysis is performed by reproducible Python code, not model-generated numbers.

## What it does
- Audits all CSV records for empty values, exact duplicate rows, inconsistent field counts, whitespace and heuristic mixed types.
- Profiles up to the first 5,000 well-formed rows for means, medians, quartiles, variability, categorical frequencies, and up to eight SVG charts.
- Emits a reproducible JSON report, Markdown report, and **evidence-backed review findings**.
- Works offline, has no runtime dependencies, does not require an API key, and never modifies its input.

## Run locally
Requires Python 3.10+.

```bash
python skills/data-detective/scripts/analyze.py examples/sample.csv --output-dir output
```

Open `output/report.md` or read `output/report.json`.

Options: `--max-rows 1000`, `--no-charts`.

## Install as an Agent Skill

Copy the folder `skills/data-detective/` into your agent's skills location, following its documented installation method. For example, in compatible Codex configurations the user-level directory is `~/.agents/skills/data-detective/`; Claude Code commonly uses `.claude/skills/data-detective/` at project level. Locations and support vary by agent version, so consult official documentation for your agent.

Example agent request:

> Use Data Detective to inspect my CSV. First give the verified data quality findings, then describe distributions and ask only the questions needed for interpretation. Do not change my data.

## Repository layout

```text
skills/data-detective/SKILL.md
skills/data-detective/scripts/analyze.py
skills/data-detective/scripts/audit_csv.py
skills/data-detective/references/interpretation.md
examples/sample.csv
tests/
.github/workflows/tests.yml
```

## Test

```bash
python -m unittest discover -s tests -v
```

## Security and limitations

- **Privacy:** Outputs may include values from the input; inspect before sharing. No network access is used.
- **Scope:** CSV encoded UTF-8 / UTF-8 BOM only. No Excel, Parquet or SQL support yet.
- **Sampling:** Quality audit checks all rows; EDA uses first N valid rows, **not a random sample**. Ordering bias is possible.
- **Inference:** Missing means blank/whitespace, not `NA`; type detection is heuristic; findings are signals to investigate, not verified root causes.
- **Resource usage:** Exact duplicate detection uses memory proportional to distinct rows and is not optimized for huge CSV files.
- **Interpretation:** Descriptive statistics are not causal evidence.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). MIT licensed; see [LICENSE](LICENSE).
