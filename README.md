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
uv run cronbach-lab run       # about 90 seconds
```

With [mise](https://mise.jdx.dev/) the tools are pinned in `mise.toml`:

```sh
mise run test      # pytest, including the R cross-check when R and psych are present
mise run lint      # ruff check
mise run format    # ruff format --line-length 100
mise run check     # lint, then test
```

`cronbach-lab run` writes to `results/` (change with `--out`; `--reps` sets the
replicates per setting, default 1000; `--seed` the random seed, default 1):

| Output                   | Content                                                                          |
| ------------------------ | -------------------------------------------------------------------------------- |
| `results/results.csv`    | one row per setting: mean alpha, 2.5-97.5% band, share of runs with alpha >= 0.7 |
| `results/plots/*.png`    | one plot per scenario                                                            |
| `results/findings.md`    | the edges and the reasons, with numbers from the run                             |
| `results/datasets/*.csv` | simulated datasets for the R cross-check                                         |
| `results/xlsx/*.xlsx`    | one Excel workbook per group of respondents, alpha in the file name              |

`results/` is committed for reading. Rerunning with the same seed reproduces it.

### Excel workbooks

Each of the 9 datasets (the 7 general ones plus one per profile,
`lima_marketing_sensorial` and `california_marketing_sensorial`) gets a workbook
named `<dataset>_alpha<raw alpha>.xlsx`, for example
`equal_k5_n200_alpha0.647.xlsx`. The age-group dataset (four groups of 100,
loadings 0.8, 0.7, 0.5 and 0.3 from 18-29 to 50+) adds one workbook per age
group and one pooled: `age_groups_pooled_alpha...`, `age_groups_18-29_alpha...`,
`age_groups_30-39_alpha...`, `age_groups_40-49_alpha...` and
`age_groups_50plus_alpha...`.

| Sheet         | Content                                                                                                     |
| ------------- | ----------------------------------------------------------------------------------------------------------- |
| `responses`   | one row per respondent, one column per item, plus `age_group` for the age-group workbooks                   |
| `reliability` | raw alpha, standardized alpha, number of items, number of respondents, and the alpha with each item dropped |

## Layout

| File                            | Role                                                                |
| ------------------------------- | ------------------------------------------------------------------- |
| `src/cronbach_lab/generate.py`  | latent-trait generator, cutpoints, reverse keys, bad respondents    |
| `src/cronbach_lab/alpha.py`     | raw alpha, standardized alpha, alpha-if-dropped, bootstrap interval |
| `src/cronbach_lab/survey.py`    | the survey's dimensions and assumed factor correlations             |
| `src/cronbach_lab/scenarios.py` | the scenarios below                                                 |
| `src/cronbach_lab/profiles.py`  | the assumed lima and california profiles                            |
| `src/cronbach_lab/report.py`    | plots and `findings.md`                                             |
| `src/cronbach_lab/datasets.py`  | the simulated datasets                                              |
| `src/cronbach_lab/excel.py`     | the Excel workbooks                                                 |
| `r/crosscheck.R`                | R cross-check against `psych::alpha`                                |

## The model

Respondent trait `theta` (one per factor); item = discretize(`loading * theta` +
noise) onto 1-5 with configurable cutpoints, so answers can be skewed or hit the
ceiling. Items have unit variance before cutting, so the loading is the
item-trait correlation. Optional per-age-group shifts in theta or loadings,
reverse-keyed items, one factor per dimension, and bad respondents (random
answers, straight-lining). The RNG is seeded.

Two response styles are traits of the respondent, drawn with the latent trait.
Acquiescence is a tendency to agree that shifts the answer to every item the
same way, and half as much on a reverse-keyed item. Extreme response style is a
gain on the respondent's score that pushes answers toward 1 and 5. Both are off
by default.

### Location profiles (assumed)

A profile in `profiles.py` bundles the answer shares that set the cutpoints, an
extreme-response strength, an acquiescence strength and a loading. `lima` has
more answers on 4-5 and on both extremes, with strong styles and loading 0.7.
`california` is more moderate (more 3s and 4s, still skewed toward agreement),
with weaker styles and loading 0.6. **Every one of these numbers is an
assumption**, chosen to show what response habits can do to alpha. None comes
from real Lima or California respondents.

The shares are those the cutpoints give before the styles act. Extreme
responding pushes answers to 1 and 5, so the shares actually produced differ a
little; `findings.md` prints both.

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
9. `profiles`: Marketing Sensorial, Satisfaccion as is and Satisfaccion with
   apatico and problematico reverse-scored, for each profile and both pooled.
   The apatico and problematico items are answered on the flipped scale, so "as
   is" and "recoded" score the same kind of answers two ways.
10. `profiles_same_loading`: the same, with one loading for both profiles, so
    only cutpoints and response style differ.
11. `response_style`: alpha as the extreme-response or acquiescence strength
    grows from 0 to 1.

## R cross-check

Python does not use R. The check confirms the Python alpha against
`psych::alpha` on every generated dataset (tolerance 1e-6), including a lima and
a california one.

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
