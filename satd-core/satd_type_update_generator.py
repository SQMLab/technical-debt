import collections

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
count = 0
s = set()
with open(os.path.expanduser('~/Documents/satd.txt'), 'r') as file:
    for line in file:
        line = line.strip()
        if len(line) > 0:
            count += 1
            id, satd_type = line.split()
            s.add(id)
            comment = commentDao.get_comment(int(id))
            if comment.td_type is not None and comment.td_type != satd_type:
                print(f'{id} {comment.td_type} {satd_type}')
            # print(f'{id} {comment.td_type} {satd_type}')
            comment.td_type = satd_type
            session.merge(comment)
            session.commit()