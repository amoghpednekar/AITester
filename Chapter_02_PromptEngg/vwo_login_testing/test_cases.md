# Test Cases — VWO (app.vwo.com) Login Page

**Draft version:** 1.0 (pending human review)
**Skill:** `stlc/04-test-case-development/test-case-writer`
**Data source:** `test_data.md`
**Scenario source:** `test_scenarios.md`

---

## Legend

- **Status:** DRAFT. Expected results marked **[to confirm]** depend on unanswered gaps G-2..G-8 and must be confirmed before execution or automation.
- **Traceability:** each TC cites its scenario (TS-x) and a verified fact (F-x) or gap (G-x).

---

## TC-1 — Login page loads and displays the login form (from TS-1, F-2/F-3) — P0

- **Preconditions:** Browser with internet access; VWO staging or app URL configured.
- **Test data:** none.
- **Steps:**
  1. Navigate to `https://app.vwo.com/#/login` → **Expected:** Login page loads without console errors; page renders.
  2. Wait for the SPA to finish client-side rendering → **Expected:** A login form is displayed (fields [to confirm] — G-1).
- **Postconditions:** none.

## TC-2 — Login with valid credentials succeeds and redirects to the app (from TS-2, G-4) — P0

- **Preconditions:** Synthetic account SYN-01 provisioned in staging; valid credentials from Data Set 1/2.
- **Test data:** `qa.synthetic@example.com` / `Vwo@Passw0rd!2026`.
- **Steps:**
  1. Open the login page → **Expected:** form displayed.
  2. Enter valid email → **Expected:** value accepted.
  3. Enter valid password → **Expected:** value accepted (masked — see TC-11).
  4. Submit → **Expected:** authentication succeeds; user lands on the app home **[to confirm]** — post-login URL/success indicator (G-4).
- **Postconditions:** log out to restore clean state.

## TC-3 — Remember-me persists the session across a browser restart (from TS-3, G-4) — P1

- **Preconditions:** SYN-01; remember-me behavior confirmed to exist (G-4).
- **Test data:** valid credentials.
- **Steps:**
  1. Log in with remember-me enabled → **Expected:** login succeeds [to confirm].
  2. Close and reopen the browser → **Expected:** session persists; user not asked to log in again [to confirm].
  3. Log out → **Expected:** session cleared [to confirm].
- **Postconditions:** session cleared.

## TC-4 — Forgot-password link opens the recovery flow (from TS-4, G-5) — P1

- **Preconditions:** Login page displayed; link exists (G-5).
- **Test data:** none.
- **Steps:**
  1. Locate the forgot-password link → **Expected:** link is visible [to confirm] — label/location (G-5).
  2. Click it → **Expected:** recovery flow opens (password reset page/email prompt) [to confirm].
- **Postconditions:** return to login page.

## TC-5 — Invalid credentials are rejected with an error (from TS-5, G-3) — P0

- **Preconditions:** Login page displayed.
- **Test data:** P-1 (wrong password).
- **Steps:**
  1. Enter valid email + wrong password → **Expected:** values accepted.
  2. Submit → **Expected:** login is rejected; an error message is shown **[to confirm]** — exact copy (G-3); user remains on the login page.
- **Postconditions:** none.

## TC-6 — Empty email and/or password shows validation error (from TS-6, G-2/G-3) — P0

- **Preconditions:** Login page displayed.
- **Test data:** P-3 (empty both), P-4 (email only), P-5 (password only).
- **Steps:**
  1. Submit with both fields empty → **Expected:** validation error(s) shown without submission [to confirm] — copy (G-3).
  2. Repeat with only email filled → **Expected:** password-required error [to confirm].
  3. Repeat with only password filled → **Expected:** email-required error [to confirm].
- **Postconditions:** none.

## TC-7 — Malformed email format is rejected (from TS-7, G-2) — P1

- **Preconditions:** Login page displayed.
- **Test data:** invalid emails from Data Set 1 (`plainaddress`, `user@@example.com`, `user@example`, `user name@example.com`).
- **Steps:** for each invalid email:
  1. Enter the invalid email + a valid password → **Expected:** field rejected / validation error [to confirm] — copy (G-3).
  2. Submit → **Expected:** no authentication attempt; error shown [to confirm].
- **Postconditions:** none.

## TC-8 — Unknown/unregistered account is rejected (from TS-8, G-3) — P1

- **Preconditions:** Login page displayed.
- **Test data:** P-2 (unknown account).
- **Steps:**
  1. Enter unknown email + any password → **Expected:** values accepted.
  2. Submit → **Expected:** rejected; error shown **[to confirm]** — copy distinguishes unknown account vs wrong password (G-3).
- **Postconditions:** none.

## TC-9 — Locked/disabled account is rejected with appropriate message (from TS-9, G-3) — P2

