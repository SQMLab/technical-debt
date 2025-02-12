from sqlalchemy import create_engine, Column, BigInteger, String, Integer, Boolean, TIMESTAMP, Text, func
from sqlalchemy.ext.declarative import declarative_base
from db_config import SessionLocal, Base
# Define the Comment ORM Model
class Comment(Base):
    __tablename__ = "comment"

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # BIGSERIAL PRIMARY KEY
    uid = Column(String(255), unique=True, nullable=False)  # Unique Comment Context ID
    repository_id = Column(BigInteger)
    repository_directory = Column(String(255), nullable=False)  # Repository Name
    text = Column(Text)  # Comment Text
    start_line = Column(Integer, nullable=False)  # Start Line
    end_line = Column(Integer, nullable=False)  # End Line
    file = Column(String(255))  # File Path and Name
    comment_hash = Column(String(255))  # Comment Hash
    commit_hash = Column(String(255))  # Commit Hash
    is_satd = Column(Boolean)  # Whether the comment is SATD
    is_random = Column(Boolean)  # Whether the comment is Randomly Picked for Manual Review
    satd_type = Column(String(255))  # SATD Type
    note = Column(Text)  # Notes can be anything from developer's perspective
    language = Column(String(50))  # Main Language of the File
    created_at = Column(TIMESTAMP, server_default=func.now())  # Auto-set creation timestamp
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())  # Auto-update timestamp

class CommentRepository:
    def __init__(self):
        self.session = SessionLocal()

    def add_comment(self, comment_data):
        """Insert a new comment"""
        new_comment = Comment(**comment_data)
        self.session.add(new_comment)
        self.session.commit()
        print(f"✅ Added comment with UID: {new_comment.uid}")

    def get_comment(self, comment_id):
        """Fetch comment by ID"""
        return self.session.query(Comment).filter_by(id=comment_id).first()

    def get_comment_by_uid(self, uid):
        """Fetch comment by unique UID"""
        return self.session.query(Comment).filter_by(uid=uid).first()

    def update_comment(self, comment_id, update_data):
        """Update comment data"""
        comment = self.get_comment(comment_id)
        if comment:
            for key, value in update_data.items():
                setattr(comment, key, value)
            self.session.commit()
            print(f"✅ Updated comment with UID: {comment.uid}")
        else:
            print("❌ Comment not found.")

    def delete_comment(self, comment_id):
        """Delete comment by ID"""
        comment = self.get_comment(comment_id)
        if comment:
            self.session.delete(comment)
            self.session.commit()
            print(f"🗑️ Deleted comment with UID: {comment.uid}")
        else:
            print("❌ Comment not found.")

    def list_all_comments(self):
        """Fetch all comments ordered by ID descending"""
        return self.session.query(Comment).order_by(Comment.id.desc()).all()

    def list_comments_by_repository(self, repository_name):
        """Fetch all comments for a specific repository"""
        return self.session.query(Comment).filter_by(repository_name=repository_name).order_by(Comment.id.desc()).all()

    def list_random_comments(self, limit=10):
        """Fetch a limited number of randomly picked comments for review"""
        return self.session.query(Comment).filter_by(is_random=True).limit(limit).all()

    def list_satd_comments(self, limit=10):
        """Fetch all comments labeled as SATD"""
        return self.session.query(Comment).filter_by(is_satd=True).limit(limit).all()

    def get_random_comment(self):
        """Fetch a single comment randomly with uniform probability"""
        return self.session.query(Comment).order_by(func.random()).first()

    def get_random_comments(self, limit=10):
        """Fetch a list of randomly selected comments with uniform probability"""
        return self.session.query(Comment).order_by(func.random()).limit(limit).all()

    def close_session(self):
        """Close the database session"""
        self.session.close()
