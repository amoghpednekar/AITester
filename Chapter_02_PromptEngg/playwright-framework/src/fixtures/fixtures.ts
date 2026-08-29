import { test as base, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

type Fixtures = {
  loginPage: LoginPage;
  mockLoginPage: LoginPage;
};

// Minimal mock login form served for the GET, so progressive disclosure never matters.
const MOCK_LOGIN_HTML = `
<html><body>
  <form action="/" method="post">
    <label for="username">Username</label>
    <input type="email" id="username" name="username" />
    <label for="password">Password</label>
    <input type="password" id="password" name="password" />
    <button type="submit" name="Login">Log In</button>
  </form>
</body></html>`;

export const test = base.extend<Fixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },

  // Advanced pattern: a page fixture with the login POST intercepted via page.route
  // (network mocking per pw-network-mocker) so the login flow is deterministic and
  // independent of live Salesforce availability. The GET is fulfilled with a minimal
  // mock form exposing both fields; the POST is fulfilled with a success or rejection
  // page based on whether a password was submitted.
  mockLoginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await page.route('**/login.salesforce.com/**', async (route) => {
      const request = route.request();
      if (request.method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'text/html',
          body: MOCK_LOGIN_HTML,
        });
      } else if (request.method() === 'POST') {
        const body = request.postData() ?? '';
        // Require a non-empty password value (the mock form always submits the password
        // field, empty or not).
        const hasPassword = /password=[^&]+/.test(body);
        if (hasPassword) {
          await route.fulfill({
            status: 200,
            contentType: 'text/html',
            body: '<html><body><h1 id="home">App Home</h1></body></html>',
          });
        } else {
          await route.fulfill({
            status: 400,
            contentType: 'text/html',
            body: '<html><body>Please enter your password.</body></html>',
          });
        }
      } else {
        await route.continue();
      }
    });
    await use(loginPage);
  },
});

export { expect };
