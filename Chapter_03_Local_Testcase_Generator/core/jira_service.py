from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

import requests

from .config import AppConfig
from .schemas import AcceptanceCriterion, JiraIssue, Requirement

KEY_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{1,19}-\d+$")


class JiraError(Exception):
    def __init__(self, message: str, category: str = "unknown", status_code: int | None = None):
        super().__init__(message)
        self.category = category
        self.status_code = status_code


class InvalidKeyError(JiraError):
    def __init__(self, message: str):
        super().__init__(message, category="invalid_key")


class ConnectionFailedError(JiraError):
    def __init__(self, message: str, category: str = "network"):
        super().__init__(message, category=category)


class AuthError(JiraError):
    def __init__(self, message: str, category: str = "auth", status_code: int | None = None):
        super().__init__(message, category=category, status_code=status_code)


def parse_jira_key(raw: str) -> str:
    if not raw or not raw.strip():
        raise InvalidKeyError("Empty input. Enter a Jira issue key such as ABC-123 or a browse URL.")

    raw = raw.strip()

    if "://" in raw:
        try:
            parsed = urlparse(raw)
        except ValueError as exc:
            raise InvalidKeyError(f"Could not parse URL: {exc}") from exc
        if not parsed.scheme or not parsed.netloc:
            raise InvalidKeyError("URL is missing a scheme or host.")
        if parsed.scheme not in ("http", "https"):
            raise InvalidKeyError(f"Unsupported URL scheme '{parsed.scheme}'; use http or https.")
        path = parsed.path
        browse_match = re.search(r"(?:/browse/|/rest/api/\d+/issue/)([A-Z][A-Z0-9_]{1,19}-\d+)", path, re.IGNORECASE)
        if not browse_match:
            raise InvalidKeyError(
                "URL does not contain a Jira issue key. Expected a /browse/<KEY> or REST issue URL."
            )
        key = browse_match.group(1).upper()
    else:
        key = raw.upper()

    if not KEY_PATTERN.match(key):
        raise InvalidKeyError(
            f"'{raw}' is not a valid Jira issue key. Expected a project key and number such as ABC-123."
        )
    return key


def _auth_headers(cfg: AppConfig) -> dict[str, str]:
    if cfg.jira_api_token is None:
        return {}
    token = cfg.jira_api_token.get_secret_value()
    if token.startswith("pat-") or ":" not in f"{cfg.jira_email}:{token}":
        return {"Authorization": f"Bearer {token}"}
    return {}


