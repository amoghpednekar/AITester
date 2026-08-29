import { test, expect } from '../fixtures/fixtures';

// Network-mocked login flow (pw-network-mocker): the GET is fulfilled with a minimal mock
// form (both fields always visible) and the POST is fulfilled deterministically — success
// home page when a password is submitted, rejection otherwise. These tests never depend on
// live Salesforce availability or real credentials. Tagged @mock (and @smoke).
test.describe('Salesforce login - mocked network flow', () => {
  test('mocked valid login renders the application home', { tag: '@mock' }, async ({
    page,
    mockLoginPage,
  }) => {
    await test.step('navigate to the mocked login page', async () => {
      await mockLoginPage.goto();
    });

    await test.step('submit credentials through the intercepted route', async () => {
      // The mock form exposes the password field immediately, so login() fills both fields.
      await mockLoginPage.login('demo.user@example.com', 'DemoPass123');
    });

    await test.step('assert the mocked success rendered the home page', async () => {
      await expect(page.getByRole('heading', { name: 'App Home' })).toBeVisible();
    });
  });

  test('mocked login rejects when the password is missing', { tag: '@mock' }, async ({
    page,
    mockLoginPage,
  }) => {
    await test.step('navigate to the mocked login page', async () => {
      await mockLoginPage.goto();
    });

    await test.step('submit username only', async () => {
      await mockLoginPage.fillUsername('demo.user@example.com');
      await mockLoginPage.clickSubmit();
    });

    await test.step('assert the mock rejection is rendered', async () => {
      await expect(page.getByText('Please enter your password.')).toBeVisible();
    });
  });
});
