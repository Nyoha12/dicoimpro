from __future__ import annotations

import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = REPO_ROOT / "docs" / "RULES_IMPLEMENTATION_AUDIT_v0.2.3-auto.md"


def read_audit() -> str:
    assert AUDIT_PATH.exists(), f"Rules implementation audit is missing: {AUDIT_PATH}"
    return AUDIT_PATH.read_text(encoding="utf-8")


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return " ".join(without_accents.casefold().split())


def assert_contains_all(document: str, required_phrases: tuple[str, ...]) -> None:
    normalized_document = normalize_text(document)
    missing = [
        phrase for phrase in required_phrases if normalize_text(phrase) not in normalized_document
    ]
    assert not missing, f"Audit document is missing required text: {missing!r}"


def test_rules_implementation_audit_is_audit_not_new_doctrine() -> None:
    audit = read_audit()

    assert_contains_all(
        audit,
        (
            "Codex 023 audit-only",
            "This document is an audit",
            "It is not new doctrine",
            "does not rewrite the protocol",
            "does not create prompt bodies",
            "does not start prompt drafting",
            "does not render or load prompts",
            "does not activate OpenAI",
            "does not change runtime behavior",
        ),
    )


def test_rules_implementation_audit_covers_required_audit_areas() -> None:
    audit = read_audit()

    assert_contains_all(
        audit,
        (
            "Agent autonomy",
            "Selection / candidate handling",
            "Sources",
            "Information quality",
            "Categorization and unit type",
            "Decision and approval",
            "Archiving / traceability",
            "Current implementation coverage",
        ),
    )


def test_rules_implementation_audit_includes_status_taxonomy_and_prompt_blockers() -> None:
    audit = read_audit()

    assert_contains_all(
        audit,
        (
            "implemented",
            "partially_implemented",
            "documented_only",
            "tested_guardrail_only",
            "missing",
            "ambiguous",
            "out_of_scope_for_v0.2.3_auto",
            "Prompt-drafting blockers",
            "not found in repository evidence",
        ),
    )


def test_rules_implementation_audit_covers_current_component_coverage() -> None:
    audit = read_audit()

    assert_contains_all(
        audit,
        (
            "Pydantic contracts",
            "Orchestration",
            "Quality gates",
            "Payload validation",
            "Fake adapter",
            "OpenAIAdapter skeleton",
            "PromptPackage contracts and fixtures",
            "CLI dry-run",
            "JSON exports",
            "Docs sync tests",
            "Runtime boundary tests",
            "Prompt activation protocol",
        ),
    )


def test_rules_implementation_audit_does_not_claim_prompt_or_runtime_activation() -> None:
    audit = read_audit()
    normalized_audit = normalize_text(audit)

    assert_contains_all(
        audit,
        (
            "No real prompt exists yet",
            "No real OpenAI/runtime activation exists",
            "Real prompt storage, rendering, loading and runtime consumption are missing by design",
            "Real OpenAI integration is missing by design",
            "Codex 023 does not create that prompt draft",
        ),
    )

    forbidden_claims = (
        "prompt drafting has started",
        "a real prompt body exists",
        "real prompts exist now",
        "openai/runtime is active",
        "runtime activation is enabled",
        "prompts.py has been created",
    )
    assert not any(claim in normalized_audit for claim in forbidden_claims)
