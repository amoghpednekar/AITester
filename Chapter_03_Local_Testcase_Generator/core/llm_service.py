from __future__ import annotations

import json

import requests

from .config import AppConfig
from .jira_service import AuthError, ConnectionFailedError, JiraError, _auth_headers, fetch_issue

OLLAMA_TAGS_PATH = "/api/tags"
OLLAMA_GENERATE_PATH = "/api/generate"


class LlmError(Exception):
    def __init__(self, message: str, category: str = "llm"):
        super().__init__(message)
        self.category = category


class ModelNotAvailableError(LlmError):
    def __init__(self, message: str, pull_command: str):
        super().__init__(message, category="model_missing")
        self.pull_command = pull_command


def _base_url(cfg: AppConfig) -> str:
    return (cfg.ollama_base_url or "http://localhost:11434").rstrip("/")


def _ollama_headers(cfg: AppConfig) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if cfg.ollama_token is not None:
        headers["Authorization"] = f"Bearer {cfg.ollama_token.get_secret_value()}"
    return headers


def test_ollama_connection(cfg: AppConfig, timeout: int | None = None) -> tuple[bool, str]:
    base = _base_url(cfg)
    timeout = timeout or cfg.connection_timeout
    try:
        resp = requests.get(
            f"{base}{OLLAMA_TAGS_PATH}",
            headers=_ollama_headers(cfg),
            timeout=timeout,
        )
    except requests.exceptions.Timeout:
        return False, f"Ollama request timed out after {timeout}s."
    except requests.exceptions.SSLError:
        return False, f"TLS error connecting to {base}."
    except requests.exceptions.ConnectionError:
        return False, f"Could not reach {base}. Is Ollama running? Try `ollama serve`."
    except requests.exceptions.RequestException as exc:
        return False, f"Request to Ollama failed: {exc}"

    if resp.status_code != 200:
        return False, f"Ollama responded with HTTP {resp.status_code}."

    try:
        models = [m.get("name", "") for m in resp.json().get("models", [])]
    except (ValueError, AttributeError):
        return False, "Ollama returned an unexpected payload."

    configured = cfg.ollama_model
    available = [m for m in models if m.split(":")[0] == configured.split(":")[0]] or [
        m for m in models if m == configured
    ]
    if not available:
        pull_command = f"ollama pull {configured}"
        return False, (
            f"Model '{configured}' is not installed on the Ollama server. "
            f"Run: {pull_command}"
        )
    return True, f"Connected to {base}. Model '{configured}' is available."


def generate_with_ollama(cfg: AppConfig, prompt: str, timeout: int | None = None) -> str:
    base = _base_url(cfg)
    payload = {
        "model": cfg.ollama_model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": cfg.temperature},
    }
    try:
        resp = requests.post(
            f"{base}{OLLAMA_GENERATE_PATH}",
            json=payload,
            headers=_ollama_headers(cfg),
            timeout=timeout or cfg.generation_timeout,
        )
    except requests.exceptions.Timeout as exc:
        raise LlmError(f"Ollama generation timed out after {timeout or cfg.generation_timeout}s.", "timeout") from exc
    except requests.exceptions.SSLError as exc:
        raise LlmError(f"TLS error connecting to {base}.", "tls") from exc
    except requests.exceptions.ConnectionError as exc:
        raise LlmError(f"Could not reach Ollama at {base}. Is it running?", "network") from exc
    except requests.exceptions.RequestException as exc:
        raise LlmError(f"Request to Ollama failed: {exc}", "network") from exc

    if resp.status_code == 404:
        raise ModelNotAvailableError(
            f"Model '{cfg.ollama_model}' was not found on the Ollama server.",
            f"ollama pull {cfg.ollama_model}",
        )
    if resp.status_code != 200:
        raise LlmError(f"Ollama generation failed with HTTP {resp.status_code}.", "http")

    try:
        data = resp.json()
    except ValueError as exc:
        raise LlmError("Ollama returned a non-JSON response.", "parse") from exc

    content = data.get("response", "")
    if not isinstance(content, str) or not content.strip():
        raise LlmError("Ollama returned an empty response.", "empty")
    return content.strip()


