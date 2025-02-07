import requests
from db_config import SessionLocal
from repository import RepositoryBase

# GitHub API URL (Sorted by stars, limited to 100 results per page)
BASE_URL = "https://api.github.com/search/repositories"

# Headers with authentication (replace with your personal GitHub token for higher limits)
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": "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"  # Optional, to avoid rate limits
}

# Fetch repositories
def fetch_trending_java_repos():
    repos = []
    for page in range(1, 11):  # Fetch 10 pages (100 results per page) to get 1000 results
        params = {
            "q": "language:Java",
            "sort": "stars",
            "order": "desc",
            "per_page": 100,
            "page": page
        }
        response = requests.get(BASE_URL, headers=HEADERS, params=params)

        if response.status_code == 200:
            data = response.json()
            repos.extend(data.get("items", []))
        else:
            raise Exception(f"GitHub API request failed with status code {response.status_code}: {response.text}")

    return repos

def save_repositories_to_db(repos_data):
    """Convert API response and store data into PostgreSQL"""
    session = SessionLocal()

    for repo in repos_data:
        repo_entry = RepositoryBase(
            id=repo["id"],
            name=repo["name"],
            full_name=repo["full_name"],
            is_fork=repo["fork"],
            owner=repo["owner"]["login"],
            owner_url=repo["owner"]["html_url"],
            repo_url=repo["html_url"],
            stars=repo["stargazers_count"],
            forks=repo["forks_count"],
            watchers=repo["watchers_count"],
            language=repo.get("language"),
            description=repo.get("description"),
            open_issues=repo.get("open_issues_count", 0),
            license_name=repo["license"]["name"] if repo.get("license") else None,
            topics=repo.get("topics", []),
            default_branch=repo.get("default_branch"),
            pushed_at=repo.get("pushed_at"),
            created_at=repo.get("created_at"),
            updated_at=repo.get("updated_at")
        )
        session.merge(repo_entry)  # Use merge to update if exists
        print(f"Stored repository: {repo_entry.name}")

    session.commit()
    session.close()

# Fetch trending repositories
repos_data = fetch_trending_java_repos()

save_repositories_to_db(repos_data)
