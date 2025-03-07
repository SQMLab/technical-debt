
from db_config import SessionLocal
from comment import CommentRepository
from repository import Repository
from db_config import SessionLocal
from dotenv import load_dotenv
import os
load_dotenv()
session = SessionLocal()
commentDao = CommentRepository()
repositoryDao = Repository()

while True:
    comments = commentDao.get_random_comments(limit=100)
    for comment in comments:
        if comment.is_td is None:
            repositoryEntity = repositoryDao.get_repository(comment.repository_id)
            location = os.getenv('REPOSITORY_DIRECTORY') + '/' + comment.repository_directory + '/'+ comment.file + ':' + str(comment.start_line)
            url = f'{repositoryEntity.repo_url}/blob/{repositoryEntity.commit_hash}/{comment.file}/#L{comment.start_line}'
            print(f'\n\n\n\n########################## {comment.id} #########################')
            print(f'Repository: {comment.repository_directory}\nFile:\n{location}\nURL: {url}\nComment:\n\n{comment.text}\n')
            yn = input('TD : ').strip().lower()
            
            if yn == 'yes' or yn == 'y':
                comment.is_td = True
            else:
                comment.is_td = False
            note = None
            if yn == 'yes' or yn == 'no':
                note = input('Note : ')
            comment.note = None if not note else note
        comment.is_random = True
        session.merge(comment)
        session.commit()
