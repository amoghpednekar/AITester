import 'dotenv/config';
import { FullConfig } from '@playwright/test';
import { existsSync, rmSync } from 'fs';
import { resolve } from 'path';

const AUTH_STATE_PATH = resolve(__dirname, 'test-results/auth.json');

export default async function globalTeardown(_config: FullConfig): Promise<void> {
  if (existsSync(AUTH_STATE_PATH)) {
    rmSync(AUTH_STATE_PATH, { force: true });
    console.log('[global-teardown] removed auth state artifact');
  }
}
