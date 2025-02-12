package com.shahidul.satd.comment.scanner;

public interface CommentScannerService {

    int scanComment(String directory, Boolean isTestCode, String outputFile);
}
