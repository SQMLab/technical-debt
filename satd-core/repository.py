from sqlalchemy import create_engine, Column, BigInteger, String, Integer, Boolean, TIMESTAMP, Text, ARRAY, func, \
    Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db_config import SessionLocal, Base


# Define the GitHub Repository ORM Model
class RepositoryBase(Base):
    __tablename__ = "repository"

    id = Column(BigInteger, Sequence('repository_id_seq', start=1, increment=1),
                primary_key=True)  # Auto-incrementing ID
    repository_id = Column(BigInteger, unique=True)  # Unique GitHub Repository ID
    name = Column(String(255), nullable=False)  # Repository Name
    full_name = Column(String(255), nullable=False)  # Full name (owner/repo)
    is_fork = Column(Boolean, nullable=False, default=False)  # Fork status
    owner = Column(String(255), nullable=False)  # Repository Owner
    owner_url = Column(Text)  # Owner GitHub Profile URL
    repo_url = Column(Text, nullable=False)  # Repository GitHub URL
    stars = Column(Integer, nullable=False, default=0)  # Star Count
    forks = Column(Integer, nullable=False, default=0)  # Fork Count
    watchers = Column(Integer, nullable=False, default=0)  # Watchers Count
    language = Column(String(50))  # Primary Language
    description = Column(Text)  # Repository Description
    open_issues = Column(Integer, default=0)  # Open Issues Count
    license_name = Column(String(255))  # License Type
    topics = Column(ARRAY(Text))  # Array of Topics/Tags
    default_branch = Column(String(50))  # Default Branch (main/master)
    commit_hash = Column(String(255))  # Latest Commit Hash
    pushed_at = Column(TIMESTAMP)  # Last Commit Push Timestamp
    repository_created_at = Column(TIMESTAMP)  # Repository Creation Date
    repository_updated_at = Column(TIMESTAMP)  # Last Update Timestamp
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


# Create table if not exists
Base.metadata.create_all(SessionLocal().bind)


# Repository CRUD Operations
class Repository:
    def __init__(self):
        self.session = SessionLocal()

    def add_repository(self, repo_data):
        """Insert a new repository"""
        new_repo = RepositoryBase(**repo_data)
        self.session.add(new_repo)
        self.session.commit()
        print(f"Added repository: {new_repo.name}")

    def get_repository(self, repo_id):
        """Fetch repository by ID"""
        return self.session.query(RepositoryBase).filter_by(id=repo_id).first()

    def update_repository(self, repo_id, update_data):
        """Update repository data"""
        repo = self.get_repository(repo_id)
        if repo:
            for key, value in update_data.items():
                setattr(repo, key, value)
            self.session.commit()
            print(f"Updated repository: {repo.name}")
        else:
            print("Repository not found.")

    def delete_repository(self, repo_id):
        """Delete repository by ID"""
        repo = self.get_repository(repo_id)
        if repo:
            self.session.delete(repo)
            self.session.commit()
            print(f"Deleted repository: {repo.name}")
        else:
            print("Repository not found.")

    def list_top_repositories(self, limit=10):
        """Fetch top repositories by stars"""
        return self.session.query(RepositoryBase).order_by(RepositoryBase.stars.desc()).limit(limit).all()

    def close_session(self):
        """Close the database session"""
        self.session.close()
