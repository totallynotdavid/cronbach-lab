# cronbach-lab

Stress-test Cronbach's alpha on a simulated Likert survey (Python via uv, R
cross-check).

The lab simulates respondents to a restaurant survey, computes Cronbach's alpha,
and shows when alpha passes the usual 0.7 mark, when it fails, and why. The code
is small and commented on the statistics so it can be read while learning about
reliability instruments.

The survey it models (Spanish): 5-point Likert answers (Nunca = 1 .. Siempre
= 5) and four age groups (18-29, 30-39, 40-49, 50+).

- **Marketing Sensorial**: 15 items in 5 dimensions of 3 (vista, tacto, olfato,
  oido, gusto).
- **Satisfaccion al cliente**: 13 items in 3 dimensions (entusiasta 5, apatico
  4, problematico 4). Apatico and problematico behave differently from
  entusiasta, so pooling all 13 items as one scale is a deliberate stress case.

The correlations between dimensions are assumptions of the simulation, not
measurements of the real survey.

## Run

Needs [uv](https://docs.astral.sh/uv/).

```sh
uv sync
uv run pytest                 # tests
uv run cronbach-lab run       # about a minute
```

`cronbach-lab run` writes to `results/` (change with `--out`; `--reps` sets the
replicates per setting, default 1000; `--seed` the random seed, default 1):

| Output                   | Content                                                                          |
| ------------------------ | -------------------------------------------------------------------------------- |
| `results/results.csv`    | one row per setting: mean alpha, 2.5-97.5% band, share of runs with alpha >= 0.7 |
| `results/plots/*.png`    | one plot per scenario                                                            |
| `results/findings.md`    | the edges and the reasons, with numbers from the run                             |
| `results/datasets/*.csv` | simulated datasets for the R cross-check                                         |

`results/` is committed for reading. Rerunning with the same seed reproduces it.

## Layout

| File                            | Role                                                                |
| ------------------------------- | ------------------------------------------------------------------- |
| `src/cronbach_lab/generate.py`  | latent-trait generator, cutpoints, reverse keys, bad respondents    |
| `src/cronbach_lab/alpha.py`     | raw alpha, standardized alpha, alpha-if-dropped, bootstrap interval |
| `src/cronbach_lab/survey.py`    | the survey's dimensions and assumed factor correlations             |
| `src/cronbach_lab/scenarios.py` | the scenarios below                                                 |
| `src/cronbach_lab/report.py`    | plots and `findings.md`                                             |
| `r/crosscheck.R`                | R cross-check against `psych::alpha`                                |

## The model

Respondent trait `theta` (one per factor); item = discretize(`loading * theta` +
noise) onto 1-5 with configurable cutpoints, so answers can be skewed or hit the
ceiling. Items have unit variance before cutting, so the loading is the
item-trait correlation. Optional per-age-group shifts in theta or loadings,
reverse-keyed items, one factor per dimension, and bad respondents (random
answers, straight-lining). The RNG is seeded.

## Scenarios

Each is replicated about 1000 times (bootstrap: 200). Rows report mean alpha,
the 2.5-97.5% band and the share of runs with alpha >= 0.7.

1. `loading_items`: loading 0.2 to 0.9 with 3, 5 and 15 items.
2. `sample_size`: n = 20, 50, 100, 400.
3. `response_shape`: symmetric, skewed high, skewed low, ceiling answers.
4. `satisfaccion`: 13 items pooled, each dimension alone, apatico
   reverse-scored, apatico and problematico reverse-scored.
5. `multidimensional`: Marketing Sensorial pooled as one 15-item scale, with
   dimensions correlated from 0 to 0.6. Alpha stays high without
   unidimensionality.
6. `age_groups`: alpha per age group versus pooled, with equal or different
   loadings and with group differences in the trait mean.
7. `bad_items`: random responders, straight-liners, a pure-noise item and one
   wrongly reversed item, with alpha-if-dropped flagging the planted item.
8. `bootstrap_interval`: width and coverage of the 95% bootstrap interval.

## R cross-check

Python does not use R. The check confirms the Python alpha against
`psych::alpha` on several generated datasets (tolerance 1e-6).

Install R and psych on Ubuntu:

```sh
sudo apt-get install r-base-core r-cran-psych
```

Then:

```sh
uv run cronbach-lab run                          # or: uv run cronbach-lab datasets
Rscript r/crosscheck.R results/datasets          # compare all datasets, exit 1 on mismatch
Rscript r/crosscheck.R results/datasets/equal_k5_n200.csv   # one dataset: print raw and standardized alpha
```

`uv run pytest` runs the same check when `Rscript` and `psych` are present, and
skips it otherwise.
