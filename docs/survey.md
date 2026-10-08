# Survey

The lab models a restaurant survey with five response categories: `Nunca = 1`
through `Siempre = 5`. The item names and dimensions are defined in
[`survey.py`](../src/cronbach_lab/survey.py).

| Scale                   | Dimensions                                  | Items |
| ----------------------- | ------------------------------------------- | ----: |
| Marketing Sensorial     | `vista`, `tacto`, `olfato`, `oido`, `gusto` |    15 |
| Satisfaccion al cliente | `entusiasta`, `apatico`, `problematico`     |    13 |

Marketing Sensorial has three items per dimension. Satisfaccion has five
`entusiasta`, four `apatico`, and four `problematico` items. The latter two
dimensions are worded against satisfaction, so their items are answered on the
flipped scale. The scenarios compare those answers as given with answers
reverse-scored before analysis.

## Item generation

For each respondent, the generator draws one standard-normal latent trait per
factor. Before categorization, item `j` is:

```text
x_j = loading_j * theta + sqrt(1 - loading_j**2) * noise_j
```

It maps the continuous score to categories 1 through 5 with configurable
standard-normal cutpoints. Without response styles, the loading is the
continuous item-trait correlation. The default factors are independent. The
survey scenarios can supply a factor-correlation matrix.

Items marked as reverse-keyed are flipped after categorization with `6 - x`. The
generator can also replace a share of respondents with uniform random answers or
with straight-line answers, where one random answer fills the row.

## Response styles

Response styles are respondent-level traits added before categorization:

- Acquiescence shifts every item toward agreement. It shifts reverse-keyed items
  half as much and with the opposite sign.
- Extreme response style multiplies the continuous score by a respondent-level
  gain, pushing answers toward 1 and 5.

Both styles are off by default. When they are on, the loading is nominal: the
style traits change the measured item-trait correlation. The implementation is
in [`generate.py`](../src/cronbach_lab/generate.py).

## Location profiles

The `lima` and `california` profiles are simulation assumptions, not data from
those places. Each profile supplies category shares for its cutpoints, an
extreme-response strength, an acquiescence strength, and a nominal loading. The
profile definitions are in [`profiles.py`](../src/cronbach_lab/profiles.py).

`lima` uses nominal loading 0.7, extreme-response strength 0.5, and acquiescence
strength 0.5. Its pre-style category shares for 1 through 5 are 6%, 6%, 13%,
30%, and 45%. `california` uses nominal loading 0.6, both style strengths 0.2,
and pre-style category shares 3%, 9%, 28%, 38%, and 22%.

In the same-loading scenario, both profiles use nominal loading 0.7. With their
styles on, the generated continuous item-trait correlation is about 0.55 for
`lima` and 0.67 for `california`. On a mirrored Satisfaccion item, the realized
4-5 shares are about 13.0% for `lima` and 12.1% for `california`; the realized
share at 1 is about 44% and 22%, respectively.

The profile scenarios use generated samples to show that alpha can change when
response habits change even when the nominal loading is held constant. The
generated findings report the realized category shares and the measured
continuous item-trait correlation.
