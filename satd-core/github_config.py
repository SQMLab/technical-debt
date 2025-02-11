# GitHub API URL (Sorted by stars, limited to 100 results per page)
import os

from dotenv import load_dotenv

BASE_URL = "https://api.github.com/search/repositories"

load_dotenv()
# GitHub API URL (Sorted by stars, limited to 100 results per page)
BASE_URL = "https://api.github.com/search/repositories"
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# Headers with authentication (replace with your personal GitHub token for higher limits)
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f'token {GITHUB_TOKEN}'
}