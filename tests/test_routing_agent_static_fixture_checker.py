from __future__ import annotations

import ast
from copy import deepcopy
import re
import unicodedata
from pathlib import Path
from typing import Any

from helpers import routing_agent_static_fixture_checker as checker


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
DOC_PATH = DOCS_DIR / "ROUTING_AGENT_STATIC_FIXTURE_CHECKER_v0.2.3-auto.md"
SYNTHETIC_FIXTURES_DOC_PATH = (
    DOCS_DIR / "ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES_v0.2.3-auto.md"
)
DRAFT_PATH = DOCS_DIR / "prompts" / "drafts" / "ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md"
GATE_PATH = DOCS_DIR / "ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md"
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "routing_agent_prompt_review_cases.json"
HELPER_PATH = REPO_ROOT / "tests" / "helpers" / "routing_agent_static_fixture_checker.py"
SRC_DIR = REPO_ROOT / "src" / "dico_impro"
RUNTIME_BOUNDARY_PATHS = (
    SRC_DIR / "cli.py",
    SRC_DIR / "agents" / "adapters" / "openai.py",
    SRC_DIR / "orchestration" / "mock_openai_plan.py",
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


def extract_markdown_section(document: str, heading_text: str) -> str:
    headings = list(re.finditer(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$", document, re.MULTILINE))
    expected_heading = normalize_text(heading_text)

    for index, heading in enumerate(headings):
        if normalize_text(heading.group("title")) != expected_heading:
            continue
        level = len(heading.group("marks"))
        end = len(document)
        for next_heading in headings[index + 1 :]:
            if len(next_heading.group("marks")) <= level:
                end = next_heading.start()
                break
        return document[heading.end() : end]

    available = [heading.group("title") for heading in headings]
    raise AssertionError(
        f"Missing markdown section {heading_text!r}. Available headings: {available!r}"
    )


def load_fixture_copy() -> dict[str, Any]:
    return deepcopy(checker.load_fixture(FIXTURE_PATH))


def joined_errors(errors: list[str]) -> str:
    return "\n".join(errors)


def test_static_checker_doc_exists_and_declares_test_only_non_llm_status() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "Status: Codex 031 static non-LLM fixture checker",
            "static non-LLM checker",
            "documentation/test-only",
            "test-only",
            "non-runtime",
            "non-consuming",
            "non-activation",
            "non-approval",
            "not a prompt evaluation runtime",
            "not a mock execution harness",
        ),
    )


def test_static_checker_doc_keeps_codex_031_non_activation_non_consuming() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "Codex 031 does not activate the prompt",
            "Codex 031 does not approve mock execution",
            "Codex 031 does not approve runtime",
            "Codex 031 does not load, render, execute or consume the prompt",
            "Codex 031 only adds test-only static checks",
            "Codex 031 is not a prompt evaluation runtime",
            "call an LLM",
            "call OpenAI",
            "approve any prompt-consuming path",
        ),
    )


def test_static_checker_doc_references_inputs_and_codex_sequence() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "tests/fixtures/routing_agent_prompt_review_cases.json",
            "docs/ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES_v0.2.3-auto.md",
            "docs/prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md",
            "docs/ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md",
            "ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md",
            "ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md",
            "AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md",
            "PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md",
            "PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md",
            "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md",
            "Codex 028 created the disabled prompt draft",
            "Codex 029 added the disabled-draft review gate",
            "Codex 030 created synthetic static review fixtures",
            "Codex 031 adds a static checker for those fixtures only",
            "Codex 031 does not consume the prompt",
        ),
    )


def test_static_checker_doc_documents_location_scope_and_responsibilities() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "tests/helpers/routing_agent_static_fixture_checker.py",
            "tests/test_routing_agent_static_fixture_checker.py",
            "must not be imported from `src/`",
            "must not create runtime APIs",
            "must not define final JSON contracts",
            "must not define runtime enums",
            "must not be used by CLI, `OpenAIAdapter`, mock planning, runtime or production code",
            "top-level `metadata` exists",
            "top-level `cases` exists",
            "`case_id` starts with `SYN-030-`",
            "`supplied_input.entry_id` starts with `SYN-030-`",
            "required case families are covered",
            "required safe routes are covered",
            "required forbidden outputs are covered",
            "required recommendation concepts are covered",
        ),
    )


