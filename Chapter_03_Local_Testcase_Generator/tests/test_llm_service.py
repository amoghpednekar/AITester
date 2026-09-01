from unittest import mock

import pytest
import requests

from core.config import AppConfig
from core.llm_service import (
    LlmError,
    ModelNotAvailableError,
    generate,
    generate_with_groq,
    generate_with_ollama,
)
from core.llm_service import test_ollama_connection as check_ollama
from pydantic import SecretStr


def _mock_response(status=200, json_data=None, text=""):
    resp = mock.Mock()
    resp.status_code = status
    resp.json.return_value = json_data if json_data is not None else {}
    resp.text = text
    return resp


def test_test_ollama_connection_success(valid_config):
    resp = _mock_response(json_data={"models": [{"name": "gemma4:e2b"}, {"name": "nomic-embed-text:latest"}]})
    with mock.patch("core.llm_service.requests.get", return_value=resp):
        ok, message = check_ollama(valid_config)
    assert ok is True
    assert "gemma4:e2b" in message


def test_test_ollama_connection_model_missing(valid_config):
    resp = _mock_response(json_data={"models": [{"name": "llama3"}]})
    with mock.patch("core.llm_service.requests.get", return_value=resp):
        ok, message = check_ollama(valid_config)
    assert ok is False
    assert "ollama pull gemma4:e2b" in message


def test_test_ollama_connection_network_down(valid_config):
    with mock.patch(
        "core.llm_service.requests.get",
        side_effect=requests.exceptions.ConnectionError("refused"),
    ):
        ok, message = check_ollama(valid_config)
    assert ok is False
    assert "Could not reach" in message


def test_generate_with_ollama_returns_response(valid_config):
    resp = _mock_response(json_data={"response": '{"ok": true}'})
    with mock.patch("core.llm_service.requests.post", return_value=resp) as mocked_post:
        output = generate_with_ollama(valid_config, "prompt")
    assert output == '{"ok": true}'
    body = mocked_post.call_args.kwargs["json"]
    assert body["model"] == "gemma4:e2b"
    assert body["format"] == "json"
    assert body["options"]["temperature"] == 0.2


def test_generate_with_ollama_missing_model(valid_config):
    resp = _mock_response(status=404)
    with mock.patch("core.llm_service.requests.post", return_value=resp):
        with pytest.raises(ModelNotAvailableError) as exc:
            generate_with_ollama(valid_config, "prompt")
    assert "ollama pull gemma4:e2b" in exc.value.pull_command


def test_generate_with_ollama_timeout(valid_config):
    with mock.patch(
        "core.llm_service.requests.post",
        side_effect=requests.exceptions.Timeout("t"),
    ):
        with pytest.raises(LlmError) as exc:
            generate_with_ollama(valid_config, "prompt")
    assert exc.value.category == "timeout"


def test_generate_routes_to_ollama_by_default(valid_config):
    resp = _mock_response(json_data={"response": '{"ok": true}'})
    with mock.patch("core.llm_service.requests.post", return_value=resp):
        assert generate(valid_config, "prompt") == '{"ok": true}'


def test_generate_groq_gated_requires_key():
    cfg = AppConfig(provider="groq")
    with pytest.raises(LlmError):
        generate(cfg, "prompt")


def test_generate_with_groq_success():
    cfg = AppConfig(provider="groq", groq_api_key=SecretStr("gsk-secret"))
    resp = _mock_response(
        json_data={"choices": [{"message": {"content": '{"ok": true}'}}]}
    )
    with mock.patch("core.llm_service.requests.post", return_value=resp):
        output = generate_with_groq(cfg, "prompt")
    assert output == '{"ok": true}'


def test_provider_never_silently_switches(valid_config):
    assert valid_config.provider == "ollama"
    resp = _mock_response(json_data={"response": '{"ok": true}'})
    with mock.patch("core.llm_service.requests.post", return_value=resp):
        generate(valid_config, "prompt")
    assert valid_config.provider == "ollama"
