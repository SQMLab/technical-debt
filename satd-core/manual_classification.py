from db_config import SessionLocal
from comment import CommentRepository
from db_config import SessionLocal
from dotenv import load_dotenv
import os
from technical_debt_type import TechnicalDebtType, find_debt_type
load_dotenv()
session = SessionLocal()
repo = CommentRepository()
while True:
    comments = repo.get_comments_with_no_classification(limit=100)
    for comment in comments:
        if comment.td_type is None:
            
            location = os.getenv('REPOSITORY_DIRECTORY') + '/' + comment.repository_directory + '/'+ comment.file + ':' + str(comment.start_line)
            print(f'\n\n\n\n########################## {comment.id} #########################')
            print(f'Repository: {comment.repository_directory}\nFile:\n{location}\nComment:\n\n{comment.text}\n')
            print(f"""
                1  Ar: Architecture        8  Pe: People
                2  Bu: Build               9  Pr: Process
                3  Co: Code                10  Re: Requirement
                4  Def: Defect             11  Se: Service
                5  Des: Design             12  Au: Automation
                6  Do: Documentation       13  Te: Test
                7  In: Infrastructure      14  Un: Unknown
            """)

            debt_code = input('Select Type : ').strip().lower()
            debt_type = find_debt_type(debt_code)
            if debt_type is not None:
                comment.td_type = debt_type
            #
            # note = None
            # if yn == 'yes' or yn == 'no':
            #     note = input('Note : ')
            # comment.note = None if not note else note
            session.merge(comment)
            session.commit()

