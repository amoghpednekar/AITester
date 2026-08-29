import 'dotenv/config';
import { defineConfig, devices } from '@playwright/test';
import { existsSync } from 'fs';
import { resolve } from 'path';

const APP_URL = process.env.APP_URL ?? 'https://login.salesforce.com/?locale=in';
const AUTH_STATE_PATH = resolve(__dirname, 'test-results/auth.json');
// storageState is applied only when global-setup produced the artifact (i.e. real
// credentials were configured). Without creds the auth/mock projects fall back to a
// fresh anonymous context instead of failing on a missing file.
const authState = existsSync(AUTH_STATE_PATH) ? { storageState: AUTH_STATE_PATH } : {};

export default defineConfig({
  testDir: './src/tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  timeout: 60_000,
  expect: {
    timeout: 15_000,
  },
  globalSetup: resolve(__dirname, 'global-setup.ts'),
  globalTeardown: resolve(__dirname, 'global-teardown.ts'),
  reporter: [
    ['html', { open: 'never' }],
    [resolve(__dirname, 'src/reporters/summary-reporter.ts')],
  ],
  use: {
    baseURL: APP_URL,
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'smoke',
      grep: /@smoke/,
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'auth',
      grep: /@auth/,
      use: {
        ...devices['Desktop Chrome'],
        ...authState,
      },
    },
    {
      name: 'mock',
      grep: /@mock/,
      use: {
        ...devices['Desktop Chrome'],
        ...authState,
      },
    },
    {
      name: 'regression',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
