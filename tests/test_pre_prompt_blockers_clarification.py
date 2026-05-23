from __future__ import annotations

import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLARIFICATION_PATH = (
    REPO_ROOT / "docs" / "PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md"
)
PROMPT_DRAFT_DIR = REPO_ROOT / "docs" / "prompts" / "drafts"
PROMPTS_MODULE = REPO_ROOT / "src" / "dico_impro" / "agents" / "prompts.py"


def read_clarification() -> str:
    assert CLARIFICATION_PATH.exists(), (
        f"Pre-prompt blockers clarification is missing: {CLARIFICATION_PATH}"
    )
    return CLARIFICATION_PATH.read_text(encoding="utf-8")


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
    assert not missing, f"Clarification document is missing required text: {missing!r}"


def test_pre_prompt_clarification_exists_and_is_no_runtime_effect() -> None:
    clarification = read_clarification()

    assert_contains_all(
        clarification,
        (
            "Codex 024 clarification-only",
            "pre-prompt",
            "no runtime effect",
            "does not create a prompt",
            "does not start prompt drafting",
            "does not create a prompt body",
            "does not render or load prompts",
            "does not activate OpenAI",
            "does not change runtime behavior",
            "No real prompt exists yet",
            "No real OpenAI/runtime activation exists",
        ),
    )


def test_pre_prompt_clarification_references_audit_and_prompt_protocol() -> None:
    clarification = read_clarification()

    assert_contains_all(
        clarification,
        (
            "RULES_IMPLEMENTATION_AUDIT_v0.2.3-auto.md",
            "PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md",
            "Codex 023 identified four ambiguity families",
            "does not change the prompt lifecycle",
            "No prompt may be consumed by `OpenAIAdapter` or CLI dry-run",
        ),
    )


def test_pre_prompt_clarification_covers_four_blocker_families() -> None:
    clarification = read_clarification()

    assert_contains_all(
        clarification,
        (
            "Attested fact vs hypothesis",
            "Source status mapping",
            "hors_perimetre vs controle_perimetre",
            "Unified decision readiness semantics",
        ),
    )


def test_each_blocker_family_uses_required_review_template() -> None:
    clarification = read_clarification()

    required_phrases = (
        "Existing ambiguity",
        "Clarification proposed from existing doctrine",
        "Affected future agents",
        "Effect on future contracts/tests",
        "Blocks RoutingAgent prompt draft?",
        "Blocks SourceAuditAgent or ClassificationAgent prompt draft?",
        "Open questions",
    )
    for phrase in required_phrases:
        assert normalize_text(clarification).count(normalize_text(phrase)) >= 4, (
            f"Every blocker family must include {phrase!r}."
        )


def test_pre_prompt_clarification_marks_unresolved_items_for_human_decision() -> None:
    clarification = read_clarification()

    assert_contains_all(
        clarification,
        (
            "requires human decision",
            "Exact structured field names",
            "Exact source status enum names",
            "Whether `hors_perimetre` should become a future controlled enum value",
            "Exact enum names for `ready`, `blocked`, `needs_audit`",
            "Which future contracts/tests own each clarified concept",
        ),
    )


def test_pre_prompt_clarification_distinguishes_safe_routing_from_blocked_source_work() -> None:
    clarification = read_clarification()

    assert_contains_all(
        clarification,
        (
            "Safe for first RoutingAgent draft",
            "use existing repository-controlled routing terms",
            "output proposed routing decisions only",
            "avoid source audit and classification claims",
            "`SourceAuditAgent` prompt drafting should remain blocked",
            "`ClassificationAgent` prompt drafting should remain blocked",
            "This document does not create that draft",
        ),
    )


def test_pre_prompt_clarification_did_not_add_prompt_artifacts() -> None:
    draft_paths = sorted(PROMPT_DRAFT_DIR.glob("*.md")) if PROMPT_DRAFT_DIR.exists() else []

    assert draft_paths == [], f"Codex 024 must not add prompt drafts: {draft_paths!r}"
    assert not PROMPTS_MODULE.exists(), f"prompts.py must not exist: {PROMPTS_MODULE}"
