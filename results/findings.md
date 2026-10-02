# Findings: when Cronbach's alpha passes 0.7, and why it fails

Every number below comes from `cronbach-lab run` (1000 replicates per setting,
each a fresh simulated sample). "Mean alpha" is the mean raw alpha over the
replicates, the band is the 2.5th to 97.5th percentile of alpha across
replicates, and "runs >= 0.7" is the share of replicates whose alpha reached
0.7.

Unless a section says otherwise: 200 respondents, 5 items, equal loadings,
symmetric 5-point answers (10/20/40/20/10% for 1..5). Loadings are the
correlation between an item and its latent trait.

## 1. Loading and number of items

For equal loadings, standardized alpha is k*rho/(1+(k-1)*rho) with rho = loading
squared, so alpha depends only on the loading and the item count. Smallest
loading on the 0.05 grid that reaches 0.7:

| items | theory (continuous items) | mean alpha >= 0.7 | >= 90% of runs >= 0.7 |
| ----- | ------------------------- | ----------------- | --------------------- |
| 3     | 0.66                      | 0.70              | 0.75                  |
| 5     | 0.56                      | 0.60              | 0.65                  |
| 15    | 0.37                      | 0.40              | 0.45                  |

Rule of thumb at 200 respondents: 3 items: loading >= 0.70 on average, >= 0.75
in 9 of 10 samples; 5 items: loading >= 0.60 on average, >= 0.65 in 9 of 10
samples; 15 items: loading >= 0.40 on average, >= 0.45 in 9 of 10 samples.

Mean alpha (share of runs >= 0.7) by loading and number of items:

| loading | 3 items     | 5 items     | 15 items    |
| ------- | ----------- | ----------- | ----------- |
| 0.20    | 0.09 (0%)   | 0.15 (0%)   | 0.35 (0%)   |
| 0.25    | 0.15 (0%)   | 0.22 (0%)   | 0.47 (0%)   |
| 0.30    | 0.20 (0%)   | 0.30 (0%)   | 0.57 (0%)   |
| 0.35    | 0.27 (0%)   | 0.38 (0%)   | 0.65 (7%)   |
| 0.40    | 0.33 (0%)   | 0.46 (0%)   | 0.72 (75%)  |
| 0.45    | 0.40 (0%)   | 0.53 (0%)   | 0.77 (100%) |
| 0.50    | 0.46 (0%)   | 0.59 (0%)   | 0.81 (100%) |
| 0.55    | 0.53 (0%)   | 0.65 (8%)   | 0.85 (100%) |
| 0.60    | 0.59 (0%)   | 0.71 (61%)  | 0.88 (100%) |
| 0.65    | 0.65 (12%)  | 0.76 (96%)  | 0.90 (100%) |
| 0.70    | 0.71 (61%)  | 0.80 (100%) | 0.92 (100%) |
| 0.75    | 0.76 (97%)  | 0.84 (100%) | 0.94 (100%) |
| 0.80    | 0.81 (100%) | 0.88 (100%) | 0.95 (100%) |
| 0.85    | 0.86 (100%) | 0.91 (100%) | 0.97 (100%) |
| 0.90    | 0.90 (100%) | 0.94 (100%) | 0.98 (100%) |

Why: alpha rises with the item count even when each item is weak, because adding
items adds shared variance faster than error variance. A long scale can pass 0.7
with weak items and a short scale needs strong ones. Cutting 1-5 categories out
of a continuous score lowers the item correlations a little, so the simulated
edge sits slightly above the theoretical one.

## 2. Sample size

Alpha is a ratio of sample variances, so a small sample widens its spread rather
than shifting its centre much. The same scale can pass or fail by chance.

| setting            | mean alpha | 2.5-97.5% band | runs >= 0.7 |
| ------------------ | ---------- | -------------- | ----------- |
| n=20, loading=0.5  | 0.55       | 0.14 to 0.79   | 17%         |
| n=50, loading=0.5  | 0.59       | 0.37 to 0.74   | 10%         |
| n=100, loading=0.5 | 0.59       | 0.44 to 0.70   | 3%          |
| n=400, loading=0.5 | 0.59       | 0.53 to 0.65   | 0%          |
| n=20, loading=0.6  | 0.68       | 0.36 to 0.85   | 50%         |
| n=50, loading=0.6  | 0.70       | 0.55 to 0.81   | 55%         |
| n=100, loading=0.6 | 0.70       | 0.60 to 0.78   | 55%         |
| n=400, loading=0.6 | 0.71       | 0.66 to 0.75   | 68%         |
| n=20, loading=0.7  | 0.78       | 0.57 to 0.89   | 86%         |
| n=50, loading=0.7  | 0.79       | 0.69 to 0.87   | 96%         |
| n=100, loading=0.7 | 0.80       | 0.73 to 0.85   | 99%         |
| n=400, loading=0.7 | 0.80       | 0.77 to 0.83   | 100%        |

