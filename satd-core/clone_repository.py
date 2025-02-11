import os

from db_config import SessionLocal
from repository import RepositoryBase
from repository_service import clone_and_checkout_commit
from dotenv import load_dotenv

load_dotenv()
session = SessionLocal()

# Fetch all repositories from the database
repositories = session.query(RepositoryBase).all()

print(os.getenv('REPOSITORY_DIRECTORY') )
for repo in repositories:
    if repo.commit_hash:
        clone_and_checkout_commit(repo.repo_url, os.getenv('REPOSITORY_DIRECTORY') + '/' + repo.name, repo.commit_hash)

session.close()
