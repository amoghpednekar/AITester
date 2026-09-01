from __future__ import annotations

import json

from .schemas import JiraIssue

ANTI_HALLUCINATION_RULES = """Anti-Hallucination Rules (MANDATORY)
1. Use ONLY facts explicitly present in the Jira requirement above.
2. DO NOT invent features, APIs, error codes, UI elements, roles, limits, messages, databases, or workflows.
3. DO NOT assume default or "typical" system behavior.
4. If information is missing or unclear, do NOT guess. Add it to "gaps" as a question.
5. Every test case must be traceable to a REQ-n or AC-n id above, or explicitly labeled "QA-HEURISTIC" (in that case, mark its expected result as requiring product confirmation).
6. Never present an unsupported assumption as a fact. List assumptions separately in "assumptions".
7. Output must be deterministic and repeatable given the same input."""

SYSTEM_INSTRUCTION = """You are a senior QA engineer. Generate traceable test cases from the Jira requirement below.

Rules:
- Derive every case from the requirement facts; do not invent behavior.
- If something is unspecified, add it to "gaps" as a question, not as a fact.
- Cover positive, negative, boundary, validation, permission, error-handling, integration, usability, accessibility, compatibility, recovery, and data-integrity where applicable.
- Each step is an atomic action with an observable expected result. Avoid vague words like "works", "properly", "correctly".
- Priorities: P0 (blocker), P1 (high), P2 (medium), P3 (low).
- IDs: REQ-n, AC-n, TC-n, GAP-n, DATA-n — deterministic, no duplicates.
- Respond with STRICT JSON only, matching the schema exactly."""

OUTPUT_SCHEMA_EXAMPLE = """{
  "requirements": [{"id": "REQ-1", "statement": "..."}],
  "acceptance_criteria": [{"id": "AC-1", "statement": "..."}],
  "gaps": [{"id": "GAP-1", "question": "..."}],
  "test_cases": [
    {
      "id": "TC-1",
      "title": "...",
      "sources": ["REQ-1", "AC-1"],
      "category": "positive|negative|boundary|validation|permission|error-handling|integration|usability|accessibility|compatibility|recovery|data-integrity|security",
      "priority": "P0",
      "preconditions": "...",
      "test_data": "DATA-1 - ...",
      "steps": [{"action": "...", "expected": "..."}],
      "cleanup": "..."
    }
  ],
  "assumptions": ["..."]
}"""


def _compact_requirement(issue: JiraIssue) -> dict:
    lines = [l.strip() for l in issue.description.splitlines() if l.strip()]
    functional = [l for l in lines if l[0].isdigit() or l.startswith("*") or l.startswith("-")]

    compact = {
        "key": issue.key,
        "summary": issue.summary,
        "requirements": functional[:12],
    }
    if issue.acceptance_criteria:
        compact["acceptance_criteria"] = issue.acceptance_criteria[:10]
    if issue.issue_type:
        compact["issue_type"] = issue.issue_type
    if issue.priority:
        compact["priority"] = issue.priority
    return compact


def build_prompt(
    issue: JiraIssue,
    include_rules: bool = True,
    max_cases: int = 5,
    batch_hint: str = "",
) -> str:
    compact = _compact_requirement(issue)
    requirement_block = json.dumps(compact, ensure_ascii=False)
    rules_block = ANTI_HALLUCINATION_RULES if include_rules else ""

    batch_instruction = (
        f"\nGenerate exactly {max_cases} test cases in this batch. "
        "Keep the JSON small and complete; every opened brace must be closed."
    )
    if batch_hint:
        batch_instruction += f"\nFocus on this batch: {batch_hint}"

    return f"""{SYSTEM_INSTRUCTION}

## GOVERNING RULES
{rules_block}

## OUTPUT SCHEMA
{OUTPUT_SCHEMA_EXAMPLE}

## JIRA REQUIREMENT (source of truth)
{requirement_block}
{batch_instruction}
Generate the test cases now."""
