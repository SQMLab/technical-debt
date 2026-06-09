"""
Drop __index_level_* columns from all CSV files under result/rq2/.
Files are overwritten in-place.
"""

import pandas as pd
from pathlib import Path

root = Path(__file__).parent  # result/rq2/

csv_files = list(root.rglob("*.csv"))
print(f"Found {len(csv_files)} CSV file(s) under {root}\n")

fixed = 0
for path in sorted(csv_files):
    df = pd.read_csv(path, low_memory=False)
    bad_cols = [c for c in df.columns if c.startswith("__index_level_")]
    if bad_cols:
        df = df.drop(columns=bad_cols)
        df.to_csv(path, index=False)
        print(f"  Fixed: {path.relative_to(root)}  (dropped {bad_cols})")
        fixed += 1
    else:
        print(f"  OK:    {path.relative_to(root)}")

print(f"\nDone — {fixed} file(s) fixed.")
