import com.shahidul.satd.comment.scanner.CommentScannerService;
import com.shahidul.satd.comment.scanner.CommentScannerServiceImpl;
import org.junit.Test;
import org.junit.jupiter.api.Assertions;

public class CommentScanTest {
    CommentScannerService commentScanner = new CommentScannerServiceImpl();

    @Test
    public void testFileFileScan() {
        commentScanner.scanComment("/home/cs/grad/islams32/dev/rnd/satd/repository/flink/flink-core/src/test/java/org/apache/flink/api/common/accumulators/AverageAccumulatorTest.java",
                true,
                "cache/AverageAccumulatorTest.csv");

    }

    @Test
    public void testFilePrimitiveArrayTypeInfoTest() {
        Assertions.assertEquals(2,
                commentScanner.scanComment("/home/cs/grad/islams32/dev/rnd/satd/repository/flink/flink-core/src/test/java/org/apache/flink/api/common/typeinfo/PrimitiveArrayTypeInfoTest.java",
                        true,
                        "cache/PrimitiveArrayTypeInfoTest.csv"));

    }

    @Test
    public void testFileFolderScan() {
        commentScanner.scanComment("/home/cs/grad/islams32/dev/rnd/satd/repository/flink/flink-core/src/test/java/org/apache/flink/api/common",
                true,
                "cache/common.csv");

    }    @Test
    public void testMySqlAlterTableTest13() {
        commentScanner.scanComment("/home/cs/grad/islams32/dev/rnd/satd/repository/alibaba--druid/core/src/test/java/com/alibaba/druid/bvt/sql/mysql/alterTable/MySqlAlterTableTest13.java",
                true,
                "cache/MySqlAlterTableTest13.csv");

    }
}
