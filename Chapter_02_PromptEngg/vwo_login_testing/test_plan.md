# Test Plan — VWO (app.vwo.com) Login Page

**Feature under test:** Login page / authentication entry at `https://app.vwo.com/#/login`
**Draft version:** 1.0 (draft — pending human review)
**Skill:** `stlc/02-test-planning/test-plan-generator`
**Governing rule:** `Chapter_01_LLM_basics/Antihallucination.rules.md`

---

## 1. Scope & Objectives

**In scope**
- Page load and rendering of the login screen
- Login with credentials (valid / invalid / boundary)
- Error handling and user feedback on failed login
- Session behavior (remember-me, logout, post-login redirect)
- Security-sensitive behavior observable at the UI level (password masking, credential handling, bot/captcha if present)

**Out of scope**
- Backend/API authentication logic (not verifiable from the page alone)
- Multi-factor authentication internals, SSO provider-side flows, password-reset email delivery
- Performance / load / security-penetration testing (flagged as non-functional gaps)

**Objective**
Produce a review-ready test plan, scenarios, data sets, and executable test cases for the VWO login page, grounded only in verified facts from the live page and with every unverified behavior explicitly flagged, per the repo anti-hallucination rules.

---

## 2. Verified Facts (from live fetch of https://app.vwo.com/)

| # | Fact | Source |
|---|------|--------|
| F-1 | The product is **VWO by Wingify**: "Wingify is the all-in-one platform that helps you conduct visitor research, build an optimization roadmap, and run continuous experimentation." | Page `<meta name="description">` |
| F-2 | The application entry URL is `https://app.vwo.com/` (canonical link present). | `<link rel="canonical">` |
| F-3 | The app is a client-side rendered **Angular SPA**; static HTML is only the app shell. | Hundreds of `.js` bundles incl. `main-*.js`, `app-*.js`; Angular patterns |
| F-4 | Login-related code exists: `LoginController-*.js`, multiple `login-*.js` bundles, `auth-flow-modal-*.js`, `token-auth-success-modal-*.js`, `backup-codes-*.js`, `settings-security-*.js`. | Script importmap |
| F-5 | Domain constants defined in `window.VWO_DOMAIN`: `app.vwo.com`, `api.vwo.com`, `help.vwo.com`, `vwo.com`, `support@wingify.com`. | Inline script |
| F-6 | The login route is under `#/login` (hash-routed SPA). | Router convention + user-specified URL |

**Missing / Unknown (per Antihallucination.rules.md → "Insufficient information to determine")**
- Exact form fields, labels, placeholders (email vs username, password field presence)
- Validation rules (email format, password length/complexity, max lengths)
- Error message copy for invalid credentials / empty fields / locked accounts
- Remember-me behavior, forgot-password flow/URL, SSO/Google/passwordless options
- CAPTCHA / bot-detection, MFA/2FA presence
- Post-login redirect target and success indicator
- Role/permission-based landing (admin vs member)
- Accessibility, i18n, and performance attributes

---

## 3. Gaps & Questions for the Author (test-plan-generator step 2)

These block full sign-off of expected results. Each is a question, not an assumed answer.

| # | Gap | Question for the author |
|---|-----|------------------------|
| G-1 | Login form composition unknown | Which fields does the login form contain (email, password, remember-me, SSO buttons)? |
| G-2 | Validation rules unknown | What are the client-side validation rules for email and password (format, length, required)? |
| G-3 | Error copy unknown | What exact error messages appear for: wrong password, unknown account, empty fields, locked/disabled account? |
| G-4 | Session behavior unknown | Does "remember me" exist? What is the session timeout and the post-login landing URL? |
| G-5 | Recovery flows unknown | What is the forgot-password link target and expected behavior? |
| G-6 | Security controls unknown | Is there CAPTCHA/bot detection, password masking, MFA? |
| G-7 | Roles/permissions unknown | Do different roles land on different pages after login? |
| G-8 | Non-functional needs unknown | Accessibility (WCAG target), supported browsers, languages? |

