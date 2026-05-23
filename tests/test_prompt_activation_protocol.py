from __future__ import annotations

import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
PROTOCOL_PATH = DOCS_DIR / "PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md"
PROMPT_DRAFT_DIR = DOCS_DIR / "prompts" / "drafts"
PROMPTS_MODULE = REPO_ROOT / "src" / "dico_impro" / "agents" / "prompts.py"


def read_protocol() -> str:
    assert PROTOCOL_PATH.exists(), f"Prompt activation protocol is missing: {PROTOCOL_PATH}"
    return PROTOCOL_PATH.read_text(encoding="utf-8")


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return without_accents.casefold()


def assert_contains_all(document: str, phrases: tuple[str, ...]) -> None:
    normalized_document = normalize_text(document)
    missing = [
        phrase for phrase in phrases if normalize_text(phrase) not in normalized_document
    ]
    assert not missing, f"Protocol document is missing required text: {missing!r}"


def test_prompt_activation_protocol_exists_and_defines_lifecycle_statuses() -> None:
    protocol = read_protocol()

    assert_contains_all(
        protocol,
        (
            "not_created",
            "draft_documented",
            "human_review_required",
            "approved_for_mock_only",
            "approved_for_real_openai_later",
            "retired",
        ),
    )


def test_prompt_activation_protocol_keeps_prompts_disabled_and_runtime_disconnected() -> None:
    protocol = read_protocol()

    assert_contains_all(
        protocol,
        (
            "no prompt is active by default",
            "no prompt may be consumed by OpenAIAdapter yet",
            "no prompt may be consumed by CLI dry-run",
            "no prompt may trigger real OpenAI",
            "real OpenAI calls",
            "network calls",
            "prompt loading or rendering",
            "CLI prompt consumption",
        ),
    )


def test_prompt_activation_protocol_preserves_project_boundary_rules() -> None:
    protocol = read_protocol()

    assert_contains_all(
        protocol,
        (
            "data/local_files",
            "active journal",
            "old PDF",
            "real project entries",
            "launch RUN",
            "candidate selection",
            "write JournalPatch",
            "XLSX/CSV exports",
            "SourceDiscoveryAgent activation",
        ),
    )


def test_prompt_activation_protocol_documents_review_and_storage_requirements() -> None:
    protocol = read_protocol()

    assert_contains_all(
        protocol,
        (
            "human-readable review note",
            "agent target",
            "input contract",
            "expected output contract",
            "forbidden context",
            "known risks",
            "docs/prompts/drafts/",
            "src/dico_impro/agents/prompts.py is forbidden",
            "inline prompt fields inside PromptPackage JSON fixtures are forbidden",
            "prompt_body_ref is a reference only, not prompt content",
        ),
    )


def test_prompt_activation_protocol_names_routing_agent_without_prompt_body() -> None:
    protocol = read_protocol()

    assert_contains_all(
        protocol,
        (
            "preferred first future prompt candidate is `RoutingAgent`",
            "`ClassificationAgent` remains higher",
            "No `RoutingAgent` prompt body is written by Codex 022",
            "mock-only and review-only",
        ),
    )


def test_prompt_activation_protocol_has_no_current_prompt_artifacts() -> None:
    draft_paths = sorted(PROMPT_DRAFT_DIR.glob("*.md")) if PROMPT_DRAFT_DIR.exists() else []

    assert draft_paths == [], f"Codex 022 must not add prompt drafts: {draft_paths!r}"
    assert not PROMPTS_MODULE.exists(), f"prompts.py must not exist: {PROMPTS_MODULE}"
