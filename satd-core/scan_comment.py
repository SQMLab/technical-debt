import os
from dotenv import load_dotenv
import jpype
import jpype.imports
from jpype import JClass
from load_comment import read_from_csv
from db_config import SessionLocal
from repository import Repository
load_dotenv()
# Set path to your JAR file
jar_path = os.getenv('COMMENT_SCANNER_JAR')

# JVM Arguments (Increase Stack Size)
jvm_args = ["-Xss512m"]  # Increase stack size to 512MB

# Start JVM with increased stack size
jpype.startJVM(jpype.getDefaultJVMPath(), "-ea", *jvm_args, classpath=[jar_path])

CommentScannerServiceImpl = JClass("com.shahidul.satd.comment.scanner.CommentScannerServiceImpl")  # Replace with actual package name

# ✅ Create an instance of CommentScannerServiceImpl
comment_scanner = CommentScannerServiceImpl()

def scan_all_comment():
    """Iterate over all repositories and update the commit_hash field"""
    session = SessionLocal()

    repositories =Repository().list_top_repositories()
    # repositories =[Repository().get_repository(491)]

    for repo in repositories:
        repository_directory = repo.full_name.replace("/", "--")
        output_file = f"cache/{repository_directory}.csv"
        if not os.path.exists(output_file):
            print(f'{repo.id} - {repo.name} : scanning')
            comment_scanner.scanComment(
                os.getenv('REPOSITORY_DIRECTORY') + '/' + repository_directory,
                True,
                output_file
            )
            print(f'{repo.id} - {repo.name} : inserting into db')
            read_from_csv(output_file, repo.id, repository_directory, repo.commit_hash)
    session.close()
scan_all_comment()
jpype.shutdownJVM()