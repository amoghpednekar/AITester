# Salesforce Login Automation — Enterprise Selenium/Java/Maven/TestNG Framework

**Code location:** `Chapter_02_PromptEngg/selenium-framework/`
**Source prompt:** `Chapter_02_PromptEngg/01_Ricepot.example.md`

## 1. Verified Facts (from live https://login.salesforce.com/?locale=in DOM)
- Username input: `input#username`, `type="email"`
- Password input: `input#password`
- Log In submit button: `input#Login` (`value="Log In"`)
- Remember Me checkbox: `input#rememberUn`
- Forgot Password link: `a#forgot_password_link`
- Login form: `form#login_form`, posts to `https://login.salesforce.com/`
- Empty-password error element: `#error` (role alert), text `"Please enter your password."`
- Login page is well-known for bot/captcha detection; hardcode public URL per user choice, add retry + graceful failure logging so CI doesn't flake.

## 2. Missing / Unknown Information
- Invalid (wrong password) error text exact copy — must be read live at runtime, not hardcoded.
- Staging domain + credentials — user will provide later; keep in `config.properties` (gitignored).

## 3. Resolved Decisions
- Code location: subfolder under `Chapter_02_PromptEngg`
- Scope: full enterprise scaffold (not just 3 files)
- Target: hardcoded public URL

## 4. Framework Structure
```
selenium-framework/
├── pom.xml
├── testng.xml
├── src/main/java/com/salesforce/framework/
│   ├── drivers/WebDriverManager.java      # ThreadLocal driver, browser factory
│   ├── pages/LoginPage.java                # PageFactory, @FindBy(xpath=...)
│   ├── base/PageBase.java                  # waits, action wrappers, exceptions
│   ├── base/TestBase.java                  # @BeforeTest/@AfterTest setup+teardown
│   ├── utils/ConfigReader.java, JavaHelpers.java
├── src/test/java/com/salesforce/tests/
│   ├── login/LoginTest_Valid.java
│   ├── login/LoginTest_Invalid.java
│   ├── listeners/ExecutionListener.java
├── src/test/resources/config.properties   # url, browser, timeouts (gitignored creds)
└── src/test/resources/testng.xml
```

### Page Object — `LoginPage.java`
- `PageFactory.initElements(driver, this)` in constructor.
- `@FindBy(xpath = "...")` only — XPath uses relative/attribute paths, NO css.
- Reusable action methods: `doLogin(user, pass)`, `enterUsername`, `enterPassword`, `clickLogin`, `toggleRememberMe`, `getErrorText`, `isLoginFormDisplayed`.
- Exceptions wrapped in try-catch rethrowing a typed `SalesforceAutomationException`; no `Thread.sleep` anywhere — `WebDriverWait` + implicit wait only.

### Test Scripts (TestNG)
| File | Test | Assertion |
|------|------|-----------|
| `LoginTest_Valid.java` | Valid creds → lands on dashboard/home | `Assert` on known post-login URL/element |
| `LoginTest_Invalid.java` | Blank / wrong pwd / bad format → error shown | `Assert` error element visible, page still on login |

- Both use `@BeforeTest` (load config, init driver, navigate) and `@AfterTest` (quit driver, teardown), structured try-catch, `TestNG Assert`.

### pom.xml
- Dependencies: `selenium-java` 4.x, `testng`, `webdrivermanager` (driver mgmt), `slf4j-simple` (logging).
- `maven-surefire-plugin` configured to run `testng.xml`.

## 5. XPath Locator Strategy (no CSS)
- Username: `//input[@id='username']`
- Password: `//input[@id='password']`
- Login: `//input[@id='Login']`
- Remember Me: `//input[@id='rememberUn']`
- Forgot link: `//a[@id='forgot_password_link']`
- Error: `//div[@id='error']` (or `//div[@role='alert']`)

## 6. Constraints Enforced
- No CSS selectors, no bare-by-id locating outside XPath.
- No comments, no `Thread.sleep()` — waits only.
- Structured try-catch + explicit exception signatures.
- Modular, readable, consistent across files.

## 7. Deliverables Per Output Spec
1. 1 Page Object file (`LoginPage.java`)
2. 2 TestNG test scripts (`LoginTest_Valid.java`, `LoginTest_Invalid.java`)
3. Maven project (pom.xml + scaffold shown above)

## 8. Implementation Steps
1. Create `Chapter_02_PromptEngg/selenium-framework/` + log `plan.md`.
2. Write `pom.xml` (selenium 4, testng, webdrivermanager, surefire).
3. Write `WebDriverManager` (ThreadLocal, browser factory, waits).
4. Write `PageBase` (wait/action wrappers, typed exceptions).
5. Write `LoginPage` (PageFactory, @FindBy XPath only).
6. Write `TestBase` (@BeforeTest/@AfterTest setup+teardown).
7. Write the 2 TestNG test classes (valid + invalid).
8. Write `config.properties` + `testng.xml`.
9. Add listener + README run instructions.
10. `mvn clean test` to verify.

## 9. Verification
- `mvn test` from `selenium-framework/` runs `testng.xml`.
- Valid test: assert successful login transition.
- Invalid tests: assert residual login page + visible error element.
- Confirm zero `Thread.sleep`, zero CSS locators via code review.

## 10. Self-Validation
- Every locator traces to verified DOM above. ✓
- Hardcoded exact invalid-password copy marked as **inference** — runtime-read instead. ✓
- Anti-hallucination: no invented elements; unknowns flagged. ✓
