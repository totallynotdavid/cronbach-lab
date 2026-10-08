# Scenarios

`cronbach-lab run` executes the functions listed in `SCENARIOS` in
[`scenarios.py`](../src/cronbach_lab/scenarios.py). Unless noted, each setting
uses the requested `--reps` count, a fresh simulated sample per replicate, and
reports mean raw alpha, its 2.5th-to-97.5th percentile band, the share of runs
at or above 0.7, and mean standardized alpha.

1. **Loading and item count** — loadings from 0.20 through 0.90 in 0.05 steps,
   with 3, 5, or 15 items and 200 respondents.
2. **Sample size** — 20, 50, 100, or 400 respondents, with 5 items and loadings
   0.5, 0.6, or 0.7.
3. **Response shape** — symmetric, skewed high, skewed low, or ceiling-heavy
   category shares, with 5 items and loadings 0.5 or 0.7.
4. **Satisfaccion** — the 13 items pooled as given, each dimension alone, and
   the pooled scale after reverse-scoring `apatico` or both `apatico` and
   `problematico`.
5. **Multidimensionality** — one 3-item dimension and all 15 Marketing Sensorial
   items, with factor correlations 0.0, 0.2, 0.4, or 0.6.
6. **Age groups** — four groups of 100 respondents, scored within group and
   pooled, with equal or different loadings and optional trait-mean shifts. The
   different loadings are 0.8, 0.7, 0.5, and 0.3 from youngest to oldest.
7. **Bad items and respondents** — a clean 8-item scale, 20% random responders,
   20% straight-liners, one noise item, one unrecoded reversed item, and one
   recoded reversed item. The planted-item cases report how often
   alpha-if-dropped identifies the planted item.
8. **Bootstrap interval** — 5 items at loading 0.7, with 20, 50, 100, or 400
   respondents. It runs `max(reps // 5, 1)` simulated samples per setting, uses
   500 bootstrap resamples per sample, and compares the interval with alpha from
   a 200,000-respondent simulated sample.
9. **Profiles** — Marketing Sensorial and Satisfaccion as given or recoded for
   the `lima` profile, the `california` profile, and both profiles pooled. The
   profiles keep their assumed cutpoints, styles, and loadings.
10. **Profiles with one loading** — the same profile comparison with both
    profiles assigned nominal loading 0.7.
11. **Response style** — extreme response and acquiescence strength from 0 to 1
    in 0.25 steps, one style at a time, for both profiles and all three scales.
12. **Style versus cutpoints** — Marketing Sensorial with the shared nominal
    loading, once with shared symmetric cutpoints and each profile's styles, and
    once with each profile's cutpoints and no styles.
13. **Small groups** — group sizes 30, 40, 50, and 200 for the two location
    profiles and four age groups, on Marketing Sensorial and recoded
    Satisfaccion. Each row includes the population alpha from 200,000
    respondents, false-pass and false-fail rates, and bootstrap interval width
    and coverage. Its bootstrap runs use 500 resamples on the first tenth of the
    requested replicates, rounded down but never below one.

The generated explanation and tables are written to `findings.md`; the
machine-readable rows are written to `results.csv`. See [outputs](outputs.md).
