"""
Wilcoxon Signed-Rank Test (pairwise) with Holm correction
Dataset  : duplicate (original)
Approach : MAT
Setting  : 0-shot
Reference: Flan-T5-XL (best performing model)
Comparisons: small, base, large, xxl  vs  xl

Per-repository metrics are computed first (108 repositories), then a two-sided
Wilcoxon signed-rank test is applied on those paired values against XL.
P-values are Holm-corrected (4 tests per model).
Effect size: Cliff's delta  →  N / S / M / L columns with x marker.

Output: ../cache/figure/wilcoxon_mat_0shot_duplicate.pdf
"""

import os
import shutil
import subprocess
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, matthews_corrcoef
from scipy.stats import wilcoxon

# ── paths ─────────────────────────────────────────────────────────────────────
_HERE    = Path(__file__).parent
BASE_DIR = (_HERE / "../result/rq3/duplicate").resolve()
OUT_DIR  = (_HERE / "../cache/figure").resolve()
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── experiment params ─────────────────────────────────────────────────────────
SIZES         = ["small", "base", "large", "xl", "xxl"]
METRICS       = ["precision", "recall", "f1", "mcc"]
METRIC_LABELS = {
    "precision": "Precision",
    "recall":    "Recall",
    "f1":        "F1-Score",
    "mcc":       "MCC",
}

EFFECT_COLS   = ["N", "S", "M", "L"]
EFFECT_THRESHOLDS = [0.147, 0.330, 0.474]   # boundaries for N/S/M/L


# ══════════════════════════════════════════════════════════════════════════════
# Statistical helpers
# ══════════════════════════════════════════════════════════════════════════════

def load_model(size: str) -> pd.DataFrame:
    path = BASE_DIR / f"detect_flan-t5-{size}-mat-0-shot.csv"
    df   = pd.read_csv(path)
    df["y_true"] = (df["label"]      == "yes").astype(int)
    df["y_pred"] = (df["label_pred"] == "yes").astype(int)

    rows = []
    for repo, grp in df.groupby("repository"):
        yt, yp = grp["y_true"].values, grp["y_pred"].values
        if   yt.sum() == 0 and yp.sum() == 0: p = r = f = 1.0
        elif yt.sum() == 0:                    p = r = f = 0.0
        else:
            p = precision_score(yt, yp, zero_division=0)
            r = recall_score(yt, yp, zero_division=0)
            f = f1_score(yt, yp, zero_division=0)
        m = matthews_corrcoef(yt, yp) if len(np.unique(yt)) > 1 else 0.0
        rows.append({"repository": repo,
                     "precision": p, "recall": r, "f1": f, "mcc": m})
    return pd.DataFrame(rows).set_index("repository")


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    count = sum(1 if xi > yi else (-1 if xi < yi else 0)
                for xi in x for yi in y)
    return count / (len(x) * len(y))


def effect_label(d: float) -> str:
    ad = abs(d)
    if ad < EFFECT_THRESHOLDS[0]: return "N"
    if ad < EFFECT_THRESHOLDS[1]: return "S"
    if ad < EFFECT_THRESHOLDS[2]: return "M"
    return "L"


def holm_correct(pvals: list) -> np.ndarray:
    n, order = len(pvals), np.argsort(pvals)
    corrected = np.zeros(n)
    for rank, idx in enumerate(order):
        corrected[idx] = min(1.0, pvals[idx] * (n - rank))
    for i in range(1, n):
        corrected[order[i]] = max(corrected[order[i]], corrected[order[i - 1]])
    return corrected


def fmt_p(p: float) -> str:
    if p < 0.001: return r"$<$0.001"
    if p < 0.005: return f"{p:.3f}"
    return f"{p:.2f}"


def compute_comparison(other_df: pd.DataFrame, xl_df: pd.DataFrame) -> list:
    raw_p = []
    for m in METRICS:
        x, y = other_df[m].values, xl_df[m].values
        diff  = x - y
        if (diff != 0).sum() == 0:
            raw_p.append(1.0)
        else:
            _, p = wilcoxon(x, y, alternative="two-sided", zero_method="wilcox")
            raw_p.append(p)

    holm_p = holm_correct(raw_p)
    results = []
    for i, m in enumerate(METRICS):
        x, y = other_df[m].values, xl_df[m].values
        d = cliffs_delta(x, y)
        ef = effect_label(d)
        results.append({
            "metric":  METRIC_LABELS[m],
            "p_holm":  holm_p[i],
            "sign":    "+" if d > 0 else "$-$",
            "effect":  ef,
            "delta":   d,
            "N": r"$\times$" if ef == "N" else "",
            "S": r"$\times$" if ef == "S" else "",
            "M": r"$\times$" if ef == "M" else "",
            "L": r"$\times$" if ef == "L" else "",
        })
    return results


# ══════════════════════════════════════════════════════════════════════════════
# LaTeX helpers
# ══════════════════════════════════════════════════════════════════════════════

def escape_latex(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&":  r"\&",
        "%":  r"\%",
        "$":  r"\$",   # NOTE: intentional $ strings are passed pre-escaped
        "#":  r"\#",
        "_":  r"\_",
        "{":  r"\{",
        "}":  r"\}",
        "~":  r"\textasciitilde{}",
        "^":  r"\textasciicircum{}",
    }
    return "".join(replacements.get(c, c) for c in text)


