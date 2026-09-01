from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class JiraIssue(BaseModel):
    key: str
    summary: str
    description: str = ""
    issue_type: str = "Unknown"
    priority: str = "Unknown"
    status: str = "Unknown"
    labels: list[str] = Field(default_factory=list)
    components: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    linked_context: str = ""

    @field_validator("key")
    @classmethod
    def normalize_key(cls, v: str) -> str:
        return v.strip().upper()


class Requirement(BaseModel):
    id: str
    statement: str


class AcceptanceCriterion(BaseModel):
    id: str
    statement: str


class Gap(BaseModel):
    id: str
    question: str


class TestStep(BaseModel):
    action: str
    expected: str

    @field_validator("action", "expected")
    @classmethod
    def non_empty(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("step action/expected must not be empty")
        return v


class TestCase(BaseModel):
    id: str = Field(..., pattern=r"^TC-\d+$")
    title: str
    sources: list[str]
    category: str
    priority: str = Field(..., pattern=r"^P[0-3]$")
    preconditions: str
    test_data: str
    steps: list[TestStep] = Field(min_length=1)
    cleanup: str = "None"

    @field_validator("title", "preconditions", "test_data")
    @classmethod
    def non_empty(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("field must not be empty")
        return v

    @field_validator("sources")
    @classmethod
    def non_empty_sources(cls, v: list[str]) -> list[str]:
        if not v or not any(s.strip() for s in v):
            raise ValueError("at least one source required (or QA-HEURISTIC)")
        return [s.strip() for s in v if s.strip()]


class CoverageSummary(BaseModel):
    by_requirement: dict[str, int] = Field(default_factory=dict)
    by_type: dict[str, int] = Field(default_factory=dict)
    uncovered: list[str] = Field(default_factory=list)


class GenerationResult(BaseModel):
    requirements: list[Requirement] = Field(default_factory=list)
    acceptance_criteria: list[AcceptanceCriterion] = Field(default_factory=list)
    gaps: list[Gap] = Field(default_factory=list)
    test_cases: list[TestCase] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    coverage: CoverageSummary = Field(default_factory=CoverageSummary)
    raw_model_output: str = ""

    def validate_structure(self) -> list[str]:
        errors: list[str] = []
        seen: set[str] = set()
        for tc in self.test_cases:
            if tc.id in seen:
                errors.append(f"duplicate test case ID: {tc.id}")
            seen.add(tc.id)
            if tc.priority not in ("P0", "P1", "P2", "P3"):
                errors.append(f"invalid priority on {tc.id}: {tc.priority}")
            if not tc.steps:
                errors.append(f"no steps on {tc.id}")
            for step in tc.steps:
                if not step.action.strip() or not step.expected.strip():
                    errors.append(f"empty step on {tc.id}")
                    break
            valid_sources = {r.id for r in self.requirements} | {
                ac.id for ac in self.acceptance_criteria
            } | {"QA-HEURISTIC", "TS"}
            for src in tc.sources:
                if src not in valid_sources and not src.startswith("TS-"):
                    errors.append(f"unknown source {src} on {tc.id}")
        if self.raw_model_output.strip() and not self.test_cases:
            errors.append("no test cases parsed from model output")
        return errors
