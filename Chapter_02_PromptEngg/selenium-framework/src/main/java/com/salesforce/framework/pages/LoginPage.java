package com.salesforce.framework.pages;

import com.salesforce.framework.base.PageBase;
import java.time.Duration;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;

public class LoginPage extends PageBase {

    @FindBy(xpath = "//input[@id='username']")
    private WebElement usernameField;

    @FindBy(xpath = "//input[@id='password']")
    private WebElement passwordField;

    @FindBy(xpath = "//input[@id='Login']")
    private WebElement loginButton;

    @FindBy(xpath = "//input[@id='rememberUn']")
    private WebElement rememberMeCheckbox;

    @FindBy(xpath = "//a[@id='forgot_password_link']")
    private WebElement forgotPasswordLink;

    @FindBy(xpath = "//div[@id='error']")
    private WebElement errorMessage;

    public LoginPage(WebDriver driver, Duration timeout) {
        super(driver, timeout);
        PageFactory.initElements(driver, this);
    }

    public LoginPage enterUsername(String username) {
        typeText(usernameField, username, "Username Field");
        return this;
    }

    public LoginPage enterPassword(String password) {
        typeText(passwordField, password, "Password Field");
        return this;
    }

    public LoginPage clickLogin() {
        click(loginButton, "Login Button");
        return this;
    }

    public LoginPage toggleRememberMe() {
        click(rememberMeCheckbox, "Remember Me Checkbox");
        return this;
    }

    public LoginPage doLogin(String username, String password) {
        enterUsername(username);
        enterPassword(password);
        return clickLogin();
    }

    public boolean isLoginFormDisplayed() {
        return isElementDisplayed(usernameField) && isElementDisplayed(loginButton);
    }

    public boolean isRememberMeChecked() {
        return rememberMeCheckbox.isSelected();
    }

    public boolean isForgotPasswordLinkDisplayed() {
        return isElementDisplayed(forgotPasswordLink);
    }

    public boolean isErrorDisplayed() {
        return isElementDisplayed(errorMessage);
    }

    public String getErrorText() {
        return getText(errorMessage, "Error Message");
    }
}
