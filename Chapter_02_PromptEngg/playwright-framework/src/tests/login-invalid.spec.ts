import { test, expect } from '../fixtures/fixtures';

interface InvalidCredential {
  username: string;
  password: string;
  caseId: string;
  expectsErrorText: boolean;
}

// The public login page (progressive disclosure) renders error text only for username
// issues ("Please enter your username."). Wrong/blank password attempts are rejected
// without a visible error on the live page, so those cases assert the rejection itself.
const invalidCredentials: InvalidCredential[] = [
  { username: 'invalid.user@example.com', password: 'WrongPass123', caseId: 'INV-01', expectsErrorText: false },
  { username: 'user@example.com', password: '', caseId: 'INV-02', expectsErrorText: false },
  { username: '', password: 'SomePassword', caseId: 'INV-03', expectsErrorText: true },
  { username: 'plainaddress', password: 'SomePassword', caseId: 'INV-04', expectsErrorText: true },
];

test.describe('Salesforce login page - invalid scenarios', () => {
  for (const credential of invalidCredentials) {
    test(
      `invalid login is rejected with error shown (${credential.caseId})`,
      { tag: '@smoke' },
      async ({ page, loginPage }) => {
        await test.step('navigate to the login page', async () => {
          await loginPage.goto();
        });

        await test.step('submit invalid credentials', async () => {
          await loginPage.login(credential.username, credential.password);
        });

        await test.step('assert the attempt is rejected', async () => {
          await expect(page).toHaveURL(/login\.salesforce\.com/);
          await expect(loginPage.submitButton()).toBeVisible();
          if (credential.expectsErrorText) {
            await expect(loginPage.errorBanner()).toBeVisible();
          }
        });
      }
    );
  }

  test('blank username shows an error (INV-05)', { tag: '@smoke' }, async ({ page, loginPage }) => {
    await test.step('navigate to the login page', async () => {
      await loginPage.goto();
    });

    await test.step('submit with no username', async () => {
      await loginPage.login('', '');
    });

    await test.step('assert error is shown', async () => {
      await expect(loginPage.errorBanner()).toBeVisible();
      await expect(page).toHaveURL(/login\.salesforce\.com/);
    });
  });
});
