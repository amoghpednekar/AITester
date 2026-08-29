package com.salesforce.framework.base;

import com.salesforce.framework.exceptions.SalesforceAutomationException;
import java.time.Duration;
import org.openqa.selenium.By;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.StaleElementReferenceException;
import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public abstract class PageBase {

    protected final WebDriver driver;
    private final WebDriverWait wait;

    protected PageBase(WebDriver driver, Duration timeout) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, timeout);
    }

    protected WebElement waitForElementVisible(WebElement element, String elementName) {
        try {
            return wait.until(ExpectedConditions.visibilityOf(element));
        } catch (TimeoutException | NoSuchElementException | StaleElementReferenceException e) {
            throw new SalesforceAutomationException("Element not visible within timeout: " + elementName, e);
        }
    }

    protected WebElement waitForElementClickable(WebElement element, String elementName) {
        try {
            return wait.until(ExpectedConditions.elementToBeClickable(element));
        } catch (TimeoutException | NoSuchElementException | StaleElementReferenceException e) {
            throw new SalesforceAutomationException("Element not clickable within timeout: " + elementName, e);
        }
    }

    protected void typeText(WebElement element, String text, String elementName) {
        try {
            waitForElementVisible(element, elementName).clear();
            waitForElementVisible(element, elementName).sendKeys(text);
        } catch (SalesforceAutomationException e) {
            throw new SalesforceAutomationException("Failed to type into element: " + elementName, e);
        }
    }

    protected void click(WebElement element, String elementName) {
        try {
            waitForElementClickable(element, elementName).click();
        } catch (SalesforceAutomationException e) {
            throw new SalesforceAutomationException("Failed to click element: " + elementName, e);
        }
    }

    protected boolean isElementDisplayed(WebElement element) {
        try {
            return element.isDisplayed();
        } catch (NoSuchElementException | StaleElementReferenceException e) {
            return false;
        }
    }

    protected boolean isElementDisplayed(By locator) {
        try {
            return driver.findElement(locator).isDisplayed();
        } catch (NoSuchElementException | StaleElementReferenceException e) {
            return false;
        }
    }

    protected String getText(WebElement element, String elementName) {
        try {
            return waitForElementVisible(element, elementName).getText();
        } catch (SalesforceAutomationException e) {
            throw new SalesforceAutomationException("Failed to read text from element: " + elementName, e);
        }
    }

    protected void navigateTo(String url) {
        try {
            driver.get(url);
        } catch (Exception e) {
            throw new SalesforceAutomationException("Failed to navigate to URL: " + url, e);
        }
    }
}
