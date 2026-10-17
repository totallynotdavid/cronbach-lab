# Usage

## Install

The project requires Python 3.11 or newer. The repository's `mise.toml` pins
Python and [uv](https://docs.astral.sh/uv/), and `mise run install` installs the
locked dependencies:

```sh
mise install
mise run install
```

## Run the lab

Run all 13 scenarios with the default settings:

```sh
uv run cronbach-lab run
```

Use a different output directory, replicate count, or seed when exploring a
change:

```sh
uv run cronbach-lab run --out "$TMPDIR/cronbach-lab-run" --reps 100 --seed 7
```

`--reps` is the requested number of simulated samples for a scenario setting.
Most settings use that count; `bootstrap_interval` uses `max(reps // 5, 1)`. For
`run`, `--seed` initializes separate NumPy generators for the scenario results
and dataset generation. The default output directory is `results/`.

See all flags with:

```sh
uv run cronbach-lab run --help
```

## Write cross-check datasets

The `datasets` command writes the CSV inputs and the Python alpha reference
without running scenarios, plots, findings, or workbooks:

```sh
uv run cronbach-lab datasets --out "$TMPDIR/cronbach-lab-datasets" --seed 1
```

The default directory is `results/datasets/`. Use the same seed when comparing
two generated datasets.

## Compare Python with R

The cross-check requires R and the `psych` package. It uses
`check.keys = FALSE`, matching Python's behavior: it does not automatically
reverse items with negative correlations.

```sh
Rscript r/crosscheck.R "$TMPDIR/cronbach-lab-datasets"
```

Pass one CSV instead to print `psych::alpha` for that file:

```sh
Rscript r/crosscheck.R "$TMPDIR/cronbach-lab-datasets/equal_k5_n200.csv"
```

The directory form exits with status 1 when a raw or standardized alpha differs
from Python by more than `1e-6`. The single-CSV form only prints `psych::alpha`
and exits 0. The test suite runs the directory comparison when both `Rscript`
and `psych` are available; otherwise the two R tests are skipped.
