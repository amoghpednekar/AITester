---
name: jira-test-case-generator
description: Build or maintain a Python web application that retrieves Jira requirements and uses a local Ollama Gemma model to generate traceable, comprehensive QA test cases. Use for this Jira-to-test-case generator, its UI, integrations, prompts, validation, tests, or Vercel-ready deployment configuration.
---

# Jira Test Case Generator

Build a simple two-page Python web application that accepts a Jira issue key or URL, retrieves the authorized issue, and generates grounded test cases using Ollama `gemma4:e2b`.

## RICE-POT

### R — Role

Act as a senior Python engineer, QA architect, and security-conscious integration developer. Produce maintainable application code and QA artifacts that are traceable to the source requirement.

### I — Instructions

When implementing or changing the application:

1. Inspect the existing repository and preserve working conventions and user changes.
2. Use Python for the application. Prefer Streamlit for the UI and application flow because both required pages can remain Python-based. Isolate Jira and Ollama access behind service modules so a separate Python API can be introduced later without rewriting core logic.
3. Provide two pages that follow the supplied low-fidelity design:
   - **Generator**: a large bordered results/conversation panel in the upper portion, followed by a bottom chat input and adjacent **Send** button. Use placeholder text such as `Create test cases for VWO-49`. Show the fetched Jira requirement in the upper panel before appending generated results.
   - **Settings**: a centered bordered settings card containing Jira email, Jira token, Jira URL, Ollama URL, and Groq token fields, followed by a prominent **Save settings** button. Add separate **Test Jira Connection** and **Test Ollama Connection** actions without disrupting the simple layout.
4. Accept a Jira issue key such as `ABC-123` or a Jira browse URL. Parse and validate the key before making requests.
5. Fetch only fields needed for generation, including key, summary, description, issue type, priority, status, labels, components, acceptance criteria when present, and relevant non-sensitive linked issue context when configured.
6. Normalize Jira Atlassian Document Format into readable plain text while preserving headings, lists, tables, and acceptance-criteria identifiers.
7. Generate test cases only after Jira retrieval succeeds and the user can review the fetched requirement.
8. Use Ollama's HTTP API with model `gemma4:e2b` by default. Make base URL, model, timeout, and optional token configurable.
   - Keep Groq as an optional cloud-provider alternative for hosted use because it appears in the supplied settings design. Never switch from Ollama to Groq silently; require explicit provider selection and user configuration.
9. Parse model output into a typed schema and validate it before display. If parsing fails, make at most one repair request using the validation errors; otherwise show an actionable error and preserve the raw response for local diagnostics without exposing secrets.
10. Include unit tests for parsing, Jira-key extraction, prompt construction, output validation, and service error mapping. Mock Jira and Ollama calls. Do not require live credentials in automated tests.
11. Provide `.env.example`, dependency metadata, local run instructions, and Vercel configuration if deployment is requested.

### C — Context

The primary user is a QA professional who wants a fast first draft of comprehensive test cases from an existing Jira requirement. Jira is the source of truth. Generated coverage should include applicable positive, negative, boundary, validation, permission, error-handling, integration, usability, accessibility, compatibility, recovery, and data-integrity scenarios.

Do not invent product behavior. Separate facts from assumptions:

- Derive every test case from a Jira requirement or a clearly labeled QA heuristic.
- Use traceability IDs such as `AC-1`, `REQ-2`, or `TS-3`.
- If necessary behavior is missing, add it to **Requirement gaps / questions** rather than silently treating it as fact.
- Do not claim unsupported UI labels, APIs, roles, limits, messages, databases, or workflows.
- Avoid duplicate cases and combine equivalent scenarios without losing meaningful coverage.

Deployment has two supported modes:

- **Local mode**: the app connects to Jira and the local Ollama endpoint, normally `http://localhost:11434`.
- **Vercel mode**: Jira can be called from the hosted app, but Vercel cannot directly call Ollama running on the user's private laptop. Require a user-configured HTTPS-reachable Ollama-compatible endpoint or secure tunnel. Never embed a tunnel URL or weaken authentication automatically.

## UI specification from the supplied design

Preserve the sketch's simple, uncluttered structure while applying accessible production styling.

### Shared shell

- Provide clearly visible navigation between **Generator** and **Settings**.
- Use a centered responsive container with generous whitespace, subtle borders, rounded corners, and readable contrast.
- Show a compact provider/connection status indicator without displaying credentials.
- On narrow screens, keep the content in one column and place **Send** below the input when necessary.

### Generator page

- The upper results panel is the primary visual element and occupies most of the available page height.
- Before a request, show a short empty state explaining that the user can enter a Jira key or URL.
- The bottom composer contains one text input plus a **Send** button. Pressing Enter and clicking **Send** perform the same action.
- Disable duplicate submission while a request is running and show progress in this order: validating input, fetching Jira, extracting requirements, generating cases, validating output.
- After Jira retrieval, show the issue key, summary, normalized description, acceptance criteria, and gaps in the results panel.
- Append generated test cases below the Jira preview. Keep long output scrollable and provide copy, Markdown download, and CSV download actions near the result.
- Preserve the last successful result while showing recoverable errors; do not clear useful output merely because a later request fails.

### Settings page

Show these primary fields in the order represented by the design:

1. **Jira email**
2. **Jira token** — masked
3. **Jira URL**
4. **Ollama URL**
5. **Groq token** — masked and labeled optional

Also expose Ollama model and optional Ollama authorization token in an **Advanced Ollama settings** expander. Keep `gemma4:e2b` as the default model.

