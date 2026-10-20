"""Scenarios: simulate many surveys, score each one, summarize the spread of alpha.

Every scenario function returns a list of result rows (dicts). One row is one
setting replicated `reps` times, each replicate a fresh simulated sample.
"""

from dataclasses import replace
from typing import NamedTuple

import numpy as np
import pandas as pd

from .alpha import alpha_if_dropped, bootstrap_ci, cronbach_alpha, standardized_alpha
from .generate import RESPONSE_SHAPES, cutpoints_from_probs, reverse_score, simulate
from .profiles import PROFILES, Profile, simulate_profile
from .survey import (
    AGE_GROUPS,
    MARKETING_SENSORIAL,
    SATISFACCION,
    SATISFACCION_CORR,
    dimension_columns,
    factor_index,
    marketing_corr,
)

THRESHOLD = 0.7
DEFAULT_N = 200
DEFAULT_K = 5
DEFAULT_LOADING = 0.6

LOADINGS = np.round(np.arange(0.20, 0.901, 0.05), 2)
ITEM_COUNTS = [3, 5, 15]
SAMPLE_SIZES = [20, 50, 100, 400]
AGE_GROUP_SIZE = 100
AGE_LOADINGS = [0.8, 0.7, 0.5, 0.3]
SAME_LOADING = 0.7  # the loading both profiles share in the same-loading runs


def cell(
    scenario, setting, draw, reps, rng, planted=None, boot=0, boot_reps=None, truth=None, **cols
):
    """Replicate one setting and summarize raw alpha over the replicates.

    draw(rng) returns one (n, k) response matrix.
    planted: column of a known bad item. Adds how often alpha-if-dropped flags it.
    boot, boot_reps, truth: bootstrap resamples per replicate, how many replicates
        get an interval (the first ones; default all), and the population alpha.
        The interval should cover the population alpha, and a group whose alpha
        is below the threshold should not pass: `false_pass` and `false_fail`
        are the shares of replicates on the wrong side, 0 when the population
        alpha is on the other side.
    """
    boot_reps = reps if boot_reps is None else boot_reps
    truth = None if truth is None else float(truth)
    records = []
    for i in range(reps):
        x = draw(rng)
        record = {"raw": cronbach_alpha(x), "std": standardized_alpha(x)}
        if planted is not None:
            dropped = alpha_if_dropped(x)
            record["flagged"] = dropped.argmax() == planted
            record["dropped"] = dropped[planted]
        if boot and i < boot_reps:
            record["ci_lo"], record["ci_hi"] = bootstrap_ci(x, rng, boot)
        records.append(record)
    s = pd.DataFrame(records)

    row = {"scenario": scenario, "setting": setting, **cols}
    row |= {
        "reps": reps,
        "mean_alpha": s.raw.mean(),
        "p2_5": s.raw.quantile(0.025),
        "p97_5": s.raw.quantile(0.975),
        "share_ge_0_7": (s.raw >= THRESHOLD).mean(),  # nan counts as a miss
        "mean_std_alpha": s["std"].mean(),
    }
    if planted is not None:
        row |= {"flag_rate": s.flagged.mean(), "mean_alpha_dropped": s.dropped.mean()}
    if truth is not None:
        passed = (s.raw >= THRESHOLD).mean()
        row |= {
            "true_alpha": truth,
            "false_pass": passed if truth < THRESHOLD else 0.0,
            "false_fail": 1 - passed if truth >= THRESHOLD else 0.0,
        }
    if boot:
        b = s.dropna(subset=["ci_lo"])
        row |= {
            "ci_reps": len(b),
            "mean_ci_width": (b.ci_hi - b.ci_lo).mean(),
            "median_ci_width": (b.ci_hi - b.ci_lo).median(),
            "share_ci_lower_ge_0_7": (b.ci_lo >= THRESHOLD).mean(),
            "ci_coverage": ((b.ci_lo <= truth) & (truth <= b.ci_hi)).mean(),
        }
    return row


def equal_loadings(k, loading=DEFAULT_LOADING):
    return np.full(k, loading)


def loading_items(reps, rng):
    """Loading from 0.2 to 0.9 for scales of 3, 5 and 15 items."""
    return [
        cell(
            "loading_items",
            f"k={k}, loading={loading:.2f}",
            lambda r, k=k, loading=loading: simulate(DEFAULT_N, equal_loadings(k, loading), r),
            reps,
            rng,
            k=k,
            n=DEFAULT_N,
            loading=loading,
        )
        for k in ITEM_COUNTS
        for loading in LOADINGS
    ]


