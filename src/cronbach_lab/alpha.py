"""Cronbach's alpha, written out from the formulas."""

import numpy as np


def cronbach_alpha(x):
    """Raw alpha: k/(k-1) * (1 - sum of item variances / variance of the total score).

    x has shape (..., n, k): n respondents by k items. Leading axes let the
    bootstrap score many resamples at once. Sample variances (ddof=1) are used
    for both terms. The ratio is the same with any consistent ddof.
    Returns nan when the total score has no variance.
    """
    x = np.asarray(x, dtype=float)
    k = x.shape[-1]
    item_var_sum = x.var(axis=-2, ddof=1).sum(axis=-1)
    total_var = x.sum(axis=-1).var(axis=-1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        alpha = k / (k - 1) * (1 - item_var_sum / total_var)
    return np.where(total_var > 0, alpha, np.nan)


def standardized_alpha(x):
    """Alpha from the mean inter-item correlation: k*r / (1 + (k-1)*r).

    Equals raw alpha after every item is rescaled to variance 1, so it ignores
    differences in item variance. Returns nan if an item is constant.
    """
    x = np.asarray(x, dtype=float)
    k = x.shape[1]
    with np.errstate(divide="ignore", invalid="ignore"):
        corr = np.corrcoef(x, rowvar=False)
    mean_r = (corr.sum() - k) / (k * (k - 1))
    return k * mean_r / (1 + (k - 1) * mean_r)


def alpha_if_dropped(x):
    """Raw alpha of the scale with each item removed in turn, shape (k,).

    A value above the full-scale alpha means that item pulls reliability down.
    """
    x = np.asarray(x)
    return np.array([cronbach_alpha(np.delete(x, j, axis=1)) for j in range(x.shape[1])])


def bootstrap_ci(x, rng, n_boot=1000, level=0.95):
    """Percentile bootstrap interval for raw alpha: resample respondents (rows)."""
    x = np.asarray(x)
    n = x.shape[0]
    resamples = x[rng.integers(0, n, size=(n_boot, n))]
    alphas = cronbach_alpha(resamples)
    tail = 100 * (1 - level) / 2
    return tuple(np.nanpercentile(alphas, [tail, 100 - tail]))
