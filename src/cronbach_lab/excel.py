"""One Excel workbook per group of respondents: their answers and their reliability."""

from pathlib import Path

import pandas as pd

from .alpha import alpha_if_dropped, cronbach_alpha, standardized_alpha
from .datasets import generic
from .survey import AGE_GROUPS


def write_workbook(out_dir, name, x, columns, age_group=None):
    """Write `<name>_alpha<raw alpha, 3 decimals>.xlsx` and return its path."""
    alpha = cronbach_alpha(x)
    responses = pd.DataFrame(x, columns=columns)
    if age_group is not None:
        responses["age_group"] = age_group

    metrics = {
        "raw alpha": alpha,
        "standardized alpha": standardized_alpha(x),
        "items": x.shape[1],
        "respondents": x.shape[0],
    }
    for column, value in zip(columns, alpha_if_dropped(x)):
        metrics[f"alpha if {column} dropped"] = value
    reliability = pd.DataFrame({"metric": list(metrics), "value": list(metrics.values())})

    # The alpha in the name changes with the seed, so drop this dataset's earlier
    # workbook. Other files in the folder are not ours to delete.
    for stale in Path(out_dir).glob(f"{name}_alpha*.xlsx"):
        stale.unlink()
    path = Path(out_dir) / f"{name}_alpha{alpha:.3f}.xlsx"
    with pd.ExcelWriter(path) as writer:
        responses.to_excel(writer, sheet_name="responses", index=False)
        reliability.to_excel(writer, sheet_name="reliability", index=False)
    return path


def write_workbooks(out_dir, datasets, age_dataset):
    """Every dataset, then the age-group dataset pooled and per group. Returns the paths.

    datasets, age_dataset: as returned by `draw_datasets`.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [write_workbook(out_dir, name, x, columns) for name, (x, columns) in datasets.items()]

    x, age = age_dataset
    columns = generic(x.shape[1])
    paths.append(write_workbook(out_dir, "age_groups_pooled", x, columns, age))
    for label in AGE_GROUPS:
        mine = age == label
        name = f"age_groups_{label.replace('+', 'plus')}"
        paths.append(write_workbook(out_dir, name, x[mine], columns, age[mine]))
    return paths
