import re

import pandas as pd
import pytest

from cronbach_lab.datasets import write_datasets
from cronbach_lab.excel import write_workbooks

DATASETS = 9
AGE_FILES = ["pooled", "18-29", "30-39", "40-49", "50plus"]


def alpha_from_variances(items):
    # Written out again here so the check does not reuse the code under test.
    k = items.shape[1]
    return k / (k - 1) * (1 - items.var(axis=0, ddof=1).sum() / items.sum(axis=1).var(ddof=1))


@pytest.fixture(scope="module")
def workbooks(tmp_path_factory):
    out = tmp_path_factory.mktemp("xlsx")
    write_workbooks(out)
    return out


def test_one_workbook_per_dataset_per_profile_and_per_age_group(workbooks):
    names = sorted(p.stem for p in workbooks.glob("*.xlsx"))
    assert len(names) == DATASETS + len(AGE_FILES)
    for part in AGE_FILES:
        assert any(n.startswith(f"age_groups_{part}_alpha") for n in names)
    for profile in ("lima", "california"):
        assert any(n.startswith(f"{profile}_marketing_sensorial_alpha") for n in names)


def test_filename_alpha_matches_the_alpha_recomputed_from_the_responses_sheet(workbooks):
    for path in workbooks.glob("*.xlsx"):
        sheets = pd.read_excel(path, sheet_name=None)
        assert set(sheets) == {"responses", "reliability"}

        responses = sheets["responses"].drop(columns="age_group", errors="ignore")
        recomputed = alpha_from_variances(responses.to_numpy(dtype=float))
        in_name = float(re.search(r"_alpha(\d\.\d{3})\.xlsx$", path.name).group(1))
        assert in_name == pytest.approx(recomputed, abs=0.0005), path.name

        reliability = sheets["reliability"].set_index("metric")["value"]
        assert reliability["raw alpha"] == pytest.approx(recomputed, abs=1e-12)
        assert reliability["items"] == responses.shape[1]
        assert reliability["respondents"] == responses.shape[0]
        assert 0 < reliability["standardized alpha"] < 1


def test_alpha_if_dropped_rows_match_a_scale_without_that_item(workbooks):
    path = next(workbooks.glob("equal_k5_n200_alpha*.xlsx"))
    sheets = pd.read_excel(path, sheet_name=None)
    responses, reliability = sheets["responses"], sheets["reliability"].set_index("metric")["value"]
    for item in responses.columns:
        without = responses.drop(columns=item).to_numpy(dtype=float)
        assert reliability[f"alpha if {item} dropped"] == pytest.approx(
            alpha_from_variances(without), abs=1e-12
        )


def test_age_workbooks_hold_their_group_and_the_oldest_group_is_least_reliable(workbooks):
    pooled = next(workbooks.glob("age_groups_pooled_alpha*.xlsx"))
    pooled_age = pd.read_excel(pooled, sheet_name="responses")["age_group"]
    assert list(pooled_age.unique()) == ["18-29", "30-39", "40-49", "50+"]

    alphas = {}
    for part, label in zip(AGE_FILES[1:], ["18-29", "30-39", "40-49", "50+"]):
        path = next(workbooks.glob(f"age_groups_{part}_alpha*.xlsx"))
        responses = pd.read_excel(path, sheet_name="responses")
        assert set(responses["age_group"]) == {label}
        assert len(responses) == 100
        alphas[label] = alpha_from_variances(responses.drop(columns="age_group").to_numpy(float))
    assert alphas["18-29"] > 0.7 > alphas["50+"]


def test_workbook_answers_equal_the_csv_dataset_of_the_same_name(workbooks, tmp_path):
    write_datasets(tmp_path)
    for csv in tmp_path.glob("*.csv"):
        if csv.stem == "python_alpha":
            continue
        book = next(workbooks.glob(f"{csv.stem}_alpha*.xlsx"))
        pd.testing.assert_frame_equal(
            pd.read_excel(book, sheet_name="responses"), pd.read_csv(csv), check_dtype=False
        )


def test_rewriting_removes_workbooks_from_an_earlier_seed(tmp_path):
    write_workbooks(tmp_path, seed=1)
    write_workbooks(tmp_path, seed=2)
    assert len(list(tmp_path.glob("*.xlsx"))) == DATASETS + len(AGE_FILES)