## 3. Skewed and ceiling answers

Same latent structure, different cutpoints.

| setting                  | mean alpha | 2.5-97.5% band | runs >= 0.7 |
| ------------------------ | ---------- | -------------- | ----------- |
| symmetric, loading=0.5   | 0.59       | 0.49 to 0.67   | 0%          |
| skewed high, loading=0.5 | 0.58       | 0.48 to 0.66   | 0%          |
| skewed low, loading=0.5  | 0.58       | 0.47 to 0.66   | 0%          |
| ceiling, loading=0.5     | 0.50       | 0.36 to 0.62   | 0%          |
| symmetric, loading=0.7   | 0.80       | 0.76 to 0.84   | 100%        |
| skewed high, loading=0.7 | 0.79       | 0.74 to 0.83   | 100%        |
| skewed low, loading=0.7  | 0.79       | 0.74 to 0.83   | 100%        |
| ceiling, loading=0.7     | 0.74       | 0.64 to 0.81   | 82%         |

Moving the bulk of the answers to one end (35% in each of the two top or bottom
categories) lowers mean alpha by 0.02 at loading 0.5 and 0.01 at loading 0.7.
Putting 70% of the answers on "Siempre" (ceiling) lowers it by 0.10 and 0.06.
Alpha is built from covariance, and when nearly everyone gives the same answer
the items have little variance left to covary.

## 4. Satisfaccion al cliente: 13 items, 3 dimensions

Assumed structure (not measured): loading 0.7; the apatico and problematico
traits correlate negatively with entusiasta (-0.6 and -0.4) and positively with
each other (0.5). Pooling puts items that move in opposite directions into one
sum, so they cancel and alpha collapses.

| setting                                         | mean alpha | 2.5-97.5% band | runs >= 0.7 |
| ----------------------------------------------- | ---------- | -------------- | ----------- |
| pooled, 13 items as is                          | 0.44       | 0.31 to 0.54   | 0%          |
| entusiasta alone, 5 items                       | 0.80       | 0.75 to 0.84   | 100%        |
| apatico alone, 4 items                          | 0.76       | 0.70 to 0.81   | 98%         |
| problematico alone, 4 items                     | 0.76       | 0.71 to 0.81   | 98%         |
| pooled, apatico reverse-scored                  | 0.60       | 0.51 to 0.67   | 0%          |
| pooled, apatico and problematico reverse-scored | 0.84       | 0.80 to 0.87   | 100%        |

Pooled as is: mean alpha 0.44, 0% of runs pass. Each dimension alone: 0.80,
0.76, 0.76 (entusiasta, apatico, problematico). Reverse-scoring apatico alone
gives 0.60; reverse-scoring both gives 0.84. Reverse-scoring apatico alone
leaves problematico running against both of the other dimensions, so alpha stays
low until both are reversed. Pooling all 13 items as one scale only makes sense
once every item points the same way, and even then it treats three behaviours as
a single trait.

## 5. A multidimensional scale can still pass

Marketing Sensorial: 5 dimensions of 3 items, loading 0.7, dimensions correlated
by r.

| setting                                 | mean alpha | 2.5-97.5% band | runs >= 0.7 |
| --------------------------------------- | ---------- | -------------- | ----------- |
| one dimension alone, 3 items            | 0.71       | 0.63 to 0.77   | 61%         |
| pooled 15 items, factor correlation=0.0 | 0.50       | 0.39 to 0.60   | 0%          |
| pooled 15 items, factor correlation=0.2 | 0.71       | 0.64 to 0.76   | 59%         |
| pooled 15 items, factor correlation=0.4 | 0.80       | 0.76 to 0.84   | 100%        |
| pooled 15 items, factor correlation=0.6 | 0.86       | 0.83 to 0.89   | 100%        |

Five unrelated dimensions pooled give 0.50. With the dimensions correlated at
0.4 the pooled 15-item alpha is 0.80, 100% of runs >= 0.7, although the data
still have five factors. One dimension alone (3 items) gets 0.71, 61% of runs >=
0.7. Alpha rewards the number of items and the average correlation; it does not
test that one trait drives them all. A high alpha is not evidence of a single
dimension.

## 6. Age groups

Four age groups of 100 (400 respondents), 5 items. "Theta shifts" moves the
group means of the trait (+0.6, +0.2, -0.2, -0.6 standard deviations). Different
loadings: 0.8, 0.7, 0.5, 0.3 for 18-29, 30-39, 40-49, 50+.

