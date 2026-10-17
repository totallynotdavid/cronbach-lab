"""Plots and findings.md, both built from the results table."""

import textwrap
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .profiles import PROFILES, item_trait_correlation, realised_shares
from .scenarios import DEFAULT_N, ITEM_COUNTS, SAME_LOADING, THRESHOLD, WORKBOOK_N


def plot_loading_items(results: pd.DataFrame, path: Path) -> None:
    d = results[results.scenario == "loading_items"]
    fig, (alpha_ax, share_ax) = plt.subplots(1, 2, figsize=(11, 4))
    for k, g in d.groupby("k"):
        alpha_ax.plot(g.loading, g.mean_alpha, label=f"{k} items")
        alpha_ax.fill_between(g.loading, g.p2_5, g.p97_5, alpha=0.2)
        share_ax.plot(g.loading, g.share_ge_0_7, label=f"{k} items")
    alpha_ax.axhline(THRESHOLD, color="k", ls="--", lw=1)
    alpha_ax.set(xlabel="item loading", ylabel="Cronbach alpha", title="mean and 2.5-97.5% band")
    share_ax.set(xlabel="item loading", ylabel=f"share of runs with alpha >= {THRESHOLD}")
    alpha_ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_bars(results: pd.DataFrame, scenario: str, path: Path) -> None:
    """One horizontal bar per setting: mean alpha, with the 2.5-97.5% band as whiskers."""
    d = results[results.scenario == scenario].iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 0.4 * len(d) + 1.5))
    ax.barh(
        d.setting,
        d.mean_alpha,
        xerr=[d.mean_alpha - d.p2_5, d.p97_5 - d.mean_alpha],
        color="tab:blue",
        alpha=0.7,
    )
    for y, share in enumerate(d.share_ge_0_7):
        ax.text(1.02, y, f"{share:.0%}", va="center", transform=ax.get_yaxis_transform())
    ax.axvline(THRESHOLD, color="k", ls="--", lw=1)
    ax.set(xlabel="Cronbach alpha (bar = mean, whiskers = 2.5-97.5%); right = share >= 0.7")
    ax.set_title(scenario)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_response_style(results: pd.DataFrame, path: Path) -> None:
    """Mean alpha against the strength of one style trait, a panel per scale."""
    d = results[results.scenario == "response_style"]
    scales = d.scale.unique()
    fig, axes = plt.subplots(1, len(scales), figsize=(4.5 * len(scales), 4), sharey=True)
    for ax, scale in zip(axes, scales, strict=True):
        for (profile, style), g in d[d.scale == scale].groupby(["profile", "style"]):
            ax.plot(
                g.strength,
                g.mean_alpha,
                color={"lima": "tab:red", "california": "tab:blue"}[profile],
                ls="-" if style == "acquiescence" else "--",
                label=f"{profile}, {style}",
            )
        ax.axhline(THRESHOLD, color="k", ls=":", lw=1)
        ax.set(title=scale, xlabel="style strength (sd of the trait)")
    axes[0].set_ylabel("mean Cronbach alpha")
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_small_groups(results: pd.DataFrame, path: Path) -> None:
    """Alpha band per group at each sample size, a panel per scale, with the population alpha."""
    d = results[results.scenario == "small_groups"]
    scales = d.scale.unique()
    sizes = sorted(d.n.unique())
    fig, axes = plt.subplots(1, len(scales), figsize=(6 * len(scales), 5.5), sharey=True)
    for ax, scale in zip(axes, scales, strict=True):
        g = d[d.scale == scale]
        groups = list(g.group.unique())
        for j, n in enumerate(sizes):
            h = g[g.n == n].set_index("group").loc[groups]
            y = np.arange(len(groups)) + (j - (len(sizes) - 1) / 2) * 0.18
            ax.errorbar(
                h.mean_alpha,
                y,
                xerr=[h.mean_alpha - h.p2_5, h.p97_5 - h.mean_alpha],
                fmt="o",
                ms=3,
                capsize=2,
                label=f"n={n}",
            )
        truth = g[g.n == sizes[0]].set_index("group").loc[groups].true_alpha
        ax.scatter(truth, np.arange(len(groups)), marker="D", color="k", s=18, zorder=3)
        ax.axvline(THRESHOLD, color="k", ls="--", lw=1)
        ax.set_yticks(np.arange(len(groups)), groups)
        ax.set(
            title=scale, xlabel="Cronbach alpha (dot = mean, bar = 2.5-97.5%, diamond = population)"
        )
    axes[0].invert_yaxis()  # the y axis is shared, so invert it once
    axes[0].legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def write_plots(results: pd.DataFrame, out_dir: str | Path) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_loading_items(results, out_dir / "loading_items.png")
    plot_response_style(results, out_dir / "response_style.png")
    for scenario in results.scenario.unique():
        if scenario not in ("loading_items", "response_style", "small_groups"):
            plot_bars(results, scenario, out_dir / f"{scenario}.png")
    plot_small_groups(results, out_dir / "small_groups.png")


