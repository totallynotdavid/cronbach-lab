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

## 9. Location profiles: lima and california

Everything in this section is an assumption of the simulation. The two profiles
are invented to show what response habits can do to alpha. They are not measured
on real Lima or California respondents. A profile sets the cutpoints (the share
of answers in each category before the styles act), an extreme-response style
(each respondent has a gain that stretches their score toward 1 and 5), an
acquiescence style (each respondent has a tendency to agree that raises the
answer to every item) and a loading.

| profile    | cutpoint shares 1..5 (%) | realised shares 1..5 (%)       | extreme sd | acquiescence sd | loading | keyed item-trait r |
| ---------- | ------------------------ | ------------------------------ | ---------- | --------------- | ------- | ------------------ |
| lima       | 6 / 6 / 13 / 30 / 45     | 8.3 / 4.7 / 10.9 / 31.7 / 44.4 | 0.5        | 0.5             | 0.7     | 0.55               |
| california | 3 / 9 / 28 / 38 / 22     | 3.6 / 8.5 / 27.6 / 38.5 / 21.8 | 0.2        | 0.2             | 0.6     | 0.58               |

The cutpoint shares are what the cutpoints give before the styles act. Extreme
responding stretches each respondent's score, so more answers fall on 1 and 5
and the realised shares (a keyed item, a large simulated sample) differ from the
cutpoint ones. Acquiescence is rescaled and leaves the shares alone.

The loading is nominal. It is the item-trait correlation only without response
styles. The last column is measured: the correlation of a keyed item's
continuous score with its own trait, before it is cut, in a large simulated
sample with the profile's styles on.

Three scales are scored, each with 200 respondents per profile. Marketing
Sensorial is pooled as 15 items (dimensions correlated 0.3). Satisfaccion is
pooled as 13 items and scored two ways. Its apatico and problematico items are
worded against satisfaccion, so respondents answer them on the flipped scale.
"As is" adds the raw answers, so those items run against entusiasta. "Recoded"
reverse-scores them first. Acquiescence pulls a reverse-keyed item half as hard
as a keyed one (an assumption). Cells show mean alpha and the share of runs >=
0.7.

A profile's cutpoints cut each item as worded, before the flip. The apatico and
problematico items are answered flipped, so on them the answered shares are the
profile's shares in reverse order. Lima still has more 4-5 answers on those
mirrored items than california (13.0% against 12.1%). What differs is the other
end: lima piles up at 1 (44% against 22%).

### Alpha per profile, and both profiles pooled

Profiles as assumed: they differ in cutpoints, style and loading.

| scale                | lima        | california | pooled      |
| -------------------- | ----------- | ---------- | ----------- |
| marketing sensorial  | 0.87 (100%) | 0.74 (88%) | 0.84 (100%) |
| satisfaccion as is   | 0.65 (15%)  | 0.44 (0%)  | 0.58 (0%)   |
| satisfaccion recoded | 0.81 (100%) | 0.76 (99%) | 0.81 (100%) |

### Same loading, with each profile's own cutpoints and style

Both profiles get the nominal loading 0.7, so the construct is the same. Each
keeps its own cutpoints and its own response style. The nominal loading is
shared, the measurement is not: measured with the styles on, the item-trait
correlation of a keyed item is 0.55 for lima and 0.67 for california.

| scale                | lima        | california  | pooled      |
| -------------------- | ----------- | ----------- | ----------- |
| marketing sensorial  | 0.87 (100%) | 0.79 (100%) | 0.86 (100%) |
| satisfaccion as is   | 0.66 (18%)  | 0.50 (0%)   | 0.60 (0%)   |
| satisfaccion recoded | 0.81 (100%) | 0.83 (100%) | 0.83 (100%) |

With the same nominal loading the profiles still differ. Lima minus california
is +0.08 on Marketing Sensorial, +0.16 on Satisfaccion as is and -0.02 on
Satisfaccion recoded. Alpha moved and the construct did not, and the gap depends
on how the scale is scored.

Marketing Sensorial separates the two sources. Give both profiles the same
symmetric cutpoints and keep their styles: lima minus california is +0.078. Keep
their own cutpoints and drop the styles: it is -0.019. The gap is mostly
response style, not the cutpoints.

### Sensitivity to the strength of the style

