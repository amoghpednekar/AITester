import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import SecretStr

import pytest

from core.config import AppConfig
from core.schemas import AcceptanceCriterion, JiraIssue, Requirement


@pytest.fixture
def sample_issue() -> JiraIssue:
    return JiraIssue(
        key="VWO-49",
        summary="A registered user can sign in with valid credentials",
        description=(
            "## Overview\n"
            "The login page accepts a registered user's email and password.\n"
            "* Uses HTTPS\n"
            "* Validates email format\n"
            "AC-1: A registered user can sign in with valid credentials.\n"
            "AC-2: The page shows a validation message for invalid credentials."
        ),
        issue_type="Story",
        priority="High",
        status="In Progress",
        labels=["auth", "login"],
        components=["Frontend"],
        acceptance_criteria=[
            "A registered user can sign in with valid credentials.",
            "The page shows a validation message for invalid credentials.",
        ],
    )


@pytest.fixture
def sample_adf() -> dict:
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Overview"}]},
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "The login page accepts "},
                    {"type": "text", "text": "valid credentials", "marks": [{"type": "strong"}]},
                ],
            },
            {
                "type": "bulletList",
                "content": [
                    {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Uses HTTPS"}]}]},
                    {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Validates email format"}]}]},
                ],
            },
            {
                "type": "orderedList",
                "content": [
                    {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Enter email"}]}]},
                    {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Submit"}]}]},
                ],
            },
        ],
    }


@pytest.fixture
def valid_config() -> AppConfig:
    return AppConfig(
        jira_base_url="https://example.atlassian.net",
        jira_email="qa@example.com",
        jira_api_token=SecretStr("ATATT3secret"),
        ollama_base_url="http://localhost:11434",
        ollama_model="gemma4:e2b",
    )
