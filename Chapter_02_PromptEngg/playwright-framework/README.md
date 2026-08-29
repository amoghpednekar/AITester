# Salesforce Playwright Framework

Enterprise-grade Playwright + TypeScript framework for the Salesforce login page
(`https://login.salesforce.com/?locale=in`), built from the `prompt_templates/playwright/`
skill suite (page-object-builder, test-generator, fixture-designer, locator-fixer, ci-configurator).

## Prerequisites

- Node.js 18+
- pnpm (via corepack) — `npm` 11.6.2 has a reify bug on this machine that silently no-ops
  installs of `@playwright/*` packages; pnpm works correctly.

## Setup

```bash
corepack pnpm install
corepack pnpm exec playwright install chromium
cp .env.example .env   # then fill in credentials
```

## Run Tests

```bash
pnpm test              # full suite (all projects)
pnpm run test:smoke    # smoke project only (@smoke tag)
pnpm run test:auth     # auth project only (@auth tag, storageState session)
pnpm run test:mock     # mock project only (@mock tag, network interception)
pnpm run test:regression  # full regression project
pnpm run test:headed   # headed (visible browser)
pnpm run typecheck     # TypeScript type check
```

## Advanced Capabilities

- **`storageState` auth** — `global-setup.ts` performs one UI login when credentials are
  present and persists the session to `test-results/auth.json`; the `auth` project injects
  it so authenticated tests never re-login through the UI (`pw-fixture-designer`).
- **Network mocking** — the `mockLoginPage` fixture intercepts the login POST via
  `page.route()` and fulfills a deterministic 302 redirect, making mocked tests immune to
  live Salesforce availability (`pw-network-mocker`).
- **Project matrix** — `smoke` / `auth` / `mock` / `regression` projects with `grep`-based
  tag routing (`@smoke`, `@auth`, `@mock`); tag a test with the `{ tag }` annotation.
- **Custom summary reporter** — `src/reporters/summary-reporter.ts` prints a pass/fail/
  skip/flaky tally and failure list on every run.
- **Global hooks** — `global-setup.ts` / `global-teardown.ts` create and remove the auth
  state artifact, keeping the workspace clean.

## Configuration

`.env` (gitignored):

- `APP_URL` — login page URL
- `VALID_USERNAME`, `VALID_PASSWORD` — valid credentials (required only for the valid spec)
- `EXPECTED_HOME_DOMAIN` — post-login domain to assert, e.g. `my.salesforce.com`

The valid-login spec requires real credentials and skips gracefully when they are absent.
The invalid-login spec runs without credentials.

## Locator Strategy

Per the Playwright skill suite: role/label-based locators only — no XPath, no CSS-class
selectors, no `nth-child`. Web-first auto-retrying assertions, no `waitForTimeout`.

## Live-Page Notes (verified 2026-08-28)

- The public login page uses **progressive disclosure**: only the Username field is shown
  initially; the Password field appears after a username is entered.
- Login errors render as **plain text** ("Please enter your username."), not inside an
  ARIA `role="alert"` wrapper — the POM uses a text locator for the error banner.
- Wrong/blank **password** attempts are rejected without a visible error on the live page;
  the invalid spec asserts the rejection (no redirect, form remains) for those cases.
- The valid-credentials test skips until `VALID_USERNAME`/`VALID_PASSWORD` are set in `.env`.

## Structure

- `src/pages/LoginPage.ts` — Page Object (locator methods return lazy `Locator`, actions only, no assertions)
- `src/fixtures/fixtures.ts` — typed fixtures via `test.extend` (test-scoped `loginPage`)
- `src/utils/env.ts` — typed env access, fails closed on missing required values
- `src/tests/login-valid.spec.ts`, `src/tests/login-invalid.spec.ts` — TestNG-equivalent specs
- `playwright.config.ts` — projects, timeouts, trace/video on failure, HTML reporter
- `.github/workflows/playwright.yml` — CI draft (manual trigger only, not enabled)

## CI Note

The workflow is `workflow_dispatch` only. Enable push/PR triggers only after a human
review gate approves the execution target, identity/data, and artifact handling
(per `pw-ci-configurator` guardrails).
