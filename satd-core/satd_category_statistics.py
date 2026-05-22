"""
satd_category_statistics.py
--------------
Prints three frequency statistics for every classification CSV:

  1. Composite  — exact cell value counts  (e.g. "defect skip-test": 12)
  2. Atomic     — per-token counts across all values
                  (e.g. "defect" counted once for every cell that contains it,
                   whether the cell is "defect", "defect skip-test", etc.)
  3. Group      — row counts for logical groupings of atomic types:
                    code-debt       : low-internal-quality, workaround
                    limited-test    : partial-test, superficial-test
                    new-type-debt   : uncertainty, partial-test, skip-test,
                                      superficial-test
                    all-debt        : all SATD types (i.e. not unspecified)

After all per-file tables, a LaTeX \\def block is printed for the
``unique_satd_comment.csv`` dataset (the canonical labelled set).
If a count has changed from the previous hardcoded baseline, the value
is wrapped with \\rev{…} so the paper diff is visible at a glance.

Usage:
    python3 satd_category_statistics.py
"""

import csv
import os
import sys
from collections import Counter
from typing import Optional

csv.field_size_limit(sys.maxsize)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ── Group definitions ──────────────────────────────────────────────────────────
GROUPS: dict[str, list[str]] = {
    "code-debt":    ["low-internal-quality", "workaround"],
    "limited-test": ["partial-test", "superficial-test"],
    "new-type-debt": ["uncertainty", "partial-test", "skip-test", "superficial-test"],
    "all-debt":     [
        "build", "defect", "dependency", "design", "documentation",
        "uncertainty", "low-internal-quality", "partial-test",
        "skip-test", "superficial-test", "workaround",
    ],
}

# ── Baseline counts for LaTeX change detection ─────────────────────────────────
# Update these after each accepted paper revision.
LATEX_BASELINE: dict[str, int] = {
    "build":               5,
    "defect":              70,
    "dependency":          11,
    "design":              15,
    "documentation":       19,
    "uncertainty":         67,
    "low-internal-quality": 32,
    "partial-test":        14,
    "unspecified":         225,
    "skip-test":           9,
    "superficial-test":    11,
    "workaround":          59,
    # groups
    "code-debt":           91,
    "new-type-debt":       190,
    "limited-test":        25,
    # totals
    "total":               615,
}

