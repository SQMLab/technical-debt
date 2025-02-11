package com.shahidul.satd.comment.scanner;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.comments.Comment;
import com.github.javaparser.ast.expr.AnnotationExpr;
import org.apache.commons.io.FileUtils;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicIntegerArray;

public class CommentScannerServiceImpl implements CommentScannerService {
    TestFileFilter testFileFilter = new HuristicTestFileFilter();

    @Override
    public int scanComment(String rootDirectory, Boolean isTestCode, String outputFile) {
        final AtomicInteger commentCount = new AtomicInteger(0);
        try {
            FileUtils.touch(new File(outputFile));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(outputFile))) {
            // Write CSV header
            writer.write("comment, start, end, file");
            writer.newLine();
            Files.walkFileTree(Path.of(rootDirectory), new SimpleFileVisitor<Path>() {
                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                    String fileUrl = file.toString();
                    boolean insideStandardTestDirectory = fileUrl.contains("src/test/java");
                    CompilationUnit compilationUnit = null;
                    try {
                        compilationUnit = StaticJavaParser.parse(file);
                        if (fileUrl.endsWith(".java") && (insideStandardTestDirectory || hasTestAnnotation(compilationUnit))) {
                            List<Comment> commentList = compilationUnit.getAllComments();
                            for (int commentIndex = 0; commentIndex < commentList.size(); commentIndex++) {
                                Comment comment = commentList.get(commentIndex);
                                int startLine = comment.getBegin().get().line;
                                int endLine = comment.getEnd().get().line;
                                String commentText = comment.getContent();
                                StringBuilder csvLine = new StringBuilder();

                                csvLine.append("\"").append(commentText).append("\",")
                                        .append(startLine).append(",")
                                        .append(endLine).append(",")
                                        .append("\"").append(file.toAbsolutePath().toString().substring(rootDirectory.length())).append("\"")
                                ;
                                writer.write(csvLine.toString());
                                writer.newLine();
                                commentCount.getAndIncrement();
                            }
                        }
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }

                    return FileVisitResult.CONTINUE;
                }
            });
        } catch (IOException e) {
            System.err.println("Error traversing project: " + e.getMessage());
        }
        return commentCount.get();
    }

    private boolean hasTestAnnotation(CompilationUnit compilationUnit) {
        return compilationUnit.findAll(MethodDeclaration.class).stream()
                .flatMap(method -> method.getAnnotations().stream())  // Flatten all annotations
                .map(AnnotationExpr::getNameAsString)  // Extract annotation names
                .anyMatch(TEST_FRAMEWORK_ANNOTATIONS::contains); // ✅ Check if it's a test annotation


    }
}