| setting                                  | mean alpha | 2.5-97.5% band | runs >= 0.7 |
| ---------------------------------------- | ---------- | -------------- | ----------- |
| equal loadings: pooled                   | 0.71       | 0.66 to 0.75   | 65%         |
| equal loadings: 18-29                    | 0.71       | 0.60 to 0.79   | 60%         |
| equal loadings: 30-39                    | 0.70       | 0.60 to 0.78   | 56%         |
| equal loadings: 40-49                    | 0.70       | 0.60 to 0.78   | 57%         |
| equal loadings: 50+                      | 0.70       | 0.60 to 0.78   | 55%         |
| equal loadings, theta shifts: pooled     | 0.74       | 0.70 to 0.78   | 98%         |
| equal loadings, theta shifts: 18-29      | 0.70       | 0.59 to 0.78   | 54%         |
| equal loadings, theta shifts: 30-39      | 0.71       | 0.61 to 0.79   | 60%         |
| equal loadings, theta shifts: 40-49      | 0.71       | 0.60 to 0.79   | 60%         |
| equal loadings, theta shifts: 50+        | 0.70       | 0.60 to 0.79   | 55%         |
| different loadings: pooled               | 0.72       | 0.67 to 0.76   | 78%         |
| different loadings: 18-29                | 0.88       | 0.83 to 0.91   | 100%        |
| different loadings: 30-39                | 0.80       | 0.73 to 0.85   | 100%        |
| different loadings: 40-49                | 0.59       | 0.43 to 0.70   | 3%          |
| different loadings: 50+                  | 0.30       | 0.05 to 0.48   | 0%          |
| different loadings, theta shifts: pooled | 0.75       | 0.70 to 0.78   | 98%         |
| different loadings, theta shifts: 18-29  | 0.87       | 0.83 to 0.91   | 100%        |
| different loadings, theta shifts: 30-39  | 0.80       | 0.73 to 0.85   | 100%        |
| different loadings, theta shifts: 40-49  | 0.59       | 0.44 to 0.70   | 3%          |
| different loadings, theta shifts: 50+    | 0.29       | 0.05 to 0.48   | 0%          |

With different loadings the pooled alpha is 0.72, while the 18-29 group has 0.88
and the 50+ group 0.30. Pooling averages over groups, so one group measured
badly is hidden. Group differences in the trait mean add between-group variance
shared by all items, which raises pooled alpha even though no group's own alpha
changes. Check alpha per group before trusting the pooled value.

## 7. Bad items and respondents

8 items, loading 0.6, 200 respondents. "flag_rate" is the share of runs where
the item with the highest alpha-if-dropped is the planted bad item (item 1);
"mean_alpha_dropped" is alpha without that item.

| setting                        | mean alpha | 2.5-97.5% band | runs >= 0.7 | flag_rate | mean_alpha_dropped |
| ------------------------------ | ---------- | -------------- | ----------- | --------- | ------------------ |
| clean                          | 0.79       | 0.75 to 0.84   | 100%        |           |                    |
| 20% random responders          | 0.70       | 0.63 to 0.76   | 57%         |           |                    |
| 20% straight-liners            | 0.90       | 0.87 to 0.92   | 100%        |           |                    |
| one noise item (loading 0)     | 0.72       | 0.66 to 0.77   | 79%         | 1.00      | 0.77               |
| one reversed item, not recoded | 0.61       | 0.53 to 0.67   | 0%          | 1.00      | 0.77               |
| one reversed item, recoded     | 0.79       | 0.75 to 0.83   | 100%        |           |                    |

Clean scale: 0.79. A single reversed item that is not recoded gives 0.61 and
alpha-if-dropped flags it in 100% of runs; one pure-noise item gives 0.72,
flagged in 100%. Without the planted item the 7 remaining items give 0.77 and
0.77. Random responders lower alpha (0.70) but straight-liners raise it (0.90):
a straight-liner adds a perfectly consistent row, so a high alpha can come from
careless respondents instead of a good scale.

## 8. Bootstrap interval

95% percentile bootstrap (500 resamples) for a 5-item, loading 0.7 scale, over
200 replicates per sample size. "coverage" is how often the interval contained
the population alpha. "lower >= 0.7" is how often the whole interval sat above
0.7.

| setting | mean alpha | mean interval width | coverage | lower >= 0.7 |
| ------- | ---------- | ------------------- | -------- | ------------ |
| n=20    | 0.78       | 0.36                | 90%      | 15%          |
| n=50    | 0.80       | 0.18                | 92%      | 50%          |
| n=100   | 0.80       | 0.12                | 94%      | 75%          |
| n=400   | 0.80       | 0.06                | 96%      | 100%         |

The interval narrows roughly with the square root of n. At n=20 an estimate near
the true value still comes with an interval that reaches well below 0.7, so a
point estimate above 0.7 from a small sample does not show the scale is
reliable. Report the interval, not only the point value. Percentile intervals
also tend to cover slightly less than 95% in small samples.
