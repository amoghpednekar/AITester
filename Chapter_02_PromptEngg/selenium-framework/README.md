# Salesforce Login Automation Framework

Enterprise-grade Selenium + Java + Maven + TestNG framework for the Salesforce login page
(`https://login.salesforce.com/?locale=in`).

## Prerequisites

- JDK 11+
- Maven 3.8+
- Chrome / Firefox / Edge

## Run Tests

```bash
mvn clean test
```

## Configuration

`src/test/resources/config.properties`:

- `app.url` — login page URL
- `browser` — chrome / firefox / edge
- `implicit.wait.seconds`, `page.load.timeout.seconds` — timeouts
- `valid.username`, `valid.password` — valid credentials (fill to run the valid test)
- `expected.home.domain` — expected post-login domain, e.g. `my.salesforce.com`

The valid-login test requires real credentials. The invalid-login tests run without credentials.

## Structure

- `src/main/java/com/salesforce/framework/drivers/` — driver factory (ThreadLocal, no leaks)
- `src/main/java/com/salesforce/framework/base/` — `TestBase` setup/teardown, `PageBase` wait/action wrappers
- `src/main/java/com/salesforce/framework/pages/` — Page Objects (`LoginPage`)
- `src/main/java/com/salesforce/framework/utils/` — config + helper utilities
- `src/test/java/com/salesforce/tests/login/` — TestNG test scripts
- `testng.xml` — suite definition (listeners, parallel execution)
