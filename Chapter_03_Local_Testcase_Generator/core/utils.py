from __future__ import annotations

import csv
import io
import re
from typing import Iterable

from .schemas import GenerationResult, TestCase

PRIORITY_LEGEND = {
    "P0": "Blocker — must be fixed before release",
    "P1": "High — major functionality affected",
    "P2": "Medium — standard coverage",
    "P3": "Low — edge / cosmetic",
}


def sanitize_secret_text(text: str, secrets: Iterable[str | None]) -> str:
    result = text
    for secret in secrets:
        if secret:
            result = result.replace(secret, "***")
    return result


def summarize_issue_for_prompt(issue) -> dict:
    from .schemas import JiraIssue

    if not isinstance(issue, JiraIssue):
        raise TypeError("expected JiraIssue")

    return {
        "key": issue.key,
        "summary": issue.summary,
        "description": issue.description,
        "issue_type": issue.issue_type,
        "priority": issue.priority,
        "status": issue.status,
        "labels": issue.labels,
        "components": issue.components,
        "acceptance_criteria": issue.acceptance_criteria,
        "linked_context": issue.linked_context,
    }


def render_result_markdown(result: GenerationResult, issue_key: str = "") -> str:
    lines: list[str] = []
    feature = issue_key or (result.test_cases[0].title if result.test_cases else "result")
    lines.append(f"## Test Cases — {feature}")
    if result.assumptions:
        lines.append("")
        lines.append("### Assumptions requiring approval")
        for a in result.assumptions:
            lines.append(f"- {a}")

    if result.test_cases:
        lines.append("")
        lines.append("| ID | Title | Source | Type | Priority |")
        lines.append("| --- | --- | --- | --- | --- |")
        for tc in result.test_cases:
            lines.append(
                f"| {tc.id} | {escape_md(tc.title)} | {', '.join(tc.sources)} | "
                f"{escape_md(tc.category)} | {tc.priority} |"
            )

    for tc in result.test_cases:
        lines.append("")
        lines.append(
            f"{tc.id}  {escape_md(tc.title)}  (from {', '.join(tc.sources)})  "
            f"Priority: {tc.priority}"
        )
        lines.append(f"  Preconditions: {escape_md(tc.preconditions)}")
        lines.append(f"  Test data: {escape_md(tc.test_data)}")
        lines.append("  Steps:")
        for step in tc.steps:
            lines.append(f"    1. {escape_md(step.action)} -> Expected: {escape_md(step.expected)}")
        lines.append(f"  Postconditions / cleanup: {escape_md(tc.cleanup)}")

    return "\n".join(lines)


def escape_md(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def render_result_csv(result: GenerationResult) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        ["ID", "Title", "Source", "Type", "Priority", "Preconditions", "Test data", "Steps", "Cleanup"]
    )
    for tc in result.test_cases:
        steps = "; ".join(f"{s.action} -> {s.expected}" for s in tc.steps)
        writer.writerow(
            [
                tc.id,
                tc.title,
                ", ".join(tc.sources),
                tc.category,
                tc.priority,
                tc.preconditions,
                tc.test_data,
                steps,
                tc.cleanup,
            ]
        )
    return buf.getvalue()


def deterministic_id(prefix: str, index: int) -> str:
    return f"{prefix}-{index}"
