import numpy as np
import pytest

from cronbach_lab.alpha import (
    alpha_if_dropped,
    bootstrap_ci,
    cronbach_alpha,
    standardized_alpha,
)
from cronbach_lab.generate import latent_items, simulate


def theoretical_alpha(k, loading):
    rho = loading**2
    return k * rho / (1 + (k - 1) * rho)


def mean_alpha(n, loadings, reps=30, seed=0, **kwargs):
    rng = np.random.default_rng(seed)
    return np.mean([cronbach_alpha(simulate(n, loadings, rng, **kwargs)) for _ in range(reps)])


def test_alpha_matches_covariance_matrix_form():
    # alpha = k/(k-1) * (1 - trace(C) / sum(C)), C the item covariance matrix.
    x = np.random.default_rng(0).integers(1, 6, size=(50, 6))
    cov = np.cov(x, rowvar=False)
    expected = 6 / 5 * (1 - np.trace(cov) / cov.sum())
    assert cronbach_alpha(x) == pytest.approx(expected, abs=1e-12)


def test_standardized_alpha_is_raw_alpha_of_z_scores():
    x = np.random.default_rng(1).integers(1, 6, size=(80, 5)) * np.array([1, 2, 3, 1, 5])
    z = (x - x.mean(axis=0)) / x.std(axis=0, ddof=1)
    assert standardized_alpha(x) == pytest.approx(cronbach_alpha(z), abs=1e-12)


def test_identical_items_give_alpha_one_and_constant_items_nan():
    column = np.random.default_rng(2).integers(1, 6, size=(40, 1))
    assert cronbach_alpha(np.hstack([column] * 4)) == pytest.approx(1.0)
    assert np.isnan(cronbach_alpha(np.full((10, 4), 3)))


def test_continuous_items_match_theoretical_standardized_alpha():
    rng = np.random.default_rng(3)
    loading, k = 0.6, 6
    alphas = [cronbach_alpha(latent_items(5000, np.full(k, loading), rng)) for _ in range(20)]
    assert np.mean(alphas) == pytest.approx(theoretical_alpha(k, loading), abs=0.01)


def test_likert_items_sit_just_below_theory():
    # Cutting into 5 categories attenuates correlations, so alpha is a little low.
    loading, k = 0.6, 6
    simulated = mean_alpha(5000, np.full(k, loading))
    assert theoretical_alpha(k, loading) - 0.04 < simulated < theoretical_alpha(k, loading)


def test_alpha_rises_with_items_and_with_loading():
    by_items = [mean_alpha(400, np.full(k, 0.5)) for k in (3, 5, 15)]
    by_loading = [mean_alpha(400, np.full(5, loading)) for loading in (0.3, 0.5, 0.7, 0.9)]
    assert by_items == sorted(by_items)
    assert by_loading == sorted(by_loading)


def test_alpha_if_dropped_flags_a_noise_item():
    loadings = np.array([0.0] + [0.7] * 6)
    x = simulate(500, loadings, np.random.default_rng(4))
    dropped = alpha_if_dropped(x)
    assert dropped.argmax() == 0
    assert dropped[0] > cronbach_alpha(x)
    assert all(dropped[1:] < cronbach_alpha(x))


def test_alpha_if_dropped_flags_a_wrongly_reversed_item():
    reverse = np.arange(6) == 2
    x = simulate(500, np.full(6, 0.7), np.random.default_rng(5), reverse=reverse)
    assert alpha_if_dropped(x).argmax() == 2


def test_bootstrap_interval_contains_estimate_and_narrows_with_n():
    rng = np.random.default_rng(6)
    widths = []
    for n in (30, 300):
        x = simulate(n, np.full(5, 0.6), rng)
        low, high = bootstrap_ci(x, rng, n_boot=500)
        assert low < cronbach_alpha(x) < high
        widths.append(high - low)
    assert widths[1] < widths[0]


def test_bootstrap_interval_covers_true_alpha_about_95_percent():
    rng = np.random.default_rng(7)
    loadings = np.full(5, 0.6)
    truth = cronbach_alpha(simulate(200_000, loadings, rng))
    covered = [
        low <= truth <= high
        for low, high in (
            bootstrap_ci(simulate(200, loadings, rng), rng, n_boot=300) for _ in range(150)
        )
    ]
    assert 0.88 < np.mean(covered) < 0.99
