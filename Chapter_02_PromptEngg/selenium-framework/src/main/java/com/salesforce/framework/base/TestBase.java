package com.salesforce.framework.base;

import com.salesforce.framework.drivers.WebDriverManager;
import com.salesforce.framework.utils.ConfigReader;
import com.salesforce.framework.utils.JavaHelpers;
import java.time.Duration;
import org.openqa.selenium.WebDriver;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;

public abstract class TestBase {

    protected WebDriver driver;
    private static final Duration DEFAULT_IMPLICIT_WAIT = Duration.ofSeconds(15);
    private static final Duration DEFAULT_PAGE_LOAD_TIMEOUT = Duration.ofSeconds(30);

    @BeforeTest
    public void setUp() {
        String browser = ConfigReader.getProperty("browser", "chrome");
        Duration implicitWait = JavaHelpers.parseTimeoutSeconds(
                ConfigReader.getProperty("implicit.wait.seconds", "15"), DEFAULT_IMPLICIT_WAIT);
        Duration pageLoadTimeout = JavaHelpers.parseTimeoutSeconds(
                ConfigReader.getProperty("page.load.timeout.seconds", "30"), DEFAULT_PAGE_LOAD_TIMEOUT);
        driver = WebDriverManager.createDriver(browser, implicitWait, pageLoadTimeout);
        driver.get(ConfigReader.getProperty("app.url"));
    }

    @AfterTest
    public void tearDown() {
        WebDriverManager.quitDriver();
    }
}