def test_static_checker_doc_documents_non_responsibilities_and_helper_guidance() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "infer expected model answers",
            "score generated output",
            "execute the prompt",
            "render a prompt package",
            "load prompt text into runtime",
            "call network",
            "validate real entries",
            "read active journal",
            "launch RUN",
            "apply JournalPatch",
            "select candidates",
            "decide final classification",
            "decide S-A or I-A",
            "create final contract/schema/enums",
            "mutate any project data",
            "load_fixture(path: Path) -> dict",
            "validate_fixture_metadata(data: dict) -> list[str]",
            "validate_fixture_cases(data: dict) -> list[str]",
            "validate_fixture_coverage(data: dict) -> list[str]",
            "validate_no_forbidden_real_data_markers(data: dict) -> list[str]",
            "validate_static_fixture(data: dict) -> list[str]",
            "Use only Python standard library",
        ),
    )


def test_static_checker_doc_verdict_has_yes_only_for_checker_creation() -> None:
    document = read_text(DOC_PATH)
    verdict = extract_markdown_section(document, "8. Verdict")

    assert_contains_all(
        verdict,
        (
            "Static fixture checker created: YES.",
            "Prompt executed: NO.",
            "Prompt loaded/rendered: NO.",
            "Approved for mock execution: NO.",
            "Approved for runtime: NO.",
            "Approved for CLI consumption: NO.",
            "Approved for OpenAI: NO.",
            "Approved for RUN: NO.",
            "Approved for final contracts/enums: NO.",
            "Approved for journal mutation: NO.",
            "Codex 031 itself grants no activation, prompt execution, runtime, OpenAI, RUN or journal permission",
        ),
    )
    assert re.findall(r": YES\b", verdict) == [": YES"]


def test_checker_helper_exists_and_uses_only_test_safe_imports() -> None:
    source = read_text(HELPER_PATH)
    tree = ast.parse(source)
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.append(node.module)

    forbidden_import_prefixes = (
        "dico_impro",
        "src",
        "socket",
        "requests",
        "urllib",
        "http",
        "openai",
    )
    forbidden = [
        module
        for module in imported_modules
        if any(module == prefix or module.startswith(f"{prefix}.") for prefix in forbidden_import_prefixes)
    ]
    assert not forbidden, f"Checker helper imports forbidden modules: {forbidden!r}"
    assert "write_text" not in source
    assert "journal_reader" not in source
    assert "data/active_journal" not in source
    assert "data\\active_journal" not in source


def test_checker_helper_validates_current_fixture_successfully() -> None:
    data = checker.load_fixture(FIXTURE_PATH)
    errors = checker.validate_static_fixture(data)

    assert errors == []


def test_metadata_checks_fail_on_missing_metadata() -> None:
    data = load_fixture_copy()
    del data["metadata"]

    errors = checker.validate_fixture_metadata(data)

    assert "metadata is missing" in joined_errors(errors)


def test_metadata_checks_fail_when_negative_flags_are_true() -> None:
    data = load_fixture_copy()
    data["metadata"]["execution_allowed"] = True
    data["metadata"]["openai_allowed"] = True

    errors = checker.validate_fixture_metadata(data)

    assert "metadata.execution_allowed must be false" in errors
    assert "metadata.openai_allowed must be false" in errors


def test_case_checks_fail_on_missing_required_fields() -> None:
    data = load_fixture_copy()
    del data["cases"][0]["expected_safe_route"]

    errors = checker.validate_fixture_cases(data)

    assert "expected_safe_route is missing" in joined_errors(errors)