def render_one_table(comp: str, rows: list, table_num: int) -> str:
    """Return a LaTeX longtable string for one model comparison."""
    SIZE_DISPLAY = {
        "small": "Small", "base": "Base", "large": "Large", "xxl": "XXL"
    }
    label = SIZE_DISPLAY[comp]

    header = (
        r"Metric & \textit{p}-value & Sign & \multicolumn{4}{c}{Effect Size} \\"
        "\n"
        r"\cmidrule(lr){4-7}"
        "\n"
        r" &  &  & N & S & M & L \\"
    )

    data_rows = []
    for r in rows:
        p_str = fmt_p(r["p_holm"])
        # Bold significant p-values
        if r["p_holm"] < 0.05:
            p_str = r"\textbf{" + p_str + "}"
        data_rows.append(
            f"{r['metric']} & {p_str} & {r['sign']} & "
            f"{r['N']} & {r['S']} & {r['M']} & {r['L']}"
            r" \\"
        )

    body = "\n".join(data_rows)

    delta_parts = " \\quad ".join(
        f"$\\delta_{{\\text{{{METRIC_LABELS[m][:2]}}}}}={rows[i]['delta']:+.3f}$"
        for i, m in enumerate(METRICS)
    )

    return rf"""
\begin{{table}}[ht]
\centering
\caption{{Wilcoxon signed-rank test: Flan-T5-{label} vs.\ Flan-T5-XL
  (MAT, 0-shot, duplicate dataset).
  Bold \textit{{p}}-values are significant at $\alpha = 0.05$ after Holm correction.
  Effect size columns: N\,=\,negligible, S\,=\,small, M\,=\,medium, L\,=\,large.}}
\label{{tab:wilcoxon_{comp}}}
\begin{{tabular}}{{lrrcccc}}
\toprule
{header}
\midrule
{body}
\bottomrule
\end{{tabular}}
\\[4pt]
\footnotesize {delta_parts}
\end{{table}}
"""


def render_latex_document(comp_results: dict) -> str:
    tables = "\n".join(
        render_one_table(comp, rows, t_num)
        for t_num, (comp, rows) in enumerate(comp_results.items(), start=1)
    )

    return rf"""\documentclass{{article}}
\usepackage[margin=1in]{{geometry}}
\usepackage{{booktabs}}
\usepackage{{multirow}}
\usepackage{{amsmath}}
\usepackage{{microtype}}
\usepackage{{caption}}
\captionsetup[table]{{skip=4pt}}

\begin{{document}}

\begin{{center}}
  {{\large\bfseries Wilcoxon Signed-Rank Test: Pairwise Model Comparison}}\\[4pt]
  {{\normalsize Approach: MAT \quad Setting: 0-shot \quad Dataset: Duplicate (original)
    \quad Reference: Flan-T5-XL}}
\end{{center}}

\medskip
\noindent\textbf{{Method.}}
For each model size (Small, Base, Large, XXL), four metrics
(Precision, Recall, F1-Score, MCC) are computed \emph{{per repository}}
across 108 project repositories.
A two-sided Wilcoxon signed-rank test (\texttt{{zero\_method='wilcox'}}) is applied on
the 108 paired values against the Flan-T5-XL reference.
Multiple-comparison correction follows the \textbf{{Holm}} procedure (4~hypotheses per
model).
Effect size is quantified via Cliff's $\delta$:
$|\delta|<0.147$\,=\,Negligible (N);
$0.147$--$0.330$\,=\,Small (S);
$0.330$--$0.474$\,=\,Medium (M);
$\geq 0.474$\,=\,Large (L).
The Sign column indicates whether the compared model outperforms~(+) or
underperforms~($-$) the XL reference.

\bigskip
{tables}

\end{{document}}
"""


# ══════════════════════════════════════════════════════════════════════════════
# Compile LaTeX → PDF
# ══════════════════════════════════════════════════════════════════════════════

def compile_latex(tex_file: Path) -> None:
    latex_engine = shutil.which("pdflatex")
    if latex_engine is None:
        warnings.warn(f"pdflatex not found; generated LaTeX only: {tex_file}")
        return

    for _ in range(2):   # two passes (resolves labels/refs)
        subprocess.run(
            [
                latex_engine,
                "-interaction=nonstopmode",
                "-halt-on-error",
                tex_file.name,
            ],
            cwd=tex_file.parent,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    print("Loading model predictions …")
    data   = {s: load_model(s) for s in SIZES}
    common = data["xl"].index
    for s in SIZES:
        data[s] = data[s].reindex(common)

    xl_df        = data["xl"]
    comparisons  = [s for s in SIZES if s != "xl"]
    comp_results = {s: compute_comparison(data[s], xl_df) for s in comparisons}

    print("Rendering LaTeX …")
    tex_source = render_latex_document(comp_results)

    stem     = "wilcoxon_mat_0shot_duplicate"
    tex_file = OUT_DIR / f"{stem}.tex"
    tex_file.write_text(tex_source, encoding="utf-8")
    print(f"  .tex → {tex_file}")

    print("Compiling PDF …")
    compile_latex(tex_file)

    pdf_file = OUT_DIR / f"{stem}.pdf"
    if pdf_file.exists():
        print(f"  .pdf → {pdf_file}")
    else:
        print("  WARNING: PDF not produced — check LaTeX log.")


if __name__ == "__main__":
    main()
