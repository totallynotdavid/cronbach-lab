"""Datasets for the R cross-check: item CSVs plus the Python alpha of each."""

from pathlib import Path

import numpy as np
import pandas as pd

from .alpha import cronbach_alpha, standardized_alpha
from .generate import RESPONSE_SHAPES, cutpoints_from_probs, simulate
from .scenarios import equal_loadings
from .survey import (
    MARKETING_SENSORIAL,
    SATISFACCION,
    SATISFACCION_CORR,
    factor_index,
    item_names,
    marketing_corr,
)


def generic(k):
    return [f"q{i + 1}" for i in range(k)]


def build_datasets(rng):
    """Name -> (responses, column names), differing in size, skew, structure and bad responders."""
    satisfaccion = factor_index(SATISFACCION)
    marketing = factor_index(MARKETING_SENSORIAL)
    ceiling = cutpoints_from_probs(RESPONSE_SHAPES["ceiling"])
    return {
        "equal_k5_n200": (simulate(200, equal_loadings(5), rng), generic(5)),
        "equal_k15_n400": (simulate(400, equal_loadings(15, 0.5), rng), generic(15)),
        "small_k3_n20": (simulate(20, equal_loadings(3, 0.7), rng), generic(3)),
        "ceiling_k5_n200": (
            simulate(200, equal_loadings(5, 0.7), rng, cutpoints=ceiling),
            generic(5),
        ),
        "straightliners_k8_n200": (
            simulate(200, equal_loadings(8), rng, straightline_share=0.2),
            generic(8),
        ),
        "satisfaccion_pooled": (
            simulate(
                200,
                equal_loadings(13, 0.7),
                rng,
                factor=satisfaccion,
                factor_corr=SATISFACCION_CORR,
            ),
            item_names(SATISFACCION),
        ),
        "marketing_sensorial": (
            simulate(
                300,
                equal_loadings(15, 0.7),
                rng,
                factor=marketing,
                factor_corr=marketing_corr(0.3),
            ),
            item_names(MARKETING_SENSORIAL),
        ),
    }


def write_datasets(out_dir, seed=1):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    reference = []
    for name, (x, columns) in build_datasets(rng).items():
        pd.DataFrame(x, columns=columns).to_csv(out_dir / f"{name}.csv", index=False)
        reference.append(
            {"dataset": name, "raw_alpha": cronbach_alpha(x), "std_alpha": standardized_alpha(x)}
        )
    pd.DataFrame(reference).to_csv(out_dir / "python_alpha.csv", index=False)
