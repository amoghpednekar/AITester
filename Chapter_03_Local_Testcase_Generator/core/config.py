from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr

GENERATION_TIMEOUT_SECONDS = 60
CONNECTION_TIMEOUT_SECONDS = 15
DEFAULT_TEMPERATURE = 0.2

VALID_PROVIDERS = ("ollama", "groq")
VALID_PRIORITIES = ("P0", "P1", "P2", "P3")


def load_env_file(path: str | Path | None = None) -> None:
    load_dotenv(dotenv_path=path, override=False)


class ValidationError(Exception):
    pass


def _as_secret(value: str | None) -> SecretStr | None:
    if value is None or value.strip() == "":
        return None
    return SecretStr(value.strip())


@dataclass
class AppConfig:
    jira_base_url: str | None = None
    jira_email: str | None = None
    jira_api_token: SecretStr | None = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma4:e2b"
    ollama_token: SecretStr | None = None
    groq_api_key: SecretStr | None = None
    provider: str = "ollama"
    temperature: float = DEFAULT_TEMPERATURE
    generation_timeout: int = GENERATION_TIMEOUT_SECONDS
    connection_timeout: int = CONNECTION_TIMEOUT_SECONDS
    jira_api_version: int = 3
    raw_last_error: str | None = field(default=None, repr=False)

    def to_dict(self, hide_secrets: bool = False) -> dict:
        def _val(value):
            if isinstance(value, SecretStr):
                return "" if hide_secrets else value.get_secret_value()
            return value

        return {k: _val(v) for k, v in self.__dict__.items() if k != "raw_last_error"}

    @classmethod
    def from_env(cls, env=None) -> "AppConfig":
        env = env if env is not None else os.environ
        return cls(
            jira_base_url=env.get("JIRA_BASE_URL") or None,
            jira_email=env.get("JIRA_EMAIL") or None,
            jira_api_token=_as_secret(env.get("JIRA_API_TOKEN")),
            ollama_base_url=env.get("OLLAMA_BASE_URL") or "http://localhost:11434",
            ollama_model=env.get("OLLAMA_MODEL") or "gemma4:e2b",
            ollama_token=_as_secret(env.get("OLLAMA_TOKEN")),
            groq_api_key=_as_secret(env.get("GROQ_API_KEY")),
            provider=(env.get("LLM_PROVIDER") or "ollama").lower(),
            jira_api_version=int(env.get("JIRA_API_VERSION") or 3),
        )

    def validate(self, require_jira: bool = True) -> list[str]:
        errors: list[str] = []
        if not self.jira_base_url or "://" not in self.jira_base_url:
            errors.append("Jira URL must be a full https:// URL.")
        elif not self.jira_base_url.lower().startswith("https://"):
            errors.append("Jira URL must use https://.")
        if require_jira and not self.jira_email:
            errors.append("Jira email is required.")
        if require_jira and not self.jira_api_token:
            errors.append("Jira API token is required.")
        if not self.ollama_base_url or "://" not in self.ollama_base_url:
            errors.append("Ollama URL must be a full URL.")
        if not self.ollama_model:
            errors.append("Ollama model is required.")
        if self.provider not in VALID_PROVIDERS:
            errors.append(f"Provider must be one of {', '.join(VALID_PROVIDERS)}.")
        if not (0.0 <= self.temperature <= 1.0):
            errors.append("Temperature must be between 0 and 1.")
        return errors

    def validate_for_groq(self) -> list[str]:
        errors = self.validate(require_jira=True)
        if not self.groq_api_key:
            errors.append("Groq API key is required when provider is Groq.")
        return errors
