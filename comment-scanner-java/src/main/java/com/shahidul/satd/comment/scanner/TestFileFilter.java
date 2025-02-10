package com.shahidul.satd.comment.scanner;

import java.io.File;
import java.nio.file.Path;

public interface TestFileFilter {
    boolean accept(Path file);
}
