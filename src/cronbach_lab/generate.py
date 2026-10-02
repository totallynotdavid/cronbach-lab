"""Latent-trait generator for Likert items.

Each respondent has a latent trait theta (one per factor). Item j is

    x_j = loading_j * theta + sqrt(1 - loading_j**2) * noise_j

so every continuous item has variance 1, the loading is the item-trait
correlation, and two items on the same factor correlate loading_i * loading_j.
The continuous score is then cut into the categories 1..5.
"""

from statistics import NormalDist

import numpy as np


def cutpoints_from_probs(probs):
    """Thresholds on the standard-normal scale that give these category shares."""
    cumulative = np.cumsum(probs)[:-1]
    return np.array([NormalDist().inv_cdf(p) for p in cumulative])


# Share of responses in categories 1..5 (Nunca .. Siempre).
RESPONSE_SHAPES = {
    "symmetric": [0.10, 0.20, 0.40, 0.20, 0.10],
    "skewed high": [0.03, 0.07, 0.20, 0.35, 0.35],
    "skewed low": [0.35, 0.35, 0.20, 0.07, 0.03],
    "ceiling": [0.01, 0.03, 0.06, 0.20, 0.70],
}
SYMMETRIC = cutpoints_from_probs(RESPONSE_SHAPES["symmetric"])


def equicorrelated(n_factors, r):
    """Correlation matrix with r between every pair of factors."""
    return np.full((n_factors, n_factors), r) + (1 - r) * np.eye(n_factors)


def latent_items(
    n,
    loadings,
    rng,
    factor=None,
    factor_corr=None,
    group=None,
    theta_shift=None,
):
    """Continuous item scores, shape (n, k).

    loadings: (k,), or (groups, k) to give each group its own loadings.
    factor: (k,) factor index of each item; default is one factor.
    factor_corr: correlation between the factors' thetas; default independent.
    group: (n,) group index of each respondent; needed for 2-D loadings
        or theta_shift.
    theta_shift: (groups,) mean of theta in each group.
    """
    loadings = np.asarray(loadings, dtype=float)
    k = loadings.shape[-1]
    factor = np.zeros(k, dtype=int) if factor is None else np.asarray(factor)
    n_factors = factor.max() + 1
    corr = np.eye(n_factors) if factor_corr is None else np.asarray(factor_corr)

    theta = rng.multivariate_normal(np.zeros(n_factors), corr, size=n)
    if theta_shift is not None:
        theta = theta + np.asarray(theta_shift)[group][:, None]
    loading = loadings[group] if loadings.ndim == 2 else loadings

    noise = rng.standard_normal((n, k)) * np.sqrt(1 - loading**2)
    return loading * theta[:, factor] + noise


def discretize(x, cutpoints=SYMMETRIC):
    """Map continuous scores to 1..len(cutpoints)+1."""
    return np.searchsorted(cutpoints, x) + 1


def simulate(
    n,
    loadings,
    rng,
    cutpoints=SYMMETRIC,
    reverse=None,
    random_share=0.0,
    straightline_share=0.0,
    **latent_kwargs,
):
    """Likert responses, shape (n, k), integers 1..5.

    reverse: (k,) bool, items answered on the flipped scale (6 - x). The data
        come back as answered; recode with `reverse_score` before analysis.
    random_share: share of respondents who answer every item uniformly at random.
    straightline_share: share who give one random answer to every item.
    """
    x = discretize(latent_items(n, loadings, rng, **latent_kwargs), cutpoints)
    k = x.shape[1]
    if reverse is not None:
        x = np.where(reverse, 6 - x, x)

    kind = rng.random(n)
    random_rows = kind < random_share
    line_rows = (kind >= random_share) & (kind < random_share + straightline_share)
    x[random_rows] = rng.integers(1, 6, size=(random_rows.sum(), k))
    x[line_rows] = rng.integers(1, 6, size=(line_rows.sum(), 1))
    return x


def reverse_score(x, reverse):
    """Undo reverse keying so every item points the same way."""
    return np.where(reverse, 6 - x, x)
