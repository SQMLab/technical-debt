/*
 * This is a multi-line comment (block comment)
 * typically used to provide an overview of the file or a large section of code.
 */

import org.junit.Test;

/**
 * This is a Javadoc comment. It is used to document classes, methods, and fields.
 * Javadoc comments can be processed using the javadoc tool to generate documentation.
 *
 * @author YourName
 * @version 1.0
 */
public class CommentExample {

    // This is a single-line comment. It is used for brief explanations.
    private int value; // This variable stores an integer value.

    /**
     * Constructor for the CommentExample class.
     *
     * @param value The initial value to be set.
     */
    public CommentExample(int value) {
        this.value = value; // Assigning the passed value to the instance variable.
    }

    /**
     * Retrieves the value.
     *
     * @return The current value.
     */
    @Test
    public int getValue() {
        return value; // Returning the stored value.
    }

    /**
     * Sets a new value.
     *
     * @param newValue The new value to be set.
     */
    public void setValue(int newValue) {
        this.value = newValue; /* Multi-line comments can also be used in the middle of methods 
                                  to describe specific operations */
    }

    /**
     * This method demonstrates a deprecated annotation and inline comments.
     */
    @Deprecated
    public void oldMethod() {
        System.out.println("This method is deprecated."); // Avoid using this method in new code.
    }

    /**
     * Main method demonstrating comments usage.
     *
     * @param args Command-line arguments.
     */
    public static void main(String[] args) {
        // Creating an instance of CommentExample
        CommentExample example = new CommentExample(10);

        /* Printing the initial value */
        System.out.println("Initial Value: " + example.getValue());

        // Setting a new value
        example.setValue(20);
        System.out.println("Updated Value: " + example.getValue());

        // Calling a deprecated method
        example.oldMethod();
        //This is a sequence of single line comment

        //with blank space at the middle
        System.out.println("New Value: " + example.getValue()); //Foo

        //This is the end comment


    }
}
