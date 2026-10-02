from dataclasses import replace

import numpy as np
import pytest

from cronbach_lab.alpha import cronbach_alpha
from cronbach_lab.generate import RESPONSE_SHAPES, latent_items, reverse_score
from cronbach_lab.profiles import PROFILES, simulate_profile

SYMMETRIC_NO_STYLE = replace(
    PROFILES["lima"], probs=tuple(RESPONSE_SHAPES["symmetric"]), extreme=0.0, acquiescence=0.0
)


def theoretical_alpha(k, loading):
    rho = loading**2
    return k * rho / (1 + (k - 1) * rho)


def mean_alpha(profile, loadings, reps=20, n=3000, seed=0, recode=None, **kwargs):
    rng = np.random.default_rng(seed)
    alphas = []
    for _ in range(reps):
        x = simulate_profile(profile, n, loadings, rng, **kwargs)
        alphas.append(cronbach_alpha(x if recode is None else reverse_score(x, recode)))
    return np.mean(alphas)


def test_profile_without_style_and_equal_loadings_matches_theory():
    # Same bound as the plain generator: 5-category cutting leaves alpha a little under theory.
    k, loading = 6, 0.6
    simulated = mean_alpha(SYMMETRIC_NO_STYLE, np.full(k, loading))
    assert theoretical_alpha(k, loading) - 0.04 < simulated < theoretical_alpha(k, loading)


def test_style_traits_off_leave_the_latent_scores_untouched():
    plain = latent_items(50, np.full(4, 0.6), np.random.default_rng(1))
    off = latent_items(50, np.full(4, 0.6), np.random.default_rng(1), acquiescence=0.0, extreme=0.0)
    assert np.array_equal(plain, off)


def test_profile_cutpoints_give_its_answer_shares_even_with_acquiescence():
    # Acquiescence is rescaled to keep unit variance, so the shares do not move.
    lima = replace(PROFILES["lima"], extreme=0.0, acquiescence=0.7)
    x = simulate_profile(lima, 200_000, np.full(4, 0.6), np.random.default_rng(2))
    shares = np.bincount(x.ravel(), minlength=6)[1:] / x.size
    assert shares == pytest.approx(lima.probs, abs=0.01)


def test_acquiescence_raises_alpha_on_a_keyed_only_scale():
    loadings = np.full(6, 0.5)
    by_strength = [
        mean_alpha(replace(SYMMETRIC_NO_STYLE, acquiescence=s), loadings) for s in (0.0, 0.5, 1.0)
    ]
    assert by_strength == sorted(by_strength)
    assert by_strength[2] > by_strength[0] + 0.1


def test_acquiescence_lowers_alpha_once_reverse_keyed_items_are_recoded():
    # Agreeing raises the answer to every item, so after recoding the reversed
    # half carries the shared factor with the opposite sign.
    loadings = np.full(6, 0.6)
    reverse = np.arange(6) >= 3
    by_strength = [
        mean_alpha(
            replace(SYMMETRIC_NO_STYLE, acquiescence=s),
            loadings,
            reverse=reverse,
            recode=reverse,
        )
        for s in (0.0, 0.5, 1.0)
    ]
    assert by_strength == sorted(by_strength, reverse=True)
    assert by_strength[0] > by_strength[2] + 0.05


def test_extreme_style_moves_answers_to_1_and_5():
    def extreme_share(strength):
        profile = replace(SYMMETRIC_NO_STYLE, extreme=strength)
        x = simulate_profile(profile, 50_000, np.full(4, 0.6), np.random.default_rng(3))
        return np.isin(x, [1, 5]).mean()

    shares = [extreme_share(s) for s in (0.0, 0.5, 1.0)]
    assert shares == sorted(shares)
    assert shares[2] > shares[0] + 0.05
