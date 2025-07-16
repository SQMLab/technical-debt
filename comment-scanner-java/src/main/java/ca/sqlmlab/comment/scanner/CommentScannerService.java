package ca.sqlmlab.comment.scanner;

public interface CommentScannerService {

    int scanComment(String directory, Boolean isTestCode, String outputFile);
}
