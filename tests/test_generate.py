import numpy as np

from cronbach_lab.generate import (
    RESPONSE_SHAPES,
    cutpoints_from_probs,
    equicorrelated,
    latent_items,
    reverse_score,
    simulate,
)


def test_same_seed_gives_same_data() -> None:
    a = simulate(50, np.full(4, 0.6), np.random.default_rng(1))
    b = simulate(50, np.full(4, 0.6), np.random.default_rng(1))
    assert (a == b).all()


def test_responses_are_likert_integers() -> None:
    x = simulate(500, np.full(4, 0.6), np.random.default_rng(1))
    assert x.shape == (500, 4)
    assert set(np.unique(x)) <= {1, 2, 3, 4, 5}


def test_cutpoints_give_the_requested_category_shares() -> None:
    for shape, probs in RESPONSE_SHAPES.items():
        x = simulate(
            100_000,
            np.array([0.5]),
            np.random.default_rng(2),
            cutpoints=cutpoints_from_probs(probs),
        )
        shares = np.bincount(x.ravel(), minlength=6)[1:] / x.size
        assert np.allclose(shares, probs, atol=0.01), shape


def test_loading_is_the_item_trait_correlation() -> None:
    rng = np.random.default_rng(3)
    x = latent_items(100_000, np.array([0.8, 0.5]), rng)
    assert np.allclose(x.var(axis=0), 1, atol=0.02)
    assert np.isclose(np.corrcoef(x, rowvar=False)[0, 1], 0.8 * 0.5, atol=0.01)


def test_factors_structure_items_correlate_more_within_a_factor() -> None:
    rng = np.random.default_rng(4)
    factor = np.array([0, 0, 1, 1])
    x = latent_items(
        50_000, np.full(4, 0.7), rng, factor=factor, factor_corr=equicorrelated(2, 0.3)
    )
    corr = np.corrcoef(x, rowvar=False)
    assert np.isclose(corr[0, 1], 0.49, atol=0.02)
    assert np.isclose(corr[0, 2], 0.49 * 0.3, atol=0.02)


def test_reverse_keyed_item_flips_and_recodes_back() -> None:
    loadings = np.full(3, 0.7)
    reverse = np.array([False, True, False])
    plain = simulate(2000, loadings, np.random.default_rng(5))
    flipped = simulate(2000, loadings, np.random.default_rng(5), reverse=reverse)
    assert (flipped[:, 1] == 6 - plain[:, 1]).all()
    assert (reverse_score(flipped, reverse) == plain).all()


def test_group_loadings_and_shifts() -> None:
    group = np.repeat([0, 1], 20_000)
    loadings = np.array([[0.9] * 3, [0.3] * 3])
    x = latent_items(
        len(group), loadings, np.random.default_rng(6), group=group, theta_shift=[1.0, -1.0]
    )
    first, second = x[group == 0], x[group == 1]
    assert np.isclose(first[:, 0].mean(), 0.9, atol=0.03)
    assert np.isclose(second[:, 0].mean(), -0.3, atol=0.03)
    assert np.corrcoef(first, rowvar=False)[0, 1] > np.corrcoef(second, rowvar=False)[0, 1] + 0.5


def test_straight_liners_answer_one_value_and_random_responders_vary() -> None:
    k = 6
    x = simulate(1000, np.full(k, 0.6), np.random.default_rng(7), straightline_share=0.3)
    constant_rows = (x == x[:, :1]).all(axis=1).mean()
    assert 0.25 < constant_rows < 0.4

    y = simulate(1000, np.full(k, 0.99), np.random.default_rng(7), random_share=0.5)
    near_constant = (y.max(axis=1) - y.min(axis=1) <= 1).mean()
    assert near_constant < 0.6
