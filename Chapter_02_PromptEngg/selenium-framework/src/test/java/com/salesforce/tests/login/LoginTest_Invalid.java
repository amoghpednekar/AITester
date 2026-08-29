package com.salesforce.tests.login;

import com.salesforce.framework.base.TestBase;
import com.salesforce.framework.exceptions.SalesforceAutomationException;
import com.salesforce.framework.pages.LoginPage;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testng.Assert;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

public class LoginTest_Invalid extends TestBase {

    private static final Logger LOGGER = LoggerFactory.getLogger(LoginTest_Invalid.class);
    private LoginPage loginPage;
    private static final Duration PAGE_TIMEOUT = Duration.ofSeconds(20);

    @BeforeClass
    public void initializePageObject() {
        loginPage = new LoginPage(driver, PAGE_TIMEOUT);
    }

    @DataProvider(name = "invalidCredentials")
    public Object[][] invalidCredentials() {
        return new Object[][] {
                {"invalid.user@example.com", "WrongPass123"},
                {"user@example.com", ""},
                {"", "SomePassword"},
                {"plainaddress", "SomePassword"}
        };
    }

    @Test(dataProvider = "invalidCredentials",
            description = "Verify login is rejected and error is shown for invalid credentials")
    public void verifyInvalidLoginShowsError(String username, String password) {
        try {
            loginPage.doLogin(username, password);
            Assert.assertTrue(loginPage.isErrorDisplayed(), "Expected an error message for invalid login");
            Assert.assertTrue(loginPage.isLoginFormDisplayed(),
                    "Login page should remain displayed after failed login");
            String errorText = loginPage.getErrorText();
            Assert.assertFalse(errorText.isEmpty(), "Error message should not be empty");
        } catch (AssertionError e) {
            throw new SalesforceAutomationException(
                    "Invalid login verification failed for user: " + username, e);
        }
    }

    @Test(description = "Verify error message for blank username and password", priority = 1)
    public void verifyBlankCredentialsError() {
        try {
            loginPage.doLogin("", "");
            Assert.assertTrue(loginPage.isErrorDisplayed(), "Expected an error message for blank credentials");
        } catch (AssertionError e) {
            throw new SalesforceAutomationException("Blank credentials error verification failed", e);
        }
    }
}
