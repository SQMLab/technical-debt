"""
migrate_rename_classification_type.py
----------------------
Renames atomic label/type tokens across ALL classification CSVs — including
the ground-truth source files.

HOW IT WORKS
  Each cell value may be a single token ("defect") or multiple space-separated
  tokens ("defect skip-test").  The script splits every value into its atomic
  tokens, applies the LABEL_MAP rename to each token individually, then
  re-joins them.  Tokens not present in LABEL_MAP are left unchanged.

HOW TO USE
  1. Edit LABEL_MAP below — change the right-hand side of any entry you want
     to rename.  The left-hand side (key) is the current token; the
     right-hand side (value) is what it becomes.
  2. Run a preview first:
       python3 migrate_rename_classification_type.py --dry-run
  3. Apply when happy:
       python3 migrate_rename_classification_type.py
"""

import csv
import os
import sys
from collections import defaultdict

csv.field_size_limit(sys.maxsize)

# ---------------------------------------------------------------------------
# ★  EDIT THIS MAP  ★
#    key   = current atomic token (as it appears in the CSV today)
#    value = the token it should become  (keep identical to do nothing)
# ---------------------------------------------------------------------------
LABEL_MAP: dict[str, str] = {
    "build":               "build",
    "composite":           "composite",
    "defect":              "defect",
    "dependency":          "dependency",
    "design":              "design",
    "documentation":       "documentation",
    "how-to":              "how-to",
    "low-internal-quality":"low-internal-quality",
    "partial-test":        "partial-test",
    "requirement":         "requirement",
    "skip-test":           "skip-test",
    "superficial-test":    "superficial-test",
    "workaround":          "workaround",
}

# ---------------------------------------------------------------------------
# Files and the column to patch
# (source ground-truth files are included this time)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ALL_FILES: list[tuple[str, str]] = [
    # ── ground-truth sources ────────────────────────────────────────────
    (os.path.join(BASE_DIR, "../data", "duplicate_classify_test.csv"), "label"),
    (os.path.join(BASE_DIR, "../data", "duplicate_classify_train.csv"), "label"),
    # ── downstream targets ──────────────────────────────────────────────
    (os.path.join(BASE_DIR, "../data", "comment.csv"), "type"),
    (os.path.join(BASE_DIR, "../data", "duplicate_satd_comment.csv"), "label"),
    (os.path.join(BASE_DIR, "../data", "unique_classify_test.csv"), "label"),
    (os.path.join(BASE_DIR, "../data", "unique_classify_train.csv"), "label"),
    (os.path.join(BASE_DIR, "../data", "unique_satd_comment.csv"), "label"),
    (os.path.join(BASE_DIR, "../data", "classify_n_shot.csv"), "label"),
]


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def remap_value(raw: str) -> str:
    """
    Split a (possibly multi-token) label value on whitespace, remap each
    token via LABEL_MAP, and rejoin with the original separator.

    Example:
        "defect skip-test"
         → tokens: ["defect", "skip-test"]
         → remapped: [LABEL_MAP["defect"], LABEL_MAP["skip-test"]]
         → result: "<new_defect> <new_skip-test>"
    """
    tokens = raw.split()
    remapped = [LABEL_MAP.get(tok, tok) for tok in tokens]
    return " ".join(remapped)


def collect_unknowns(filepath: str, col: str) -> set[str]:
    """Return atomic tokens present in the file that are not in LABEL_MAP."""
    unknown: set[str] = set()
    with open(filepath, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            val = row.get(col, "").strip()
            if val:
                for tok in val.split():
                    if tok not in LABEL_MAP:
                        unknown.add(tok)
    return unknown


def process_file(
    filepath: str,
    col: str,
    dry_run: bool,
) -> tuple[int, int]:
    """
    Remap every cell in `col` using LABEL_MAP.
    Returns (rows_changed, total_rows).
    """
    with open(filepath, newline="", encoding="utf-8") as fh:
        reader    = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if col not in fieldnames:
        raise ValueError(
            f"Column '{col}' not found in {os.path.basename(filepath)}. "
            f"Available: {fieldnames}"
        )

    changed = 0
    for row in rows:
        old_val = row.get(col, "").strip()
        if not old_val:
            continue
        new_val = remap_value(old_val)
        if new_val != old_val:
            row[col] = new_val
            changed += 1

    if not dry_run:
        with open(filepath, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    return changed, len(rows)


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

def effective_renames() -> dict[str, str]:
    """Return only entries where the value actually differs from the key."""
    return {k: v for k, v in LABEL_MAP.items() if k != v}


def _sep(title: str = "") -> None:
    width = 68
    if title:
        pad = width - len(title) - 4
        print(f"\n{'─' * 2} {title} {'─' * max(pad, 2)}")
    else:
        print("─" * width)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(dry_run: bool = False) -> None:
    if dry_run:
        print("*** DRY RUN — no files will be modified ***\n")

    # ── Show active renames ────────────────────────────────────────────────
    _sep("Active renames in LABEL_MAP")
    renames = effective_renames()
    if renames:
        for old, new in sorted(renames.items()):
            print(f"  '{old}'  →  '{new}'")
    else:
        print("  (none — all keys map to themselves; edit LABEL_MAP to rename)")

    # ── Warn about unknown tokens ──────────────────────────────────────────
    _sep("Unknown tokens (not in LABEL_MAP)")
    any_unknown = False
    for filepath, col in ALL_FILES:
        filename = os.path.basename(filepath)
        if not os.path.exists(filepath):
            continue
        unknowns = collect_unknowns(filepath, col)
        if unknowns:
            any_unknown = True
            print(f"  {filename!s:<40}  col={col!r}  unknown: {sorted(unknowns)}")
    if not any_unknown:
        print("  ✓  All tokens are covered by LABEL_MAP.")

    # ── Process files ──────────────────────────────────────────────────────
    _sep("Processing files")
    total_changed = 0
    for filepath, col in ALL_FILES:
        filename = os.path.basename(filepath)
        if not os.path.exists(filepath):
            print(f"  SKIP  {filename} — file not found")
            continue
        try:
            changed, total = process_file(filepath, col, dry_run=dry_run)
            total_changed += changed
            tag = "(DRY RUN)" if dry_run else "✓"
            print(
                f"  {tag}  {filename!s:<42} col={col!r:<8} "
                f"rows={total:>6}  changed={changed:>5}"
            )
        except ValueError as exc:
            print(f"  [ERROR]  {filename}: {exc}")

    # ── Summary ───────────────────────────────────────────────────────────
    _sep()
    action = "Would change" if dry_run else "Changed"
    print(f"  {action} {total_changed} cell(s) across all files.")
    print("  Done.\n")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    main(dry_run=dry_run)
