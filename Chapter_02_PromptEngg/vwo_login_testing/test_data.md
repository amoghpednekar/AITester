# Test Data — VWO (app.vwo.com) Login Page

**Draft version:** 1.0 (pending human review)
**Skill:** `stlc/04-test-case-development/test-data-generator`
**Governing rule:** `Antihallucination.rules.md` — no fabricated validation rules; unknown constraints are questions

---

## Data Set 1 — Email (login identifier)

**Known constraints:** email format (standard). **All other constraints (max length, allowed domains, case-sensitivity) are UNKNOWN — to confirm (G-2).**

| Class | Value | Why | Expected |
|-------|-------|-----|----------|
| Valid | `qa.synthetic@example.com` | representative, non-prod, fabricated | accepted → to confirm (G-2) |
| Valid (case variant) | `QA.Synthetic@Example.com` | case-handling check | depends on case-sensitivity → to confirm |
| Invalid | `plainaddress` | missing `@` and domain | rejected (format) → to confirm copy (G-3) |
| Invalid | `user@@example.com` | double `@` | rejected (format) → to confirm |
| Invalid | `user@example` | missing TLD | rejected (format) → to confirm |
| Invalid | `user name@example.com` | embedded space | rejected (format) → to confirm |
| Boundary | `` (empty) | required-field check | rejected → to confirm (G-2/G-3) |
| Boundary | `   ` (whitespace-only) | trim behavior | rejected or trimmed → to confirm |
| Boundary | max-length string (e.g. 256 chars) | length limit | depends on max length → to confirm |
| Boundary | `usér@example.com` (unicode) | unicode support | depends on validation → to confirm |

## Data Set 2 — Password

**Known constraints:** none verified. **Length/complexity rules are UNKNOWN — to confirm (G-2).**

| Class | Value | Why | Expected |
|-------|-------|-----|----------|
| Valid | `Vwo@Passw0rd!2026` | representative synthetic password | accepted → to confirm |
| Invalid (short) | `abc` | likely under min length | rejected → to confirm |
| Invalid (weak) | `password` | common weak value | rejected if complexity enforced → to confirm |
| Invalid | `12345678` | numeric only | depends on complexity rules → to confirm |
| Boundary | `` (empty) | required-field check | rejected → to confirm |
| Boundary | `   ` (whitespace-only) | trim behavior | rejected or trimmed → to confirm |
| Boundary | 1000-char string | length limit | depends on max length → to confirm |
| Boundary | unicode pass `pässwörd!` | unicode support | depends on rules → to confirm |

## Data Set 3 — Credential Pairs (for negative scenarios)

| Pair | Username | Password | Intended outcome |
|------|----------|----------|------------------|
| P-1 wrong password | `qa.synthetic@example.com` | `WrongPass999` | rejected → error shown (to confirm) |
| P-2 unknown account | `no.such.user@example.com` | `Whatever123!` | rejected → error shown (to confirm) |
| P-3 empty both | `` | `` | validation errors shown (to confirm) |
| P-4 valid email + empty password | `qa.synthetic@example.com` | `` | password required error (to confirm) |
| P-5 empty email + valid password | `` | `Vwo@Passw0rd!2026` | email required error (to confirm) |

## Data Set 4 — Synthetic Accounts (must be provisioned in staging)

**Env:** NON-PROD ONLY. Never use real customer data. Fabricated records to confirm with the VWO admin.

| Account | Email | Password | Role |
|---------|-------|----------|------|
| SYN-01 | `qa.synthetic@example.com` | `Vwo@Passw0rd!2026` | member (or admin — to confirm) |
| SYN-02 | `qa.admin@example.com` | `Vwo@Passw0rd!2026` | admin (role model to confirm) |
| SYN-03 | `qa.disabled@example.com` | `Vwo@Passw0rd!2026` | disabled/locked (to be provisioned) |

---

## Environment Safety

- All data above is **fabricated** — no real PII, customer, or production data.
- Synthetic accounts must exist **only in the staging VWO environment**; running against `app.vwo.com` (production) risks account lockout and is not authorized.
- Exact staging URL, password policy, and account provisioning are **to be provided by the VWO admin** (G-7/G-8).

---

## Human Review Gate

**Assumed constraints (must confirm):** email format rules (standard), presence of a min-length password rule, trim behavior, case-sensitivity.

**Questions before this data drives test cases:** G-2 (validation rules), G-3 (error copy), G-7 (roles), staging URL + account provisioning.

**Status:** DRAFT. Confirm the field rules before wiring these values into `test_cases.md`.
