import requests
from db_config import SessionLocal
from repository import RepositoryBase
from github_config import BASE_URL, HEADERS



def fetch_latest_commit(owner, repo, branch):
    """Fetch the latest commit hash for a given repository"""
    commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"

    response = requests.get(commit_url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        return data["sha"]  # Extract latest commit hash
    else:
        raise Exception(f"❌ Failed to fetch latest commit for {owner}/{repo}: {response.status_code}")


def update_all_commit_hashes():
    """Iterate over all repositories and update the commit_hash field"""
    session = SessionLocal()

    # Fetch all repositories from the database
    repositories = session.query(RepositoryBase).list_top_repositories()

    for repo in repositories:
        if repo.commit_hash is None:
            repo.commit_hash = fetch_latest_commit(repo.owner, repo.name, repo.default_branch or "main")
            session.commit()
    session.close()


# Run the update function
update_all_commit_hashes()