def generate_with_groq(cfg: AppConfig, prompt: str, timeout: int | None = None) -> str:
    if cfg.groq_api_key is None:
        raise LlmError("Groq API key is not configured.", "config")
    model = "llama-3.3-70b-versatile"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cfg.groq_api_key.get_secret_value()}",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": cfg.temperature,
        "response_format": {"type": "json_object"},
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout or cfg.generation_timeout)
    except requests.exceptions.Timeout as exc:
        raise LlmError("Groq request timed out.", "timeout") from exc
    except requests.exceptions.RequestException as exc:
        raise LlmError(f"Request to Groq failed: {exc}", "network") from exc

    if resp.status_code != 200:
        raise LlmError(f"Groq API error (HTTP {resp.status_code}).", "http")
    try:
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except (ValueError, KeyError, IndexError) as exc:
        raise LlmError("Groq returned an unexpected payload.", "parse") from exc


def generate(cfg: AppConfig, prompt: str, timeout: int | None = None) -> str:
    if cfg.provider == "groq":
        return generate_with_groq(cfg, prompt, timeout)
    return generate_with_ollama(cfg, prompt, timeout)


def generate_batched(
    cfg: AppConfig,
    prompts: list[str],
    timeout: int | None = None,
) -> list[str]:
    results: list[str] = []
    for prompt in prompts:
        results.append(generate(cfg, prompt, timeout))
    return results


def test_jira_connection(cfg: AppConfig, timeout: int | None = None) -> None:
    if not cfg.jira_base_url or not cfg.jira_email:
        raise ConnectionFailedError(
            "Jira URL and email are not configured.", category="config"
        )
    if cfg.jira_api_token is None:
        raise ConnectionFailedError("Jira API token is not configured.", category="config")

    base = cfg.jira_base_url.rstrip("/")
    url = f"{base}/rest/api/{cfg.jira_api_version}/issue/picker"
    headers = {"Accept": "application/json", **_auth_headers(cfg)}
    auth = None
    if not headers.get("Authorization"):
        auth = (cfg.jira_email, cfg.jira_api_token.get_secret_value())
    try:
        resp = requests.get(
            url,
            params={"query": ""},
            headers=headers,
            auth=auth,
            timeout=timeout or cfg.connection_timeout,
        )
    except requests.exceptions.Timeout as exc:
        raise ConnectionFailedError(
            f"Jira request timed out after {timeout or cfg.connection_timeout}s.", category="timeout"
        ) from exc
    except requests.exceptions.SSLError as exc:
        raise ConnectionFailedError(f"TLS error connecting to {cfg.jira_base_url}.", category="tls") from exc
    except requests.exceptions.ConnectionError as exc:
        raise ConnectionFailedError(
            f"Could not reach {cfg.jira_base_url}. Check the URL and your network.", category="network"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise ConnectionFailedError(f"Request to Jira failed: {exc}", category="network") from exc

    if resp.status_code == 200:
        return
    if resp.status_code in (401, 403):
        raise AuthError(
            f"Jira authentication failed ({resp.status_code}). Verify your email and API token.",
            category="auth",
            status_code=resp.status_code,
        )
    if resp.status_code == 404:
        raise JiraError("Jira connection test failed (404).", category="not_found", status_code=404)
    if resp.status_code == 429:
        raise JiraError("Jira rate limit reached (429). Wait and try again.", category="rate_limit", status_code=429)
    if resp.status_code == 410:
        raise JiraError(
            f"Jira API v{cfg.jira_api_version} is not available on this instance (410 Gone). "
            "Try setting JIRA_API_VERSION=3 in .env or the Settings page.",
            category="api_version",
            status_code=410,
        )
    raise JiraError(
        f"Jira connection test failed (HTTP {resp.status_code}).", category="unexpected", status_code=resp.status_code
    )


def test_provider_connection(cfg: AppConfig) -> tuple[bool, str]:
    if cfg.provider == "groq":
        if cfg.groq_api_key is None:
            return False, "Groq API key is not configured."
        try:
            resp = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {cfg.groq_api_key.get_secret_value()}"},
                timeout=cfg.connection_timeout,
            )
            if resp.status_code == 200:
                return True, "Connected to Groq API."
            return False, f"Groq API responded with HTTP {resp.status_code}."
        except requests.exceptions.RequestException as exc:
            return False, f"Could not reach Groq API: {exc}"
    return test_ollama_connection(cfg)