One style at a time (the other is zero), the profile's own cutpoints and
loading. Strength is the standard deviation of the respondent trait. The plot is
`plots/response_style.png`.

| scale                | profile    | extreme 0 | extreme 1 | acquiescence 0 | acquiescence 1 |
| -------------------- | ---------- | --------- | --------- | -------------- | -------------- |
| marketing sensorial  | lima       | 0.74      | 0.80      | 0.74           | 0.94           |
| marketing sensorial  | california | 0.68      | 0.72      | 0.68           | 0.94           |
| satisfaccion as is   | lima       | 0.43      | 0.37      | 0.43           | 0.84           |
| satisfaccion as is   | california | 0.35      | 0.32      | 0.35           | 0.85           |
| satisfaccion recoded | lima       | 0.82      | 0.85      | 0.82           | 0.72           |
| satisfaccion recoded | california | 0.77      | 0.78      | 0.77           | 0.63           |

Acquiescence adds one factor to every answer as given, whatever the item says,
so it raises alpha when the answers are scored as given, without
reverse-scoring. Marketing Sensorial, where every item points the same way, goes
from 0.74 to 0.94 for lima. Satisfaccion as is, whose dimensions run against
each other, also rises, from 0.43 to 0.84, because the raw answers all carry the
shared factor with the same sign. After reverse-scoring apatico and
problematico, the shared factor enters the entusiasta items with a plus sign and
the recoded items with a minus sign, so it splits the scale instead of uniting
it and alpha falls, from 0.82 to 0.72 for lima. Extreme responding moves alpha
less than acquiescence on Marketing Sensorial.

### What alpha can and cannot tell here

Alpha computed within each group does detect a group whose items hang together
less: california Marketing Sensorial sits at 0.74 against 0.87 for lima. Pooled
it is 0.84, so the pooled value hides the weaker group.

Alpha cannot tell why a group scores high or low. In the same-loading runs the
construct and the nominal loading are identical and alpha still differs, because
answer habits add or remove shared variance. The sensitivity table shows the
extreme case: Satisfaccion as is mixes items that run against each other, yet
with strong acquiescence lima's alpha reaches 0.84 against 0.43 with none. A
pass can come from acquiescence, not from measuring one trait well. Pooled alpha
also hides that the groups use the scale differently: it is one number from one
covariance matrix, and a mixture of groups with different cutpoints and loadings
gives a matrix that belongs to neither.

Telling a real difference in the construct from a difference in how the groups
answer takes a multi-group invariance test (multi-group confirmatory factor
analysis). It asks, in order, whether the groups share the factor structure
(configural), the loadings (metric) and the item intercepts or thresholds
(scalar). Only with scalar invariance can the groups' scores be pooled or
compared. This lab does not run one, because it needs structural equation
modelling tools beyond its dependencies.

## 10. Small groups of 30 to 50, against the population alpha

Everything here is an assumption of the simulation, like section 9. Each group
is a profile (lima, california) or an age group (loadings 0.8, 0.7, 0.5 and 0.3,
as in section 6, symmetric answers, no response styles), scored on Marketing
Sensorial and on Satisfaccion recoded. Each is drawn at n=30, 40, 50 and 200
respondents, 1000 replicates per row. "Population alpha" is the alpha of the
same setting at 200000 respondents, one draw.

A false pass is a run with alpha >= 0.7 in a group whose population alpha is
below it. A false fail is a run below 0.7 in a group whose population alpha is
0.7 or more. A group is on one side, so the other column shows a dash. The
interval is the 95% percentile bootstrap (500 resamples). To keep the run short
it is computed on the first 100 of the 1000 replicates of each row, so its width
and coverage rest on 100 samples per row and are noisier than the alpha columns.
The plot is `plots/small_groups.png`.

### Marketing Sensorial

