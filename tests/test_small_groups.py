from typing import Any

import numpy as np
import pandas as pd
import pytest

from cronbach_lab.generate import Array, simulate
from cronbach_lab.scenarios import (
    SMALL_SIZES,
    THRESHOLD,
    small_group_profiles,
    small_groups,
)
from cronbach_lab.survey import MARKETING_SENSORIAL, factor_index, marketing_corr

REPS = 150


def alpha_from_variances(items: Array) -> float:
    # Written out again here so the check does not reuse the code under test.
    k = items.shape[1]
    return float(
        k / (k - 1) * (1 - items.var(axis=0, ddof=1).sum() / items.sum(axis=1).var(ddof=1))
    )


@pytest.fixture(scope="module")
def rows() -> pd.DataFrame:
    return pd.DataFrame(small_groups(REPS, np.random.default_rng(3)))


def row(rows: pd.DataFrame, scale: str, group: str, n: int) -> Any:
    return rows[(rows.scale == scale) & (rows.group == group) & (rows.n == n)].iloc[0]


def test_every_group_and_scale_is_run_at_every_size(rows: pd.DataFrame) -> None:
    assert len(rows) == 2 * len(small_group_profiles()) * len(SMALL_SIZES)
    assert set(rows.n) == {30, 40, 50, 200}
    assert set(rows.group) == {"lima", "california", "18-29", "30-39", "40-49", "50+"}
    assert (rows.reps == REPS).all()


def test_the_band_at_n50_is_wider_than_at_n200_for_every_setting(rows: pd.DataFrame) -> None:
    width: dict[Any, float] = (
        (rows.p97_5 - rows.p2_5).groupby([rows.scale, rows.group, rows.n]).first().to_dict()
    )
    for (scale, group), _ in rows.groupby(["scale", "group"]):
        assert width[scale, group, 50] > width[scale, group, 200]
        assert width[scale, group, 30] > width[scale, group, 50]


def test_the_bootstrap_interval_is_wider_at_n50_than_at_n200(rows: pd.DataFrame) -> None:
    narrow = rows[rows.n == 200].set_index(["scale", "group"]).median_ci_width
    wide = rows[rows.n == 50].set_index(["scale", "group"]).median_ci_width
    assert (wide > narrow).all()
    assert (rows.ci_reps == REPS // 10).all()
    assert rows.ci_coverage.between(0, 1).all()


def test_a_group_far_above_the_threshold_never_falsely_passes(rows: pd.DataFrame) -> None:
    for scale in rows.scale.unique():
        r = row(rows, scale, "18-29", 50)
        assert r.true_alpha > 0.8
        assert r.false_pass == 0.0
        assert r.share_ge_0_7 > 0.9


def test_a_group_far_below_the_threshold_never_falsely_fails_and_seldom_passes(
    rows: pd.DataFrame,
) -> None:
    for scale in rows.scale.unique():
        r = row(rows, scale, "50+", 50)
        assert r.true_alpha < 0.5
        assert r.false_fail == 0.0
        assert r.false_pass == r.share_ge_0_7 < 0.05


def test_false_rates_are_the_wrong_side_of_the_population_alpha(rows: pd.DataFrame) -> None:
    above = rows[rows.true_alpha >= THRESHOLD]
    below = rows[rows.true_alpha < THRESHOLD]
    assert (above.false_pass == 0).all()
    assert np.allclose(above.false_fail, 1 - above.share_ge_0_7)
    assert (below.false_fail == 0).all()
    assert (below.false_pass == below.share_ge_0_7).all()


def test_a_group_near_the_threshold_fails_often_at_n50_and_less_at_n200(
    rows: pd.DataFrame,
) -> None:
    r50 = row(rows, "marketing sensorial", "california", 50)
    r200 = row(rows, "marketing sensorial", "california", 200)
    assert THRESHOLD < r50.true_alpha < 0.8
    assert r50.false_fail > 0.15
    assert r200.false_fail < r50.false_fail


def test_the_population_alpha_is_the_same_at_every_size_and_matches_a_second_computation(
    rows: pd.DataFrame,
) -> None:
    by_setting = rows.groupby(["scale", "group"]).true_alpha
    assert (by_setting.nunique() == 1).all()

    # Age group 18-29 on Marketing Sensorial: loading 0.8, symmetric answers, no styles.
    rng = np.random.default_rng(99)
    x = simulate(
        200_000,
        np.full(15, 0.8),
        rng,
        factor=factor_index(MARKETING_SENSORIAL),
        factor_corr=marketing_corr(0.3),
    )
    expected = alpha_from_variances(x)
    assert row(rows, "marketing sensorial", "18-29", 50).true_alpha == pytest.approx(
        expected, abs=0.01
    )


def test_a_small_sample_reads_below_the_population_alpha(rows: pd.DataFrame) -> None:
    r = row(rows, "marketing sensorial", "30-39", 30)
    assert r.mean_alpha < r.true_alpha
