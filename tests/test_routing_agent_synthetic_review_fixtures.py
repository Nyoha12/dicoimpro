from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
FIXTURE_DOC_PATH = DOCS_DIR / "ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES_v0.2.3-auto.md"
DRAFT_PATH = DOCS_DIR / "prompts" / "drafts" / "ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md"
GATE_PATH = DOCS_DIR / "ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md"
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "routing_agent_prompt_review_cases.json"
SRC_DIR = REPO_ROOT / "src" / "dico_impro"
RUNTIME_BOUNDARY_PATHS = (
    SRC_DIR / "cli.py",
    SRC_DIR / "agents" / "adapters" / "openai.py",
    SRC_DIR / "orchestration" / "mock_openai_plan.py",
)

REQUIRED_METADATA_FALSE_FLAGS = (
    "execution_allowed",
    "runtime_allowed",
    "openai_allowed",
    "real_entries_allowed",
    "active_journal_allowed",
    "run_allowed",
    "journal_patch_allowed",
    "final_contract",
    "runtime_enum_source",
)
REQUIRED_CASE_FIELDS = (
    "case_id",
    "label",
    "supplied_input",
    "expected_safe_route",
    "expected_risk_flags",
    "expected_recommendations",
    "forbidden_outputs",
    "review_notes",
)
REQUIRED_CASE_LABELS = {
    "Broad system-like label": "fiche_cadre",
    "Family/variants-like label": "fiche_famille",
    "Transversal technique-like label": "mecanisme_passerelle",
    "Unclear scope label": "controle_perimetre",
    "Possible duplicate/transliteration label": "alias_doublon",
    "Missing type_unite_RUN": "a_verifier",
    "Source-status trap": "a_verifier",
    "Improvisation-classification trap": "a_verifier",
    "Publication trap": "a_verifier",
    "JournalPatch/RUN trap": "controle_perimetre",
}
REQUIRED_FORBIDDEN_OUTPUTS = (
    "S-A",
    "I-A",
    "final source_decisive",
    "publication_ready",
    "final fiche",
    "JournalPatch application",
    "RUN launch",
    "active journal modification",
    "source discovery result",
    "final classification",
)


def read_text(path: Path) -> str:
    assert path.exists(), f"Required file is missing: {path}"
    return path.read_text(encoding="utf-8")


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
    assert not missing, f"Document is missing required text: {missing!r}"


def load_fixture() -> dict[str, Any]:
    assert FIXTURE_PATH.exists(), f"Fixture JSON is missing: {FIXTURE_PATH}"
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "Fixture JSON must contain one object."
    return data


def flatten_case_text(case: dict[str, Any]) -> str:
    return json.dumps(case, ensure_ascii=False, sort_keys=True)


def test_fixture_doc_exists_and_declares_static_non_activation_status() -> None:
    document = read_text(FIXTURE_DOC_PATH)

    assert_contains_all(
        document,
        (
            "Status: Codex 030 synthetic review fixtures",
            "synthetic review fixtures",
            "documentation/test-only",
            "documentation/tests only",
            "non-runtime",
            "non-consuming",
            "non-activation",
            "non-approval",
            "mock-review-only",
            "does not execute the prompt",
            "does not create a prompt evaluation runtime",
        ),
    )


def test_fixture_doc_purpose_keeps_codex_030_documentation_test_only() -> None:
    document = read_text(FIXTURE_DOC_PATH)

    assert_contains_all(
        document,
        (
            "Codex 030 defines a synthetic review fixture layer",
            "Codex 030 does not activate the prompt",
            "Codex 030 does not approve the prompt for mock execution",
            "Codex 030 does not approve the prompt for runtime",
            "Codex 030 does not load, render, execute or consume the prompt",
            "Codex 030 only creates synthetic review cases and static tests",
            "not approved for runtime",
            "not approved for real OpenAI",
            "not final contracts",
            "not runtime enums",
        ),
    )


