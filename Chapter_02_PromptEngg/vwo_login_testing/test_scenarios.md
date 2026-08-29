# Test Scenarios — VWO (app.vwo.com) Login Page

**Draft version:** 1.0 (pending human review)
**Skill:** `stlc/03-test-design/test-scenario-designer`
**Traceability source:** `test_plan.md` (Verified Facts F-1..F-6, Gaps G-1..G-8)

---

## Coverage Map

| ID | Scenario | Type | Risk | Covers |
|----|----------|------|------|--------|
| TS-1 | Login page loads and displays the login form | Positive | P0 | F-2, F-3 |
| TS-2 | Login with valid credentials succeeds and redirects to the app home | Positive | P0 | G-4 (to confirm) |
| TS-3 | Remember-me checkbox persists the session across a browser restart | Positive | P1 | G-4 (to confirm) |
| TS-4 | Forgot-password link opens the recovery flow | Positive | P1 | G-5 (to confirm) |
| TS-5 | Login with invalid credentials is rejected with an error message | Negative | P0 | G-3 (to confirm) |
| TS-6 | Empty email and/or password shows a validation error without submission | Negative | P0 | G-2, G-3 (to confirm) |
| TS-7 | Malformed email format is rejected | Negative | P1 | G-2 (to confirm) |
| TS-8 | Unknown/unregistered account is rejected | Negative | P1 | G-3 (to confirm) |
| TS-9 | Locked/disabled account is rejected with an appropriate message | Negative | P2 | G-3 (to confirm) |
| TS-10 | Boundary inputs: whitespace-only, max-length, unicode in email/password | Boundary | P1 | G-2 (to confirm) |
| TS-11 | Password field masks input (not displayed in plaintext) | Security | P0 | G-6 (to confirm) |
| TS-12 | Credentials are not exposed in the URL after submission | Security | P1 | G-6 (to confirm) |
| TS-13 | CAPTCHA / bot-detection engages after repeated failed attempts | Security | P2 | G-6 (to confirm) |
| TS-14 | Logout ends the session and returns to the login page | Cross-state | P1 | G-4 (to confirm) |
| TS-15 | Login page is keyboard-accessible (tab order, focus states) | Non-functional | P2 | G-8 (to confirm) |
| TS-16 | Login page renders correctly on a supported mobile viewport | Non-functional | P2 | G-8 (to confirm) |

---

## Traceability Notes

- **Scenarios traceable to verified facts:** TS-1 → F-2 (URL) + F-3 (SPA). All others depend on answers to G-2..G-8 and are **drafts whose expected results must be confirmed**.
- **Facts with no scenario:** F-1 (product identity), F-4 (login code bundles), F-5 (domain constants) — context/implementation evidence, not directly testable UI behavior. F-4 supports the low-confidence assumption A2 (credential-based login).
- **Deliberate exclusions:** API-level authentication, SSO provider internals, password-reset email delivery, load/performance testing — out of scope per test plan.

---

## Human Review Gate

**Assumptions:** A1–A4 from the test plan; credential-based login inferred from F-4 (low confidence).

**Deliberate exclusions:** backend/API auth, SSO internals, email delivery, performance.

**Status:** DRAFT. Confirm the scenario set (especially TS-13, TS-15, TS-16 which depend on unverified security/a11y/mobile behavior) before this proceeds to detailed test cases.
