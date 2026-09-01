import pytest

from core.config import AppConfig, ValidationError
from core.schemas import GenerationResult, TestCase, TestStep


def test_config_from_env():
    cfg = AppConfig.from_env(
        {
            "JIRA_BASE_URL": "https://x.atlassian.net",
            "JIRA_EMAIL": "a@b.com",
            "JIRA_API_TOKEN": "tok",
            "OLLAMA_BASE_URL": "http://localhost:11434",
            "OLLAMA_MODEL": "gemma4:e2b",
            "LLM_PROVIDER": "ollama",
        }
    )
    assert cfg.jira_email == "a@b.com"
    assert cfg.ollama_model == "gemma4:e2b"
    assert cfg.provider == "ollama"


def test_config_defaults():
    cfg = AppConfig()
    assert cfg.ollama_base_url == "http://localhost:11434"
    assert cfg.ollama_model == "gemma4:e2b"
    assert cfg.provider == "ollama"
    assert cfg.temperature == 0.2


def test_config_validate_requires_jira():
    cfg = AppConfig()
    errors = cfg.validate()
    assert any("Jira" in e for e in errors)


def test_config_validate_ollama_url():
    cfg = AppConfig(jira_base_url="https://x.atlassian.net", jira_email="a@b.com", jira_api_token="t")
    cfg.ollama_base_url = "not-a-url"
    errors = cfg.validate()
    assert any("Ollama" in e for e in errors)


def test_config_rejects_invalid_provider():
    cfg = AppConfig(provider="openai")
    errors = cfg.validate()
    assert any("Provider" in e for e in errors)


def test_config_groq_requires_key():
    cfg = AppConfig(jira_base_url="https://x.atlassian.net", jira_email="a@b.com", jira_api_token="t", provider="groq")
    errors = cfg.validate_for_groq()
    assert any("Groq" in e for e in errors)


def test_secret_hidden_in_to_dict():
    from pydantic import SecretStr

    cfg = AppConfig(
        jira_api_token=SecretStr("tok"),
        ollama_token=SecretStr("o-tok"),
        groq_api_key=SecretStr("g-tok"),
    )
    d = cfg.to_dict(hide_secrets=True)
    assert d["jira_api_token"] == ""
    assert d["ollama_token"] == ""
    assert d["groq_api_key"] == ""
    assert "raw_last_error" not in d


def test_generation_result_validate_structure_detects_duplicates():
    tc = TestCase(
        id="TC-1",
        title="t",
        sources=["REQ-1"],
        category="positive",
        priority="P0",
        preconditions="p",
        test_data="d",
        steps=[TestStep(action="a", expected="e")],
    )
    result = GenerationResult(test_cases=[tc, tc])
    errors = result.validate_structure()
    assert any("duplicate" in e for e in errors)