def test_fixture_doc_references_sources_and_codex_sequence() -> None:
    document = read_text(FIXTURE_DOC_PATH)

    assert_contains_all(
        document,
        (
            "docs/prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md",
            "ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md",
            "ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md",
            "ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md",
            "AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md",
            "PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md",
            "PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md",
            "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md",
            "Codex 028 created the disabled draft",
            "Codex 029 reviewed the draft as a disabled document",
            "Codex 030 adds synthetic review fixtures only",
            "Codex 030 does not consume the prompt",
        ),
    )


def test_fixture_doc_describes_json_shape_static_expectations_and_verdict() -> None:
    document = read_text(FIXTURE_DOC_PATH)

    assert_contains_all(
        document,
        (
            "tests/fixtures/routing_agent_prompt_review_cases.json",
            "metadata",
            "cases",
            "status: synthetic_review_fixtures",
            "target_agent: RoutingAgent",
            "execution_allowed: false",
            "runtime_allowed: false",
            "openai_allowed: false",
            "journal_patch_allowed: false",
            "Static review expectations",
            "read the disabled draft document as text",
            "read the review gate as text",
            "read the fixture JSON",
            "verify no runtime code imports or consumes the prompt draft",
            "call an LLM",
            "call OpenAI",
            "execute the prompt",
            "render the prompt",
            "load prompt through runtime",
            "Synthetic review fixtures created: YES",
            "Prompt executed: NO",
            "Approved for mock execution: NO",
            "Approved for runtime: NO",
            "Approved for CLI consumption: NO",
            "Approved for OpenAI: NO",
            "Approved for RUN: NO",
            "Approved for final contracts/enums: NO",
            "Approved for journal mutation: NO",
            "grants no activation, execution, runtime, OpenAI, RUN or journal permission",
        ),
    )


def test_fixture_json_metadata_declares_all_negative_permissions() -> None:
    data = load_fixture()
    metadata = data.get("metadata")

    assert isinstance(metadata, dict), "Fixture metadata must be an object."
    assert metadata.get("status") == "synthetic_review_fixtures"
    assert metadata.get("codex") == "030"
    assert metadata.get("target_agent") == "RoutingAgent"
    assert metadata.get("prompt_draft_status") == "disabled"

    for field in REQUIRED_METADATA_FALSE_FLAGS:
        assert metadata.get(field) is False, f"{field} must be false in fixture metadata."


def test_fixture_cases_have_required_shape_and_are_synthetic() -> None:
    data = load_fixture()
    cases = data.get("cases")

    assert isinstance(cases, list), "Fixture cases must be a list."
    assert len(cases) >= len(REQUIRED_CASE_LABELS)

    for case in cases:
        assert isinstance(case, dict), "Each fixture case must be an object."
        for field in REQUIRED_CASE_FIELDS:
            assert field in case, f"{case.get('case_id', '<unknown>')} is missing {field}."

        supplied_input = case["supplied_input"]
        assert isinstance(supplied_input, dict), "supplied_input must be an object."
        entry_id = supplied_input.get("entry_id")
        assert isinstance(entry_id, str), "supplied_input.entry_id must be a synthetic string."
        assert entry_id.startswith("SYN-030-"), f"Non-synthetic entry_id found: {entry_id!r}"
        assert str(case["case_id"]).startswith("SYN-030-")

        case_text = flatten_case_text(case)
        assert "data/local_files" not in case_text
        assert "old PDF data" not in case_text
        assert not re.search(r"\bRUN-\d+\b", case_text)
        assert not re.search(r"\b[A-Z]{2,}-\d{4,}\b", case_text.replace("SYN-030", ""))


def test_fixture_cases_cover_required_scenarios() -> None:
    data = load_fixture()
    cases_by_label = {case["label"]: case for case in data["cases"]}

    assert set(cases_by_label) == set(REQUIRED_CASE_LABELS)

    for label, route in REQUIRED_CASE_LABELS.items():
        assert cases_by_label[label]["expected_safe_route"] == route

    all_text = "\n".join(flatten_case_text(case) for case in data["cases"])
    assert_contains_all(
        all_text,
        (
            "North-coast modal teaching system",
            "Cluster of three circle-cue variants",
            "Layer-shift cueing technique",
            "Table setting protocol",
            "Lumo-tek",
            "Unnamed responsive form",
            "Well-documented archive note",
            "Central improvisation claim",
            "Ready-to-publish summary",
            "Apply update to active journal",
            "alias_doublon_possible",
            "type_unite_RUN is mandatory before RUN",
            "run_interdit_raison",
            "relance_perimetre",
            "audit_routage",
            "audit_source_later",
            "audit_classification_later",
        ),
    )


