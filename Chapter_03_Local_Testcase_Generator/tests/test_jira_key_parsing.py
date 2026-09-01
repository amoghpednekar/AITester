import pytest

from core.jira_service import InvalidKeyError, parse_jira_key


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("ABC-123", "ABC-123"),
        ("abc-123", "ABC-123"),
        ("VWO-49", "VWO-49"),
        ("https://example.atlassian.net/browse/VWO-49", "VWO-49"),
        ("https://example.atlassian.net/rest/api/2/issue/VWO-49", "VWO-49"),
        ("https://example.atlassian.net/browse/VWO-49?filter=all", "VWO-49"),
        ("https://jira.example.com:8080/browse/PROJ_1-77", "PROJ_1-77"),
    ],
)
def test_parse_valid_keys(raw, expected):
    assert parse_jira_key(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        "VWO",
        "VWO-",
        "123-ABC",
        "-123",
        "VWO-49-extra",
        "https://example.atlassian.net/browse/",
        "https://example.atlassian.net",
        "not a url",
        "https://example.atlassian.net/issues/VWO-49",
    ],
)
def test_parse_invalid_keys(raw):
    with pytest.raises(InvalidKeyError):
        parse_jira_key(raw)