| group      | n   | population alpha | mean alpha | 2.5-97.5% band | runs >= 0.7 | false pass | false fail | median interval width | interval covers |
| ---------- | --- | ---------------- | ---------- | -------------- | ----------- | ---------- | ---------- | --------------------- | --------------- |
| lima       | 30  | 0.87             | 0.86       | 0.75 to 0.93   | 99%         | -          | 1%         | 0.18                  | 92%             |
| lima       | 40  | 0.87             | 0.87       | 0.77 to 0.93   | 100%        | -          | 0%         | 0.15                  | 93%             |
| lima       | 50  | 0.87             | 0.87       | 0.78 to 0.92   | 100%        | -          | 0%         | 0.14                  | 81%             |
| lima       | 200 | 0.87             | 0.87       | 0.84 to 0.90   | 100%        | -          | 0%         | 0.06                  | 92%             |
| california | 30  | 0.74             | 0.72       | 0.52 to 0.84   | 63%         | -          | 37%        | 0.33                  | 91%             |
| california | 40  | 0.74             | 0.72       | 0.56 to 0.83   | 68%         | -          | 32%        | 0.27                  | 92%             |
| california | 50  | 0.74             | 0.73       | 0.58 to 0.83   | 71%         | -          | 29%        | 0.23                  | 96%             |
| california | 200 | 0.74             | 0.74       | 0.68 to 0.79   | 88%         | -          | 12%        | 0.11                  | 95%             |
| 18-29      | 30  | 0.82             | 0.81       | 0.68 to 0.89   | 96%         | -          | 4%         | 0.22                  | 91%             |
| 18-29      | 40  | 0.82             | 0.81       | 0.71 to 0.88   | 98%         | -          | 2%         | 0.17                  | 91%             |
| 18-29      | 50  | 0.82             | 0.81       | 0.71 to 0.88   | 99%         | -          | 1%         | 0.15                  | 93%             |
| 18-29      | 200 | 0.82             | 0.82       | 0.78 to 0.85   | 100%        | -          | 0%         | 0.07                  | 92%             |
| 30-39      | 30  | 0.77             | 0.75       | 0.58 to 0.85   | 78%         | -          | 22%        | 0.26                  | 90%             |
| 30-39      | 40  | 0.77             | 0.76       | 0.61 to 0.85   | 84%         | -          | 16%        | 0.22                  | 92%             |
| 30-39      | 50  | 0.77             | 0.76       | 0.64 to 0.84   | 86%         | -          | 14%        | 0.20                  | 92%             |
| 30-39      | 200 | 0.77             | 0.76       | 0.71 to 0.81   | 99%         | -          | 1%         | 0.09                  | 98%             |
| 40-49      | 30  | 0.60             | 0.57       | 0.25 to 0.75   | 12%         | 12%        | -          | 0.49                  | 91%             |
| 40-49      | 40  | 0.60             | 0.58       | 0.35 to 0.74   | 9%          | 9%         | -          | 0.38                  | 94%             |
| 40-49      | 50  | 0.60             | 0.59       | 0.36 to 0.73   | 7%          | 7%         | -          | 0.34                  | 90%             |
| 40-49      | 200 | 0.60             | 0.60       | 0.50 to 0.67   | 0%          | 0%         | -          | 0.16                  | 94%             |
| 50+        | 30  | 0.34             | 0.30       | -0.20 to 0.60  | 0%          | 0%         | -          | 0.77                  | 95%             |
| 50+        | 40  | 0.34             | 0.31       | -0.06 to 0.57  | 0%          | 0%         | -          | 0.64                  | 90%             |
| 50+        | 50  | 0.34             | 0.32       | 0.00 to 0.55   | 0%          | 0%         | -          | 0.55                  | 93%             |
| 50+        | 200 | 0.34             | 0.33       | 0.19 to 0.45   | 0%          | 0%         | -          | 0.27                  | 96%             |

### Satisfaccion recoded

