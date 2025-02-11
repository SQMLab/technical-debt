import os
from dotenv import load_dotenv
import jpype
import jpype.imports
from jpype import JClass

# Start JVM
jpype.startJVM(classpath=[os.getenv('COMMENT_SCANNER_JAR')])

CommentScannerServiceImpl = JClass("com.shahidul.satd.comment.scanner.CommentScannerServiceImpl")  # Replace with actual package name

# ✅ Create an instance of CommentScannerServiceImpl
comment_scanner = CommentScannerServiceImpl()

# ✅ Call scanComment method
comment_scanner.scanComment(
    "/home/cs/grad/islams32/dev/rnd/satd/repository/flink/flink-core/src/test/java/org/apache/flink/api/common",
    True,
    "cache/common.csv"
)

# ✅ Shutdown JVM after execution
jpype.shutdownJVM()