import os
import pandas as pd
from pathlib import Path
from tqdm import tqdm

def main():
    base_dir = Path("/home/cs/grad/islams32/dev/project/academic/technical-debt")
    unique_test_path = base_dir / "data" / "unique_detect_test.csv"
    duplicate_test_path = base_dir / "data" / "duplicate_detect_test.csv"
    
    merged_dir = base_dir / "cache" / "output" / "merged"
    unique_out_dir = base_dir / "cache" / "output" / "detect" / "unique"
    deduplicate_out_dir = base_dir / "cache" / "output" / "detect" / "deduplicate"
    
    # Create the output directories if they do not exist
    unique_out_dir.mkdir(parents=True, exist_ok=True)
    deduplicate_out_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading test dataset IDs...")
    # Load only the 'id' column to save memory
    unique_ids = set(pd.read_csv(unique_test_path, usecols=['id'])['id'])
    duplicate_ids = set(pd.read_csv(duplicate_test_path, usecols=['id'])['id'])
    
    print(f"Loaded {len(unique_ids)} unique IDs and {len(duplicate_ids)} duplicate IDs.")
    
    # Get all CSV files in the merged directory
    csv_files = list(merged_dir.glob("*.csv"))
    print(f"Found {len(csv_files)} CSV files to process in {merged_dir}")
    
    for file_path in tqdm(csv_files):
        try:
            # Read the merged result file
            # We use low_memory=False in case there are mixed types in large files
            df = pd.read_csv(file_path, low_memory=False)
            
            if 'id' not in df.columns:
                print(f"\nWarning: 'id' column not found in {file_path.name}, skipping.")
                continue
                
            # Filter for unique
            unique_df = df[df['id'].isin(unique_ids)]
            unique_out_path = unique_out_dir / file_path.name
            unique_df.to_csv(unique_out_path, index=False)
            
            # Filter for deduplicate
            duplicate_df = df[df['id'].isin(duplicate_ids)]
            duplicate_out_path = deduplicate_out_dir / file_path.name
            duplicate_df.to_csv(duplicate_out_path, index=False)
            
        except pd.errors.EmptyDataError:
            print(f"\nWarning: {file_path.name} is empty, skipping.")
        except Exception as e:
            print(f"\nError processing {file_path.name}: {e}")
            
    print("Done!")

if __name__ == "__main__":
    main()