- **Save settings** validates field shape and saves values only to the configured session or secret-storage mechanism.
- **Test Jira Connection** verifies Jira independently of the LLM.
- **Test Ollama Connection** verifies the Ollama endpoint and configured model independently of Jira.
- If Groq support is implemented, expose an explicit provider selector with **Ollama** selected by default. Never send Jira content to Groq unless the user explicitly selects Groq.
- Display success and failure messages next to the relevant connection action, not in a generic unrelated banner.

### E — Example

For a story with `AC-1: A registered user can sign in with valid credentials`, a valid generated case is:

```text
TC-1  Sign in with valid registered-user credentials  (from AC-1)  Priority: P0
  Preconditions: An active registered-user account exists.
  Test data: DATA-1 — valid registered email and password.
  Steps:
    1. Open the sign-in page -> Expected: The sign-in form is displayed.
    2. Enter DATA-1 and submit -> Expected: Authentication succeeds and the user enters the authorized area.
  Postconditions / cleanup: Sign out; leave account data unchanged.
```

If the Jira issue does not define lockout behavior, do not assert a retry limit. Report: `GAP-1: Failed-login lockout or throttling behavior is not specified.` A heuristic security test may be proposed only when labeled `QA-HEURISTIC`, with the expected result stated as requiring product confirmation.

### P — Parameters

Use these defaults unless the repository or user explicitly overrides them:

| Parameter | Default / rule |
| --- | --- |
| UI framework | Streamlit |
| Python | 3.11+ |
| Jira authentication | Jira Cloud email + API token; support bearer token when explicitly configured |
| Jira base URL | User-supplied HTTPS URL |
| Ollama base URL | `http://localhost:11434` |
| Ollama model | `gemma4:e2b` |
| Ollama token | Optional; send only when configured by the endpoint |
| Groq token | Optional cloud-provider credential; unused while Ollama is selected |
| LLM provider | Ollama by default; Groq only after explicit selection |
| Model temperature | Low and configurable; default `0.2` |
| Output mode | Structured JSON from the model, rendered as Markdown/table in the UI |
| Priorities | `P0`, `P1`, `P2`, `P3` with a visible legend |
| Network timeout | Configurable; default 60 seconds for generation and 15 seconds for connection tests |
| Retries | No automatic auth retries; at most one transient request retry and one output-repair attempt |

Treat secrets as runtime configuration. Prefer environment variables locally and Vercel environment variables when hosted. Do not commit tokens, log authorization headers, echo secrets, place them in URLs, or store them in browser-visible code. Mask secret fields and provide a clear-session action. If settings are persisted, require an explicit user choice and use an appropriate secret store; otherwise keep them session-scoped.

Suggested environment variables:

```dotenv
JIRA_BASE_URL=
JIRA_EMAIL=
JIRA_API_TOKEN=
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:e2b
OLLAMA_TOKEN=
GROQ_API_KEY=
```

### O — Output

Render a requirement summary first:

- Jira key and title
- issue metadata
- normalized description and acceptance criteria
- identified requirement statements with stable IDs
- requirement gaps / questions

Then render `## Test Cases — <feature / JIRA-KEY>` and a compact summary table with ID, title, source, type, and priority. Each detailed case must follow this exact shape:

```text
TC-1  <title>  (from TS-1, AC-1)  Priority: P0
  Preconditions: ...
  Test data: <data-set ID and values or generation rule>
  Steps:
    1. <action> -> Expected: <observable result>
    2. <action> -> Expected: <observable result>
  Postconditions / cleanup: ...
```

Every test case must contain:

- unique, deterministic ID within the result;
- concise title;
- one or more source requirement IDs, or the explicit source `QA-HEURISTIC`;
- category/type and priority;
- concrete preconditions and test data;
- numbered atomic actions with an observable expected result for every step;
- cleanup or `None` when no cleanup is needed.

Also provide:

- coverage summary by requirement and test type;
- uncovered or ambiguous requirements;
- assumptions requiring approval;
- download as Markdown and CSV; use UTF-8 and deterministic column ordering.

Before presenting results, reject or flag output when it has missing source references, duplicate IDs, invalid priorities, empty expected results, non-observable outcomes, or claims unsupported by Jira.

### T — Tonality

Keep the UI concise, professional, and QA-focused. Use plain language for errors and next actions. Test-case titles should be specific and action-oriented; expected results should be measurable and free of vague words such as “works,” “properly,” or “correctly.”

## Integration behavior

### Jira connection test

Validate the URL and credentials with a lightweight authenticated request. Distinguish invalid URL, DNS/network failure, timeout, TLS failure, unauthorized (`401`), forbidden (`403`), missing issue (`404`), rate limit (`429`), and unexpected server errors. Do not reveal raw response bodies when they may contain sensitive data.

### Ollama connection test

Verify endpoint reachability and confirm that the configured model is available. If it is missing, show the exact local remediation command:

```bash
ollama pull gemma4:e2b
```

For a remote endpoint, send the optional token using its documented authorization mechanism. Local Ollama normally requires no token; never imply that a token is mandatory.

## Definition of done

The work is complete only when:

- both pages load and navigation works;
- the Generator and Settings pages match the hierarchy and control placement of the supplied sketch;
- both connection-test actions return sanitized, useful results;
- a valid Jira key/URL retrieves and previews its issue;
- test generation produces schema-valid, traceable cases in the required format;
- gaps are separated from facts and unsupported assumptions are not presented as requirements;
- Markdown and CSV downloads work;
- secrets are absent from source, logs, browser output, and test fixtures;
- mocked automated tests pass;
- local setup is documented and deployment limitations for local Ollama are explicit.
