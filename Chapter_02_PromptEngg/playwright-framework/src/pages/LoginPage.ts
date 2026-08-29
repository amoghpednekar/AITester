import { type Page, type Locator } from '@playwright/test';

export class LoginPage {
  static readonly PATH = '/?locale=in';

  constructor(private readonly page: Page) {}

  usernameInput = (): Locator => this.page.getByLabel('Username');
  submitButton = (): Locator => this.page.getByRole('button', { name: 'Log In' });
  rememberMeCheckbox = (): Locator => this.page.getByRole('checkbox', { name: 'Remember me' });
  forgotPasswordLink = (): Locator => this.page.getByRole('link', { name: 'Forgot Your Password?' });
  // TODO: confirm — live page renders the login error as plain text (e.g. "Please enter
  // your username." / "Please enter your password.") with no role="alert" wrapper; text
  // locator is the resilience-ladder fallback (pw-locator-fixer). Switch to getByRole('alert')
  // if a wrapper appears.
  errorBanner = (): Locator => this.page.getByText(/Please enter your/);

  // The public login page uses progressive disclosure: the password field is revealed only
  // after a username is entered. On staging/classic variants the field is present immediately.
  passwordInput = (): Locator => this.page.getByLabel('Password');

  async goto(): Promise<void> {
    await this.page.goto(LoginPage.PATH);
  }

  async fillUsername(username: string): Promise<void> {
    await this.usernameInput().fill(username);
  }

  async fillPassword(password: string): Promise<void> {
    await this.passwordInput().fill(password);
  }

  async clickSubmit(): Promise<void> {
    await this.submitButton().click();
  }

  async login(username: string, password: string): Promise<void> {
    await this.fillUsername(username);
    // Progressive disclosure: the password field appears only for recognized usernames.
    // Wait web-first, and only fill if the field is actually revealed.
    if (password) {
      const revealed = await this.passwordInput()
        .waitFor({ state: 'visible', timeout: 8_000 })
        .then(() => true)
        .catch(() => false);
      if (revealed) {
        await this.fillPassword(password);
      }
    }
    await this.clickSubmit();
  }

  async checkRememberMe(): Promise<void> {
    await this.rememberMeCheckbox().check();
  }

  async uncheckRememberMe(): Promise<void> {
    await this.rememberMeCheckbox().uncheck();
  }
}