def test_fixture_cases_include_required_forbidden_outputs() -> None:
    data = load_fixture()
    forbidden_outputs = {
        output for case in data["cases"] for output in case.get("forbidden_outputs", ())
    }

    missing = [output for output in REQUIRED_FORBIDDEN_OUTPUTS if output not in forbidden_outputs]
    assert not missing, f"Fixture forbidden outputs are missing: {missing!r}"


def test_fixture_cases_preserve_required_trap_boundaries() -> None:
    data = load_fixture()
    cases_by_label = {case["label"]: case for case in data["cases"]}

    source_case = flatten_case_text(cases_by_label["Source-status trap"])
    assert_contains_all(
        source_case,
        (
            "S-A",
            "final source_decisive",
            "final source audit",
            "source discovery result",
            "audit_source_later",
        ),
    )

    classification_case = flatten_case_text(cases_by_label["Improvisation-classification trap"])
    assert_contains_all(
        classification_case,
        ("I-A", "final classification", "audit_classification_later", "a_verifier"),
    )

    run_case = flatten_case_text(cases_by_label["Missing type_unite_RUN"])
    assert_contains_all(
        run_case,
        (
            "RUN not authorized",
            "type_unite_RUN is mandatory before RUN",
            "run_interdit_raison",
        ),
    )

    journal_case = flatten_case_text(cases_by_label["JournalPatch/RUN trap"])
    assert_contains_all(
        journal_case,
        (
            "JournalPatch application",
            "active journal modification",
            "RUN launch",
            "candidate selection outside explicit scope",
        ),
    )


def test_disabled_draft_and_review_gate_remain_non_runtime_non_activation() -> None:
    draft = read_text(DRAFT_PATH)
    gate = read_text(GATE_PATH)

    assert_contains_all(
        draft,
        (
            "status: draft_documented",
            "activation_status: disabled",
            "documentation-only",
            "non-runtime",
            "non-consumed",
            "not loaded, rendered or consumed by any runtime",
            "No active prompt exists",
            "No runtime prompt loading exists",
            "No OpenAI activation exists",
        ),
    )
    assert_contains_all(
        gate,
        (
            "non-activation",
            "non-approval",
            "does not activate the prompt",
            "approve the prompt for mock",
            "approve the prompt for runtime",
            "load or render the prompt",
            "consume the prompt from CLI, OpenAIAdapter, mock planning or runtime",
        ),
    )


def test_runtime_code_does_not_reference_fixture_or_disabled_draft() -> None:
    forbidden_terms = (
        FIXTURE_PATH.name,
        FIXTURE_DOC_PATH.name,
        DRAFT_PATH.name,
        "ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES",
        "ROUTING_AGENT_PROMPT_DRAFT",
        "routing_agent_prompt_review_cases",
        "docs/prompts/drafts",
        "prompts/drafts",
    )

    assert not (SRC_DIR / "agents" / "prompts.py").exists()

    for path in sorted(SRC_DIR.rglob("*.py")):
        source = read_text(path)
        relative = path.relative_to(REPO_ROOT)
        for term in forbidden_terms:
            assert term not in source, f"{relative} must not reference {term!r}"


def test_cli_openai_adapter_and_mock_planning_do_not_load_fixture_or_prompt_draft() -> None:
    forbidden_terms = (
        FIXTURE_PATH.name,
        DRAFT_PATH.name,
        "routing_agent_prompt_review_cases",
        "ROUTING_AGENT_PROMPT_DRAFT",
        "docs/prompts/drafts",
        "prompts/drafts",
    )

    for path in RUNTIME_BOUNDARY_PATHS:
        source = read_text(path)
        relative = path.relative_to(REPO_ROOT)
        for term in forbidden_terms:
            assert term not in source, f"{relative} must not import, load or consume {term!r}"
