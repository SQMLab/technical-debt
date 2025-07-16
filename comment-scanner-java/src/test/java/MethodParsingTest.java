import ca.sqlmlab.comment.scanner.MethodExtractor;
import org.junit.Test;

/**
 * @author Shahidul Islam
 * @since 2025-07-16
 */
public class MethodParsingTest {
    @Test
    public void testMethodParsing() {
        try {
            String method = MethodExtractor.extractMethod("/home/cs/grad/islams32/dev/rnd/technical-debt/repository/apache--calcite/core/src/test/java/org/apache/calcite/test/enumerable/EnumerableSortedAggregateTest.java", 32);
            System.out.println(method);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
