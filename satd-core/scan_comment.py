import os
from dotenv import load_dotenv
import jpype
import jpype.imports
from jpype import JClass
from load_comment import read_from_csv
from db_config import SessionLocal
from repository import RepositoryBase
load_dotenv()
# Start JVM
jpype.startJVM(classpath=[os.getenv('COMMENT_SCANNER_JAR')])

CommentScannerServiceImpl = JClass("com.shahidul.satd.comment.scanner.CommentScannerServiceImpl")  # Replace with actual package name

# ✅ Create an instance of CommentScannerServiceImpl
comment_scanner = CommentScannerServiceImpl()

def scan_all_comment():
    """Iterate over all repositories and update the commit_hash field"""
    session = SessionLocal()

    repositories = session.query(RepositoryBase).all()

    for repo in repositories:
        repository_name = repo.full_name.replace("/", "--")
        output_file = f"cache/{repository_name}.csv"
        if not os.path.exists(output_file):
            print(f'scanning repository {repository_name}')
            comment_scanner.scanComment(
                os.getenv('REPOSITORY_DIRECTORY') + '/' + repository_name,
                True,
                output_file
            )
            read_from_csv(output_file, repository_name, repo.commit_hash)
    session.close()
scan_all_comment()
jpype.shutdownJVM()