def fetch_issue(key: str, cfg: AppConfig, timeout: int | None = None) -> JiraIssue:
    if not cfg.jira_base_url or not cfg.jira_email:
        raise ConnectionFailedError(
            "Jira URL and email are not configured. Open Settings and save them first.",
            category="config",
        )
    if cfg.jira_api_token is None:
        raise ConnectionFailedError(
            "Jira API token is not configured. Open Settings and save it first.",
            category="config",
        )

    base = cfg.jira_base_url.rstrip("/")
    url = f"{base}/rest/api/{cfg.jira_api_version}/issue/{key}"
    params = {
        "fields": "summary,description,issuetype,priority,status,labels,components,issuelinks"
    }
    headers = {"Accept": "application/json", **_auth_headers(cfg)}
    auth = None
    if not headers.get("Authorization"):
        auth = (cfg.jira_email, cfg.jira_api_token.get_secret_value())

    try:
        resp = requests.get(
            url,
            params=params,
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
        try:
            return _issue_from_payload(key, resp.json())
        except ValueError as exc:
            raise JiraError(f"Jira returned an unexpected payload: {exc}", category="parse") from exc

    if resp.status_code in (401, 403):
        raise AuthError(
            f"Jira authentication failed ({resp.status_code}). Verify your email and API token.",
            category="auth",
            status_code=resp.status_code,
        )
    if resp.status_code == 404:
        raise JiraError(f"Issue {key} was not found (404).", category="not_found", status_code=404)
    if resp.status_code == 429:
        raise JiraError("Jira rate limit reached (429). Wait and try again.", category="rate_limit", status_code=429)
    if resp.status_code == 410:
        raise JiraError(
            f"Jira API v{cfg.jira_api_version} is not available on this instance (410 Gone). "
            "Your instance may require a different API version — set JIRA_API_VERSION in .env "
            "or the Settings page (try 3).",
            category="api_version",
            status_code=410,
        )
    if resp.status_code >= 500:
        raise JiraError(f"Jira server error ({resp.status_code}).", category="server", status_code=resp.status_code)
    raise JiraError(f"Unexpected Jira response ({resp.status_code}).", category="unexpected", status_code=resp.status_code)


def _issue_from_payload(key: str, payload: dict[str, Any]) -> JiraIssue:
    fields = payload.get("fields", {}) if isinstance(payload, dict) else {}
    if not isinstance(fields, dict):
        raise ValueError("missing fields object")

    description_adf = fields.get("description")
    description_text = normalize_adf(description_adf) if description_adf else ""

    issue_type = fields.get("issuetype", {})
    if isinstance(issue_type, dict):
        issue_type = issue_type.get("name", "Unknown")
    priority = fields.get("priority", {})
    if isinstance(priority, dict):
        priority = priority.get("name", "Unknown")
    status = fields.get("status", {})
    if isinstance(status, dict):
        status = status.get("name", "Unknown")

    labels = fields.get("labels", []) or []
    components = fields.get("components", []) or []
    if isinstance(components, list):
        components = [
            c.get("name", "") if isinstance(c, dict) else str(c)
            for c in components
            if (c.get("name") if isinstance(c, dict) else str(c))
        ]

    acceptance_criteria = _extract_acceptance_criteria(description_text)
    linked_context = _extract_linked_context(fields.get("issuelinks", []))

    return JiraIssue(
        key=key,
        summary=fields.get("summary", "") or "",
        description=description_text,
        issue_type=issue_type,
        priority=priority,
        status=status,
        labels=[str(x) for x in labels],
        components=components,
        acceptance_criteria=acceptance_criteria,
        linked_context=linked_context,
    )


def _extract_acceptance_criteria(text: str) -> list[str]:
    criteria: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        match = re.match(r"^(?:AC[- ]?\d*[.:-]?|Acceptance [Cc]riteria?[:\- ]*)\s*(.+)$", stripped)
        if match and match.group(1).strip():
            criteria.append(match.group(1).strip())
    return criteria


def _extract_linked_context(issuelinks: list[Any]) -> str:
    if not isinstance(issuelinks, list):
        return ""
    parts: list[str] = []
    for link in issuelinks:
        if not isinstance(link, dict):
            continue
        for direction in ("outwardIssue", "inwardIssue"):
            target = link.get(direction)
            if isinstance(target, dict) and target.get("key"):
                parts.append(target["key"])
    return ", ".join(sorted(set(parts)))


def normalize_adf(adf: Any) -> str:
    if adf is None:
        return ""
    if isinstance(adf, str):
        return adf
    if isinstance(adf, list):
        return "\n".join(normalize_adf(node) for node in adf).strip()
    if not isinstance(adf, dict):
        return str(adf)

    node_type = adf.get("type", "")
    text = adf.get("text", "")

    if node_type == "table":
        rows = adf.get("content", [])
        lines: list[str] = []
        for row in rows:
            cells = [normalize_adf(cell) for cell in row.get("content", [])]
            lines.append("| " + " | ".join(cells) + " |")
        return "\n".join(lines)

    if node_type in ("bulletList", "orderedList"):
        items = [normalize_adf(item) for item in adf.get("content", [])]
        if node_type == "bulletList":
            return "\n".join(f"* {item}" for item in items if item)
        return "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1) if item)

    if node_type == "listItem":
        return normalize_adf(adf.get("content", []))

    if node_type == "heading":
        level = adf.get("attrs", {}).get("level", 1)
        inner = normalize_adf(adf.get("content", []))
        return f"{'#' * level} {inner}".strip()

    if node_type == "codeBlock":
        inner = normalize_adf(adf.get("content", []))
        return f"```\n{inner}\n```"

    if node_type == "blockquote":
        inner = normalize_adf(adf.get("content", []))
        return "\n".join(f"> {line}" for line in inner.splitlines())

    if node_type in ("paragraph", "text", "media", "emoji", "mention", "hardBreak", "rule"):
        inner = ""
        if node_type == "text":
            inner = text
        elif node_type == "mention":
            attrs = adf.get("attrs", {})
            inner = attrs.get("text") or attrs.get("id") or "@mention"
        elif node_type == "emoji":
            inner = adf.get("attrs", {}).get("shortName", "")
        elif node_type == "hardBreak":
            return "\n"
        elif node_type == "rule":
            return "---"

        content = adf.get("content", [])
        if content:
            child_parts = [normalize_adf(child) for child in content]
            child_text = " ".join(p.strip() for p in child_parts if p and p.strip())
            if inner:
                inner = f"{inner} {child_text}" if child_text else inner
            else:
                inner = child_text
        return inner.strip()

    if node_type == "panel":
        return normalize_adf(adf.get("content", []))

    content = adf.get("content", [])
    if content:
        return normalize_adf(content)
    return text or ""


def extract_requirements(issue: JiraIssue) -> list[Requirement]:
    requirements: list[Requirement] = []
    seen: set[str] = set()

    def add(statement: str) -> None:
        normalized = " ".join(statement.split()).strip()
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        requirements.append(Requirement(id=f"REQ-{len(requirements) + 1}", statement=normalized))

    if issue.summary:
        add(f"{issue.summary}.")
    if issue.acceptance_criteria:
        for i, criterion in enumerate(issue.acceptance_criteria, 1):
            add(f"AC-{i}: {criterion}")
            if criterion in seen:
                pass

    for line in issue.description.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("|"):
            continue
        if re.match(r"^AC[- ]?\d*[.:-]", stripped):
            continue
        lowered = stripped.lower()
        if any(
            marker in lowered
            for marker in (
                "as a ",
                "i want to ",
                "so that ",
                "user story",
                "requirement",
                "must be able",
                "should be able",
                "acceptance criteria",
            )
        ):
            add(stripped)

    return requirements
