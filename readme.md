# AITesterBlueprint4X

An AI-assisted QA engineering blueprint: a collection of reusable **prompt templates / agent skills**, and working **test automation frameworks**, built around a strict **anti-hallucination rule base** — every test decision must be traceable to verified facts, with unknown behavior explicitly flagged.

## Repository Contents

```
.
├── Chapter_01_LLM_basics/            # LLM testing fundamentals
│   ├── Antihallucination.rules.md    # Governing rules: no invented facts, traceable assertions
│   └── TestCases_AI_PRD_Reviewer.md  # AI PRD-reviewer test cases (traceable to a PRD)
├── Chapter_02_PromptEngg/            # Prompt engineering + frameworks
│   ├── prompt_templates/             # Reusable agent skill templates by testing domain
│   │   ├── AI_QA_Shiftleft_test_analyser/  # Test-layer selection skill (Unit→API→Integration→E2E)
│   │   ├── api_testing/              # API contract, workflow, auth-boundary, collection, resilience
│   │   ├── playwright/               # POM, test-generator, fixtures, locator, mocking, CI, visual
│   │   ├── selenium/                 # Selenium skill suite (scaffold, POM, grid, cross-browser)
│   │   ├── safety_guardrails/        # Prompt-injection, data-leakage, bias, threat-modeling
│   │   ├── stlc/                     # Full STLC: requirement analysis → test closure
│   │   └── test_deliverables/        # Test status, evidence, traceability, audit handoff
│   ├── selenium-framework/         # Selenium + Java + Maven + TestNG (Salesforce login)
│   ├── playwright-framework/       # Playwright + TypeScript (Salesforce login)
│   ├── vwo_login_testing/          # VWO login: test plan, scenarios, data, cases (draft)
│   └── 01_Ricepot.*.md             # Prompt recipe template + example
├── Chapter_03_Local_Testcase_Generator/  # Streamlit web app: Jira → traceable test cases via local Ollama
└── readme.md
```

## What's Inside

### Prompt Templates (Agent Skills)

Reusable, task-specific prompt templates organized by testing discipline:

- **AI QA test-layer selection** — decides the *lowest reliable testing layer* for each scenario: **Unit → API → Integration → E2E** (preferring fewer unnecessary E2E tests).
- **API testing** — contract validation, workflow, authorization-boundary, collection building, resilience/performance planning.
- **Playwright** — page-object builder, test generator, fixture designer, locator fixer, network mocker, CI configurator, trace analyzer, visual regression, flaky debugger.
- **Selenium** — framework scaffolder, driver manager, page-object builder, data-driven designer, cross-browser runner, grid configurator, flaky debugger, report integrator.
- **Safety guardrails** — prompt-injection resilience, sensitive-data-leakage, fairness/bias, threat modeling, content-safety evaluation.
- **STLC workflow** — requirement analysis → test planning → design → case development → execution → defect management → closure.
- **Test deliverables** — status briefs, evidence bundles, traceability, release decision records, QA audit handoff.

### Selenium Framework (`selenium-framework/`)

Enterprise Selenium + Java + Maven + TestNG framework for the Salesforce login page.

- Page Object Model, ThreadLocal driver factory, config-driven (browser, timeouts)
- Valid + invalid login tests, TestNG suite, parallel execution
- Credentials live in `src/test/resources/config.properties` (fill locally; never commit real values)

### Playwright Framework (`playwright-framework/`)

Enterprise Playwright + TypeScript framework for the Salesforce login page.

- POM, typed fixtures (`test.extend`), storageState auth, network mocking via `page.route`
- Project matrix: `smoke` / `auth` / `mock` / `regression`, tag-routed (`@smoke`, `@auth`, `@mock`)
- Custom summary reporter, global setup/teardown, HTML report + trace/video on failure
- CI workflow (`workflow_dispatch` only) reads credentials from GitHub Secrets

### VWO Login Testing (`vwo_login_testing/`)

Review-ready draft test plan, scenarios, data sets, and test cases for the VWO login page — every unverified behavior explicitly flagged `[to confirm]` per the anti-hallucination rules.

### Jira Test Case Generator (`Chapter_03_Local_Testcase_Generator/`)

Two-page Streamlit web app that retrieves an authorized Jira issue and generates **traceable QA test cases** via a local Ollama model (`gemma4:e2b`). Output follows the anti-hallucination rule base: every case is grounded in verified requirement facts, and unspecified behavior is reported as a gap rather than invented. See its [README](Chapter_03_Local_Testcase_Generator/README.md) for setup and deployment notes.

## Anti-Hallucination Rule Base

The shared governing principle across this repo (`Chapter_01_LLM_basics/Antihallucination.rules.md`):

- **Do not invent** features, APIs, error codes, UI elements, or behavior.
- Every assertion must be **traceable** to provided input (PRD, docs, logs, live page).
- Missing or unclear information → **"Insufficient information to determine."**
- Inferred details are labeled explicitly as low-confidence.

## Getting Started

### Playwright framework

```bash
cd Chapter_02_PromptEngg/playwright-framework
corepack pnpm install
corepack pnpm exec playwright install chromium
cp .env.example .env     # fill in credentials (optional)
pnpm test                # or: pnpm run test:smoke / test:mock / test:auth
```

### Selenium framework

```bash
cd Chapter_02_PromptEngg/selenium-framework
mvn clean test
```

## Security Notes

- `.env` files and credentials are **gitignored** — never commit real usernames/passwords.
- The Playwright CI workflow is **manual trigger only** (`workflow_dispatch`); enable push/PR triggers only after a human review gate.
- Test data in `vwo_login_testing/` is entirely **fabricated** and staging-only.

## License

TBD