def md_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """Markdown table with padded columns, laid out as oxfmt would."""
    cells = [[str(cell) for cell in row] for row in rows]
    widths = [max(len(c) for c in column) for column in zip(headers, *cells, strict=True)]

    def line(row: Sequence[str]) -> str:
        return "| " + " | ".join(c.ljust(w) for c, w in zip(row, widths, strict=True)) + " |"

    rule = "| " + " | ".join("-" * w for w in widths) + " |"
    return "\n".join([line(headers), rule, *(line(row) for row in cells)])


def rows_of(results: pd.DataFrame, scenario: str, extra: Sequence[str] = ()) -> list[list[Any]]:
    """Table rows for one scenario: setting, mean, band, share passing, plus extra columns."""
    d = results[results.scenario == scenario]
    return [
        [
            r.setting,
            f"{r.mean_alpha:.2f}",
            f"{r.p2_5:.2f} to {r.p97_5:.2f}",
            f"{r.share_ge_0_7:.0%}",
        ]
        + ["" if np.isnan(getattr(r, column)) else f"{getattr(r, column):.2f}" for column in extra]
        for r in d.itertuples()
    ]


def scenario_table(results: pd.DataFrame, scenario: str, extra: Sequence[str] = ()) -> str:
    headers = ["setting", "mean alpha", "2.5-97.5% band", "runs >= 0.7", *extra]
    return md_table(headers, rows_of(results, scenario, extra))


def one(results: pd.DataFrame, scenario: str, setting: str) -> Any:
    d = results[(results.scenario == scenario) & (results.setting == setting)]
    return d.iloc[0]


def loading_edges(results: pd.DataFrame) -> list[list[Any]]:
    """Per item count: the loading needed for alpha 0.7 in theory and in the simulation."""
    d = results[results.scenario == "loading_items"]
    rows: list[list[Any]] = []
    for k in ITEM_COUNTS:
        g = d[d.k == k]
        # Standardized alpha = k*rho/(1+(k-1)*rho) with rho = loading**2 for equal
        # loadings. Solve for alpha = 0.7. Discretizing to 5 categories lowers
        # correlations a little, so the simulation needs a slightly higher loading.
        theory = np.sqrt(THRESHOLD / (k - (k - 1) * THRESHOLD))
        mean_edge = g[g.mean_alpha >= THRESHOLD].loading.min()
        reliable_edge = g[g.share_ge_0_7 >= 0.9].loading.min()
        rows.append([k, f"{theory:.2f}", f"{mean_edge:.2f}", f"{reliable_edge:.2f}"])
    return rows


def loading_grid(results: pd.DataFrame) -> str:
    d = results[results.scenario == "loading_items"]
    rows: list[list[str]] = []
    for loading, g in d.groupby("loading"):
        by_k = {r.k: r for r in g.itertuples()}
        rows.append(
            [f"{loading:.2f}"]
            + [f"{by_k[k].mean_alpha:.2f} ({by_k[k].share_ge_0_7:.0%})" for k in ITEM_COUNTS]
        )
    return md_table(["loading", *(f"{k} items" for k in ITEM_COUNTS)], rows)


