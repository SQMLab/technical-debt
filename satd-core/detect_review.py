from db_config import SessionLocal
from comment import CommentRepository
from db_config import SessionLocal

session = SessionLocal()
repo = CommentRepository()
while True:
    comments = repo.get_random_comments()
    for comment in comments:
        if comment.is_satd is None:
            print(comment.text)
            yn = input('SATD : ')
            note = input('Note : ')
            comment.is_satd = yn.lower() == 'yes' or yn.lower() == 'y'
            comment.note = None if not note else note
            session.add(comment)
    session.commit()
