import os
from git import Repo, GitCommandError

def clone_and_checkout_commit(repo_url, repository_directory, commit_hash):
    """Clone a GitHub repository and checkout a specific commit hash.
       Raises an exception if cloning or checking out fails.
    """
    try:
        if os.path.exists(repository_directory):
            print(f"🔄 Repository already exists at {repository_directory}. Pulling latest changes...")
            repo = Repo(repository_directory)

            # Ensure the repository is valid
            if repo.bare:
                raise Exception(f"❌ Error: The repository at {repository_directory} is corrupted or incomplete.")

            repo.remotes.origin.pull()
        else:
            print(f"🚀 Cloning repository {repo_url} into {repository_directory}...")
            repo = Repo.clone_from(repo_url, repository_directory)

        # Checkout specific commit hash
        print(f"🔀 Checking out commit {commit_hash}...")
        repo.git.checkout(commit_hash)

        # Verify checkout success
        current_commit = repo.head.object.hexsha
        if current_commit != commit_hash:
            raise Exception(f"❌ Failed to checkout the correct commit. Expected: {commit_hash}, Got: {current_commit}")

        print(f"✅ Successfully checked out commit: {commit_hash}")

    except GitCommandError as e:
        raise Exception(f"❌ Git command failed: {str(e)}")
    except Exception as e:
        raise Exception(f"❌ Error: {str(e)}")
