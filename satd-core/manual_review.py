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
        if comment.is_satd is None:
            
            location = os.getenv('REPOSITORY_DIRECTORY') + '/' + comment.repository_directory + '/'+ comment.file + ':' + str(comment.start_line) + ':2'
            print(f'##########################{comment.id}#########################\nRepository: {comment.repository_directory}\nFile:{location}\nComment: {comment.text}')
            yn = input('SATD : ')
            note = input('Note : ')
            if yn.lower() == 'yes' or yn.lower() == 'y':
                comment.is_satd = True
            elif yn.lower() == 'no' or yn.lower() == 'n':
                comment.is_satd = False
            comment.is_random = True
            comment.note = None if not note else note
            #session.add(comment)
    session.commit()
