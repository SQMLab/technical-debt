package rnd.comment.scanner;

import com.github.javaparser.ParserConfiguration;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.List;
import java.util.stream.Collectors;

/**
 * @since 2025-07-16
 */
public class MethodExtractor {
    public static String extractMethod(String javaFile, int lineNumber) throws IOException {
        StaticJavaParser.getConfiguration().setLanguageLevel(ParserConfiguration.LanguageLevel.BLEEDING_EDGE);
        File file = new File(javaFile);
        CompilationUnit cu = StaticJavaParser.parse(file);

        MethodDeclaration methodDeclaration = cu.findAll(MethodDeclaration.class).stream()
                .filter(m -> m.getRange().isPresent()
                        && m.getRange().get().begin.line <= lineNumber
                        && m.getRange().get().end.line >= lineNumber)
                .findFirst().orElse(null);
        if (methodDeclaration != null) {
            int startLine = methodDeclaration.getName().getBegin().get().line;
            startLine = Math.min(startLine, methodDeclaration.hasJavaDocComment() ? methodDeclaration.getJavadocComment().get().getBegin().get().line : startLine);

            List<String> lineListInFile = Util.getLines(Files.readString(file.toPath()));
            int endLine = methodDeclaration.getEnd().isPresent() ? methodDeclaration.getEnd().get().line : 0;
            return lineListInFile.subList(startLine - 1, endLine).stream().map(Object::toString)
                    .collect(Collectors.joining("\n"));
        } else {
            return null;
        }
    }
}