# Map from internal key → LaTeX command name
LATEX_CMD: dict[str, str] = {
    "build":               "buildCount",
    "defect":              "defectCount",
    "dependency":          "dependencyCount",
    "design":              "designCount",
    "documentation":       "documentationCount",
    "uncertainty":         "uncertaintyCount",
    "low-internal-quality": "lowInternalQualityCount",
    "partial-test":        "partialTestCount",
    "unspecified":         "unspecifiedCount",
    "skip-test":           "skipTestCount",
    "superficial-test":    "superficialTestCount",
    "workaround":          "workaroundCount",
    "code-debt":           "codeCount",
    "new-type-debt":       "newTypeCount",
    "limited-test":        "limitedTestCount",
    "total":               "totalSatdCount",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _group_count(values: list[str], members: list[str]) -> int:
    """Count rows where the cell contains AT LEAST ONE of the member tokens."""
    member_set = set(members)
    return sum(1 for v in values if member_set.intersection(v.split()))


def _latex_def(key: str, count: int, baseline: Optional[int]) -> str:
    """Return a single \\def line, wrapping with \\rev{} when count changed."""
    cmd = LATEX_CMD.get(key, key + "Count")
    if baseline is not None and count != baseline:
        value_str = r"\rev{" + str(count) + "}"
    else:
        value_str = str(count)
    return rf"\def\{cmd}{{{value_str}}}"


# ── Per-file statistics ────────────────────────────────────────────────────────

def stats(filepath: str, col: str) -> None:
    filename = os.path.basename(filepath)

    if not os.path.exists(filepath):
        print(f"  [SKIP] {filename} — file not found\n")
        return

    with open(filepath, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        values = [row[col].strip() for row in reader if row.get(col, "").strip()]

    total = len(values)
    composite_counter = Counter(values)
    atomic_counter: Counter = Counter()
    for v in values:
        for token in v.split():
            atomic_counter[token] += 1

    width = 56
    print("═" * width)
    print(f"  {filename}  (col='{col}', rows={total})")
    print("═" * width)

    # ── 1. Composite ──────────────────────────────────────────────────
    print("  [1] Composite label frequency")
    print(f"  {'Label':<35} {'Count':>6}  {'%':>6}")
    print("  " + "─" * (width - 2))
    for label, count in sorted(composite_counter.items()):
        pct = count / total * 100
        print(f"  {label:<35} {count:>6}  {pct:>5.1f}%")

    # ── 2. Atomic ─────────────────────────────────────────────────────
    print()
    print("  [2] Atomic token frequency")
    print(f"  {'Token':<35} {'Count':>6}  {'%':>6}")
    print("  " + "─" * (width - 2))
    for token, count in sorted(atomic_counter.items()):
        pct = count / total * 100
        print(f"  {token:<35} {count:>6}  {pct:>5.1f}%")

    # ── 3. Group counts ───────────────────────────────────────────────
    print()
    print("  [3] Group counts  (rows containing ≥1 member token)")
    print(f"  {'Group':<20} {'Members':<40} {'Count':>6}  {'%':>6}")
    print("  " + "─" * (width - 2))
    for group_name, members in GROUPS.items():
        g_count = _group_count(values, members)
        pct = g_count / total * 100 if total else 0
        members_str = ", ".join(members)
        # Wrap long member lists for display
        if len(members_str) > 38:
            members_str = members_str[:35] + "…"
        print(f"  {group_name:<20} {members_str:<40} {g_count:>6}  {pct:>5.1f}%")

    print()


# ── LaTeX \def block ───────────────────────────────────────────────────────────

def generate_latex(filepath: str, col: str) -> None:
    """Print a LaTeX \\def block for the given file, highlighting changed counts."""
    filename = os.path.basename(filepath)

    if not os.path.exists(filepath):
        print(f"  [SKIP] LaTeX block — {filename} not found\n")
        return

    with open(filepath, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        values = [row[col].strip() for row in reader if row.get(col, "").strip()]

    total = len(values)

    # Atomic counts
    atomic_counter: Counter = Counter()
    for v in values:
        for token in v.split():
            atomic_counter[token] += 1

    # Group counts
    group_counts = {
        group: _group_count(values, members) for group, members in GROUPS.items()
    }

    width = 56
    print("═" * width)
    print(f"  LaTeX \\def block  ({filename}, rows={total})")
    print("  Values wrapped in \\rev{{}} have changed from baseline.")
    print("═" * width)
    print()

    # Atomic types (ordered as in the paper)
    ordered_atomic = [
        "build", "defect", "dependency", "design", "documentation",
        "uncertainty", "low-internal-quality", "partial-test",
        "unspecified", "skip-test", "superficial-test", "workaround",
    ]
    for key in ordered_atomic:
        count = atomic_counter.get(key, 0)
        baseline = LATEX_BASELINE.get(key)
        print(_latex_def(key, count, baseline))

    print()

    # Groups
    for group_key in ("code-debt", "new-type-debt", "limited-test"):
        count = group_counts[group_key]
        baseline = LATEX_BASELINE.get(group_key)
        print(_latex_def(group_key, count, baseline))

    print()

    # Grand total
    baseline_total = LATEX_BASELINE.get("total")
    print(_latex_def("total", total, baseline_total))
    print()


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # LaTeX block for the canonical labelled dataset
    latex_file = os.path.join(BASE_DIR, "../data", "duplicate_satd_comment.csv")
    stats(latex_file, "label")
    generate_latex(latex_file, "label")