def sample_size(reps, rng):
    return [
        cell(
            "sample_size",
            f"n={n}, loading={loading}",
            lambda r, n=n, loading=loading: simulate(n, equal_loadings(DEFAULT_K, loading), r),
            reps,
            rng,
            k=DEFAULT_K,
            n=n,
            loading=loading,
        )
        for loading in [0.5, 0.6, 0.7]
        for n in SAMPLE_SIZES
    ]


def response_shape(reps, rng):
    """Same latent structure, answers piled toward one end of the scale."""
    return [
        cell(
            "response_shape",
            f"{shape}, loading={loading}",
            lambda r, probs=probs, loading=loading: simulate(
                DEFAULT_N,
                equal_loadings(DEFAULT_K, loading),
                r,
                cutpoints=cutpoints_from_probs(probs),
            ),
            reps,
            rng,
            k=DEFAULT_K,
            n=DEFAULT_N,
            loading=loading,
        )
        for loading in [0.5, 0.7]
        for shape, probs in RESPONSE_SHAPES.items()
    ]


def satisfaccion(reps, rng):
    """13 items, 3 dimensions: pooled as one scale, per dimension, and recoded."""
    factor = factor_index(SATISFACCION)
    loadings = equal_loadings(len(factor), 0.7)

    def draw(r, columns=slice(None), reversed_dims=()):
        x = simulate(DEFAULT_N, loadings, r, factor=factor, factor_corr=SATISFACCION_CORR)
        flip = np.isin(factor, [list(SATISFACCION).index(d) for d in reversed_dims])
        return reverse_score(x, flip)[:, columns]

    pooled = len(factor)
    settings = {"pooled, 13 items as is": (draw, pooled)}
    for name, size in SATISFACCION.items():
        columns = dimension_columns(SATISFACCION, name)
        settings[f"{name} alone, {size} items"] = (lambda r, c=columns: draw(r, c), size)
    settings["pooled, apatico reverse-scored"] = (
        lambda r: draw(r, reversed_dims=["apatico"]),
        pooled,
    )
    settings["pooled, apatico and problematico reverse-scored"] = (
        lambda r: draw(r, reversed_dims=["apatico", "problematico"]),
        pooled,
    )
    return [
        cell("satisfaccion", setting, d, reps, rng, k=k, n=DEFAULT_N, loading=0.7)
        for setting, (d, k) in settings.items()
    ]


def multidimensional(reps, rng):
    """Five correlated dimensions of 3 items, scored as one 15-item scale."""
    factor = factor_index(MARKETING_SENSORIAL)
    loadings = equal_loadings(len(factor), 0.7)
    vista = dimension_columns(MARKETING_SENSORIAL, "vista")

    def draw(r, factor_r, columns=slice(None)):
        x = simulate(DEFAULT_N, loadings, r, factor=factor, factor_corr=marketing_corr(factor_r))
        return x[:, columns]

    rows = [
        cell(
            "multidimensional",
            "one dimension alone, 3 items",
            lambda r: draw(r, 0.0, vista),
            reps,
            rng,
            k=3,
            n=DEFAULT_N,
            loading=0.7,
        )
    ]
    rows += [
        cell(
            "multidimensional",
            f"pooled 15 items, factor correlation={factor_r}",
            lambda r, factor_r=factor_r: draw(r, factor_r),
            reps,
            rng,
            k=15,
            n=DEFAULT_N,
            loading=0.7,
        )
        for factor_r in [0.0, 0.2, 0.4, 0.6]
    ]
    return rows


def age_groups(reps, rng):
    """Four age groups of 100: alpha inside each group versus pooled."""
    per_group = AGE_GROUP_SIZE
    group = np.repeat(np.arange(len(AGE_GROUPS)), per_group)
    variants = {
        "equal loadings": ([0.6, 0.6, 0.6, 0.6], None),
        "equal loadings, theta shifts": ([0.6, 0.6, 0.6, 0.6], [0.6, 0.2, -0.2, -0.6]),
        "different loadings": (AGE_LOADINGS, None),
        "different loadings, theta shifts": (AGE_LOADINGS, [0.6, 0.2, -0.2, -0.6]),
    }
    rows = []
    for variant, (group_loadings, shift) in variants.items():
        loadings = np.repeat(np.array(group_loadings)[:, None], DEFAULT_K, axis=1)

        def draw(r, loadings=loadings, shift=shift):
            return simulate(len(group), loadings, r, group=group, theta_shift=shift)

        parts = {"pooled": draw}
        for g, label in enumerate(AGE_GROUPS):
            parts[label] = lambda r, g=g, draw=draw: draw(r)[group == g]
        for part, d in parts.items():
            rows.append(
                cell(
                    "age_groups",
                    f"{variant}: {part}",
                    d,
                    reps,
                    rng,
                    k=DEFAULT_K,
                    n=len(group) if part == "pooled" else per_group,
                )
            )
    return rows


