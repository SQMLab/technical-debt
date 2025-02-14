from db_config import SessionLocal
from comment import CommentRepository
from db_config import SessionLocal
from dotenv import load_dotenv
import os
load_dotenv()
session = SessionLocal()
repo = CommentRepository()
while True:
    comments = repo.get_random_comments()
    for comment in comments:
        if comment.is_td is None:
            
            location = os.getenv('REPOSITORY_DIRECTORY') + '/' + comment.repository_directory + '/'+ comment.file + ':' + str(comment.start_line)
            print(f'########################## {comment.id} #########################')
            print(f'Repository: {comment.repository_directory}\nFile:\n{location}\nComment:\n{comment.text}')
            yn = input('TD : ').strip().lower()
            note = input('Note : ')
            if yn == 'yes' or yn == 'y':
                comment.is_td = True
            elif yn == 'no' or yn == 'n':
                comment.is_td = False
            comment.is_random = True
            comment.note = None if not note else note
            session.merge(comment)
            session.commit()
