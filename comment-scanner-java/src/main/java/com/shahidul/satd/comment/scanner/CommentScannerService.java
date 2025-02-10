package com.shahidul.satd.comment.scanner;

import java.util.Set;

public interface CommentScannerService {
    Set<String> TEST_FRAMEWORK_ANNOTATIONS = Set.of(
            // JUnit 4
            "Test", "Before", "After", "BeforeClass", "AfterClass",
            // JUnit 5
            "BeforeEach", "AfterEach", "BeforeAll", "AfterAll", "DisplayName",
            // Mockito
            "Mock", "InjectMocks", "Spy", "Captor",
            // TestNG
            "Test", "BeforeMethod", "AfterMethod", "BeforeClass", "AfterClass"
    );

    int scanComment(String directory, Boolean isTestCode, String outputFile);
}
