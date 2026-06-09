from db_config import SessionLocal
from comment import CommentRepository
from repository import Repository
from db_config import SessionLocal
from dotenv import load_dotenv
import os
from technical_debt_type import TechnicalDebtType, find_debt_type

load_dotenv()
session = SessionLocal()
commentDao = CommentRepository()
repositoryDao = Repository()

# comments = commentDao.get_predicted_satd_comments_with_no_classification(limit=20)
comments = commentDao.get_satd_comments_with_no_classification(limit=100)
for comment in comments:
    if comment.td_type is None:
        repositoryEntity = repositoryDao.get_repository(comment.repository_id)
        location = os.getenv(
            'REPOSITORY_DIRECTORY') + '/' + comment.repository_directory + '/' + comment.file + ':' + str(
            comment.start_line)
        url = f'{repositoryEntity.repo_url}/blob/{repositoryEntity.commit_hash}/{comment.file}/#L{comment.start_line}'
        print(f'\n\n\n\n########################## {comment.id} #########################')

        print(f'Repository: {comment.repository_directory}\nFile:\n{location}\nURL: {url}\nComment:\n\n{comment.text}\n')

        # print(f"""
        #     0: Na: Na
        #     1  Des: Design              8   Pe: People
        #     2  Co: Code                 9   Pr: Process
        #     3  Te: Test                 10  Se: Service
        #     4  Re: other          11  Au: Automation
        #     5  Ar: Architecture         12  Do: Documentation
        #     6  Bu: Build                13  In: Infrastructure
        #     7  Def: Defect              14  Un: Unknown
        # """)
        #
        # debt_code = input('Select Type : ').strip().lower()
        # debt_type = find_debt_type(debt_code)
        debt_type = input('Enter Type : ').strip().lower()
        if debt_type:
            comment.td_type = debt_type
        #
        # note = None
        # if yn == 'yes' or yn == 'no':
        #     note = input('Note : ')
        # comment.note = None if not note else note
        session.merge(comment)
        session.commit()

