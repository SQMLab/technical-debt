import csv
from db_config import SessionLocal
from sqlalchemy.exc import IntegrityError
from comment_model import Comment, CommentRepository
from util import sha1


def read_from_csv(file_path, repository_name, commit_hash):
    """Read a CSV file and update or insert comments into the database."""

    session = SessionLocal()
    repo = CommentRepository()  # Instantiate Comment repository

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:

                comment_text = row['comment']
                file = row['file']
                start_line = int(row['start'])
                end_line = int(row['end'])
                uid = sha1(repository_name + commit_hash + file + str(start_line) + str(end_line))
                comment = repo.get_comment_by_uid(uid)

                if not comment:
                    new_comment = Comment(
                        uid=uid,
                        repository_name=repository_name,
                        commit_hash=commit_hash,
                        text=comment_text,
                        start_line=start_line,
                        end_line=end_line,
                        file=file,
                        comment_hash=sha1(comment_text)
                    )

                    session.add(new_comment)
                    session.commit()

    except IntegrityError as e:
        session.rollback()
        raise Exception("❌ Integrity error:", str(e))
    except Exception as e:
        raise Exception("❌ Error:", str(e))
    finally:
        session.close()