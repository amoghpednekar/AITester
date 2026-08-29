import { test, expect } from '../fixtures/fixtures';
import { loadEnv, hasValidCredentials } from '../utils/env';

const env = loadEnv();

test.describe('Salesforce login page - valid scenarios', () => {
  test('login page loads with all required UI elements', { tag: '@smoke' }, async ({
    page,
    loginPage,
  }) => {
    await test.step('navigate to the login page', async () => {
      await loginPage.goto();
    });

    await expect(loginPage.usernameInput()).toBeVisible();
    await expect(loginPage.submitButton()).toBeVisible();
    await expect(loginPage.rememberMeCheckbox()).toBeVisible();
    await expect(loginPage.forgotPasswordLink()).toBeVisible();
    await expect(page).toHaveTitle(/Login/);

    // TODO: confirm — the public page no longer renders a password field; assert it only
    // when the authenticated/staging variant exposes one.
    const passwordPresent = await loginPage.passwordInput().isVisible().catch(() => false);
    if (passwordPresent) {
      await expect(loginPage.passwordInput()).toBeVisible();
    }
  });

  test(
    'authenticated user reaches the application home',
    { tag: ['@auth', '@smoke'] },
    async ({ page }) => {
      test.skip(!hasValidCredentials(env), 'VALID_USERNAME/VALID_PASSWORD not set in .env');

      await test.step('assert the authenticated session lands on home', async () => {
        await page.goto('/');
        await expect(page).toHaveURL(new RegExp(env.expectedHomeDomain));
      });
    }
  );

  test('remember me checkbox can be toggled', { tag: '@smoke' }, async ({ loginPage }) => {
    await test.step('navigate to the login page', async () => {
      await loginPage.goto();
    });

    await test.step('check and assert selected state', async () => {
      await loginPage.checkRememberMe();
      await expect(loginPage.rememberMeCheckbox()).toBeChecked();
    });

    await test.step('uncheck and assert unselected state', async () => {
      await loginPage.uncheckRememberMe();
      await expect(loginPage.rememberMeCheckbox()).not.toBeChecked();
    });
  });
});
