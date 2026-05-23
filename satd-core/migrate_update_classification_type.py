"""
migrate_update_classification_type.py
-----------------
Migrates classification labels from the latest ground-truth files into all
downstream CSV files.

Source of truth  (column: label):
    data/duplicate_classify_test.csv
    data/duplicate_classify_train.csv

Targets to update:
    data/comment.csv              → column: type
    data/duplicate_satd_comment.csv  → column: label
    data/unique_satd_comment.csv     → column: label
    data/unique_classify_test.csv    → column: label
    data/unique_classify_train.csv   → column: label
    data/classify_n_shot.csv         → column: label

Integrity rule:
    Any two rows (across all files) that share the same hash value must be
    assigned the same label.  Violations are reported but do NOT abort the run.
"""

import csv
import os
import sys
from collections import defaultdict

# Some rows contain large code snippets — raise the field-size limit to max.
csv.field_size_limit(sys.maxsize)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SOURCE_FILES = [
    os.path.join(BASE_DIR, "../data", "duplicate_classify_test.csv"),
    os.path.join(BASE_DIR, "../data", "duplicate_classify_train.csv"),
]

# (file path, column to update)
TARGET_FILES = [
    (os.path.join(BASE_DIR, "../data", "comment.csv"), "type"),
    (os.path.join(BASE_DIR, "../data", "duplicate_satd_comment.csv"), "label"),
    (os.path.join(BASE_DIR, "../data", "unique_classify_test.csv"), "label"),
    (os.path.join(BASE_DIR, "../data", "unique_classify_train.csv"), "label"),
    (os.path.join(BASE_DIR, "../data", "unique_satd_comment.csv"), "label"),
    (os.path.join(BASE_DIR, "../data", "classify_n_shot.csv"), "label"),
    (os.path.join(BASE_DIR, "../data", "satd_comment_example.csv"), "label"),
]

# ---------------------------------------------------------------------------
# Step 1 – Load source labels
# ---------------------------------------------------------------------------

