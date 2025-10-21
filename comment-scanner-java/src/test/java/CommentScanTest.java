import rnd.comment.scanner.CommentScannerService;
import rnd.comment.scanner.CommentScannerServiceImpl;
import org.junit.Test;
import org.junit.jupiter.api.Assertions;

public class CommentScanTest {
    CommentScannerService commentScanner = new CommentScannerServiceImpl();

    @Test
    public void testFileFileScan() {
        commentScanner.scanComment("/dev/rnd/satd/repository/flink/flink-core/src/test/java/org/apache/flink/api/common/accumulators/AverageAccumulatorTest.java",
                true,
                "cache/AverageAccumulatorTest.csv");

    }

    @Test
    public void testFilePrimitiveArrayTypeInfoTest() {
        Assertions.assertEquals(2,
                commentScanner.scanComment("/dev/rnd/satd/repository/flink/flink-core/src/test/java/org/apache/flink/api/common/typeinfo/PrimitiveArrayTypeInfoTest.java",
                        true,
                        "cache/PrimitiveArrayTypeInfoTest.csv"));

    }

    @Test
    public void testFileFolderScan() {
        commentScanner.scanComment("/dev/rnd/satd/repository/flink/flink-core/src/test/java/org/apache/flink/api/common",
                true,
                "cache/common.csv");

    }    @Test
    public void testMySqlAlterTableTest13() {
        commentScanner.scanComment("/dev/rnd/satd/repository/alibaba--druid/core/src/test/java/com/alibaba/druid/bvt/sql/mysql/alterTable/MySqlAlterTableTest13.java",
                true,
                "cache/MySqlAlterTableTest13.csv");

    }
    @Test
    public void testCommentExample() {
        commentScanner.scanComment("/dev/project/academic/satd/comment-scanner-java/src/test/resources/CommentExample.java",
                true,
                "cache/CommentExample.csv");

    }
    @Test
    public void test3Sum() {
        commentScanner.scanComment("/dev/rnd/satd/repository/kdn251--interviews/leetcode/two-pointers/3Sum.java",
                true,
                "cache/3Sum.csv");

    }
}