def bad_items(reps, rng):
    """One scale of 8 good items, spoiled in turn. Alpha-if-dropped looks for the culprit."""
    k, n, loading = 8, DEFAULT_N, 0.6
    good = equal_loadings(k, loading)
    noise_item = good.copy()
    noise_item[0] = 0.0
    reverse_first = np.arange(k) == 0

    cases = {
        "clean": (lambda r: simulate(n, good, r), None),
        "20% random responders": (lambda r: simulate(n, good, r, random_share=0.2), None),
        "20% straight-liners": (lambda r: simulate(n, good, r, straightline_share=0.2), None),
        "one noise item (loading 0)": (lambda r: simulate(n, noise_item, r), 0),
        "one reversed item, not recoded": (
            lambda r: simulate(n, good, r, reverse=reverse_first),
            0,
        ),
        "one reversed item, recoded": (
            lambda r: reverse_score(simulate(n, good, r, reverse=reverse_first), reverse_first),
            None,
        ),
    }
    return [
        cell("bad_items", setting, draw, reps, rng, planted=planted, k=k, n=n, loading=loading)
        for setting, (draw, planted) in cases.items()
    ]


def bootstrap_interval(reps, rng):
    """How wide the 95% bootstrap interval is, and whether it covers the true alpha."""
    reps = max(reps // 5, 1)
    loading = 0.7
    loadings = equal_loadings(DEFAULT_K, loading)
    truth = cronbach_alpha(simulate(200_000, loadings, rng))
    return [
        cell(
            "bootstrap_interval",
            f"n={n}",
            lambda r, n=n: simulate(n, loadings, r),
            reps,
            rng,
            boot=500,
            truth=truth,
            k=DEFAULT_K,
            n=n,
            loading=loading,
        )
        for n in SAMPLE_SIZES
    ]


STYLE_STRENGTHS = [0.0, 0.25, 0.5, 0.75, 1.0]


class Scale(NamedTuple):
    factor: np.ndarray  # factor of each item
    corr: np.ndarray  # correlation between the factors' traits
    reverse: np.ndarray | None  # items answered on the flipped scale
    recoded: bool  # whether the analyst scores the reverse-keyed items back


def profile_scales():
    """Marketing Sensorial, and Satisfaccion with the same answers scored as is and recoded."""
    satisfaccion = factor_index(SATISFACCION)
    # Apatico and problematico (dimensions 1 and 2) are worded against satisfaccion.
    dimension_against = np.arange(len(SATISFACCION)) > 0
    against = dimension_against[satisfaccion]
    # SATISFACCION_CORR relates the behaviours. These items are answered on the flipped
    # scale, so the traits are taken in the direction of satisfaccion: flipping a trait
    # flips the sign of its correlations. Recoding then gives positively correlated items.
    sign = np.where(dimension_against, -1, 1)
    corr = SATISFACCION_CORR * np.outer(sign, sign)
    return {
        "marketing sensorial": Scale(
            factor_index(MARKETING_SENSORIAL), marketing_corr(0.3), None, False
        ),
        "satisfaccion as is": Scale(satisfaccion, corr, against, False),
        "satisfaccion recoded": Scale(satisfaccion, corr, against, True),
    }


def profile_draw(profiles, scale, n=DEFAULT_N):
    """draw(rng): n respondents from each profile, stacked into one sample.

    The reverse-keyed items are generated as such, so acquiescence pulls them as the
    generator documents, and are scored back when the scale is recoded. The profile's
    cutpoints cut the item as worded, before the flip, so the answered shares on a
    reverse-keyed item are the profile's shares in reverse order.
    """

    def draw(r):
        samples = [
            simulate_profile(
                p,
                n,
                equal_loadings(len(scale.factor), p.loading),
                r,
                factor=scale.factor,
                factor_corr=scale.corr,
                reverse=scale.reverse,
            )
            for p in profiles
        ]
        x = np.vstack(samples)
        return reverse_score(x, scale.reverse) if scale.recoded else x

    return draw


def profile_rows(scenario, groups, reps, rng):
    """One row per scale and group of profiles; groups maps a label to a list of profiles."""
    return [
        cell(
            scenario,
            f"{name}, {label}",
            profile_draw(profiles, scale),
            reps,
            rng,
            k=len(scale.factor),
            n=DEFAULT_N * len(profiles),
            scale=name,
            profile=label,
        )
        for name, scale in profile_scales().items()
        for label, profiles in groups.items()
    ]


def profiles_assumed(reps, rng):
    """Each profile as assumed (cutpoints, style and loading differ), then both pooled."""
    both = list(PROFILES.values())
    return profile_rows("profiles", {p.name: [p] for p in both} | {"pooled": both}, reps, rng)


def profiles_same_loading(reps, rng):
    """Both profiles share one nominal loading: only cutpoints and response style differ."""
    both = [replace(p, loading=SAME_LOADING) for p in PROFILES.values()]
    return profile_rows(
        "profiles_same_loading", {p.name: [p] for p in both} | {"pooled": both}, reps, rng
    )


def profiles_style_split(reps, rng):
    """Marketing Sensorial at the shared loading, with only the styles or only the cutpoints."""
    scale = profile_scales()["marketing sensorial"]
    no_style = {"extreme": 0.0, "acquiescence": 0.0}
    shared_cutpoints = {"probs": tuple(RESPONSE_SHAPES["symmetric"])}
    variants = {"style only": shared_cutpoints, "cutpoints only": no_style}
    return [
        cell(
            "profiles_style_split",
            f"marketing sensorial, {p.name}, {variant}",
            profile_draw([replace(p, loading=SAME_LOADING, **change)], scale),
            reps,
            rng,
            k=len(scale.factor),
            n=DEFAULT_N,
            scale="marketing sensorial",
            profile=p.name,
        )
        for variant, change in variants.items()
        for p in PROFILES.values()
    ]


def response_style(reps, rng):
    """Alpha as one style trait grows from 0 to 1 while the other stays off."""
    return [
        cell(
            "response_style",
            f"{name}, {p.name}, {style}={strength}",
            profile_draw(
                [replace(p, **({"extreme": 0.0, "acquiescence": 0.0} | {style: strength}))], scale
            ),
            reps,
            rng,
            k=len(scale.factor),
            n=DEFAULT_N,
            scale=name,
            profile=p.name,
            style=style,
            strength=strength,
        )
        for name, scale in profile_scales().items()
        for p in PROFILES.values()
        for style in ["extreme", "acquiescence"]
        for strength in STYLE_STRENGTHS
    ]


SMALL_SIZES = [30, 40, 50, DEFAULT_N]
SMALL_SCALES = ["marketing sensorial", "satisfaccion recoded"]
SMALL_BOOT = 500
POPULATION_N = 200_000
# The sample the workbooks hold: the size of a small group.
WORKBOOK_N = 50


def small_group_profiles():
    """Lima and california as assumed, then each age group: symmetric answers, no styles.

    An age group takes the loading of the age-group scenario for every item.
    """
    symmetric = tuple(RESPONSE_SHAPES["symmetric"])
    ages = {
        label: Profile(label, symmetric, extreme=0.0, acquiescence=0.0, loading=loading)
        for label, loading in zip(AGE_GROUPS, AGE_LOADINGS, strict=True)
    }
    return dict(PROFILES) | ages


def small_groups(reps, rng):
    """Small groups at 30, 40, 50 and 200 respondents against the population alpha.

    The population alpha is that of the same setting at 200000 respondents. The
    bootstrap runs on a tenth of the replicates to keep the run short.
    """
    scales = profile_scales()
    rows = []
    for name in SMALL_SCALES:
        scale = scales[name]
        for label, profile in small_group_profiles().items():
            truth = cronbach_alpha(profile_draw([profile], scale, POPULATION_N)(rng))
            rows += [
                cell(
                    "small_groups",
                    f"{name}, {label}, n={n}",
                    profile_draw([profile], scale, n),
                    reps,
                    rng,
                    boot=SMALL_BOOT,
                    boot_reps=max(reps // 10, 1),
                    truth=truth,
                    k=len(scale.factor),
                    n=n,
                    scale=name,
                    group=label,
                )
                for n in SMALL_SIZES
            ]
    return rows


SCENARIOS = [
    loading_items,
    sample_size,
    response_shape,
    satisfaccion,
    multidimensional,
    age_groups,
    bad_items,
    bootstrap_interval,
    profiles_assumed,
    profiles_same_loading,
    response_style,
    profiles_style_split,
    small_groups,
]


def run_all(reps, seed):
    rng = np.random.default_rng(seed)
    return pd.DataFrame([row for scenario in SCENARIOS for row in scenario(reps, rng)])
