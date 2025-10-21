package rnd.comment.scanner;

import java.nio.file.Path;

public interface TestFileFilter {
    boolean accept(Path file);
}
