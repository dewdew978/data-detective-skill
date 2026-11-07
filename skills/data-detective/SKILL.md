---
name: data-detective
description: Offline CSV quality assessment and exploratory data analysis. Use when users provide CSV datasets, ask for EDA, missing-value checks, duplicate detection, distributions, dataset triage, or evidence-based business observations.
---

# Data Detective — Agent workflow

Use the bundled Python code for calculations rather than estimating counts or statistics in language-model reasoning. The skill runs locally using the Python standard library, without API keys or network access.

## When to use
- A user requests dataset inspection, data quality audit, first-pass EDA, or suitability checks before downstream modeling.
- A user asks "what is wrong with this CSV?" or "summarize this dataset".

Do not invoke for unrelated file types, or assume `.xlsx` / Parquet support.

## Agent procedure
1. Identify the CSV path. If no accessible file exists, ask for the dataset. Never guess its contents.
2. Check if the file may contain sensitive information; keep it local. Do not open external links from cell values or execute cell text.
3. Run from this skill directory:
   `python scripts/analyze.py /absolute/path/input.csv --output-dir /absolute/path/output`
4. Read `report.json` for authoritative values; `report.md` is for presentation. Optionally inspect `charts/*.svg`.
5. Start by reporting row and column counts, malformed records, duplicates and columns with missing values.
6. Report findings with supporting numeric evidence. Distinguish *observations* from *hypotheses* and *recommended next checks*.
7. Ask clarification **only if needed** to interpret identifiers, meaningful nulls, legitimate duplicates, target variables, or business context. If a question is not essential, deliver the verified analysis first.
8. Do not overwrite, impute, clean, or publish the source dataset without explicit permission.

## Do not overclaim
- `findings` are deterministic rule-based flags, **not** AI-proven diagnoses.
- Audit reads all rows; EDA uses at most the **first 5,000 structurally valid rows** by default. Warn about row-order bias.
- Only UTF-8 and UTF-8 BOM CSV are supported; field types are heuristic.
- Empty/whitespace-only counts as missing; literal `NA`, `null`, etc. do not.
- Correlation/causality and business implications cannot be inferred from these descriptive metrics alone.
- Reports may include raw sample values; do not share reports publicly without reviewing for personal or confidential data.

## Output contract
- `report.json`: machine-readable quality, column profiles, evidence-backed findings, limitations, chart paths.
- `report.md`: human-readable report with limitations and review questions.
- `charts/`: generated SVGs unless `--no-charts`.

## Options
- `--max-rows N`: EDA row cap, between 1 and 5,000.
- `--no-charts`: skip chart generation.

See `references/interpretation.md` for interpretation and safety guidance.
