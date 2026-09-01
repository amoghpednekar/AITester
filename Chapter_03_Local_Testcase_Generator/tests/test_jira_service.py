from unittest import mock

import pytest
import requests

from core.config import AppConfig
from core.jira_service import (
    AuthError,
    ConnectionFailedError,
    InvalidKeyError,
    JiraError,
    extract_requirements,
    fetch_issue,
    normalize_adf,
)
from core.schemas import JiraIssue


def test_normalize_adf_headings_lists_and_text(sample_adf):
    text = normalize_adf(sample_adf)
    assert "## Overview" in text
    assert "The login page accepts valid credentials" in text
    assert "Uses HTTPS" in text
    assert "1. Enter email" in text


def test_normalize_adf_plain_string_passthrough():
    assert normalize_adf("plain text") == "plain text"


def test_normalize_adf_none():
    assert normalize_adf(None) == ""


def test_extract_requirements_from_issue(sample_issue):
    reqs = extract_requirements(sample_issue)
    ids = [r.id for r in reqs]
    assert "REQ-1" in ids
    assert any("AC-1" in r.statement for r in reqs)
    assert any("AC-2" in r.statement for r in reqs)
    assert len(reqs) == len(set(r.id for r in reqs))


def test_fetch_issue_success(valid_config):
    payload = {
        "key": "VWO-49",
        "fields": {
            "summary": "Login works",
            "description": None,
            "issuetype": {"name": "Story"},
            "priority": {"name": "High"},
            "status": {"name": "Open"},
            "labels": ["auth"],
            "components": [{"name": "Frontend"}],
            "issuelinks": [],
        },
    }
    with mock.patch("core.jira_service.requests.get") as mocked_get:
        mocked_get.return_value = mock.Mock(status_code=200, json=lambda: payload)
        issue = fetch_issue("VWO-49", valid_config)
    assert issue.key == "VWO-49"
    assert issue.summary == "Login works"
    assert issue.labels == ["auth"]
    assert issue.components == ["Frontend"]


def test_fetch_issue_unauthorized(valid_config):
    with mock.patch("core.jira_service.requests.get") as mocked_get:
        mocked_get.return_value = mock.Mock(status_code=401, json=lambda: {})
        with pytest.raises(AuthError):
            fetch_issue("VWO-49", valid_config)


def test_fetch_issue_not_found(valid_config):
    with mock.patch("core.jira_service.requests.get") as mocked_get:
        mocked_get.return_value = mock.Mock(status_code=404, json=lambda: {})
        with pytest.raises(JiraError) as exc_info:
            fetch_issue("VWO-49", valid_config)
    assert exc_info.value.status_code == 404


def test_fetch_issue_rate_limited(valid_config):
    with mock.patch("core.jira_service.requests.get") as mocked_get:
        mocked_get.return_value = mock.Mock(status_code=429, json=lambda: {})
        with pytest.raises(JiraError) as exc_info:
            fetch_issue("VWO-49", valid_config)
    assert exc_info.value.category == "rate_limit"


def test_fetch_issue_network_error(valid_config):
    with mock.patch("core.jira_service.requests.get", side_effect=requests.exceptions.ConnectionError("boom")):
        with pytest.raises(ConnectionFailedError):
            fetch_issue("VWO-49", valid_config)


def test_fetch_issue_missing_config():
    cfg = AppConfig(jira_base_url=None, jira_email=None)
    with pytest.raises(ConnectionFailedError):
        fetch_issue("VWO-49", cfg)


def test_acceptance_criteria_extracted_from_adf_text():
    from core.jira_service import _extract_acceptance_criteria

    text = "AC-1: A registered user can sign in.\nAC-2: Invalid login shows an error."
    assert _extract_acceptance_criteria(text) == [
        "A registered user can sign in.",
        "Invalid login shows an error.",
    ]