def load_source_labels():
    """
    Read both source files and return:
        id_to_label : dict  str(id) -> str(label)
        id_to_hash  : dict  str(id) -> str(hash)

    Emits a WARNING when the same id appears in both source files with a
    different label (last-writer wins so the caller sees the conflict).
    """
    id_to_label: dict[str, str] = {}
    id_to_hash:  dict[str, str] = {}

    for filepath in SOURCE_FILES:
        filename = os.path.basename(filepath)
        if not os.path.exists(filepath):
            print(f"  [WARN] Source file not found, skipping: {filename}")
            continue

        with open(filepath, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            _require_cols(reader.fieldnames or [], ["id", "hash", "label"], filename)
            for row in reader:
                row_id   = row["id"].strip()
                label    = row["label"].strip()
                hash_val = row["hash"].strip()

                if row_id in id_to_label and id_to_label[row_id] != label:
                    print(
                        f"  [WARN] ID {row_id!r} has conflicting labels across source files: "
                        f"'{id_to_label[row_id]}' (previous) vs '{label}' (in {filename}). "
                        f"Using '{label}'."
                    )

                id_to_label[row_id] = label
                id_to_hash[row_id]  = hash_val

    return id_to_label, id_to_hash


# ---------------------------------------------------------------------------
# Step 2 – Integrity checks
# ---------------------------------------------------------------------------

def check_source_integrity(id_to_label: dict, id_to_hash: dict) -> bool:
    """
    Within the source mapping: every id that shares a hash value must map to
    the same label.  Returns True if clean.
    """
    hash_to_ids: dict[str, list[str]] = defaultdict(list)
    for row_id, hash_val in id_to_hash.items():
        hash_to_ids[hash_val].append(row_id)

    violations_found = False
    for hash_val, ids in hash_to_ids.items():
        labels = {id_to_label[i] for i in ids}
        if len(labels) > 1:
            violations_found = True
            print(f"    [VIOLATION] hash={hash_val!r}")
            for i in ids:
                print(f"      ID {i!r} → label '{id_to_label[i]}'")

    return not violations_found


def check_target_integrity(
    filepath: str,
    label_col: str,
    id_to_label: dict,
) -> bool:
    """
    Within a target file: for each unique hash value, every row whose id maps
    to a source label must receive the same label.  Returns True if clean.
    """
    filename = os.path.basename(filepath)

    with open(filepath, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        if "hash" not in fieldnames:
            print(f"    [SKIP] {filename} has no 'hash' column — integrity not checkable.")
            return True

        hash_to_mapped: dict[str, dict[str, str]] = defaultdict(dict)  # hash -> {id: new_label}
        for row in reader:
            row_id   = row["id"].strip()
            hash_val = row["hash"].strip()
            if row_id in id_to_label:
                hash_to_mapped[hash_val][row_id] = id_to_label[row_id]

    clean = True
    for hash_val, id_label_map in hash_to_mapped.items():
        unique_labels = set(id_label_map.values())
        if len(unique_labels) > 1:
            clean = False
            print(f"    [VIOLATION] {filename}  hash={hash_val!r}")
            for vid, vlabel in id_label_map.items():
                print(f"      ID {vid!r} → label '{vlabel}'")

    return clean


# ---------------------------------------------------------------------------
# Step 3 – Update a target file in-place
# ---------------------------------------------------------------------------

def update_file(
    filepath: str,
    label_col: str,
    id_to_label: dict,
    dry_run: bool = False,
) -> tuple[int, int, int]:
    """
    Overwrite label_col for every row whose id is present in id_to_label.
    Returns (rows_updated, ids_not_in_source, total_rows).
    """
    with open(filepath, newline="", encoding="utf-8") as fh:
        reader    = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        _require_cols(fieldnames, ["id", label_col], os.path.basename(filepath))
        rows = list(reader)

    updated     = 0
    not_in_src  = 0

    for row in rows:
        row_id = row["id"].strip()
        if row_id in id_to_label:
            new_label = id_to_label[row_id]
            if row.get(label_col, "").strip() != new_label:
                row[label_col] = new_label
                updated += 1
        else:
            not_in_src += 1

    if not dry_run:
        with open(filepath, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    return updated, not_in_src, len(rows)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_cols(fieldnames: list, required: list, filename: str) -> None:
    missing = [c for c in required if c not in fieldnames]
    if missing:
        raise ValueError(
            f"File '{filename}' is missing required column(s): {missing}. "
            f"Found: {fieldnames}"
        )


def _sep(title: str = "") -> None:
    width = 64
    if title:
        pad = width - len(title) - 4
        print(f"\n{'─' * 2} {title} {'─' * max(pad, 2)}")
    else:
        print("─" * width)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(dry_run: bool = False) -> None:
    if dry_run:
        print("*** DRY RUN — no files will be modified ***")

    _sep("1. Loading source labels")
    id_to_label, id_to_hash = load_source_labels()
    print(f"  Loaded {len(id_to_label)} unique ID → label mappings from source files.")

    # ── integrity: source ──────────────────────────────────────────────────
    _sep("2. Source integrity  (same hash ⇒ same label)")
    src_clean = check_source_integrity(id_to_label, id_to_hash)
    if src_clean:
        print("  ✓  No violations in source files.")
    else:
        print("  ✗  Integrity violations found in source files (see above).")

    # ── integrity: targets ─────────────────────────────────────────────────
    _sep("3. Target-file integrity")
    all_targets_clean = True
    for filepath, label_col in TARGET_FILES:
        filename = os.path.basename(filepath)
        if not os.path.exists(filepath):
            print(f"  [SKIP] {filename} — file not found")
            continue
        clean = check_target_integrity(filepath, label_col, id_to_label)
        status = "✓" if clean else "✗"
        if clean:
            print(f"  {status}  {filename}")
        else:
            all_targets_clean = False

    if all_targets_clean:
        print("  ✓  All target files passed integrity checks.")

    # ── update ─────────────────────────────────────────────────────────────
    _sep("4. Updating target files")
    total_updated = 0
    for filepath, label_col in TARGET_FILES:
        filename = os.path.basename(filepath)
        if not os.path.exists(filepath):
            print(f"  SKIP  {filename} — file not found")
            continue

        try:
            updated, not_in_src, total = update_file(
                filepath, label_col, id_to_label, dry_run=dry_run
            )
            total_updated += updated
            flag = "(DRY RUN)" if dry_run else ""
            print(
                f"  {filename!s:<40} col={label_col!r:<8} "
                f"rows={total:>6}  updated={updated:>5}  "
                f"no_src={not_in_src:>5}  {flag}"
            )
        except ValueError as exc:
            print(f"  [ERROR] {filename}: {exc}")

    _sep()
    action = "Would update" if dry_run else "Updated"
    print(f"  {action} {total_updated} cell(s) across all target files.")
    print("  Done.\n")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    main(dry_run=dry_run)