> These gaps mean **expected results in test cases are marked "expected result to confirm"** where they depend on unverified behavior. The plan is a draft until these are answered.

---

## 4. Test Scenarios (P0/P1/P2 risk-tagged)

| ID | Scenario | Type | Risk | Covers |
|----|----------|------|------|--------|
| TS-1 | Login page loads and displays the login form | Positive | P0 | F-2, F-3 |
| TS-2 | Login with valid credentials succeeds and redirects to the app | Positive | P0 | G-4 (to confirm) |
| TS-3 | Remember-me checkbox persists the session across browser restart | Positive | P1 | G-4 (to confirm) |
| TS-4 | Forgot-password link opens the recovery flow | Positive | P1 | G-5 (to confirm) |
| TS-5 | Invalid credentials are rejected with an error message | Negative | P0 | G-3 (to confirm) |
| TS-6 | Empty email and/or password shows validation error | Negative | P0 | G-2, G-3 (to confirm) |
| TS-7 | Malformed email format is rejected | Negative | P1 | G-2 (to confirm) |
| TS-8 | Unknown/unregistered account is rejected | Negative | P1 | G-3 (to confirm) |
| TS-9 | Locked/disabled account is rejected with appropriate message | Negative | P2 | G-3 (to confirm) |
| TS-10 | Boundary: whitespace-only / max-length / unicode inputs | Boundary | P1 | G-2 (to confirm) |
| TS-11 | Password field masks input (not plaintext) | Security | P0 | G-6 (to confirm) |
| TS-12 | Credentials are not exposed in the URL after submission | Security | P1 | G-6 (to confirm) |
| TS-13 | CAPTCHA / bot-detection engages after repeated failed attempts | Security | P2 | G-6 (to confirm) |
| TS-14 | Logout ends the session and returns to the login page | Cross-state | P1 | G-4 (to confirm) |

**Coverage note:** F-1 and F-5 (product identity/domains) have no dedicated scenario — they are context facts, not testable UI behavior. Scenarios TS-2..TS-14 depend on G-* answers and are therefore partially unconfirmed.

---

## 5. Test Data & Environment

- **Environments:** non-production staging instance of VWO (per `test-data-generator` guardrail, no live/prod data). Exact staging URL is **unknown — to confirm**.
- **Accounts:** synthetic accounts only — fabricated email + password, never real customer data.
- **Browsers:** to confirm — at minimum Chromium and Firefox (cross-browser smoke).
- **Test data sets:** see `test_data.md` (valid / invalid / boundary / synthetic).

---

## 6. Risks & Assumptions

**Assumptions (flagged)**
- A1: The login form is reachable at `https://app.vwo.com/#/login` (user-specified URL).
- A2: Login is credential-based (email + password) — this is **inferred from the existence of `login-*.js` / `LoginController` bundles, low confidence**, not verified.
- A3: A staging/non-prod VWO instance exists for testing — to confirm.
- A4: Browser automation (Selenium/Playwright) can render the SPA login form — the page is JS-rendered, so static fetching cannot confirm field details.

**Risks**
- R1: Public `app.vwo.com` may have CAPTCHA / bot-detection that interferes with automated testing.
- R2: SPA hash-routing may change; selectors and routes are not yet verified.
- R3: Real account data must never be used; a lockout/abuse risk exists if tests run against production.

---

## 7. Entry / Exit Criteria

**Entry criteria**
- Staging environment URL is provided and reachable.
- At least one synthetic test account is provisioned.
- G-1..G-8 have answers (or are explicitly accepted as "to confirm").

**Exit criteria**
- All P0 scenarios executed and results recorded.
- Every test case traceable to a scenario and a verified fact or flagged gap.
- Human review completed on plan, scenarios, data, and cases.

---

## 8. Human Review Gate

**Assumptions made (must confirm):** A1–A4 above; credential-based login (low confidence).

**Open questions that block sign-off:** G-1..G-8.

**Status:** DRAFT. Do not treat this plan as final or begin automation against it until a human has confirmed the gaps above and approved the coverage set.
