"""Plots and findings.md, both built from the results table."""

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .profiles import PROFILES
from .scenarios import DEFAULT_N, ITEM_COUNTS, THRESHOLD


def plot_loading_items(results, path):
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


def plot_bars(results, scenario, path):
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


def plot_response_style(results, path):
    """Mean alpha against the strength of one style trait, a panel per scale."""
    d = results[results.scenario == "response_style"]
    scales = d.scale.unique()
    fig, axes = plt.subplots(1, len(scales), figsize=(4.5 * len(scales), 4), sharey=True)
    for ax, scale in zip(axes, scales):
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


def write_plots(results, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_loading_items(results, out_dir / "loading_items.png")
    plot_response_style(results, out_dir / "response_style.png")
    for scenario in results.scenario.unique():
        if scenario not in ("loading_items", "response_style"):
            plot_bars(results, scenario, out_dir / f"{scenario}.png")


def md_table(headers, rows):
    """Markdown table with padded columns, laid out as prettier would."""
    rows = [[str(cell) for cell in row] for row in rows]
    widths = [max(len(c) for c in column) for column in zip(headers, *rows)]
    line = lambda cells: "| " + " | ".join(c.ljust(w) for c, w in zip(cells, widths)) + " |"
    rule = "| " + " | ".join("-" * w for w in widths) + " |"
    return "\n".join([line(headers), rule] + [line(row) for row in rows])


def rows_of(results, scenario, extra=()):
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


def scenario_table(results, scenario, extra=()):
    headers = ["setting", "mean alpha", "2.5-97.5% band", "runs >= 0.7"] + list(extra)
    return md_table(headers, rows_of(results, scenario, extra))


def one(results, scenario, setting):
    d = results[(results.scenario == scenario) & (results.setting == setting)]
    return d.iloc[0]


def loading_edges(results):
    """Per item count: the loading needed for alpha 0.7 in theory and in the simulation."""
    d = results[results.scenario == "loading_items"]
    rows = []
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


def loading_grid(results):
    d = results[results.scenario == "loading_items"]
    rows = []
    for loading, g in d.groupby("loading"):
        by_k = {r.k: r for r in g.itertuples()}
        rows.append(
            [f"{loading:.2f}"]
            + [f"{by_k[k].mean_alpha:.2f} ({by_k[k].share_ge_0_7:.0%})" for k in ITEM_COUNTS]
        )
    return md_table(["loading"] + [f"{k} items" for k in ITEM_COUNTS], rows)


def profile_findings(results):
    """Section 9: lima and california."""
    at = lambda scenario, scale, profile: one(results, scenario, f"{scale}, {profile}").mean_alpha
    sensitivity = lambda scale, profile, style, strength: (
        one(results, "response_style", f"{scale}, {profile}, {style}={strength}").mean_alpha
    )

    marketing, as_is, recoded = "marketing sensorial", "satisfaccion as is", "satisfaccion recoded"
    assumptions = md_table(
        ["profile", "answers 1..5 (%)", "extreme sd", "acquiescence sd", "loading"],
        [
            [
                p.name,
                " / ".join(f"{100 * share:.0f}" for share in p.probs),
                p.extreme,
                p.acquiescence,
                p.loading,
            ]
            for p in PROFILES.values()
        ],
    )

    def table(scenario):
        rows = [
            [scale]
            + [
                f"{one(results, scenario, f'{scale}, {p}').mean_alpha:.2f} "
                f"({one(results, scenario, f'{scale}, {p}').share_ge_0_7:.0%})"
                for p in [*PROFILES, "pooled"]
            ]
            for scale in [marketing, as_is, recoded]
        ]
        return md_table(["scale", *PROFILES, "pooled"], rows)

    sweep = md_table(
        ["scale", "profile", "extreme 0", "extreme 1", "acquiescence 0", "acquiescence 1"],
        [
            [scale, profile]
            + [
                f"{sensitivity(scale, profile, style, strength):.2f}"
                for style in ["extreme", "acquiescence"]
                for strength in [0.0, 1.0]
            ]
            for scale in [marketing, as_is, recoded]
            for profile in PROFILES
        ],
    )
    gap = lambda scenario, scale: at(scenario, scale, "lima") - at(scenario, scale, "california")

    return f"""## 9. Location profiles: lima and california

Everything in this section is an assumption of the simulation. The two profiles
are invented to show what response habits can do to alpha. They are not measured
on real Lima or California respondents. A profile sets the share of answers in
each category, an extreme-response style (each respondent has a gain that
stretches their score toward 1 and 5), an acquiescence style (each respondent
has a tendency to agree that raises the answer to every item) and a loading.

{assumptions}

Three scales are scored, each with {DEFAULT_N} respondents per profile: Marketing
Sensorial pooled as 15 items (dimensions correlated 0.3), Satisfaccion pooled as
is, and Satisfaccion with apatico and problematico reverse-scored. Cells show
mean alpha and the share of runs >= {THRESHOLD}.

### Alpha per profile, and both profiles pooled

Profiles as assumed: they differ in cutpoints, style and loading.

{table("profiles")}

### Same loading, different response style only

Both profiles get loading 0.7, so the construct and its measurement are the same.
Only the cutpoints and the response style differ.

{table("profiles_same_loading")}

With identical loadings, lima still beats california by {
        gap("profiles_same_loading", marketing):.2f} on Marketing Sensorial and by {
        gap("profiles_same_loading", as_is):.2f} on Satisfaccion as is. Alpha moved and nothing
about the construct did.

### Sensitivity to the strength of the style

One style at a time (the other is zero), the profile's own cutpoints and loading.
Strength is the standard deviation of the respondent trait. The plot is
`plots/response_style.png`.

{sweep}

Acquiescence adds one factor shared by all items, whatever they say, so on a
scale where every item points the same way it raises alpha: Marketing Sensorial
goes from {sensitivity(marketing, "lima", "acquiescence", 0.0):.2f} to {
        sensitivity(marketing, "lima", "acquiescence", 1.0):.2f} for lima, and Satisfaccion as is
from {sensitivity(as_is, "lima", "acquiescence", 0.0):.2f} to {
        sensitivity(as_is, "lima", "acquiescence", 1.0):.2f}, although its three dimensions
still run against each other. After reverse-scoring apatico and problematico the
shared factor points in opposite directions on the two halves and alpha falls, from {
        sensitivity(recoded, "lima", "acquiescence", 0.0):.2f} to {
        sensitivity(
            recoded, "lima", "acquiescence", 1.0
        ):.2f} for lima. Extreme responding moves alpha
less than acquiescence in these runs.

### What alpha can and cannot tell here

Alpha computed within each group does detect a group whose items hang together
less: california Marketing Sensorial sits at {at("profiles", marketing, "california"):.2f} against {
        at("profiles", marketing, "lima"):.2f} for lima. Pooled it is {
        at("profiles", marketing, "pooled"):.2f}, so the pooled value hides the weaker group.

Alpha cannot tell why a group scores high or low. In the same-loading runs the
construct is identical and alpha still differs, because answer habits add or
remove shared variance. Lima passes 0.7 on Satisfaccion as is ({
        at("profiles", as_is, "lima"):.2f}) and california does not ({
        at("profiles", as_is, "california"):.2f}) even though the scale pools
dimensions that oppose each other. A pass can come from acquiescence, not from
measuring one trait well. Pooled alpha also hides that the groups use the scale
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


def findings_text(results, reps):
    sat = lambda s: one(results, "satisfaccion", s)
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

    age = lambda s: one(results, "age_groups", s)
    mixed_pooled = age("different loadings: pooled")
    mixed_worst = age("different loadings: 50+")
    mixed_best = age("different loadings: 18-29")

    bad = lambda s: one(results, "bad_items", s)
    clean = bad("clean")
    wrong = bad("one reversed item, not recoded")
    noise = bad("one noise item (loading 0)")
    liners = bad("20% straight-liners")
    randoms = bad("20% random responders")

    boot = results[results.scenario == "bootstrap_interval"]

    def shape_alpha(shape, loading):
        return one(results, "response_shape", f"{shape}, loading={loading}").mean_alpha

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

{profile_findings(results)}"""


def write_findings(results, reps, path):
    """Wrap prose at 80 columns, as prettier does, so reformatting leaves the file alone."""
    blocks = findings_text(results, reps).strip().split("\n\n")
    wrapped = [
        block
        if block.startswith(("|", "#"))
        else textwrap.fill(" ".join(block.split()), 80, break_on_hyphens=False)
        for block in blocks
    ]
    Path(path).write_text("\n\n".join(wrapped) + "\n")
