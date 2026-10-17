"""Cronbach's alpha, written out from the formulas."""

import numpy as np
from numpy.typing import ArrayLike, NDArray


def cronbach_alpha(x: ArrayLike) -> NDArray[np.float64]:
    """Raw alpha: k/(k-1) * (1 - sum of item variances / variance of the total score).

    x has shape (..., n, k): n respondents by k items. Leading axes let the
    bootstrap score many resamples at once. Sample variances (ddof=1) are used
    for both terms. The ratio is the same with any consistent ddof.
    Returns nan when the total score has no variance.
    """
    arr = np.asarray(x, dtype=float)
    k = arr.shape[-1]
    item_var_sum = arr.var(axis=-2, ddof=1).sum(axis=-1)
    total_var = arr.sum(axis=-1).var(axis=-1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        alpha = k / (k - 1) * (1 - item_var_sum / total_var)
    return np.where(total_var > 0, alpha, np.nan)


def standardized_alpha(x: ArrayLike) -> float:
    """Alpha from the mean inter-item correlation: k*r / (1 + (k-1)*r).

    Equals raw alpha after every item is rescaled to variance 1, so it ignores
    differences in item variance. Returns nan if an item is constant.
    """
    arr = np.asarray(x, dtype=float)
    k = arr.shape[1]
    with np.errstate(divide="ignore", invalid="ignore"):
        corr = np.corrcoef(arr, rowvar=False)
    mean_r = (corr.sum() - k) / (k * (k - 1))
    return float(k * mean_r / (1 + (k - 1) * mean_r))


def alpha_if_dropped(x: ArrayLike) -> NDArray[np.float64]:
    """Raw alpha of the scale with each item removed in turn, shape (k,).

    A value above the full-scale alpha means that item pulls reliability down.
    """
    arr = np.asarray(x)
    return np.array([cronbach_alpha(np.delete(arr, j, axis=1)) for j in range(arr.shape[1])])


def bootstrap_ci(
    x: ArrayLike, rng: np.random.Generator, n_boot: int = 1000, level: float = 0.95
) -> tuple[float, float]:
    """Percentile bootstrap interval for raw alpha: resample respondents (rows)."""
    arr = np.asarray(x)
    n = arr.shape[0]
    resamples = arr[rng.integers(0, n, size=(n_boot, n))]
    alphas = cronbach_alpha(resamples)
    tail = 100 * (1 - level) / 2
    low, high = np.nanpercentile(alphas, [tail, 100 - tail])
    return float(low), float(high)
