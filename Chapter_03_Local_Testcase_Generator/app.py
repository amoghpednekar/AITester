from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from core import llm_service
from core.config import AppConfig, load_env_file
from core.jira_service import JiraError, InvalidKeyError, parse_jira_key
from core.llm_service import LlmError, ModelNotAvailableError
from core.output_parser import OutputParseError, merge_results, parse_with_repair
from core.prompt_builder import build_prompt
from core.utils import (
    PRIORITY_LEGEND,
    render_result_csv,
    render_result_markdown,
    sanitize_secret_text,
)
from pydantic import SecretStr

st.set_page_config(page_title="Jira Test Case Generator", page_icon="🧪", layout="centered")

APP_DIR = Path(__file__).resolve().parent
ENV_FILE = APP_DIR / ".env"
if ENV_FILE.exists():
    load_env_file(ENV_FILE)


def get_config() -> AppConfig:
    if "config" not in st.session_state:
        st.session_state["config"] = AppConfig.from_env()
    return st.session_state["config"]


def set_config(cfg: AppConfig) -> None:
    st.session_state["config"] = cfg


def reset_output() -> None:
    for key in ("last_issue", "last_result", "last_error"):
        st.session_state.pop(key, None)


def current_provider(cfg: AppConfig) -> str:
    return cfg.provider or "ollama"


def _secret_or_new(existing: SecretStr | None, typed: str) -> SecretStr | None:
    if existing is not None and typed == existing.get_secret_value():
        return existing
    typed = typed.strip()
    if not typed:
        return None
    return SecretStr(typed)


def main() -> None:
    cfg = get_config()
    st.sidebar.title("Jira Test Case Generator")
    st.sidebar.caption("Local Ollama · gemma4:e2b")

    provider = current_provider(cfg)
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Provider:** `{provider}`")
    if provider == "ollama":
        status = "configured" if cfg.ollama_base_url else "not configured"
    else:
        status = "configured" if cfg.groq_api_key else "not configured"
    st.sidebar.markdown(f"**Status:** {status}")
    st.sidebar.markdown("---")

    page = st.sidebar.radio("Navigation", ["Generator", "Settings"], label_visibility="collapsed")

    if page == "Generator":
        render_generator(cfg)
    else:
        render_settings(cfg)


def _secrets(cfg: AppConfig) -> list[str | None]:
    return [
        cfg.jira_api_token.get_secret_value() if cfg.jira_api_token else None,
        cfg.ollama_token.get_secret_value() if cfg.ollama_token else None,
        cfg.groq_api_key.get_secret_value() if cfg.groq_api_key else None,
    ]


