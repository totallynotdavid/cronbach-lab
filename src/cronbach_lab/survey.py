"""The restaurant survey: items per dimension and how the dimensions relate."""

import numpy as np

from .generate import equicorrelated

AGE_GROUPS = ["18-29", "30-39", "40-49", "50+"]

MARKETING_SENSORIAL = {"vista": 3, "tacto": 3, "olfato": 3, "oido": 3, "gusto": 3}
SATISFACCION = {"entusiasta": 5, "apatico": 4, "problematico": 4}

# Assumed, not measured: apatico and problematico behaviour runs against
# entusiasta, so their traits correlate negatively with it.
SATISFACCION_CORR = np.array(
    [
        [1.0, -0.6, -0.4],
        [-0.6, 1.0, 0.5],
        [-0.4, 0.5, 1.0],
    ]
)


def factor_index(dimensions):
    """Factor of each item, one factor per dimension."""
    return np.repeat(np.arange(len(dimensions)), list(dimensions.values()))


def item_names(dimensions):
    return [f"{d}_{i + 1}" for d, size in dimensions.items() for i in range(size)]


def dimension_columns(dimensions, name):
    """Column positions of one dimension's items."""
    return np.flatnonzero(factor_index(dimensions) == list(dimensions).index(name))


def marketing_corr(r):
    return equicorrelated(len(MARKETING_SENSORIAL), r)
