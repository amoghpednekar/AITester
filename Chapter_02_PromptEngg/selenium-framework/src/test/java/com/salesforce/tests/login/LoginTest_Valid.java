package com.salesforce.tests.login;

import com.salesforce.framework.base.TestBase;
import com.salesforce.framework.exceptions.SalesforceAutomationException;
import com.salesforce.framework.pages.LoginPage;
import com.salesforce.framework.utils.ConfigReader;
import java.time.Duration;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testng.Assert;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;

public class LoginTest_Valid extends TestBase {

    private static final Logger LOGGER = LoggerFactory.getLogger(LoginTest_Valid.class);
    private LoginPage loginPage;
    private static final Duration PAGE_TIMEOUT = Duration.ofSeconds(20);

    @BeforeClass
    public void initializePageObject() {
        loginPage = new LoginPage(driver, PAGE_TIMEOUT);
    }

    @Test(description = "Verify login page loads with all required UI elements")
    public void verifyLoginPageElements() {
        try {
            Assert.assertTrue(loginPage.isLoginFormDisplayed(), "Login form is not displayed");
            Assert.assertFalse(loginPage.isRememberMeChecked(), "Remember me should be unchecked by default");
            Assert.assertTrue(loginPage.isForgotPasswordLinkDisplayed(), "Forgot password link is not displayed");
        } catch (AssertionError e) {
            throw new SalesforceAutomationException("Login page UI element verification failed", e);
        }
    }

    @Test(description = "Verify login succeeds with valid credentials", priority = 1)
    public void verifyValidLogin() {
        try {
            String username = ConfigReader.getProperty("valid.username");
            String password = ConfigReader.getProperty("valid.password");
            loginPage.doLogin(username, password);
            WebDriverWait wait = new WebDriverWait(driver, PAGE_TIMEOUT);
            boolean redirected = wait.until(driver -> !driver.getCurrentUrl().contains("login.salesforce.com"));
            Assert.assertTrue(redirected, "Login did not redirect away from the login page");
            String expectedDomain = ConfigReader.getProperty("expected.home.domain");
            Assert.assertTrue(driver.getCurrentUrl().contains(expectedDomain),
                    "Unexpected post-login URL: " + driver.getCurrentUrl());
        } catch (AssertionError e) {
            throw new SalesforceAutomationException("Valid login verification failed", e);
        }
    }

    @Test(description = "Verify Remember Me checkbox can be toggled", priority = 2)
    public void verifyRememberMeToggle() {
        try {
            loginPage.toggleRememberMe();
            Assert.assertTrue(loginPage.isRememberMeChecked(), "Remember me checkbox should be selected after toggle");
            loginPage.toggleRememberMe();
            Assert.assertFalse(loginPage.isRememberMeChecked(), "Remember me checkbox should be unchecked after second toggle");
        } catch (AssertionError e) {
            throw new SalesforceAutomationException("Remember me toggle verification failed", e);
        }
    }
}