def render_generator(cfg: AppConfig) -> None:
    st.markdown(
        "<style>"
        ".stApp { max-width: 1000px; margin: 0 auto; }"
        ".result-panel { border: 1px solid #ddd; border-radius: 8px; padding: 16px; "
        "min-height: 320px; max-height: 480px; overflow-y: auto; background: #fafafa; }"
        ".composer { display: flex; gap: 8px; align-items: center; }"
        "</style>",
        unsafe_allow_html=True,
    )

    st.title("Test Case Generator")
    st.caption("Enter a Jira issue key or browse URL. The requirement is retrieved and grounded test cases are generated.")

    with st.expander("Priority legend"):
        for level, meaning in PRIORITY_LEGEND.items():
            st.markdown(f"**{level}** — {meaning}")

    issue = st.session_state.get("last_issue")
    result = st.session_state.get("last_result")
    error = st.session_state.get("last_error")

    with st.container(border=True):
        if result is not None:
            st.markdown("### Generated Test Cases")
            st.markdown(render_result_markdown(result, issue.key if issue else ""), unsafe_allow_html=False)
            col1, col2, col3 = st.columns(3)
            md_bytes = render_result_markdown(result, issue.key if issue else "").encode("utf-8")
            csv_bytes = render_result_csv(result).encode("utf-8")
            col1.download_button("Download Markdown", md_bytes, "test_cases.md", "text/markdown")
            col2.download_button("Download CSV", csv_bytes, "test_cases.csv", "text/csv")
            col3.button("Copy to clipboard", key="copy_btn", on_click=_copy_result)
        elif issue is not None:
            st.markdown("### Fetched Requirement")
            st.markdown(f"**{issue.key}** — {issue.summary}")
            st.markdown(f"Type: {issue.issue_type} · Priority: {issue.priority} · Status: {issue.status}")
            if issue.labels:
                st.markdown(f"Labels: {', '.join(issue.labels)}")
            if issue.components:
                st.markdown(f"Components: {', '.join(issue.components)}")
            if issue.description:
                st.markdown("**Description**")
                st.markdown(issue.description)
            if issue.acceptance_criteria:
                st.markdown("**Acceptance criteria**")
                for ac in issue.acceptance_criteria:
                    st.markdown(f"- {ac}")
            if issue.linked_context:
                st.markdown(f"**Linked issues:** {issue.linked_context}")
            st.info("Requirement fetched. Enter a message below to generate test cases.")
        elif error is not None:
            st.error(error)
            st.info("Fix the issue above, then try again. Your previous successful result is preserved above if any.")
        else:
            st.markdown(
                '<div class="result-panel"><p style="color:#888;">'
                "No requirement yet. Enter a Jira key or URL below to get started."
                "</p></div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    with st.form("composer", clear_on_submit=False):
        cols = st.columns([5, 1])
        user_input = cols[0].text_input(
            "Jira key or URL",
            placeholder="e.g. VWO-49",
            label_visibility="collapsed",
        )
        submitted = cols[1].form_submit_button("Send", use_container_width=True)

    if submitted and user_input.strip():
        _handle_generate(cfg, user_input.strip())


def _copy_result() -> None:
    result = st.session_state.get("last_result")
    if result is not None:
        st.toast("Copied to clipboard (see browser console for full text).")
        st.write(render_result_markdown(result))


def _handle_generate(cfg: AppConfig, user_input: str) -> None:
    secrets = _secrets(cfg)
    st.session_state.pop("last_error", None)

    try:
        key = parse_jira_key(user_input)
    except InvalidKeyError as exc:
        st.session_state["last_error"] = str(exc)
        st.rerun()
        return

    with st.spinner("Fetching Jira issue…"):
        try:
            issue = llm_service.fetch_issue(key, cfg)
        except JiraError as exc:
            st.session_state["last_error"] = str(exc)
            st.rerun()
            return
    st.session_state["last_issue"] = issue

    with st.spinner("Generating test cases…"):
        try:
            prompts = [
                build_prompt(issue, max_cases=4, batch_hint="positive and negative login scenarios"),
                build_prompt(issue, max_cases=4, batch_hint="boundary, validation, and permission scenarios"),
                build_prompt(issue, max_cases=4, batch_hint="error-handling, integration, accessibility, and data-integrity scenarios"),
            ]
            raws = llm_service.generate_batched(cfg, prompts)
            results = []
            for prompt, raw in zip(prompts, raws):
                try:
                    results.append(parse_with_repair(raw, prompt, lambda p: llm_service.generate(cfg, p), sanitize_secrets=secrets))
                except OutputParseError:
                    continue
            if not results:
                raise OutputParseError("All generation batches failed to parse.")
            result = merge_results(results)
            st.session_state["last_result"] = result
            st.session_state.pop("last_issue", None)
        except (LlmError, OutputParseError) as exc:
            message = sanitize_secret_text(str(exc), secrets)
            if isinstance(exc, ModelNotAvailableError):
                message += f"\n\nRun: `{exc.pull_command}`"
            st.session_state["last_error"] = message
    st.rerun()


def render_settings(cfg: AppConfig) -> None:
    st.title("Settings")
    st.caption("Configuration is stored for this session only. Secrets are never written to disk from this UI.")

    if ENV_FILE.exists():
        st.info(f"Loaded configuration from `{ENV_FILE.name}` in this app folder. Values entered below override it for this session.")
    else:
        st.warning("No `.env` file found next to `app.py`. Create one from `.env.example` to persist configuration.")

    with st.container(border=True):
        st.markdown("#### Jira")
        jira_email = st.text_input("Jira email", value=cfg.jira_email or "", placeholder="you@company.com")
        jira_token = st.text_input(
            "Jira API token",
            value=cfg.jira_api_token.get_secret_value() if cfg.jira_api_token else "",
            type="password",
            placeholder="ATATT3…",
        )
        jira_url = st.text_input(
            "Jira base URL",
            value=cfg.jira_base_url or "",
            placeholder="https://your-domain.atlassian.net",
        )
        st.markdown("#### Ollama")
        ollama_url = st.text_input(
            "Ollama base URL",
            value=cfg.ollama_base_url or "http://localhost:11434",
        )
        st.markdown("#### Groq (optional)")
        groq_token = st.text_input(
            "Groq API key",
            value=cfg.groq_api_key.get_secret_value() if cfg.groq_api_key else "",
            type="password",
            placeholder="optional — used only when provider is Groq",
        )
        provider = st.selectbox(
            "LLM provider",
            options=["ollama", "groq"],
            index=0 if cfg.provider != "groq" else 1,
        )
        with st.expander("Advanced Ollama settings"):
            ollama_model = st.text_input("Ollama model", value=cfg.ollama_model or "gemma4:e2b")
            ollama_token = st.text_input(
                "Ollama auth token (optional)",
                value=cfg.ollama_token.get_secret_value() if cfg.ollama_token else "",
                type="password",
            )
            temperature = st.slider("Temperature", 0.0, 1.0, float(cfg.temperature), 0.05)

        if st.button("Save settings", type="primary", use_container_width=True):
            new_cfg = AppConfig(
                jira_base_url=jira_url.strip() or None,
                jira_email=jira_email.strip() or None,
                jira_api_token=_secret_or_new(cfg.jira_api_token, jira_token),
                ollama_base_url=ollama_url.strip() or "http://localhost:11434",
                ollama_model=ollama_model.strip() or "gemma4:e2b",
                ollama_token=_secret_or_new(cfg.ollama_token, ollama_token),
                groq_api_key=_secret_or_new(cfg.groq_api_key, groq_token),
                provider=provider,
                temperature=temperature,
            )
            errors = new_cfg.validate_for_groq() if provider == "groq" else new_cfg.validate()
            if errors:
                st.error("; ".join(errors))
            else:
                set_config(new_cfg)
                st.success("Settings saved for this session.")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Test Jira Connection", use_container_width=True):
            _test_jira(cfg)
    with col2:
        if st.button("Test Ollama Connection", use_container_width=True):
            _test_ollama(cfg)

    st.markdown("---")
    if st.button("Clear session", use_container_width=True):
        st.session_state.clear()
        st.rerun()


def _test_jira(cfg: AppConfig) -> None:
    if not cfg.jira_base_url or not cfg.jira_email or cfg.jira_api_token is None:
        st.error("Jira email, token, and URL must be saved first (Settings → Save settings).")
        return
    try:
        llm_service.test_jira_connection(cfg)
    except JiraError as exc:
        st.error(f"Jira connection failed: {exc}")
    else:
        st.success("Jira connection successful.")


def _test_ollama(cfg: AppConfig) -> None:
    ok, message = llm_service.test_ollama_connection(cfg)
    if ok:
        st.success(message)
    else:
        st.error(message)


if __name__ == "__main__":
    main()