def profile_findings(results: pd.DataFrame) -> str:
    def at(scenario: str, scale: str, profile: str) -> float:
        return float(one(results, scenario, f"{scale}, {profile}").mean_alpha)

    def sensitivity(scale: str, profile: str, style: str, strength: float) -> float:
        setting = f"{scale}, {profile}, {style}={strength}"
        return float(one(results, "response_style", setting).mean_alpha)

    marketing, as_is, recoded = "marketing sensorial", "satisfaccion as is", "satisfaccion recoded"
    assumptions = md_table(
        [
            "profile",
            "cutpoint shares 1..5 (%)",
            "realised shares 1..5 (%)",
            "extreme sd",
            "acquiescence sd",
            "loading",
            "keyed item-trait r",
        ],
        [
            [
                p.name,
                " / ".join(f"{100 * share:.0f}" for share in p.probs),
                " / ".join(f"{100 * share:.1f}" for share in realised_shares(p)),
                p.extreme,
                p.acquiescence,
                p.loading,
                f"{item_trait_correlation(p):.2f}",
            ]
            for p in PROFILES.values()
        ],
    )

    def table(scenario: str) -> str:
        rows = [
            [
                scale,
                *(
                    f"{one(results, scenario, f'{scale}, {p}').mean_alpha:.2f} "
                    f"({one(results, scenario, f'{scale}, {p}').share_ge_0_7:.0%})"
                    for p in [*PROFILES, "pooled"]
                ),
            ]
            for scale in [marketing, as_is, recoded]
        ]
        return md_table(["scale", *PROFILES, "pooled"], rows)

    sweep = md_table(
        ["scale", "profile", "extreme 0", "extreme 1", "acquiescence 0", "acquiescence 1"],
        [
            [
                scale,
                profile,
                *(
                    f"{sensitivity(scale, profile, style, strength):.2f}"
                    for style in ["extreme", "acquiescence"]
                    for strength in [0.0, 1.0]
                ),
            ]
            for scale in [marketing, as_is, recoded]
            for profile in PROFILES
        ],
    )

    def gap(scenario: str, scale: str) -> float:
        return at(scenario, scale, "lima") - at(scenario, scale, "california")

    gap_marketing = gap("profiles_same_loading", marketing)
    gap_as_is = gap("profiles_same_loading", as_is)
    gap_recoded = gap("profiles_same_loading", recoded)

    def split_gap(variant: str) -> float:
        return at("profiles_style_split", marketing, f"lima, {variant}") - at(
            "profiles_style_split", marketing, f"california, {variant}"
        )

    gap_style_only = split_gap("style only")
    gap_cutpoints_only = split_gap("cutpoints only")

    same_loading_r = {
        p.name: item_trait_correlation(replace(p, loading=SAME_LOADING)) for p in PROFILES.values()
    }
    # Shares as answered on a mirrored item: the keyed shares in reverse order.
    answered = {name: 100 * realised_shares(p)[::-1] for name, p in PROFILES.items()}
    lima_high, california_high = answered["lima"][3:].sum(), answered["california"][3:].sum()
    lima_nunca, california_nunca = answered["lima"][0], answered["california"][0]

    def acquiescence(scale: str) -> tuple[float, float]:
        return (
            sensitivity(scale, "lima", "acquiescence", 0.0),
            sensitivity(scale, "lima", "acquiescence", 1.0),
        )

    marketing_off, marketing_on = acquiescence(marketing)
    as_is_off, as_is_on = acquiescence(as_is)
    recoded_off, recoded_on = acquiescence(recoded)

    california_marketing = at("profiles", marketing, "california")
    lima_marketing = at("profiles", marketing, "lima")
    pooled_marketing = at("profiles", marketing, "pooled")

    return f"""## 9. Location profiles: lima and california

Everything in this section is an assumption of the simulation. The two profiles
are invented to show what response habits can do to alpha. They are not measured
on real Lima or California respondents. A profile sets the cutpoints (the share
of answers in each category before the styles act), an extreme-response style (each respondent has a gain that
stretches their score toward 1 and 5), an acquiescence style (each respondent
has a tendency to agree that raises the answer to every item) and a loading.

{assumptions}

The cutpoint shares are what the cutpoints give before the styles act. Extreme
responding stretches each respondent's score, so more answers fall on 1 and 5
and the realised shares (a keyed item, a large simulated sample) differ from the
cutpoint ones. Acquiescence is rescaled and leaves the shares alone.

The loading is nominal. It is the item-trait correlation only without response
styles. The last column is measured: the correlation of a keyed item's
continuous score with its own trait, before it is cut, in a large simulated
sample with the profile's styles on.

Three scales are scored, each with {DEFAULT_N} respondents per profile.
Marketing Sensorial is pooled as 15 items (dimensions correlated 0.3).
Satisfaccion is pooled as 13 items and scored two ways. Its apatico and
problematico items are worded against satisfaccion, so respondents answer them
on the flipped scale. "As is" adds the raw answers, so those items run against
entusiasta. "Recoded" reverse-scores them first. Acquiescence pulls a
reverse-keyed item half as hard as a keyed one (an assumption). Cells show mean
alpha and the share of runs >= {THRESHOLD}.

A profile's cutpoints cut each item as worded, before the flip. The apatico and
problematico items are answered flipped, so on them the answered shares are the
profile's shares in reverse order. Lima still has more 4-5 answers on those
mirrored items than california ({lima_high:.1f}% against {california_high:.1f}%). What
differs is the other end: lima piles up at 1 ({lima_nunca:.0f}% against
{california_nunca:.0f}%).

### Alpha per profile, and both profiles pooled

Profiles as assumed: they differ in cutpoints, style and loading.

{table("profiles")}

### Same loading, with each profile's own cutpoints and style

Both profiles get the nominal loading {SAME_LOADING}, so the construct is the same. Each keeps its
own cutpoints and its own response style. The nominal loading is shared, the
measurement is not: measured with the styles on, the item-trait correlation of a
keyed item is {same_loading_r["lima"]:.2f} for lima and {same_loading_r["california"]:.2f} for california.

{table("profiles_same_loading")}

With the same nominal loading the profiles still differ. Lima minus california is
{gap_marketing:+.2f} on Marketing Sensorial, {gap_as_is:+.2f} on Satisfaccion as is and
{gap_recoded:+.2f} on Satisfaccion recoded. Alpha moved and the construct did not, and the
gap depends on how the scale is scored.

Marketing Sensorial separates the two sources. Give both profiles the same symmetric
cutpoints and keep their styles: lima minus california is {gap_style_only:+.3f}. Keep
their own cutpoints and drop the styles: it is {gap_cutpoints_only:+.3f}. The gap
is mostly response style, not the cutpoints.

### Sensitivity to the strength of the style

One style at a time (the other is zero), the profile's own cutpoints and loading.
Strength is the standard deviation of the respondent trait. The plot is
`plots/response_style.png`.

{sweep}

Acquiescence adds one factor to every answer as given, whatever the item says,
so it raises alpha when the answers are scored as given, without
reverse-scoring. Marketing Sensorial,
where every item points the same way, goes from {marketing_off:.2f} to {marketing_on:.2f} for lima.
Satisfaccion as is, whose dimensions run against each other, also rises, from
{as_is_off:.2f} to {as_is_on:.2f}, because the raw answers all carry the shared factor with the
same sign. After reverse-scoring apatico and problematico, the shared factor
enters the entusiasta items with a plus sign and the recoded items with a minus
sign, so it splits the scale instead of uniting it and alpha falls, from
{recoded_off:.2f} to {recoded_on:.2f} for lima. Extreme responding moves alpha less than
acquiescence on Marketing Sensorial.

### What alpha can and cannot tell here

Alpha computed within each group does detect a group whose items hang together
less: california Marketing Sensorial sits at {california_marketing:.2f} against {lima_marketing:.2f}
for lima. Pooled it is {pooled_marketing:.2f}, so the pooled value hides the weaker group.

Alpha cannot tell why a group scores high or low. In the same-loading runs the
construct and the nominal loading are identical and alpha still differs, because
answer habits add or remove shared variance. The sensitivity table shows the
extreme case: Satisfaccion as is mixes items that run against each other, yet
with strong acquiescence lima's alpha reaches {as_is_on:.2f} against {as_is_off:.2f} with none. A
pass can come from acquiescence, not from measuring one trait well. Pooled alpha also hides that the groups use the scale
differently: it is one number from one covariance matrix, and a mixture of groups
with different cutpoints and loadings gives a matrix that belongs to neither.

Telling a real difference in the construct from a difference in how the groups
answer takes a multi-group invariance test (multi-group confirmatory factor
analysis). It asks, in order, whether the groups share the factor structure
(configural), the loadings (metric) and the item intercepts or thresholds
(scalar). Only with scalar invariance can the groups' scores be pooled or
compared. This lab does not run one, because it needs structural equation
modelling tools beyond its dependencies.
"""