| group      | n   | population alpha | mean alpha | 2.5-97.5% band | runs >= 0.7 | false pass | false fail | median interval width | interval covers |
| ---------- | --- | ---------------- | ---------- | -------------- | ----------- | ---------- | ---------- | --------------------- | --------------- |
| lima       | 30  | 0.81             | 0.79       | 0.63 to 0.89   | 89%         | -          | 11%        | 0.24                  | 93%             |
| lima       | 40  | 0.81             | 0.80       | 0.67 to 0.89   | 93%         | -          | 7%         | 0.21                  | 91%             |
| lima       | 50  | 0.81             | 0.80       | 0.68 to 0.88   | 95%         | -          | 5%         | 0.19                  | 84%             |
| lima       | 200 | 0.81             | 0.81       | 0.76 to 0.85   | 100%        | -          | 0%         | 0.09                  | 88%             |
| california | 30  | 0.77             | 0.75       | 0.53 to 0.86   | 77%         | -          | 23%        | 0.28                  | 94%             |
| california | 40  | 0.77             | 0.75       | 0.60 to 0.85   | 83%         | -          | 17%        | 0.24                  | 87%             |
| california | 50  | 0.77             | 0.76       | 0.63 to 0.84   | 85%         | -          | 15%        | 0.21                  | 92%             |
| california | 200 | 0.77             | 0.76       | 0.71 to 0.81   | 99%         | -          | 1%         | 0.10                  | 94%             |
| 18-29      | 30  | 0.89             | 0.88       | 0.79 to 0.93   | 100%        | -          | 0%         | 0.14                  | 93%             |
| 18-29      | 40  | 0.89             | 0.88       | 0.81 to 0.93   | 100%        | -          | 0%         | 0.11                  | 94%             |
| 18-29      | 50  | 0.89             | 0.88       | 0.82 to 0.92   | 100%        | -          | 0%         | 0.10                  | 89%             |
| 18-29      | 200 | 0.89             | 0.89       | 0.86 to 0.91   | 100%        | -          | 0%         | 0.05                  | 96%             |
| 30-39      | 30  | 0.84             | 0.83       | 0.70 to 0.90   | 98%         | -          | 3%         | 0.19                  | 90%             |
| 30-39      | 40  | 0.84             | 0.83       | 0.73 to 0.89   | 99%         | -          | 1%         | 0.16                  | 86%             |
| 30-39      | 50  | 0.84             | 0.83       | 0.75 to 0.89   | 100%        | -          | 0%         | 0.13                  | 96%             |
| 30-39      | 200 | 0.84             | 0.84       | 0.80 to 0.87   | 100%        | -          | 0%         | 0.06                  | 92%             |
| 40-49      | 30  | 0.69             | 0.67       | 0.43 to 0.80   | 43%         | 43%        | -          | 0.40                  | 91%             |
| 40-49      | 40  | 0.69             | 0.67       | 0.46 to 0.79   | 42%         | 42%        | -          | 0.29                  | 92%             |
| 40-49      | 50  | 0.69             | 0.68       | 0.53 to 0.79   | 43%         | 43%        | -          | 0.26                  | 97%             |
| 40-49      | 200 | 0.69             | 0.69       | 0.62 to 0.74   | 38%         | 38%        | -          | 0.13                  | 94%             |
| 50+        | 30  | 0.42             | 0.37       | -0.09 to 0.64  | 0%          | 0%         | -          | 0.69                  | 92%             |
| 50+        | 40  | 0.42             | 0.38       | 0.01 to 0.61   | 0%          | 0%         | -          | 0.59                  | 90%             |
| 50+        | 50  | 0.42             | 0.40       | 0.10 to 0.60   | 0%          | 0%         | -          | 0.51                  | 97%             |
| 50+        | 200 | 0.42             | 0.41       | 0.27 to 0.53   | 0%          | 0%         | -          | 0.23                  | 95%             |

### What a small group can show

A group of 50 reads a little low. Its mean alpha is under the population alpha
in 12 of the 12 settings, by at most 0.02, and the spread is wide: the middle
95% of alpha spans 0.21 at n=50 (median over the settings), against 0.10 at
n=200.

How often a weak group looks fine by chance depends on how close it is to 0.7.
The worst false pass at n=50 is 40-49 on satisfaccion recoded, with population
alpha 0.69: 43% of samples reach 0.7. A group that close to the threshold passes
often by chance, and more respondents do not remove that: at n=200 the same
group still passes 38% of the time. A group far below, such as the 50+ group,
almost never passes. The reverse also happens: the worst false fail at n=50 is
california on marketing sensorial, population alpha 0.74, where 29% of samples
fall below 0.7 although the group's population alpha is above it. At n=200 that
falls to 12%.

### The bootstrap interval

The median 95% interval is 0.21 wide at n=50 (median over the settings) and 0.10
at n=200. Pooled over the 12 settings of each size (1200 intervals each), the
share of intervals that contain the population alpha is 91.9% at n=30, 91.0% at
n=40, 91.7% at n=50, 93.8% at n=200. Yes: coverage falls below 95% at n=30 and
n=40, by more than the sampling error of this estimate (about 1.2%). It is also
below 95% at n=50, so the shortfall is not limited to the smallest groups.
