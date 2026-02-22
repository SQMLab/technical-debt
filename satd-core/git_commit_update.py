import  pandas as pd
import os
from repository_service import clone_and_checkout_commit, get_all_commit_info
repository_df = pd.read_csv(os.path.join("../data/repository", "repository.csv"))

def get_commit_count(row):
    try:
        repository_path = f"../../td-repository/{row['name']}"
        clone_and_checkout_commit(
            row["url"],
            repository_path,
            row["commit_hash"])
        commits = get_all_commit_info(repository_path, row["commit_hash"])
        return len(commits)
    except Exception as e:
        print(e)
        return 0

repository_df["commits"] = repository_df.apply(
    get_commit_count,
    axis=1)
repository_df.to_csv(os.path.join("../data/repository", "repository2.csv"), index=False)