from __future__ import annotations

import json
import re

from .schemas import AcceptanceCriterion, CoverageSummary, Gap, GenerationResult, Requirement
from .utils import sanitize_secret_text


class OutputParseError(Exception):
    def __init__(self, message: str, raw_output: str = "", repair_payload: str = ""):
        super().__init__(message)
        self.raw_output = raw_output
        self.repair_payload = repair_payload


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    raise OutputParseError("Model output was not valid JSON.", raw_output=text)


def parse_output(raw: str) -> GenerationResult:
    if not raw or not raw.strip():
        raise OutputParseError("Model returned an empty response.", raw_output=raw or "")

    try:
        data = _extract_json(raw)
    except OutputParseError as exc:
        raise exc

    try:
        result = GenerationResult.model_validate(data)
    except Exception as exc:  # pydantic ValidationError etc.
        raise OutputParseError(
            f"Output did not match the required schema: {exc}", raw_output=raw
        ) from exc

    errors = result.validate_structure()
    if errors:
        raise OutputParseError(
            "Output validation failed: " + "; ".join(errors), raw_output=raw
        )

    result.raw_model_output = raw
    return result


def build_repair_payload(original_prompt: str, raw_output: str, errors: list[str]) -> str:
    return f"""{original_prompt}

Your previous response failed validation with these errors:
{chr(10).join('- ' + e for e in errors)}

Return the corrected STRICT JSON only. Do not add commentary or markdown fences.
Your previous (invalid) output was:
{raw_output}"""


def merge_results(results: list[GenerationResult]) -> GenerationResult:
    combined = GenerationResult(
        requirements=[],
        acceptance_criteria=[],
        gaps=[],
        test_cases=[],
        assumptions=[],
        coverage=CoverageSummary(),
        raw_model_output="\n".join(r.raw_model_output for r in results),
    )
    seen_req: set[str] = set()
    seen_ac: set[str] = set()
    seen_gap: set[str] = set()
    seen_tc: set[str] = set()
    next_req = 1
    next_ac = 1
    next_gap = 1
    next_tc = 1

    for result in results:
        for req in result.requirements:
            if req.statement in seen_req:
                continue
            seen_req.add(req.statement)
            combined.requirements.append(Requirement(id=f"REQ-{next_req}", statement=req.statement))
            next_req += 1
        for ac in result.acceptance_criteria:
            if ac.statement in seen_ac:
                continue
            seen_ac.add(ac.statement)
            combined.acceptance_criteria.append(
                AcceptanceCriterion(id=f"AC-{next_ac}", statement=ac.statement)
            )
            next_ac += 1
        for gap in result.gaps:
            if gap.question in seen_gap:
                continue
            seen_gap.add(gap.question)
            combined.gaps.append(Gap(id=f"GAP-{next_gap}", question=gap.question))
            next_gap += 1
        for tc in result.test_cases:
            if tc.title in seen_tc:
                continue
            seen_tc.add(tc.title)
            combined.test_cases.append(tc.model_copy(update={"id": f"TC-{next_tc}"}))
            next_tc += 1
        combined.assumptions.extend(a for a in result.assumptions if a not in combined.assumptions)

    return combined


def _parse_with_diagnostics(raw: str) -> tuple[GenerationResult | None, list[str]]:
    try:
        return parse_output(raw), []
    except OutputParseError as exc:
        if hasattr(exc, "raw_output") and exc.raw_output:
            return None, [str(exc)]
        return None, [str(exc)]


def parse_with_repair(
    raw: str,
    prompt: str,
    repair_fn,
    sanitize_secrets: list[str | None] | None = None,
) -> GenerationResult:
    try:
        return parse_output(raw)
    except OutputParseError as first_error:
        sanitize_secrets = sanitize_secrets or []
        first_message = str(first_error)

        try:
            repaired_raw = repair_fn(build_repair_payload(prompt, raw, [first_message]))
        except OutputParseError as repair_error:
            combined = sanitize_secret_text(
                f"Generation failed during repair.\n"
                f"Original error: {first_message}\n"
                f"Repair error: {repair_error}",
                sanitize_secrets,
            )
            raise OutputParseError(combined, raw_output=raw) from repair_error
        try:
            return parse_output(repaired_raw)
        except OutputParseError as second_error:
            combined = (
                f"Generation failed after one repair attempt.\n"
                f"Original error: {first_message}\n"
                f"Repair error: {second_error}"
            )
            combined = sanitize_secret_text(combined, sanitize_secrets)
            raise OutputParseError(combined, raw_output=raw) from second_error


def diagnostics_from_result(result: GenerationResult) -> list[str]:
    issues: list[str] = []
    seen: set[str] = set()
    for tc in result.test_cases:
        if tc.id in seen:
            issues.append(f"duplicate ID {tc.id}")
        seen.add(tc.id)
        if tc.priority not in ("P0", "P1", "P2", "P3"):
            issues.append(f"invalid priority {tc.priority} on {tc.id}")
        if not tc.steps:
            issues.append(f"no steps on {tc.id}")
    return issues
