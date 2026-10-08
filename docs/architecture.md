# Architecture

`cronbach-lab` is a seeded simulation pipeline. The CLI builds one results table
from the scenarios and sends it, along with the seeded datasets, to separate
output writers:

```text
cli.py
  ├── scenarios.py ── generate.py, survey.py, profiles.py, alpha.py
  │                    └── results table
  ├── report.py ────── plots and findings.md
  ├── datasets.py ──── scenarios.py settings and profile draws
  │                    └── CSV datasets and python_alpha.csv
  └── excel.py ─────── responses and reliability workbooks
```

## Command boundary

[`cli.py`](../src/cronbach_lab/cli.py) owns command parsing and output
directories. `run` executes all scenarios, writes `results.csv`, plots,
findings, datasets, and workbooks. `datasets` draws only the cross-check data
and writes CSV files.

## Simulation boundary

[`generate.py`](../src/cronbach_lab/generate.py) turns latent traits into
continuous item scores, applies cutpoints and response styles, and produces
Likert responses. It also owns reverse-keying and the random-responder and
straight-liner substitutions.

[`survey.py`](../src/cronbach_lab/survey.py) defines the two survey scales,
their item names, factor indexes, and assumed factor correlations.

[`profiles.py`](../src/cronbach_lab/profiles.py) defines the `lima` and
`california` simulation profiles and adapts the generator to their cutpoints and
response styles.

## Analysis boundary

[`alpha.py`](../src/cronbach_lab/alpha.py) implements raw alpha, standardized
alpha, alpha-if-dropped, and percentile bootstrap intervals. It does not choose
items or automatically reverse-score them.

[`scenarios.py`](../src/cronbach_lab/scenarios.py) owns the experimental
settings and uses `alpha.py` to summarize repeated samples. It does not write
files. Each scenario returns rows. `run_all` combines them into a pandas
DataFrame.

## Output boundary

[`report.py`](../src/cronbach_lab/report.py) turns the results table into PNG
plots and the generated findings document.
[`datasets.py`](../src/cronbach_lab/datasets.py) writes CSV inputs and the
Python reference values. [`excel.py`](../src/cronbach_lab/excel.py) writes the
workbook sheets and filenames. [`r/crosscheck.R`](../r/crosscheck.R) is a
separate verification tool: it reads the CSVs and compares them with
`psych::alpha`.

Tests exercise the numerical functions, generators, output writers, complete
pipeline, and optional R comparison. The test suite is under
[`tests/`](../tests/).
