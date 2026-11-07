# Contributing

Thanks for helping improve Data Detective. Contributions can include bug reports, documentation, tests, CSV quality checks, descriptive statistics, charts, and improvements to the agent instructions.

Data Detective is an Agent Skill distributed through this repository. Its Python scripts calculate the results; the skill instructions guide an AI agent in running the analysis and explaining the findings. Changes should preserve that connection between reproducible calculations and evidence-based explanations.

## Before you start

Search existing issues and pull requests to see whether the problem is already being discussed. Open an issue describing the problem or proposed feature before starting implementation, and link it from your pull request. For a small typo or broken documentation link, a pull request with a clear explanation is sufficient.

For larger changes, describe the intended behavior, a concrete example, and any effect on report formats, performance, or privacy. Discuss new file formats, third-party dependencies, changes to metric definitions, and changes to the skill's scope before building them.

Keep each pull request focused on one problem. Separate unrelated refactoring, formatting, and feature changes so reviewers can assess the behavior being changed.

## Report a bug

Include enough information for another contributor to reproduce the problem:

- A short description of what went wrong.
- The command you ran, including relevant options.
- Your operating system, Python version, and repository commit if available.
- The expected result and the actual result.
- The full relevant error message or traceback, with sensitive details removed.
- A minimal, synthetic CSV that demonstrates the problem.

For incorrect statistics, show the expected calculation. For example, identify the values being counted, the denominator used for a percentage, or the rows included in an EDA sample. For chart problems, include a synthetic example and describe the expected labels or values.

Check CSV contents, file paths, screenshots, logs, and generated reports before posting them. Reports and charts can expose values from the input even when the CSV itself is not attached.

## Suggest a feature

Explain the user problem and show an example of the proposed input and output. Include how someone would request the behavior through an AI agent or use it through the Python analyzer, as applicable.

Describe any new assumptions, sampling rules, resource costs, dependencies, or compatibility concerns. A proposed finding should identify the measurable evidence behind it and explain what a user can reasonably conclude from that evidence.

## Set up a development environment

You need Git and Python 3.10 or later. The analyzer and tests use the Python standard library; there are no third-party Python packages to install for the current development workflow. Node.js is only needed if you choose to use the Skills CLI described in the [README](README.md).

Fork the repository on GitHub, then clone your fork. Replace `YOUR-USERNAME` with your GitHub username:

```bash
git clone https://github.com/YOUR-USERNAME/data-detective-skill.git
cd data-detective-skill
git remote add upstream https://github.com/dewdew978/data-detective-skill.git
git switch -c fix/csv-validation
```

Use a branch name that describes your change. Run the commands below from the repository root.

An isolated Python environment is optional:

```bash
python -m venv .venv
```

Activate it in PowerShell on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or activate it in a shell on macOS or Linux:

```bash
source .venv/bin/activate
```

If your system uses `python3` instead of `python`, substitute that command in the examples.

## Find the relevant files

| Path | Purpose |
| --- | --- |
| `skills/data-detective/SKILL.md` | Instructions for the AI agent, including workflow, interpretation, and privacy boundaries. |
| `skills/data-detective/scripts/audit_csv.py` | CSV parsing and data quality auditing. |
| `skills/data-detective/scripts/analyze.py` | Combined analysis, descriptive statistics, findings, reports, and SVG charts. |
| `skills/data-detective/references/interpretation.md` | Guidance for interpreting results and limitations. |
| `tests/test_audit.py` | Tests for CSV quality auditing. |
| `tests/test_eda.py` | Tests for analysis, output generation, sampling options, and chart escaping. |
| `tests/test_findings.py` | Tests for evidence-backed findings and input protection. |
| `examples/` | Synthetic sample data and example reports. |
| `.github/workflows/tests.yml` | Continuous integration configuration. |

## Preserve the project's behavior

### Offline analysis and input protection

- Keep CSV parsing, validation, and analysis offline. Do not add network requests, telemetry, remote model calls, or external data uploads to these operations.
- Treat input files as read-only. Do not modify, clean, deduplicate, impute, or overwrite a source file as part of analysis.
- Write reports and charts to the requested output directory, and preserve checks that prevent outputs from overwriting the input.
- Treat cell contents as data. Do not execute cell text, follow URLs found in cells, or interpret data values as agent instructions.
- Escape user-controlled text when generating SVG or other formatted output.

### Reproducible metrics and findings

