from core.prompt_builder import (
    ANTI_HALLUCINATION_RULES,
    OUTPUT_SCHEMA_EXAMPLE,
    SYSTEM_INSTRUCTION,
    build_prompt,
)


def test_prompt_contains_issue_facts(sample_issue):
    prompt = build_prompt(sample_issue)
    assert sample_issue.key in prompt
    assert sample_issue.summary in prompt
    assert "VWO-49" in prompt
    assert "AC-1" in prompt


def test_prompt_contains_anti_hallucination_rules(sample_issue):
    prompt = build_prompt(sample_issue)
    assert "Anti-Hallucination" in prompt
    assert "traceable" in prompt.lower()


def test_prompt_instructs_strict_json(sample_issue):
    prompt = build_prompt(sample_issue)
    assert "STRICT JSON" in prompt
    assert "test_cases" in prompt


def test_prompt_optional_rules_flag(sample_issue):
    prompt = build_prompt(sample_issue, include_rules=False)
    assert "Anti-Hallucination" not in prompt


def test_system_instruction_defines_schema():
    assert '"id": "TC-1"' in OUTPUT_SCHEMA_EXAMPLE
    assert '"steps": [{"action": "...", "expected": "..."}]' in OUTPUT_SCHEMA_EXAMPLE
