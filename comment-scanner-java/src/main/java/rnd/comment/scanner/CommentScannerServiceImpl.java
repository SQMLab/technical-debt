package rnd.comment.scanner;

import com.github.javaparser.ParserConfiguration;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.comments.Comment;
import com.github.javaparser.ast.expr.AnnotationExpr;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;
import org.apache.commons.text.StringEscapeUtils;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.Comparator;
import java.util.List;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;

@Slf4j
public class CommentScannerServiceImpl implements CommentScannerService {
    TestFileFilter testFileFilter = new HuristicTestFileFilter();
    Set<String> TEST_FRAMEWORK_ANNOTATIONS = Set.of(
            // JUnit 4
            "Test", "Before", "After", "BeforeClass", "AfterClass",
            // JUnit 5
            "BeforeEach", "AfterEach", "BeforeAll", "AfterAll", "DisplayName",
            // Mockito
            "Mock", "InjectMocks", "Spy", "Captor",
            // TestNG
            /*"Test",*/ "BeforeMethod", "AfterMethod"/*, "BeforeClass", "AfterClass"*/
    );

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
            writer.write("comment,start,end,file");
            writer.newLine();
            Files.walkFileTree(Path.of(rootDirectory), new SimpleFileVisitor<Path>() {
                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                    String fileUrl = file.toString();
                    boolean insideStandardTestDirectory = fileUrl.contains("src/test/java");
                    try {
                        if (fileUrl.endsWith(".java")) {
                            StaticJavaParser.getConfiguration().setLanguageLevel(ParserConfiguration.LanguageLevel.BLEEDING_EDGE);
                            CompilationUnit compilationUnit = StaticJavaParser.parse(file);
                            if (insideStandardTestDirectory || hasTestAnnotation(compilationUnit)) {
                                String fileContent = Files.readString(file);
                                List<Comment> commentList = compilationUnit.getAllComments();
                                commentList.sort(Comparator.comparing(c -> c.getBegin()
                                        .map(pos -> pos.line)
                                        .orElse(Integer.MAX_VALUE)));

                                int startLine = -1;
                                int endLine = -1;
                                StringBuilder commentBuilder = new StringBuilder();

                                for (int commentIndex = 0; commentIndex < commentList.size(); commentIndex++) {
                                    Comment comment = commentList.get(commentIndex);
                                    if (comment.isLineComment()) {
                                        int commentLineNo = comment.getBegin().get().line;

                                        String lineCommentText = comment.toString();
                                        String commentLineSourceText = Util.getLinesInRange(fileContent, commentLineNo, commentLineNo + 1).trim();

                                        //Total line is comment
                                        if (commentLineSourceText.equals(lineCommentText.trim())) {
                                            if (commentBuilder.isEmpty()) {
                                                startLine = commentLineNo;
                                                endLine = commentLineNo;
                                                commentBuilder.append(lineCommentText);
                                            } else {
                                                String middleText = Util.getLinesInRange(fileContent, endLine + 1, commentLineNo).trim();
                                                if (middleText.isEmpty()) {
                                                    commentBuilder.append("\n".repeat(Math.max(0, commentLineNo - endLine - 1)));
                                                    commentBuilder.append(lineCommentText);
                                                    endLine = commentLineNo;
                                                } else {
                                                    //Flush previous
                                                    writeToCsv(startLine, endLine, commentBuilder.toString(), file, rootDirectory, writer, commentCount);
                                                    commentBuilder.setLength(0);

                                                    //Add this
                                                    startLine = commentLineNo;
                                                    endLine = commentLineNo;
                                                    commentBuilder.append(lineCommentText);
                                                }

                                            }

                                        } else {
                                            //Flush previous
                                            writeToCsv(startLine, endLine, commentBuilder.toString(), file, rootDirectory, writer, commentCount);
                                            commentBuilder.setLength(0);

                                            //Flush this comment
                                            writeToCsv(commentLineNo, commentLineNo, lineCommentText, file, rootDirectory, writer, commentCount);

                                        }
                                    } else {
                                        //Flush previous
                                        writeToCsv(startLine, endLine, commentBuilder.toString(), file, rootDirectory, writer, commentCount);
                                        commentBuilder.setLength(0);

                                        String leadingWhiteSpaces = extractLeadingChars(comment.getContent());
                                        //Flush this comment
                                        String commentContext = comment.toString();
                                        writeToCsv(comment.getBegin().get().line, comment.getEnd().get().line, commentContext, file, rootDirectory, writer, commentCount);
                                    }

                                }

                                //Flush remaining at the end of the loop
                                writeToCsv(startLine, endLine, commentBuilder.toString(), file, rootDirectory, writer, commentCount);
                                commentBuilder.setLength(0);
                            }
                        }
                    } catch (Exception e) {
                        log.error("{}", file, e);
                    }

                    return FileVisitResult.CONTINUE;
                }
            });
        } catch (Exception e) {
            log.error("", e);
        }
        return commentCount.get();
    }

    public static String extractLeadingChars(String input) {
        StringBuilder leadingChars = new StringBuilder();
        int index = 0;

        // Collect leading characters (spaces, tabs, etc.)
        while (index < input.length() && Character.isWhitespace(input.charAt(index))) {
            leadingChars.append(input.charAt(index));
            index++;
        }

        return leadingChars.toString();
    }

    private void writeToCsv(int startLine, int endLine, String comment, Path file, String rootDirectory, BufferedWriter writer, AtomicInteger commentCount) throws IOException {
        if (!comment.isEmpty()) {
            int lastIndexSubtract = comment.charAt(comment.length() - 1) == '\n' ? 1 : 0;
            String commentText = StringEscapeUtils.escapeCsv(comment.substring(0, comment.length() - lastIndexSubtract));
            StringBuilder csvLine = new StringBuilder();

            String absoluteFile = file.toAbsolutePath().toString();
            csvLine.append(commentText).append(",")
                    .append(startLine).append(",")
                    .append(endLine).append(",")
                    .append(StringEscapeUtils.escapeCsv(absoluteFile.substring(rootDirectory.length() != absoluteFile.length() ? rootDirectory.length() + 1 : 0)))
            ;
            writer.write(csvLine.toString());
            writer.newLine();
            commentCount.getAndIncrement();
        }
    }

    private boolean hasTestAnnotation(CompilationUnit compilationUnit) {
        return compilationUnit.findAll(MethodDeclaration.class).stream()
                .flatMap(method -> method.getAnnotations().stream())  // Flatten all annotations
                .map(AnnotationExpr::getNameAsString)  // Extract annotation names
                .anyMatch(TEST_FRAMEWORK_ANNOTATIONS::contains); // ✅ Check if it's a test annotation


    }
}
