export interface AppEnv {
  appUrl: string;
  validUsername: string;
  validPassword: string;
  expectedHomeDomain: string;
}

export function loadEnv(): AppEnv {
  return {
    appUrl: process.env.APP_URL ?? 'https://login.salesforce.com/?locale=in',
    validUsername: process.env.VALID_USERNAME ?? '',
    validPassword: process.env.VALID_PASSWORD ?? '',
    expectedHomeDomain: process.env.EXPECTED_HOME_DOMAIN ?? '',
  };
}

export function requireValidCredentials(env: AppEnv): void {
  if (!env.validUsername || !env.validPassword) {
    throw new Error(
      'VALID_USERNAME and VALID_PASSWORD must be set in .env to run the valid login spec.'
    );
  }
}

export function hasValidCredentials(env: AppEnv): boolean {
  return Boolean(env.validUsername && env.validPassword);
}
