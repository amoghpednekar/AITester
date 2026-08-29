import 'dotenv/config';
import { FullConfig } from '@playwright/test';
import { chromium, Browser, Page } from '@playwright/test';
import { existsSync, mkdirSync } from 'fs';
import { dirname, resolve } from 'path';

const AUTH_STATE_PATH = resolve(__dirname, '../test-results/auth.json');
const env = process.env;

async function performLogin(page: Page, username: string, password: string): Promise<void> {
  const loginUrl = env.APP_URL ?? 'https://login.salesforce.com/?locale=in';
  await page.goto(loginUrl);
  await page.getByLabel('Username').fill(username);

  const passwordVisible = await page.getByLabel('Password').isVisible().catch(() => false);
  if (passwordVisible) {
    await page.getByLabel('Password').fill(password);
  }
  await page.getByRole('button', { name: 'Log In' }).click();

  const homeDomain = env.EXPECTED_HOME_DOMAIN ?? '';
  if (homeDomain) {
    await page.waitForURL(new RegExp(homeDomain), { timeout: 45_000 });
  } else {
    await page.waitForURL((url) => !url.hostname.includes('login.salesforce.com'), {
      timeout: 45_000,
    });
  }
}

export default async function globalSetup(_config: FullConfig): Promise<void> {
  const username = env.VALID_USERNAME ?? '';
  const password = env.VALID_PASSWORD ?? '';

  if (!username || !password) {
    console.log('[global-setup] VALID_USERNAME/VALID_PASSWORD not set — skipping auth state creation');
    return;
  }

  const browser: Browser = await chromium.launch();
  try {
    const context = await browser.newContext();
    const page = await context.newPage();
    await performLogin(page, username, password);
    mkdirSync(dirname(AUTH_STATE_PATH), { recursive: true });
    await context.storageState({ path: AUTH_STATE_PATH });
    console.log(`[global-setup] auth state saved to ${AUTH_STATE_PATH}`);
  } finally {
    await browser.close();
  }
}
