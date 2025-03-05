import pandas as pd
from technical_debt_type import TechnicalDebtType, find_debt_type
import os
target_model = 'gemini'
while True:
    comment_df = pd.read_csv('../data/comments.csv')
    target_df = comment_df[comment_df[target_model] == True and comment_df['td_type'] is None].sample(frac=1, random_state=42).head(10)

    for index, row in target_df.iterrows():
        if row['td_type'] is None:
            
            location = os.getenv('REPOSITORY_DIRECTORY') + '/' + row['repository_directory'] + '/'+ row['file'] + ':' + str(row['start_line'])
            comment_id = row['id']
            print(f'\n\n\n\n########################## {comment_id} #########################')
            print(f'Repository: {row['repository_directory']}\nFile:\n{location}\nComment:\n\n{row['text']}\n')
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
                comment_df.loc[comment_df[comment_df['id'] == comment_id], 'td_type'] = debt_type
            comment_df.tocsv('../data/comments.csv', index=False)

