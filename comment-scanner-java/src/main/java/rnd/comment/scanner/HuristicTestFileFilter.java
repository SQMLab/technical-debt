package rnd.comment.scanner;

import java.nio.file.Path;

public class HuristicTestFileFilter implements TestFileFilter {
    @Override
    public boolean accept(Path file) {
        return file.toString().contains("src/test/java");
    }
}
