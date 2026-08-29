package com.salesforce.framework.exceptions;

public class SalesforceAutomationException extends RuntimeException {

    public SalesforceAutomationException(String message) {
        super(message);
    }

    public SalesforceAutomationException(String message, Throwable cause) {
        super(message, cause);
    }
}
