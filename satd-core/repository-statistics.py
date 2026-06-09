#!/usr/bin/env python3
"""
repo_boxplots.py — matplotlib-only boxplots for repository metrics

Reads a CSV with the exact header:
id,project_id,name,stars,forks,watchers,commits,comments,analyzed_comments,satd_comments,
percent_analyzed_comments,percent_satd_comments,repo_url,commit_hash,pushed_at,repository_created_at

Produces:
- <output_prefix>_boxplots_raw.JPG
- <output_prefix>_boxplots_log10.JPG  (optional)

Key requirements implemented:
- Coerce metrics to numeric and report N + missing counts.
- Five subplots in one row (layout='five' default), one metric per subplot, independent y-scales.
- Two figures: raw-count and log10(x) view (NOT log10(1+x)).
- Log plot includes zeros visually without altering stored data:
    default sentinel ε = min_positive / 10**zero_floor_decades (applied to plotting arrays only).
- Print counts of zeros and non-positive values per metric before plotting.
- Show outliers.
- Median-only annotation, placed to the right of the median line.
- No subplot titles and no per-axis epsilon text (epsilon is only printed).
- Thinner boxes + reduced horizontal whitespace via widths, x-limits, and tight layout.

other details:
- Colour palette and hatch patterns are unspecified by user; defaults are provided but overrideable
  by calling main(..., facecolours=..., hatches=...).
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


EXPECTED_COLUMNS = [
    "id", "project_id", "name", "stars", "forks", "watchers", "commits", "comments",
    "analyzed_comments", "satd_comments", "percent_analyzed_comments", "percent_satd_comments",
    "repo_url", "commit_hash", "pushed_at", "repository_created_at",
]

METRICS = ["stars", "forks", "watchers", "commits", "comments"]

# Optional layout requested by user; default 'five' satisfies the primary requirement.
GROUPS = [["stars", "forks", "watchers"], ["commits", "comments"]]

# Unspecified palette/hatches: provide accessible defaults (colour + pattern).
DEFAULT_HATCHES = {
    "stars": "///",
    "forks": "\\\\\\",
    "watchers": "xx",
    "commits": "..",
    "comments": "++",
}


def default_facecolours() -> Dict[str, Tuple[float, float, float, float]]:
    """Unspecified palette: default to Matplotlib 'tab10' colours."""
    cmap = plt.get_cmap("tab10")
    cols = [cmap(i) for i in range(len(METRICS))]
    return dict(zip(METRICS, cols))


def default_log10_transform(x: np.ndarray) -> np.ndarray:
    """
    Optional parameter requested by user:
    - returns log10(x) for x > 0
    - returns NaN for x <= 0 (robust to non-positive values)
    """
    x = np.asarray(x, dtype=float)
    y = np.full_like(x, np.nan, dtype=float)
    m = x > 0
    y[m] = np.log10(x[m])
    return y


def validate_header(df: pd.DataFrame) -> None:
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("CSV is missing required columns: " + ", ".join(missing))


def coerce_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce target metrics to numeric; invalid parsing becomes NaN."""
    df = df.copy()
    for m in METRICS:
        df[m] = pd.to_numeric(df[m], errors="coerce")
    return df


def fmt_int(v: float) -> str:
    if np.isnan(v):
        return "NaN"
    return f"{v:,.0f}"


def print_n_and_missing(df: pd.DataFrame) -> None:
    print(f"Rows (N): {len(df):,}")
    missing = df[METRICS].isna().sum().astype(int)
    print("\nMissing values per metric:")
    print(missing.to_string())


def summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compact summary table (requested output):
    Includes non-missing counts, missing counts, zeros, non-positives, negatives, and median.
    """
    rows = []
    for m in METRICS:
        s = df[m]
        non_missing = s.dropna().to_numpy(dtype=float)
        rows.append({
            "metric": m,
            "n_non_missing": int(non_missing.size),
            "missing": int(s.isna().sum()),
            "zeros": int((non_missing == 0).sum()),
            "non_positive": int((non_missing <= 0).sum()),
            "negatives": int((non_missing < 0).sum()),
            "median": float(np.median(non_missing)) if non_missing.size else np.nan,
        })
    return pd.DataFrame(rows).set_index("metric")


def data_quality_checks(df: pd.DataFrame, *, comments_sparse_threshold: float = 0.25) -> None:
    """
    - watchers==stars warning: often indicates watchers_count == stargazers_count extraction.
    - comments sparsity warning: many zeros → heavy skew.
    """
    mask = df["watchers"].notna() & df["stars"].notna()
    if mask.any():
        same_ratio = (df.loc[mask, "watchers"] == df.loc[mask, "stars"]).mean()
        if same_ratio >= 0.95:
            print(
                f"\nWARNING: watchers == stars for {same_ratio*100:.1f}% of comparable rows. "
                "If unintended, verify your data extraction."
            )

    cm = df["comments"].dropna().to_numpy(dtype=float)
    if cm.size:
        zero_ratio = float((cm == 0).mean())
        if zero_ratio >= comments_sparse_threshold:
            print(
                f"\nWARNING: comments sparsity: {zero_ratio*100:.1f}% of non-missing rows are zero. "
                "On the log figure, zeros are shown via ε in plotting arrays (see log report)."
            )


def build_log_arrays_and_report(
    df: pd.DataFrame,
    *,
    zero_floor_decades: float = 1.0,
) -> Tuple[Dict[str, np.ndarray], pd.DataFrame]:
    """
    Build plotting arrays for the log-axis figure without altering stored data:
    - Map 0 -> ε (plotting array only), where ε = min_positive / 10**zero_floor_decades
    - Exclude negatives entirely (invalid for count metrics, and not plottable on log axis)
    Returns arrays and a report to print BEFORE plotting.
    """
    arrays: Dict[str, np.ndarray] = {}
    rows = []
    for m in METRICS:
        x = df[m].dropna().to_numpy(dtype=float)
        zeros = int((x == 0).sum())
        negatives = int((x < 0).sum())
        non_positive = int((x <= 0).sum())

        pos = x[x > 0]
        if pos.size:
            min_pos = float(np.min(pos))
            epsilon = min_pos / (10.0 ** zero_floor_decades)
        else:
            # Unspecified edge-case: no positive values. Use a small fallback.
            epsilon = 10.0 ** (-zero_floor_decades)

        x_plot = x.copy()
        x_plot[x_plot == 0] = epsilon
        x_plot = x_plot[x_plot >= 0]  # drop negatives

        arrays[m] = x_plot
        rows.append({
            "metric": m,
            "n_non_missing": int(x.size),
            "zeros": zeros,
            "non_positive_total": non_positive,
            "negatives_excluded": negatives,
            "zeros_mapped_to_epsilon": zeros,
            "epsilon_used": epsilon,
            "n_used_on_log_plot": int(x_plot.size),
        })

    return arrays, pd.DataFrame(rows).set_index("metric")


def style_box(bp, metric: str, facecolours: Dict, hatches: Dict) -> None:
    """Apply distinct colour + hatch per metric box."""
    box_patch = bp["boxes"][0]
    box_patch.set_facecolor(facecolours[metric])
    box_patch.set_edgecolor("black")
    box_patch.set_hatch(hatches[metric])
    box_patch.set_alpha(0.65)

    bp["medians"][0].set_color("black")
    bp["medians"][0].set_linewidth(1.6)

    for flier in bp.get("fliers", []):
        flier.set_marker("o")
        flier.set_markersize(3)
        flier.set_markerfacecolor("none")
        flier.set_markeredgecolor("black")


def annotate_median_right_of_line(ax, bp) -> None:
    """
    Median-only annotation placed to the right of the median line.
    Uses the median line artist returned by Matplotlib.
    """
    med_line = bp["medians"][0]
    xdata = med_line.get_xdata()
    ydata = med_line.get_ydata()
    x_right = float(np.max(xdata))
    y_med = float(ydata[0])
    ax.annotate(
        fmt_int(y_med),
        xy=(x_right, y_med),
        xytext=(4, 0),
        textcoords="offset points",
        ha="left",
        va="center",
        fontsize=16,
    )


def tighten_horizontal_padding(ax, bp, *, widths: float) -> None:
    """
    Reduce left/right whitespace around the single box in each subplot.
    We set x-limits tightly around the box and leave a small right pad for the median label.
    """
    med_line = bp["medians"][0]
    x_left = float(np.min(med_line.get_xdata()))
    x_right = float(np.max(med_line.get_xdata()))
    w = max(x_right - x_left, widths * 0.5)

    left_pad = 0.25 * w
    right_pad = 0.50 * w  # space for the right-of-line median label
    ax.set_xlim(x_left - left_pad, x_right + right_pad)


def plot_five_subplots(
    *,
    arrays: Dict[str, np.ndarray],
    out_path: Path,
    figsize: Tuple[float, float],
    dpi: int,
    facecolours: Dict,
    hatches: Dict,
    yscale: Optional[str] = None,
    yscale_kwargs: Optional[Dict] = None,
    box_width: float = 0.50,  # thinner boxes (requested)
) -> None:
    """
    Always produces 1x5 subplots (primary requirement).
    No titles, no per-axis ε text.
    """
    fig, axes = plt.subplots(1, 5, figsize=figsize, sharey=False)
    fig.subplots_adjust(wspace=0.6)
    for ax, m in zip(axes, METRICS):
        x = arrays[m]
        bp = ax.boxplot(
            [x],
            tick_labels=[m],
            showfliers=True,
            patch_artist=True,
            widths=box_width,
        )
        ax.tick_params(axis='both', which='major', labelsize=22)
        style_box(bp, m, facecolours, hatches)

        if yscale:
            ax.set_yscale(yscale, **(yscale_kwargs or {}))

        ax.grid(True, axis="y", linestyle=":", linewidth=0.5)

        # Tight horizontal padding + median annotation (right of median line).
        # tighten_horizontal_padding(ax, bp, widths=box_width)
        annotate_median_right_of_line(ax, bp)

    # Tighten subplot spacing (requested minimal whitespace).
    os.makedirs(Path(out_path).parent, exist_ok=True)
    # fig.tight_layout(pad=0.3, w_pad=0.25, h_pad=0.2)
    # fig.tight_layout(...)   # remove
    # fig.subplots_adjust(wspace=0.8, left=0.04, right=0.99)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    print(f"Saved: {out_path}")
    plt.show()


def main(
    *,
    csv_path: str,
    output_prefix: str = "repository_statistics",
    figsize: Tuple[float, float] = (18.0, 4.2),
    dpi: int = 200,
    show_log: bool = True,
    log_transform: Callable[[np.ndarray], np.ndarray] = default_log10_transform,
    layout: str = "five",  # 'grouped' accepted but 'five' is used to satisfy the requirement
    zero_floor_decades: float = 1.0,
    facecolours: Optional[Dict] = None,
    hatches: Optional[Dict] = None,
) -> None:
    """
    layout option is accepted ('five' or 'grouped') as requested.
    For this task, 'five' is the canonical output (1x5). If layout='grouped',
    the script will still run but will not match the 'five subplots' requirement.

    facecolours/hatches: override by passing dicts when calling main() programmatically.
    """
    if facecolours is None:
        facecolours = default_facecolours()
    if hatches is None:
        hatches = DEFAULT_HATCHES

    df = pd.read_csv(csv_path)
    validate_header(df)
    df = coerce_metrics(df)

    print_n_and_missing(df)

    # Summary table output (requested)
    print("\nSummary table (raw counts):")
    print(summary_table(df).to_string())

    # Required: counts of zeros / non-positives per metric BEFORE plotting
    print("\nZeros / non-positives report (before plotting):")
    print(summary_table(df)[["n_non_missing", "zeros", "non_positive", "negatives"]].to_string())

    data_quality_checks(df)

    # Raw arrays (stored df unchanged)
    raw_arrays = {m: df[m].dropna().to_numpy(dtype=float) for m in METRICS}

    out_raw = Path(f"../cache/figure/{output_prefix}_raw.jpg")
    plot_five_subplots(
        arrays=raw_arrays,
        out_path=out_raw,
        figsize=figsize,
        dpi=dpi,
        facecolours=facecolours,
        hatches=hatches,
        yscale=None,
        yscale_kwargs=None,
        box_width=0.25,
    )

    if show_log:
        # Build log plotting arrays + print a detailed log-handling report BEFORE plotting.
        log_arrays, log_report = build_log_arrays_and_report(df, zero_floor_decades=zero_floor_decades)
        print("\nLog handling report (printed before log plotting; zeros mapped to ε; negatives excluded):")
        print(log_report.to_string())

        # log_transform is included as requested (robust to non-positives); not needed for axis-based log display.
        _ = log_transform(np.array([10.0, 1.0, 0.0, -1.0], dtype=float))

        out_log = Path(f"../cache/figure/{output_prefix}.jpg")
        plot_five_subplots(
            arrays=log_arrays,
            out_path=out_log,
            figsize=figsize,
            dpi=dpi,
            facecolours=facecolours,
            hatches=hatches,
            yscale="log",
            yscale_kwargs={"base": 10, "nonpositive": "clip"},
            box_width=0.25,
        )


if __name__ == "__main__":
    # Default csv_path requested by user
    default_csv = "../data/repository.csv" if Path("../data/repository.csv").exists() else "repository.csv"

    parser = argparse.ArgumentParser(
        description="Matplotlib-only boxplots for repo metrics (raw + log10 axis with zeros shown as ε)."
    )
    parser.add_argument("--csv-path", default=default_csv, help="Path to input CSV.")
    parser.add_argument("--output-prefix", default="repository_statistics", help="Prefix for output JPG filenames.")
    parser.add_argument("--figsize", nargs=2, type=float, default=[18.0, 4.2], help="Figure size: width height.")
    parser.add_argument("--dpi", type=int, default=300, help="DPI for saved JPGs.")
    parser.add_argument("--no-log", action="store_true", help="Disable log figure.")
    parser.add_argument("--layout", choices=["five", "grouped"], default="five", help="Layout option.")
    parser.add_argument(
        "--zero-floor-decades",
        type=float,
        default=1.0,
        help="Zero sentinel for log: ε = min_positive / 10**k (default k=1).",
    )

    args = parser.parse_args()

    main(
        csv_path=args.csv_path,
        output_prefix=args.output_prefix,
        figsize=(args.figsize[0], args.figsize[1]),
        dpi=args.dpi,
        show_log=(not args.no_log),
        log_transform=default_log10_transform,
        layout=args.layout,
        zero_floor_decades=args.zero_floor_decades,
        facecolours=None,
        hatches=None,
    )
