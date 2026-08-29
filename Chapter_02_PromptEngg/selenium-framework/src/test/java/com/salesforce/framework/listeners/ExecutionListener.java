package com.salesforce.framework.listeners;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testng.ITestContext;
import org.testng.ITestListener;
import org.testng.ITestResult;

public class ExecutionListener implements ITestListener {

    private static final Logger LOGGER = LoggerFactory.getLogger(ExecutionListener.class);

    @Override
    public void onTestStart(ITestResult result) {
        LOGGER.info("Test started: {}", result.getName());
    }

    @Override
    public void onTestSuccess(ITestResult result) {
        LOGGER.info("Test passed: {}", result.getName());
    }

    @Override
    public void onTestFailure(ITestResult result) {
        LOGGER.error("Test failed: {} - {}", result.getName(), result.getThrowable());
    }

    @Override
    public void onTestSkipped(ITestResult result) {
        LOGGER.warn("Test skipped: {}", result.getName());
    }

    @Override
    public void onStart(ITestContext context) {
        LOGGER.info("Suite started: {}", context.getName());
    }

    @Override
    public void onFinish(ITestContext context) {
        LOGGER.info("Suite finished: {}", context.getName());
    }
}
