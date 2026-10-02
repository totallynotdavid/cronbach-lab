from dataclasses import replace

import numpy as np
import pytest

from cronbach_lab.alpha import cronbach_alpha
from cronbach_lab.generate import RESPONSE_SHAPES, latent_items, reverse_score
from cronbach_lab.profiles import PROFILES, realised_shares, simulate_profile
from cronbach_lab.scenarios import profile_draw, profile_scales

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


@pytest.mark.parametrize("name", ["lima", "california"])
def test_real_profile_without_style_sits_a_known_gap_under_theory(name):
    # Before cutting, equal loadings give the theoretical alpha exactly. Cutting into
    # 5 categories turns the items into coarse Pearson variables, which correlate less
    # than the latent scores do, so alpha falls under theory. Skewed cutpoints leave
    # few answers in the thin tail categories, so the loss is larger than for the
    # symmetric cutpoints (about 0.03): about 0.05 for lima and 0.03 for california.
    k, loading = 6, 0.6
    profile = replace(PROFILES[name], extreme=0.0, acquiescence=0.0)
    theory = theoretical_alpha(k, loading)

    rng = np.random.default_rng(0)
    continuous = np.mean(
        [cronbach_alpha(latent_items(3000, np.full(k, loading), rng)) for _ in range(20)]
    )
    assert continuous == pytest.approx(theory, abs=0.01)

    gap = theory - mean_alpha(profile, np.full(k, loading))
    assert 0.025 < gap < 0.07


def test_skewed_cutpoints_lose_more_alpha_than_symmetric_ones():
    loadings = np.full(6, 0.6)
    lima = replace(PROFILES["lima"], extreme=0.0, acquiescence=0.0)
    assert mean_alpha(lima, loadings) < mean_alpha(SYMMETRIC_NO_STYLE, loadings) - 0.01


def test_symmetric_profile_without_style_is_just_under_theory():
    k, loading = 6, 0.6
    simulated = mean_alpha(SYMMETRIC_NO_STYLE, np.full(k, loading))
    assert theoretical_alpha(k, loading) - 0.04 < simulated < theoretical_alpha(k, loading)


def test_style_traits_off_leave_the_latent_scores_untouched():
    plain = latent_items(50, np.full(4, 0.6), np.random.default_rng(1))
    off = latent_items(50, np.full(4, 0.6), np.random.default_rng(1), acquiescence=0.0, extreme=0.0)
    assert np.array_equal(plain, off)


def test_profile_cutpoints_give_its_answer_shares_even_with_acquiescence():
    # Acquiescence is rescaled item by item to keep unit variance, so the shares do not
    # move, on the reverse-keyed items either (the answered scale is flipped for them).
    lima = replace(PROFILES["lima"], extreme=0.0, acquiescence=0.7)
    reverse = np.array([False, False, True, True])
    x = simulate_profile(lima, 200_000, np.full(4, 0.6), np.random.default_rng(2), reverse=reverse)
    for item, flipped in enumerate(reverse):
        shares = np.bincount(x[:, item], minlength=6)[1:] / len(x)
        expected = lima.probs[::-1] if flipped else lima.probs
        assert shares == pytest.approx(expected, abs=0.01)


@pytest.mark.parametrize("name", ["lima", "california"])
def test_realised_loading_is_the_item_trait_correlation_under_acquiescence(name):
    profile = replace(PROFILES[name], extreme=0.0, loading=0.7)
    seed = 8
    x = latent_items(
        200_000,
        np.array([profile.loading]),
        np.random.default_rng(seed),
        acquiescence=profile.acquiescence,
    )
    # The first draw of latent_items is theta.
    theta = np.random.default_rng(seed).multivariate_normal([0.0], [[1.0]], size=200_000)
    assert np.corrcoef(x[:, 0], theta[:, 0])[0, 1] == pytest.approx(
        profile.realised_loading, abs=0.01
    )
    assert profile.realised_loading < profile.loading


def test_style_scores_have_unit_variance_on_every_item():
    reverse = np.array([False, False, True, True])
    x = latent_items(
        200_000, np.full(4, 0.6), np.random.default_rng(4), reverse=reverse, acquiescence=1.0
    )
    assert x.var(axis=0) == pytest.approx(1.0, abs=0.02)


def test_realised_shares_differ_from_the_declared_ones_only_through_extreme_style():
    lima = PROFILES["lima"]
    assert realised_shares(lima).sum() == pytest.approx(1.0)
    assert realised_shares(lima)[0] > lima.probs[0] + 0.01
    calm = replace(lima, extreme=0.0)
    assert realised_shares(calm) == pytest.approx(lima.probs, abs=0.01)


def test_recoding_turns_the_reverse_keyed_items_from_negative_to_positive_correlations():
    # The same answers are scored two ways. Without style, flipping and recoding must not
    # cancel: the reverse-keyed items run against the others as answered and with them once
    # recoded.
    scales = profile_scales()

    def cross_corr(name):
        scale = scales[name]
        x = profile_draw([SYMMETRIC_NO_STYLE], scale, n=40_000)(np.random.default_rng(6))
        corr = np.corrcoef(x, rowvar=False)
        return corr[np.ix_(~scale.reverse, scale.reverse)].mean()

    assert cross_corr("satisfaccion as is") < -0.1
    assert cross_corr("satisfaccion recoded") > 0.1


def test_recoded_scenario_uses_the_reduced_acquiescence_pull():
    # Loading 0 leaves only acquiescence, so the correlation between an item and a
    # recoded item is the shared tendency. In the answered scale the recoded items get
    # pull -0.5 against +1 for the others: corr = -0.5 s^2 / sqrt((1 + s^2)(1 + 0.25 s^2)),
    # -0.32 for s = 1. Applying the full pull to them would give -0.5.
    profile = replace(SYMMETRIC_NO_STYLE, loading=0.0, acquiescence=1.0)
    scale = profile_scales()["satisfaccion recoded"]
    x = profile_draw([profile], scale, n=60_000)(np.random.default_rng(5))
    corr = np.corrcoef(x, rowvar=False)
    keyed_vs_recoded = corr[np.ix_(~scale.reverse, scale.reverse)].mean()
    assert -0.36 < keyed_vs_recoded < -0.27


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