def small_group_findings(results: pd.DataFrame) -> str:
    d = results[results.scenario == "small_groups"]
    sizes = sorted(d.n.unique())
    smallest, small, largest = sizes[0], WORKBOOK_N, sizes[-1]
    ci_reps = int(d.ci_reps.iloc[0])
    replicates = int(d.reps.iloc[0])

    def table(scale: str) -> str:
        rows: list[list[Any]] = []
        r: Any
        for r in d[d.scale == scale].itertuples():
            below = r.true_alpha < THRESHOLD
            rows.append(
                [
                    r.group,
                    r.n,
                    f"{r.true_alpha:.2f}",
                    f"{r.mean_alpha:.2f}",
                    f"{r.p2_5:.2f} to {r.p97_5:.2f}",
                    f"{r.share_ge_0_7:.0%}",
                    f"{r.false_pass:.0%}" if below else "-",
                    "-" if below else f"{r.false_fail:.0%}",
                    f"{r.median_ci_width:.2f}",
                    f"{r.ci_coverage:.0%}",
                ]
            )
        headers = [
            "group",
            "n",
            "population alpha",
            "mean alpha",
            "2.5-97.5% band",
            "runs >= 0.7",
            "false pass",
            "false fail",
            "median interval width",
            "interval covers",
        ]
        return md_table(headers, rows)

    at = d[d.n == small]
    wrong_pass = at.iloc[int(at.false_pass.argmax())]
    wrong_fail = at.iloc[int(at.false_fail.argmax())]

    def same(n: int, row: Any) -> Any:
        return d[(d.n == n) & (d.scale == row.scale) & (d.group == row.group)].iloc[0]

    wrong_pass_large, wrong_fail_large = (
        same(largest, wrong_pass).false_pass,
        same(largest, wrong_fail).false_fail,
    )
    gap = (at.true_alpha - at.mean_alpha).max()
    under = int((at.mean_alpha < at.true_alpha).sum())

    def band_width(n: int) -> float:
        return float((d[d.n == n].p97_5 - d[d.n == n].p2_5).median())

    def interval_width(n: int) -> float:
        return float(d[d.n == n].median_ci_width.median())

    coverage = d.groupby("n").ci_coverage.mean()
    intervals = ci_reps * d.groupby("n").size().iloc[0]
    error = 1.96 * np.sqrt(0.95 * 0.05 / intervals)
    below = [n for n in sizes if coverage[n] < 0.95 - error]

    def names(ns: Sequence[int]) -> str:
        return " and ".join(f"n={n}" for n in ns)

    tiny = sizes[:2]
    if any(n in below for n in tiny):
        verdict = (
            f"Yes: coverage falls below 95% at {names([n for n in tiny if n in below])}, "
            f"by more than the sampling error of this estimate (about {error:.1%})."
        )
    else:
        verdict = (
            f"No: at {names(tiny)} the coverage is within the sampling error of this "
            f"estimate (about {error:.1%}) of 95%."
        )
    others = [n for n in sizes[2:] if n in below]
    if others:
        verdict += f" It is also below 95% at {names(others)}, so the shortfall is not limited to the smallest groups."
    covers = ", ".join(f"{coverage[n]:.1%} at n={n}" for n in sizes)

    return f"""## 10. Small groups of 30 to 50, against the population alpha

Everything here is an assumption of the simulation, like section 9. Each group
is a profile (lima, california) or an age group (loadings 0.8, 0.7, 0.5 and 0.3,
as in section 6, symmetric answers, no response styles), scored on Marketing
Sensorial and on Satisfaccion recoded. Each is drawn at n={smallest}, {sizes[1]}, {small}
and {largest} respondents, {replicates} replicates per row. "Population alpha" is the
alpha of the same setting at 200000 respondents, one draw.

A false pass is a run with alpha >= {THRESHOLD} in a group whose population alpha
is below it. A false fail is a run below {THRESHOLD} in a group whose population alpha
is {THRESHOLD} or more. A group is on one side, so the other column shows a dash. The
interval is the 95% percentile bootstrap (500 resamples). To keep the run short
it is computed on the first {ci_reps} of the {replicates} replicates of each row, so
its width and coverage rest on {ci_reps} samples per row and are noisier than the
alpha columns. The plot is `plots/small_groups.png`.

### Marketing Sensorial

{table("marketing sensorial")}

### Satisfaccion recoded

{table("satisfaccion recoded")}

### What a small group can show

A group of {small} reads a little low. Its mean alpha is under the population
alpha in {under} of the {len(at)} settings, by at most {gap:.2f}, and the spread is
wide: the middle 95% of alpha spans {band_width(small):.2f} at n={small} (median over the settings), against
{band_width(largest):.2f} at n={largest}.

How often a weak group looks fine by chance depends on how close it is to 0.7.
The worst false pass at n={small} is {wrong_pass.group} on {wrong_pass.scale}, with
population alpha {wrong_pass.true_alpha:.2f}: {wrong_pass.false_pass:.0%} of samples reach 0.7. A group that
close to the threshold passes often by chance, and more respondents do not remove
that: at n={largest} the same group still passes {wrong_pass_large:.0%} of the time. A group far
below, such as the 50+ group, almost never passes. The reverse also happens: the
worst false fail at n={small} is {wrong_fail.group} on {wrong_fail.scale}, population alpha
{wrong_fail.true_alpha:.2f}, where {wrong_fail.false_fail:.0%} of samples fall below 0.7 although the
group's population alpha is above it. At n={largest} that falls to {wrong_fail_large:.0%}.

### The bootstrap interval

The median 95% interval is {interval_width(small):.2f} wide at n={small} (median over the settings)
and {interval_width(largest):.2f} at n={largest}. Pooled over the {len(at)} settings
of each size ({intervals} intervals each), the share of intervals that contain the
population alpha is {covers}. {verdict}
"""


