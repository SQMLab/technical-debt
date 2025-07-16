package ca.sqlmlab.comment.scanner;

import org.apache.commons.lang3.StringUtils;

import java.util.Arrays;
import java.util.List;

public class Util {
    public static String getLinesInRange(String text, int beginLine, int endLine) {
        if (beginLine >= endLine){
            return "";
        }else {
            List<String> lines = getLines(text);
            List<String> fragmentLines = lines.subList(beginLine - 1, endLine - 1);
            return StringUtils.join(fragmentLines, "\n");
        }

    }

    public static List<String> getLines(String string) {
        return Arrays.asList(string.split("\r\n|\r|\n"));
    }
}
