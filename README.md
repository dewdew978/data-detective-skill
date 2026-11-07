# Data Detective 🔎📊

**Open-source, offline Agent Skill for CSV quality auditing and exploratory data analysis.** Agent instructions are in [`skills/data-detective/SKILL.md`](skills/data-detective/SKILL.md); the analysis is performed by reproducible Python code, not model-generated numbers.

Install the skill from this GitHub repository, then ask your AI agent to inspect a CSV. The agent follows the skill instructions and runs the bundled Python scripts locally.

## What it does

- Audits all CSV records for empty values, exact duplicate rows, inconsistent field counts, whitespace and heuristic mixed types.
- Profiles up to the first 5,000 well-formed rows for means, medians, quartiles, variability, categorical frequencies, and up to eight SVG charts.
- Emits a reproducible JSON report, Markdown report, and **evidence-backed review findings**.
- Analysis works offline, uses only the Python standard library, does not require an API key, and never modifies its input.

## Install as an Agent Skill

Requires Python 3.10+ to analyze CSV files. Installation with the [Skills CLI](https://github.com/vercel-labs/skills) also requires Node.js 22.20+ and Git, with internet access to download the skill.

### Using CLI

Run this command from the project where you want to use the skill:

```bash
npx skills add dewdew978/data-detective-skill --skill data-detective
```

Follow the prompts to choose your AI agent. To install at user level and use the skill across projects, add `-g`:

```bash
npx skills add dewdew978/data-detective-skill --skill data-detective -g
```

Check the installed skills with `npx skills list`, or `npx skills list -g` for a user-level installation. See the [Skills CLI reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) for agent selection and other options.

### Manual installation

Download or clone this repository, then copy the entire `skills/data-detective/` folder into your agent's documented skills directory. Keep `SKILL.md`, `scripts/`, and `references/` together. This method does not require Node.js or the Skills CLI.

## Use with your AI agent

After installing the skill, give your agent the CSV path and ask:

> Use Data Detective to inspect my CSV. First give the verified data quality findings, then describe distributions and ask only the questions needed for interpretation. Do not change my data.

The agent runs the analysis and reads the generated reports. Analysis runs locally and does not require an API key for Data Detective.

## Run the analyzer directly (optional)

To run the bundled analyzer yourself, clone or download this repository and run from its root:

```bash
python skills/data-detective/scripts/analyze.py examples/sample.csv --output-dir output
```

Open `output/report.md` or read `output/report.json`.

Options: `--max-rows 1000`, `--no-charts`. Use `--help` to see all options.

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
