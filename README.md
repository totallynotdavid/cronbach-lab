# cronbach-lab

`cronbach-lab` is a Python lab that simulates five-point Likert survey data and
measures Cronbach's alpha under different item, respondent, and response-style
conditions. It does not estimate the reliability of a real questionnaire, and
its Python run does not require R.

Install the pinned tools and the locked dependencies with
[mise](https://mise.jdx.dev/):

```sh
mise install
mise run install
```

Write the datasets used by the R cross-check:

```sh
uv run cronbach-lab datasets --out "$TMPDIR/cronbach-lab-datasets"
```

Run every scenario and write the complete report:

```sh
uv run cronbach-lab run
```

The run accepts `--out` for the output directory, `--reps` for the requested
replicate count (default `1000`; `bootstrap_interval` uses `max(reps // 5, 1)`),
and `--seed` for the random seed (default `1`).

The lab:

- compares raw and standardized alpha, alpha-if-dropped, and percentile
  bootstrap intervals;
- varies loadings, item counts, sample sizes, response shapes, dimensions,
  age-group measurement, bad items, and response styles;
- writes CSV data, plots, findings, and Excel workbooks; and
- writes datasets that an optional R script can cross-check against
  `psych::alpha` when R and `psych` are installed.

Read the [manual](docs/readme.md) for commands, the simulated survey, scenarios,
and generated files. Contributors can start with
[contributing](.github/contributing.md).
