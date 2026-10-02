"""Assumed respondent profiles: how a group tends to answer, apart from what it feels.

Every number here is an assumption of the simulation. None was measured on the
real survey or taken from a study of Lima or California respondents.
"""

from dataclasses import dataclass

import numpy as np

from .generate import cutpoints_from_probs, latent_draw, simulate


@dataclass(frozen=True)
class Profile:
    name: str
    # Share of answers in categories 1..5 that the cutpoints give before the styles act.
    # Extreme responding stretches scores outward, so the realised shares differ:
    # see `realised_shares`.
    probs: tuple
    extreme: float  # extreme response style: sd of the log gain, see generate.latent_draw
    acquiescence: float  # sd of the tendency to agree, see generate.latent_draw
    # Nominal loading, the same for every item. It is the item-trait correlation only
    # without response styles: see `item_trait_correlation`.
    loading: float = 0.7


PROFILES = {
    # More answers on 4-5 and on both extremes.
    "lima": Profile("lima", (0.06, 0.06, 0.13, 0.30, 0.45), extreme=0.5, acquiescence=0.5),
    # More 3s and 4s, still skewed toward agreement, and a weaker measurement of the trait.
    "california": Profile(
        "california", (0.03, 0.09, 0.28, 0.38, 0.22), extreme=0.2, acquiescence=0.2, loading=0.6
    ),
}


def simulate_profile(profile, n, loadings, rng, **kwargs):
    """`simulate` with the profile's cutpoints and response style. The loadings stay the caller's."""
    return simulate(
        n,
        loadings,
        rng,
        cutpoints=cutpoints_from_probs(profile.probs),
        extreme=profile.extreme,
        acquiescence=profile.acquiescence,
        **kwargs,
    )


def realised_shares(profile, n=200_000, seed=0):
    """Share of answers 1..5 on a keyed item once the styles have acted."""
    x = simulate_profile(profile, n, np.array([profile.loading]), np.random.default_rng(seed))
    return np.bincount(x.ravel(), minlength=6)[1:] / x.size


def item_trait_correlation(profile, n=200_000, seed=0):
    """Correlation of a keyed item's continuous score with its own trait, styles on.

    Measured on a large simulated sample, before the score is cut into categories.
    """
    theta, x = latent_draw(
        n,
        np.array([profile.loading]),
        np.random.default_rng(seed),
        extreme=profile.extreme,
        acquiescence=profile.acquiescence,
    )
    return np.corrcoef(theta[:, 0], x[:, 0])[0, 1]
