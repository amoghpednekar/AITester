package com.salesforce.framework.drivers;

import io.github.bonigarcia.wdm.WebDriverManager;
import java.time.Duration;
import java.util.Locale;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.edge.EdgeOptions;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class WebDriverManager {

    private static final Logger LOGGER = LoggerFactory.getLogger(WebDriverManager.class);
    private static final ThreadLocal<WebDriver> DRIVER_POOL = new ThreadLocal<>();

    private WebDriverManager() {
    }

    public static WebDriver createDriver(String browserName, Duration implicitWait, Duration pageLoadTimeout) {
        Browser browser = Browser.fromString(browserName);
        WebDriver driver = switch (browser) {
            case CHROME -> createChromeDriver();
            case FIREFOX -> createFirefoxDriver();
            case EDGE -> createEdgeDriver();
        };
        driver.manage().window().maximize();
        driver.manage().timeouts().implicitlyWait(implicitWait);
        driver.manage().timeouts().pageLoadTimeout(pageLoadTimeout);
        DRIVER_POOL.set(driver);
        LOGGER.info("Browser {} started successfully", browserName);
        return driver;
    }

    private static WebDriver createChromeDriver() {
        WebDriverManager.chromedriver().setup();
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--start-maximized", "--no-sandbox", "--disable-notifications");
        options.setAcceptInsecureCerts(true);
        return new ChromeDriver(options);
    }

    private static WebDriver createFirefoxDriver() {
        WebDriverManager.firefoxdriver().setup();
        FirefoxOptions options = new FirefoxOptions();
        options.setAcceptInsecureCerts(true);
        return new FirefoxDriver(options);
    }

    private static WebDriver createEdgeDriver() {
        WebDriverManager.edgedriver().setup();
        EdgeOptions options = new EdgeOptions();
        options.addArguments("--start-maximized", "--no-sandbox", "--disable-notifications");
        options.setAcceptInsecureCerts(true);
        return new EdgeDriver(options);
    }

    public static WebDriver getDriver() {
        return DRIVER_POOL.get();
    }

    public static void setDriver(WebDriver driver) {
        DRIVER_POOL.set(driver);
    }

    public static void quitDriver() {
        WebDriver driver = DRIVER_POOL.get();
        if (driver != null) {
            try {
                driver.quit();
            } catch (Exception e) {
                LOGGER.warn("Exception while quitting driver: {}", e.getMessage());
            } finally {
                DRIVER_POOL.remove();
            }
        }
    }

    private enum Browser {
        CHROME, FIREFOX, EDGE;

        static Browser fromString(String value) {
            try {
                return Browser.valueOf(value.trim().toUpperCase(Locale.ROOT));
            } catch (IllegalArgumentException e) {
                throw new IllegalArgumentException("Unsupported browser: " + value, e);
            }
        }
    }
}
