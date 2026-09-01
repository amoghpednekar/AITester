# Jira Test Case Generator

A two-page Python web application that retrieves an authorized Jira issue and generates
**grounded, traceable QA test cases** using the local Ollama model `gemma4:e2b`.

Built from `SKILL.md` in this folder. It follows the repository's
[anti-hallucination rule base](../Chapter_01_LLM_basics/Antihallucination.rules.md):
every test case is derived from verified Jira facts; anything unspecified is reported as a
**Requirement gap / question** rather than invented.

## Features

- **Generator page** — enter a Jira key (`VWO-49`) or browse URL, preview the fetched requirement
  (summary, normalized description, acceptance criteria, gaps), then generate test cases.
- **Settings page** — Jira email / token / URL, Ollama URL, optional Groq key; save settings
  (session-scoped only), **Test Jira Connection** and **Test Ollama Connection** actions.
- **Traceable output** — test cases carry IDs (`TC-1`), source references (`REQ-1`, `AC-1`),
  priorities (`P0`–`P3`), atomic steps with observable expected results, and cleanup.
- **Downloads** — Markdown and CSV export of the generated suite.
- **Anti-hallucination** — the prompt embeds the repo's governing rules; missing behavior becomes a
  `GAP-n` question, never a fabricated test.
- **Repair-on-validation** — model output is parsed into a typed schema; on failure the app makes at
  most one repair request, then shows an actionable error while preserving the raw output locally.
- **Provider safety** — Ollama is the default. Groq is optional and is **never** used unless you
  explicitly select it in Settings.

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) running locally, with the model pulled:

```bash
ollama pull gemma4:e2b
```

- A Jira Cloud account with an **API token**
  ([create one here](https://id.atlassian.com/manage-profile/security/api-tokens)).

## Local setup

```bash
cd Chapter_03_Local_Testcase_Generator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # optional; you can also enter settings in the UI
streamlit run app.py
```

Open the printed URL (default `http://localhost:5000`). Go to **Settings**, enter your Jira
email/token/URL, and use **Test Jira Connection** and **Test Ollama Connection** to verify both
backends.

## Configuration

Settings entered in the UI are kept for the current browser session only and are never written to
disk. Secrets are masked in the UI and never logged. Environment variables (`.env`) are the
recommended way to persist configuration for repeated local runs:

```dotenv
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=you@company.com
JIRA_API_TOKEN=ATATT3...
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:e2b
OLLAMA_TOKEN=
GROQ_API_KEY=
LLM_PROVIDER=ollama
```

### Connection tests

- **Test Jira Connection** performs a lightweight authenticated request and distinguishes invalid
  URL, network/TLS, timeout, 401/403, 404, 429, and server errors. Raw response bodies are never
  shown.
- **Test Ollama Connection** checks the endpoint via `/api/tags` and confirms the configured model
  is installed. If the model is missing it prints the exact remediation command:
  `ollama pull gemma4:e2b`.

## Tests

All tests are mocked — no live credentials are required:

```bash
cd Chapter_03_Local_Testcase_Generator
.venv/bin/python -m pytest tests/ -v
```

Covers Jira key parsing, ADF normalization, requirement extraction, error mapping, prompt
construction, output validation (valid / invalid / one-repair / unrecoverable), and the LLM service
including Groq gating.

## Deployment (Vercel)

`vercel.json` and `runtime.txt` are provided for a Python deployment. **Important limitation:**
Vercel cannot reach Ollama running on your private laptop (`localhost`). For hosted use you must
either:

- point `OLLAMA_BASE_URL` at a user-configured, HTTPS-reachable Ollama-compatible endpoint or secure
  tunnel, and set any required token yourself, or
- select **Groq** as the provider in Settings with your own Groq API key.

The app will never embed a tunnel URL or weaken authentication automatically.