- **Preconditions:** Disabled account SYN-03 provisioned in staging.
- **Test data:** SYN-03 credentials.
- **Steps:**
  1. Enter SYN-03 credentials → **Expected:** values accepted.
  2. Submit → **Expected:** rejected; account-status message [to confirm] — copy (G-3).
- **Postconditions:** none.

## TC-10 — Boundary inputs are handled (from TS-10, G-2) — P1

- **Preconditions:** Login page displayed.
- **Test data:** Data Set 1/2 boundary values (empty, whitespace-only, max-length, unicode).
- **Steps:** for each boundary value:
  1. Enter the boundary value in the relevant field → **Expected:** field accepts or rejects per rules [to confirm] — trim/length behavior (G-2).
  2. Submit → **Expected:** no crash; deterministic outcome [to confirm].
- **Postconditions:** none.

## TC-11 — Password field masks input (from TS-11, G-6) — P0

- **Preconditions:** Login page displayed.
- **Test data:** any password.
- **Steps:**
  1. Focus the password field and type a password → **Expected:** characters are masked (bullets), not plaintext [to confirm] — G-6.
  2. (If a show/hide toggle exists) toggle visibility → **Expected:** toggle reveals/masks as designed [to confirm].
- **Postconditions:** clear the field.

## TC-12 — Credentials are not exposed in the URL after submission (from TS-12, G-6) — P1

- **Preconditions:** Login page displayed.
- **Test data:** valid credentials (SYN-01).
- **Steps:**
  1. Submit credentials → **Expected:** post-submit URL contains no email/password query parameters [to confirm] — G-6.
  2. Inspect browser history/network for the submission → **Expected:** no credential leakage in URL [to confirm].
- **Postconditions:** log out.

## TC-13 — CAPTCHA / bot-detection engages after repeated failed attempts (from TS-13, G-6) — P2

- **Preconditions:** Login page displayed; bot-detection confirmed present (G-6).
- **Test data:** P-1 repeated.
- **Steps:**
  1. Submit wrong credentials N times → **Expected:** after N failures, a CAPTCHA/block appears [to confirm] — threshold N (G-6).
- **Postconditions:** wait for block to clear before further tests.

## TC-14 — Logout ends the session and returns to login (from TS-14, G-4) — P1

- **Preconditions:** Logged in as SYN-01.
- **Test data:** valid credentials.
- **Steps:**
  1. Log in successfully → **Expected:** in app.
  2. Click logout → **Expected:** session ends; redirected to login page [to confirm] — G-4.
  3. Attempt to access the app URL directly → **Expected:** redirected to login (session invalid) [to confirm].
- **Postconditions:** none.

## TC-15 — Login page is keyboard-accessible (from TS-15, G-8) — P2

- **Preconditions:** Login page displayed.
- **Test data:** none.
- **Steps:**
  1. Navigate the form using only the keyboard (Tab/Shift+Tab) → **Expected:** logical focus order; all fields/buttons reachable [to confirm] — G-8.
  2. Submit via keyboard (Enter) → **Expected:** form submits [to confirm].
- **Postconditions:** none.

## TC-16 — Login page renders correctly on a mobile viewport (from TS-16, G-8) — P2

- **Preconditions:** Mobile viewport emulation or device.
- **Test data:** none.
- **Steps:**
  1. Open the login page at a mobile viewport (e.g. 375x667) → **Expected:** form is usable; no horizontal overflow [to confirm] — G-8.
  2. Complete a login → **Expected:** works as on desktop [to confirm].
- **Postconditions:** none.

---

## Traceability Summary

| Case | Scenario | Traces to |
|------|----------|-----------|
| TC-1 | TS-1 | F-2, F-3 |
| TC-2 | TS-2 | G-4 |
| TC-3 | TS-3 | G-4 |
| TC-4 | TS-4 | G-5 |
| TC-5 | TS-5 | G-3 |
| TC-6 | TS-6 | G-2, G-3 |
| TC-7 | TS-7 | G-2 |
| TC-8 | TS-8 | G-3 |
| TC-9 | TS-9 | G-3 |
| TC-10 | TS-10 | G-2 |
| TC-11 | TS-11 | G-6 |
| TC-12 | TS-12 | G-6 |
| TC-13 | TS-13 | G-6 |
| TC-14 | TS-14 | G-4 |
| TC-15 | TS-15 | G-8 |
| TC-16 | TS-16 | G-8 |

**No orphan cases:** every TC maps to a TS. **No orphan scenarios:** every TS maps to a fact (F-2/F-3) or a gap (G-2..G-8).

---

## Human Review Gate

**Assumptions / unconfirmed expected results:** all `[to confirm]` markers above (exact error copy, validation rules, session behavior, security controls, roles, a11y, mobile) — these depend on G-2..G-8 answers or live rendered-DOM inspection.

**Status:** DRAFT. A human must approve these cases (after confirming gaps or accepting the "to confirm" markers) before they are used to drive automation or manual execution.