def test_case_checks_fail_on_non_synthetic_case_id_or_entry_id() -> None:
    data = load_fixture_copy()
    data["cases"][0]["case_id"] = "REAL-030-A"
    data["cases"][0]["supplied_input"]["entry_id"] = "12345"

    errors = checker.validate_fixture_cases(data)

    assert "case_id must start with 'SYN-030-'" in joined_errors(errors)
    assert "supplied_input.entry_id must start with 'SYN-030-'" in joined_errors(errors)


def test_real_data_marker_checks_fail_on_old_pdf_or_real_numeric_id() -> None:
    data = load_fixture_copy()
    data["cases"][0]["supplied_input"]["synthetic_context"] = (
        "Use old PDF data for project entry 12345"
    )

    errors = checker.validate_no_forbidden_real_data_markers(data)

    assert "old pdf" in joined_errors(errors)
    assert "real entry-like numeric id" in joined_errors(errors)


def test_coverage_checks_fail_when_required_case_family_is_missing() -> None:
    data = load_fixture_copy()
    data["cases"] = [
        case for case in data["cases"] if case["case_id"] != "SYN-030-A-broad-system"
    ]

    errors = checker.validate_fixture_coverage(data)

    assert "required case family is missing: broad system" in errors


def test_coverage_checks_fail_when_required_forbidden_outputs_are_missing() -> None:
    data = load_fixture_copy()
    for case in data["cases"]:
        case["forbidden_outputs"] = [
            output for output in case["forbidden_outputs"] if output != "source discovery result"
        ]

    errors = checker.validate_fixture_coverage(data)

    assert "required forbidden output is missing: source discovery result" in errors


def test_coverage_checks_fail_when_required_recommendations_are_missing() -> None:
    data = load_fixture_copy()
    for case in data["cases"]:
        case["expected_recommendations"] = [
            recommendation
            for recommendation in case["expected_recommendations"]
            if "relance_perimetre" not in recommendation
        ]

    errors = checker.validate_fixture_coverage(data)

    assert "required recommendation concept is missing: relance_perimetre" in errors


def test_disabled_prompt_draft_and_review_gate_remain_non_runtime_non_activation() -> None:
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


def test_fixture_doc_still_frames_codex_030_as_static_non_consuming_fixture_layer() -> None:
    document = read_text(SYNTHETIC_FIXTURES_DOC_PATH)

    assert_contains_all(
        document,
        (
            "Codex 030 does not activate the prompt",
            "Codex 030 does not approve the prompt for mock execution",
            "Codex 030 does not approve the prompt for runtime",
            "Codex 030 does not load, render, execute or consume the prompt",
            "Codex 030 only creates synthetic review cases and static tests",
        ),
    )


def test_no_src_code_references_fixture_checker_or_disabled_prompt_draft() -> None:
    forbidden_terms = (
        FIXTURE_PATH.name,
        HELPER_PATH.name,
        DRAFT_PATH.name,
        "routing_agent_prompt_review_cases",
        "routing_agent_static_fixture_checker",
        "ROUTING_AGENT_PROMPT_DRAFT",
        "docs/prompts/drafts",
        "prompts/drafts",
    )

    assert not (SRC_DIR / "agents" / "prompts.py").exists()

    for path in sorted(SRC_DIR.rglob("*.py")):
        source = read_text(path)
        relative = path.relative_to(REPO_ROOT)
        for term in forbidden_terms:
            assert term not in source, f"{relative} must not reference {term!r}"


def test_cli_openai_adapter_and_mock_planning_do_not_load_fixture_checker_or_draft() -> None:
    forbidden_terms = (
        FIXTURE_PATH.name,
        HELPER_PATH.name,
        DRAFT_PATH.name,
        "routing_agent_prompt_review_cases",
        "routing_agent_static_fixture_checker",
        "ROUTING_AGENT_PROMPT_DRAFT",
        "docs/prompts/drafts",
        "prompts/drafts",
    )

    for path in RUNTIME_BOUNDARY_PATHS:
        source = read_text(path)
        relative = path.relative_to(REPO_ROOT)
        for term in forbidden_terms:
            assert term not in source, f"{relative} must not import, load or consume {term!r}"