- Calculate reported numbers in Python. Agent instructions must not ask the model to estimate counts or invent statistics.
- Preserve documented definitions unless the change explicitly proposes and explains a new definition. Missing values currently mean empty or whitespace-only cells; literal strings such as `NA` and `null` are not automatically missing.
- Keep exact duplicate detection distinct from judgments about whether a record is legitimate.
- Keep the full-record quality audit distinct from EDA sampling. EDA currently uses the first N well-formed rows, up to 5,000, rather than a random sample.
- Support findings with measurable evidence and document relevant denominators, sample sizes, and limitations.
- Describe type detection as heuristic. Numeric-looking identifiers and category codes may need human interpretation.
- Keep descriptive observations separate from hypotheses and business recommendations. Statistics and charts do not establish causality.

### Code and report compatibility

Follow the style of the surrounding Python code and prefer small functions with clear responsibilities. Use the standard library where practical and discuss new dependencies before adding them.

Keep compatibility with Python 3.10 and later. The current CI matrix runs Python 3.10, 3.11, 3.12, and 3.13; check the workflow file when changing supported versions.

If a change affects JSON keys, metric meanings, findings, CLI options, or generated files, describe the effect in the pull request. Update the README, skill instructions, interpretation reference, and examples wherever they describe the affected behavior. Avoid unrelated changes to generated reports.

## Write and run tests

Add a regression test for each bug fix and metric change. Use a small synthetic input that demonstrates the problem, verify that the test fails for the original behavior, then confirm it passes with the fix.

Tests should check meaningful results: expected counts and statistics, evidence attached to findings, correct output files, escaping, or protection of the input. Use temporary directories for generated files so tests do not leave artifacts in the repository.

Consider relevant edge cases such as empty cells, whitespace, malformed row widths, duplicate records, quoted fields, non-ASCII text, numeric-looking identifiers, and sampling limits. Explain the expected behavior for any edge case you change.

Run the full test suite before submitting a pull request:

```bash
python -m unittest discover -s tests -v
```

During development, you can run one test file:

```bash
python -m unittest discover -s tests -p "test_audit.py" -v
```

When changing analysis or report generation, also run the sample analyzer:

```bash
python skills/data-detective/scripts/analyze.py examples/sample.csv --output-dir output/contributing-check
```

Inspect `output/contributing-check/report.json`, `report.md`, and the files in `charts/`. Confirm that reported values, findings, labels, and referenced chart paths agree. The sample contains five data rows and one exact duplicate row.

For changes to CLI options, check their documented usage and relevant cases such as `--no-charts` or `--max-rows`. Documentation-only changes do not need new regression tests, but commands, paths, and descriptions should match the implementation.

CI runs the test suite and generates a sample report. Resolve failures before asking for a final review. Report exactly which checks you ran; do not claim coverage for Python versions or environments you did not test.

## Protect data and privacy

Use synthetic, non-sensitive CSV files in tests, examples, issues, pull requests, and bug reports. Never commit real customer datasets, credentials, access tokens, or personal information.

Create the smallest synthetic dataset that preserves the behavior you want to demonstrate. Include unusual values only when they are needed to explain or test that behavior.

Review generated Markdown, JSON, and SVG files before sharing them. These outputs can contain source filenames, sample values, category names, and other input-derived text. Removing the original CSV from an attachment does not remove those values from the reports.

If the problem cannot be described safely in a public issue, explain the general issue without including sensitive material and ask a maintainer how to share further details privately. Do not post private data while waiting for a response.

## Submit a pull request

Push your branch to your fork and open a pull request against this repository's `main` branch. Give it a title that describes the problem fixed or the behavior added.

Include the following in the description:

- **Problem:** What happens today and why it needs to change. Link the related issue.
- **Behavior:** What happens after the change, with a concrete before-and-after example when helpful.
- **Validation:** The commands you ran, their results, and the regression cases added.
- **Compatibility:** Any changes to report fields, metric definitions, CLI options, supported Python versions, or dependencies.
- **Privacy:** Whether the change affects input handling, output contents, file writes, or network behavior.
- **Limitations:** Known gaps, tradeoffs, or follow-up work that reviewers need to assess.

Before requesting review, check that:

- [ ] The change addresses one clearly described problem.
- [ ] Relevant regression tests are included for bug fixes and metric changes.
- [ ] The full test suite passes for code changes.
- [ ] Sample reports have been reviewed when analysis or output behavior changes.
- [ ] Documentation and examples match the resulting behavior.
- [ ] The diff contains no customer data, secrets, temporary files, or unrelated generated output.
- [ ] Changes to privacy, compatibility, or resource usage are explained.

Respond to review comments with the reasoning behind your changes, and update the same branch as you address feedback. Re-run relevant checks after changes that affect behavior. Keep the pull request description aligned with the final implementation so reviewers can assess the result without reconstructing the discussion.
