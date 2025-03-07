from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Load database URL from environment variables or use default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://satd:satd@localhost:5432/postgres")

# Create a database engine
engine = create_engine(DATABASE_URL)

# Base class for ORM models
Base = declarative_base()

# Create a session factory
SessionLocal = sessionmaker(bind=engine)
