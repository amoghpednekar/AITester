import json

import pytest

from core.output_parser import (
    OutputParseError,
    build_repair_payload,
    parse_output,
    parse_with_repair,
)
from core.schemas import GenerationResult


def valid_payload():
    return {
        "requirements": [{"id": "REQ-1", "statement": "A user can sign in."}],
        "acceptance_criteria": [{"id": "AC-1", "statement": "Sign in with valid creds."}],
        "gaps": [{"id": "GAP-1", "question": "Is there a lockout policy?"}],
        "test_cases": [
            {
                "id": "TC-1",
                "title": "Sign in with valid credentials",
                "sources": ["REQ-1", "AC-1"],
                "category": "positive",
                "priority": "P0",
                "preconditions": "Active account exists.",
                "test_data": "DATA-1 — valid email and password",
                "steps": [
                    {"action": "Open sign-in page", "expected": "Form is displayed."},
                    {"action": "Submit valid creds", "expected": "User enters authorized area."},
                ],
                "cleanup": "Sign out.",
            }
        ],
        "assumptions": [],
    }


def test_parse_valid_output():
    result = parse_output(json.dumps(valid_payload()))
    assert isinstance(result, GenerationResult)
    assert result.test_cases[0].id == "TC-1"
    assert result.test_cases[0].priority == "P0"


def test_parse_output_with_fenced_json():
    raw = "```json\n" + json.dumps(valid_payload()) + "\n```"
    result = parse_output(raw)
    assert result.test_cases[0].id == "TC-1"


def test_parse_output_extracts_embedded_json():
    raw = "Here you go:\n" + json.dumps(valid_payload())
    result = parse_output(raw)
    assert result.test_cases[0].id == "TC-1"


def test_parse_output_rejects_non_json():
    with pytest.raises(OutputParseError):
        parse_output("this is not json")


def test_parse_output_rejects_empty():
    with pytest.raises(OutputParseError):
        parse_output("   ")


def test_parse_output_rejects_duplicate_ids():
    payload = valid_payload()
    payload["test_cases"].append({**payload["test_cases"][0], "title": "Duplicate"})
    with pytest.raises(OutputParseError) as exc:
        parse_output(json.dumps(payload))
    assert "duplicate" in str(exc.value).lower()


def test_parse_output_rejects_invalid_priority():
    payload = valid_payload()
    payload["test_cases"][0]["priority"] = "P5"
    with pytest.raises(OutputParseError):
        parse_output(json.dumps(payload))


def test_parse_output_rejects_empty_expected():
    payload = valid_payload()
    payload["test_cases"][0]["steps"][0]["expected"] = "   "
    with pytest.raises(OutputParseError):
        parse_output(json.dumps(payload))


def test_build_repair_payload_contains_errors():
    payload = build_repair_payload("original", "bad", ["invalid priority P5"])
    assert "invalid priority P5" in payload
    assert "original" in payload
    assert "bad" in payload


def test_parse_with_repair_succeeds_on_first_try():
    def no_repair_needed(_):
        raise AssertionError("repair should not be called")

    result = parse_with_repair(json.dumps(valid_payload()), "prompt", no_repair_needed)
    assert result.test_cases[0].id == "TC-1"


def test_parse_with_repair_recovers():
    broken = json.dumps(valid_payload()).replace('"P0"', '"P9"')
    repaired = json.dumps(valid_payload())

    def repair(_payload):
        return repaired

    result = parse_with_repair(broken, "prompt", repair)
    assert result.test_cases[0].priority == "P0"


def test_parse_with_repair_fails_after_one_attempt():
    broken = json.dumps(valid_payload()).replace('"P0"', '"P9"')

    def repair(_payload):
        return broken

    with pytest.raises(OutputParseError) as exc:
        parse_with_repair(broken, "prompt", repair)
    assert "one repair attempt" in str(exc.value)


def test_parse_with_repair_sanitizes_secrets():
    broken = 'this is not json'
    secrets = ["super-secret-token"]

    def repair(_payload):
        raise OutputParseError("super-secret-token leaked here", raw_output="x")

    with pytest.raises(OutputParseError) as exc:
        parse_with_repair(broken, "prompt", repair, sanitize_secrets=secrets)
    assert "super-secret-token" not in str(exc.value)
