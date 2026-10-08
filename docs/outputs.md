# Outputs

The `run` command writes this layout below its `--out` directory:

```text
results/
├── results.csv
├── findings.md
├── plots/
├── datasets/
└── xlsx/
```

The repository keeps a generated `results/` tree so readers can inspect an
example without running the full lab.

## Results table

`results.csv` has one row per scenario setting. The common columns are:

| Column                | Meaning                                                           |
| --------------------- | ----------------------------------------------------------------- |
| `scenario`, `setting` | The experiment and its setting label                              |
| `k`, `n`, `loading`   | Item count, respondent count, and nominal loading when applicable |
| `reps`                | Number of simulated samples summarized                            |
| `mean_alpha`          | Mean raw Cronbach's alpha                                         |
| `p2_5`, `p97_5`       | 2.5th and 97.5th percentiles of raw alpha                         |
| `share_ge_0_7`        | Share of samples with raw alpha at least 0.7                      |
| `mean_std_alpha`      | Mean standardized alpha                                           |

Scenario-specific columns add these values when the scenario uses them:

| Column                                           | Meaning                                                                                      |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| `flag_rate`                                      | Share of replicates where the item with the highest alpha-if-dropped is the planted bad item |
| `mean_alpha_dropped`                             | Mean alpha after dropping the planted bad item                                               |
| `true_alpha`                                     | Alpha from the same setting simulated with 200,000 respondents                               |
| `false_pass`                                     | Share of replicates at or above 0.7 when `true_alpha` is below 0.7; otherwise 0              |
| `false_fail`                                     | Share of replicates below 0.7 when `true_alpha` is at least 0.7; otherwise 0                 |
| `ci_reps`                                        | Number of replicates for which a bootstrap interval was computed                             |
| `mean_ci_width`, `median_ci_width`               | Mean and median width of those intervals                                                     |
| `share_ci_lower_ge_0_7`                          | Share of intervals whose lower bound is at least 0.7                                         |
| `ci_coverage`                                    | Share of intervals containing `true_alpha`                                                   |
| `scale`, `profile`, `style`, `strength`, `group` | Labels and settings for profile, response-style, and small-group rows                        |

## Plots and findings

`plots/` contains 13 PNGs, one for each scenario. The loading and response-style
plots use lines. Scenario plots use horizontal bars with percentile whiskers,
and the small-group plot uses points with percentile error bars. The loading,
bar, and small-group plots use a dashed 0.7 reference line; the response-style
plot uses a dotted 0.7 reference line.

`findings.md` is generated from the results table. It explains the scenario
tables and records the numbers from that run. It is the source for the
interpretation of a particular generated run, not a second configuration for the
simulator.

## Datasets

`datasets/` contains 21 simulated input CSVs and `python_alpha.csv`, the
reference table of Python raw and standardized alpha. The input CSVs cover the
seven general datasets, two location-profile datasets, and 12 samples of 50
respondents used by the small-group workbooks.

The CSV files are the inputs to [`r/crosscheck.R`](../r/crosscheck.R). The
script compares every CSV with `psych::alpha` and uses a tolerance of `1e-6`.

## Excel workbooks

`xlsx/` contains 26 workbooks: one for each of the 21 CSV datasets, one pooled
age-group workbook, and one workbook for each of the four age groups. A file
name includes the raw alpha rounded to three decimals.

Each workbook has two sheets:

- `responses` contains one row per respondent and one column per item. The age
  workbooks also include `age_group`.
- `reliability` contains raw alpha, standardized alpha, item and respondent
  counts, and alpha-if-dropped for every item.