def findings_text(results: pd.DataFrame, reps: int) -> str:
    def sat(s: str) -> Any:
        return one(results, "satisfaccion", s)

    pooled = sat("pooled, 13 items as is")
    recoded_apatico = sat("pooled, apatico reverse-scored")
    recoded_both = sat("pooled, apatico and problematico reverse-scored")
    alone = [
        sat(f"{d} alone, {n} items")
        for d, n in [("entusiasta", 5), ("apatico", 4), ("problematico", 4)]
    ]

    unidim = one(results, "multidimensional", "pooled 15 items, factor correlation=0.0")
    multi = one(results, "multidimensional", "pooled 15 items, factor correlation=0.4")
    single = one(results, "multidimensional", "one dimension alone, 3 items")

    def age(s: str) -> Any:
        return one(results, "age_groups", s)

    mixed_pooled = age("different loadings: pooled")
    mixed_worst = age("different loadings: 50+")
    mixed_best = age("different loadings: 18-29")

    def bad(s: str) -> Any:
        return one(results, "bad_items", s)

    clean = bad("clean")
    wrong = bad("one reversed item, not recoded")
    noise = bad("one noise item (loading 0)")
    liners = bad("20% straight-liners")
    randoms = bad("20% random responders")

    boot = results[results.scenario == "bootstrap_interval"]

    def shape_alpha(shape: str, loading: float) -> float:
        return float(one(results, "response_shape", f"{shape}, loading={loading}").mean_alpha)

    skew_cost = [
        shape_alpha("symmetric", loading)
        - (shape_alpha("skewed high", loading) + shape_alpha("skewed low", loading)) / 2
        for loading in [0.5, 0.7]
    ]
    ceiling_cost = [
        shape_alpha("symmetric", loading) - shape_alpha("ceiling", loading)
        for loading in [0.5, 0.7]
    ]
    edge_rule = "; ".join(
        f"{k} items: loading >= {mean_edge} on average, >= {reliable_edge} in 9 of 10 samples"
        for k, _, mean_edge, reliable_edge in loading_edges(results)
    )

    return f"""# Findings: when Cronbach's alpha passes 0.7, and why it fails

Every number below comes from `cronbach-lab run` ({reps} replicates per setting,
each a fresh simulated sample). "Mean alpha" is the mean raw alpha over the
replicates, the band is the 2.5th to 97.5th percentile of alpha across replicates,
and "runs >= 0.7" is the share of replicates whose alpha reached {THRESHOLD}.

Unless a section says otherwise: 200 respondents, 5 items, equal loadings,
symmetric 5-point answers (10/20/40/20/10% for 1..5). Loadings are the
correlation between an item and its latent trait.

## 1. Loading and number of items

For equal loadings, standardized alpha is k*rho/(1+(k-1)*rho) with rho =
loading squared, so alpha depends only on the loading and the item count.
Smallest loading on the 0.05 grid that reaches 0.7:

{
        md_table(
            ["items", "theory (continuous items)", "mean alpha >= 0.7", ">= 90% of runs >= 0.7"],
            loading_edges(results),
        )
    }

Rule of thumb at 200 respondents: {edge_rule}.

Mean alpha (share of runs >= 0.7) by loading and number of items:

{loading_grid(results)}

Why: alpha rises with the item count even when each item is weak, because
adding items adds shared variance faster than error variance. A long scale can
pass 0.7 with weak items and a short scale needs strong ones. Cutting 1-5
categories out of a continuous score lowers the item correlations a little, so
the simulated edge sits slightly above the theoretical one.

## 2. Sample size

Alpha is a ratio of sample variances, so a small sample widens its spread
rather than shifting its centre much. The same scale can pass or fail by chance.

{scenario_table(results, "sample_size")}

## 3. Skewed and ceiling answers

Same latent structure, different cutpoints.

{scenario_table(results, "response_shape")}

Moving the bulk of the answers to one end (35% in each of the two top or bottom
categories) lowers mean alpha by {skew_cost[0]:.2f} at loading 0.5 and {
        skew_cost[1]:.2f} at loading 0.7.
Putting 70% of the answers on "Siempre" (ceiling) lowers it by {ceiling_cost[0]:.2f} and {
        ceiling_cost[1]:.2f}.
Alpha is built from covariance, and when nearly everyone gives the same answer the
items have little variance left to covary.

## 4. Satisfaccion al cliente: 13 items, 3 dimensions

Assumed structure (not measured): loading 0.7; the apatico and problematico
traits correlate negatively with entusiasta (-0.6 and -0.4) and positively with
each other (0.5). Pooling puts items that move in opposite directions into one
sum, so they cancel and alpha collapses.

{scenario_table(results, "satisfaccion")}

Pooled as is: mean alpha {pooled.mean_alpha:.2f}, {pooled.share_ge_0_7:.0%} of runs
pass. Each dimension alone: {", ".join(f"{a.mean_alpha:.2f}" for a in alone)}
(entusiasta, apatico, problematico). Reverse-scoring apatico alone gives
{recoded_apatico.mean_alpha:.2f}; reverse-scoring both gives {recoded_both.mean_alpha:.2f}.
Reverse-scoring apatico alone leaves problematico running against both of the other
dimensions, so alpha stays low until both are reversed. Pooling all 13 items as one
scale only makes sense once every item points the same way, and even then it treats
three behaviours as a single trait.

## 5. A multidimensional scale can still pass

Marketing Sensorial: 5 dimensions of 3 items, loading 0.7, dimensions
correlated by r.

{scenario_table(results, "multidimensional")}

Five unrelated dimensions pooled give {unidim.mean_alpha:.2f}. With the dimensions correlated at 0.4
the pooled 15-item alpha is {multi.mean_alpha:.2f}, {multi.share_ge_0_7:.0%} of runs >= 0.7,
although the data still have five factors. One dimension alone (3 items) gets
{single.mean_alpha:.2f}, {
        single.share_ge_0_7:.0%} of runs >= 0.7. Alpha rewards the number of items and the average
correlation; it does not test that one trait drives them all. A high alpha is
not evidence of a single dimension.

## 6. Age groups

Four age groups of 100 (400 respondents), 5 items. "Theta shifts" moves the group
means of the trait (+0.6, +0.2, -0.2, -0.6 standard deviations). Different
loadings: 0.8, 0.7, 0.5, 0.3 for 18-29, 30-39, 40-49, 50+.

{scenario_table(results, "age_groups")}

With different loadings the pooled alpha is {mixed_pooled.mean_alpha:.2f}, while the 18-29 group
has {mixed_best.mean_alpha:.2f} and the 50+ group {mixed_worst.mean_alpha:.2f}. Pooling averages
over groups, so one group measured badly is hidden. Group differences in the trait
mean add between-group variance shared by all items, which raises pooled alpha even
though no group's own alpha changes. Check alpha per group before trusting the pooled value.

## 7. Bad items and respondents

8 items, loading 0.6, 200 respondents. "flag_rate" is the share of runs where the
item with the highest alpha-if-dropped is the planted bad item (item 1);
"mean_alpha_dropped" is alpha without that item.

{scenario_table(results, "bad_items", extra=["flag_rate", "mean_alpha_dropped"])}

Clean scale: {clean.mean_alpha:.2f}. A single reversed item that is not recoded gives
{wrong.mean_alpha:.2f} and alpha-if-dropped flags it in {
        wrong.flag_rate:.0%} of runs; one pure-noise
item gives {noise.mean_alpha:.2f}, flagged in {noise.flag_rate:.0%}. Without the planted item the
7 remaining items give {wrong.mean_alpha_dropped:.2f} and {
        noise.mean_alpha_dropped:.2f}. Random responders
lower alpha ({randoms.mean_alpha:.2f}) but straight-liners raise it ({liners.mean_alpha:.2f}):
a straight-liner adds a perfectly consistent row, so a high alpha can come from
careless respondents instead of a good scale.

## 8. Bootstrap interval

95% percentile bootstrap (500 resamples) for a 5-item, loading 0.7 scale, over
{boot.iloc[0].reps} replicates per sample size. "coverage" is how often the interval contained the
population alpha. "lower >= 0.7" is how often the whole interval sat above 0.7.

{
        md_table(
            ["setting", "mean alpha", "mean interval width", "coverage", "lower >= 0.7"],
            [
                [
                    r.setting,
                    f"{r.mean_alpha:.2f}",
                    f"{r.mean_ci_width:.2f}",
                    f"{r.ci_coverage:.0%}",
                    f"{r.share_ci_lower_ge_0_7:.0%}",
                ]
                for r in boot.itertuples()
            ],
        )
    }

The interval narrows roughly with the square root of n. At n=20 an estimate near the
true value still comes with an interval that reaches well below 0.7, so a point
estimate above 0.7 from a small sample does not show the scale is reliable. Report
the interval, not only the point value. Percentile intervals also tend to cover
slightly less than 95% in small samples.

{profile_findings(results)}

{small_group_findings(results)}"""


def write_findings(results: pd.DataFrame, reps: int, path: str | Path) -> None:
    """Wrap prose at 80 columns, as oxfmt does, so reformatting leaves the file alone."""
    blocks = findings_text(results, reps).strip().split("\n\n")
    wrapped = [
        block
        if block.startswith(("|", "#"))
        else textwrap.fill(" ".join(block.split()), 80, break_on_hyphens=False)
        for block in blocks
    ]
    Path(path).write_text("\n\n".join(wrapped) + "\n")
