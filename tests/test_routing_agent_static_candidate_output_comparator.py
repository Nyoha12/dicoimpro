from __future__ import annotations

import ast
import json
import re
import unicodedata
from copy import deepcopy
from pathlib import Path
from typing import Any

from helpers import routing_agent_static_candidate_output_comparator as comparator


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
DOC_PATH = DOCS_DIR / "ROUTING_AGENT_STATIC_CANDIDATE_OUTPUT_COMPARATOR_v0.2.3-auto.md"
EXPECTED_DOC_PATH = DOCS_DIR / "ROUTING_AGENT_STATIC_EXPECTED_OUTPUT_EVALUATOR_v0.2.3-auto.md"
CHECKER_DOC_PATH = DOCS_DIR / "ROUTING_AGENT_STATIC_FIXTURE_CHECKER_v0.2.3-auto.md"
FIXTURE_DOC_PATH = DOCS_DIR / "ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES_v0.2.3-auto.md"
DRAFT_PATH = DOCS_DIR / "prompts" / "drafts" / "ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md"
GATE_PATH = DOCS_DIR / "ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md"
CANDIDATE_OUTPUT_PATH = REPO_ROOT / "tests" / "fixtures" / "routing_agent_candidate_outputs.json"
EXPECTED_OUTPUT_PATH = REPO_ROOT / "tests" / "fixtures" / "routing_agent_expected_outputs.json"
REVIEW_CASES_PATH = REPO_ROOT / "tests" / "fixtures" / "routing_agent_prompt_review_cases.json"
HELPER_PATH = (
    REPO_ROOT
    / "tests"
    / "helpers"
    / "routing_agent_static_candidate_output_comparator.py"
)
SRC_DIR = REPO_ROOT / "src" / "dico_impro"

REQUIRED_CASE_IDS = (
    "SYN-030-A-broad-system",
    "SYN-030-B-family-variants",
    "SYN-030-C-transversal-technique",
    "SYN-030-D-unclear-scope",
    "SYN-030-E-duplicate-transliteration",
    "SYN-030-F-missing-type-unite-run",
    "SYN-030-G-source-status-trap",
    "SYN-030-H-improvisation-classification-trap",
    "SYN-030-I-publication-trap",
    "SYN-030-J-journalpatch-run-trap",
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


def load_candidates() -> dict[str, Any]:
    return comparator.load_json(CANDIDATE_OUTPUT_PATH)


def load_expected() -> dict[str, Any]:
    return comparator.load_json(EXPECTED_OUTPUT_PATH)


def load_cases() -> dict[str, Any]:
    return comparator.load_json(REVIEW_CASES_PATH)


def load_candidates_copy() -> dict[str, Any]:
    return deepcopy(load_candidates())


def candidates_by_id(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {candidate["candidate_id"]: candidate for candidate in data["candidates"]}


def candidate_by_id(data: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    return candidates_by_id(data)[candidate_id]


def expected_by_case(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["case_id"]: entry for entry in data["expected_outputs"]}


def cases_by_id(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {case["case_id"]: case for case in data["cases"]}


def joined_errors(errors: list[str]) -> str:
    return "\n".join(errors)


def compare_candidate(candidate: dict[str, Any]) -> list[str]:
    expected = expected_by_case(load_expected())[candidate["case_id"]]
    source_case = cases_by_id(load_cases())[candidate["case_id"]]
    return comparator.compare_candidate_to_expected(candidate, expected, source_case)


def test_candidate_comparator_doc_exists_and_declares_static_non_llm_test_only_status() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "Status: Codex 033 static candidate-output comparator",
            "static candidate-output comparator",
            "documentation/tests only",
            "docs/tests-only",
            "static, non-LLM",
            "deterministic fake candidate provider",
            "documentation/test-only",
            "non-runtime",
            "non-consuming",
            "non-activation",
            "non-approval",
            "not a prompt evaluation runtime",
            "not a mock execution harness",
            "not model-output scoring",
        ),
    )


def test_candidate_comparator_doc_keeps_codex_033_non_activation_and_non_consuming() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "Codex 033 does not activate the prompt",
            "Codex 033 does not approve mock execution",
            "Codex 033 does not approve runtime",
            "Codex 033 does not load, render, execute or consume the prompt",
            "Codex 033 only adds hand-written synthetic candidate outputs",
            "Codex 033 is not a prompt evaluation runtime",
            "Codex 033 does not claim RoutingAgent works",
            "Codex 033 only checks whether comparison diagnostics detect PASS/FAIL synthetic candidates",
            "fake provider must not be presented as RoutingAgent behavior",
            "It does not create model outputs",
            "It does not execute the prompt",
            "It does not call an LLM",
            "It does not evaluate model behavior",
        ),
    )


def test_candidate_comparator_doc_references_inputs_and_codex_sequence() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "tests/fixtures/routing_agent_prompt_review_cases.json",
            "tests/fixtures/routing_agent_expected_outputs.json",
            "tests/fixtures/routing_agent_candidate_outputs.json",
            "tests/helpers/routing_agent_static_fixture_checker.py",
            "tests/helpers/routing_agent_static_expected_output_evaluator.py",
            "docs/ROUTING_AGENT_STATIC_EXPECTED_OUTPUT_EVALUATOR_v0.2.3-auto.md",
            "docs/ROUTING_AGENT_STATIC_FIXTURE_CHECKER_v0.2.3-auto.md",
            "docs/ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES_v0.2.3-auto.md",
            "docs/prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md",
            "docs/ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md",
            "ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md",
            "ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md",
            "AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md",
            "PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md",
            "PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md",
            "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md",
            "Codex 030 created synthetic review cases",
            "Codex 031 added a fixture-shape/guardrail checker",
            "Codex 032 added static expected outputs",
            "Codex 033 adds static synthetic candidate outputs and comparison diagnostics",
            "Codex 033 does not consume the prompt",
        ),
    )


def test_candidate_comparator_doc_describes_fixture_shape_and_non_contract_status() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "tests/fixtures/routing_agent_candidate_outputs.json",
            "metadata",
            "candidates",
            "status: static_candidate_outputs",
            "codex: 033",
            "target_agent: RoutingAgent",
            "source_fixture: tests/fixtures/routing_agent_prompt_review_cases.json",
            "expected_outputs_fixture: tests/fixtures/routing_agent_expected_outputs.json",
            "prompt_draft_status: disabled",
            "candidate_generation_from_prompt: false",
            "deterministic_fake_provider_only: true",
            "prompt_execution_allowed: false",
            "runtime_allowed: false",
            "openai_allowed: false",
            "real_entries_allowed: false",
            "active_journal_allowed: false",
            "run_allowed: false",
            "journal_patch_allowed: false",
            "final_contract: false",
            "runtime_enum_source: false",
            "model_output_scoring: false",
            "type_unite_propose",
            "decision_pre_RUN_proposee",
            "uncertainty_note",
            "risks_initiaux",
            "controle_perimetre_recommande",
            "alias_doublon_possible",
            "relance_recommandee",
            "audit_recommande",
            "run_autorise_provisoirement",
            "run_interdit_raison",
            "justification_courte",
            "trace_notes",
            "static candidate-output fixture fields only",
            "not final JSON contracts",
            "not runtime enums",
            "not production schemas",
        ),
    )


def test_candidate_comparator_doc_documents_required_scenarios_and_diagnostics() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "Broad system-like label",
            "Family/variants-like label",
            "Transversal technique-like label",
            "Unclear scope label",
            "Possible duplicate/transliteration",
            "Missing `type_unite_RUN`",
            "Source-status trap",
            "Improvisation-classification trap",
            "Publication trap",
            "JournalPatch/RUN trap",
            "expected_result",
            "pass",
            "fail",
            "disallowed_route",
            "missing_uncertainty",
            "run_authorized_without_type_unite_RUN",
            "missing_run_interdit_raison",
            "forbidden_output_present",
            "alias_flag_missing",
            "definitive_merge_or_scission",
            "source_status_forbidden",
            "classification_forbidden",
            "publication_forbidden",
            "journal_action_forbidden",
            "candidate_selection_forbidden",
            "missing_required_recommendation",
            "disallowed_expected_output_field",
            "real_data_marker_present",
            "Diagnostics are test-only strings",
            "not runtime enums and not final contracts",
        ),
    )


def test_candidate_comparator_doc_documents_responsibilities_and_non_responsibilities() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "load candidate outputs JSON",
            "load expected outputs JSON",
            "load review cases JSON",
            "verify metadata and false permission flags",
            "verify `candidates` is non-empty",
            "verify every candidate `case_id` exists in expected outputs and review cases",
            "verify `candidate_output` uses only allowed conceptual fields",
            "compare `candidate_output` to `expected_output` using static rules",
            "emit human-readable diagnostics",
            "verify PASS candidates produce no error diagnostics",
            "verify FAIL candidates produce expected diagnostic keywords",
            "verify RUN remains blocked when `type_unite_RUN` is missing",
            "verify `run_interdit_raison` exists",
            "verify duplicate/transliteration PASS has `alias_doublon_possible: true`",
            "load_json(path: Path) -> dict",
            "validate_candidate_metadata(data: dict) -> list[str]",
            "validate_candidate_shape(data: dict) -> list[str]",
            "compare_candidate_to_expected(candidate: dict, expected: dict, source_case: dict) -> list[str]",
            "validate_candidate_scenarios(candidate_data: dict, expected_data: dict, cases_data: dict) -> list[str]",
            "validate_no_forbidden_real_data_markers(data: dict) -> list[str]",
            "validate_static_candidates(candidate_data: dict, expected_data: dict, cases_data: dict) -> list[str]",
            "Use only Python standard library",
            "Do not use pydantic",
            "Do not import from `src/dico_impro`",
            "infer model answers",
            "score generated model output",
            "execute the prompt",
            "render a prompt package",
            "load prompt text into runtime",
            "call OpenAI or any LLM",
            "call network",
            "validate real entries",
            "read active journal",
            "launch RUN",
            "apply JournalPatch",
            "select real candidates",
            "decide final classification",
            "decide S-A or I-A",
            "create final contract/schema/enums",
            "mutate any project data",
        ),
    )


def test_candidate_comparator_doc_verdict_has_yes_only_for_comparator_and_provider() -> None:
    document = read_text(DOC_PATH)
    verdict = extract_markdown_section(document, "9. Verdict")

    assert_contains_all(
        verdict,
        (
            "Static candidate-output comparator created: YES.",
            "Synthetic fake provider created: YES, test-only and deterministic.",
            "Prompt executed: NO.",
            "Prompt loaded/rendered: NO.",
            "Model output scored: NO.",
            "Approved for mock execution: NO.",
            "Approved for runtime: NO.",
            "Approved for CLI consumption: NO.",
            "Approved for OpenAI: NO.",
            "Approved for RUN: NO.",
            "Approved for final contracts/enums: NO.",
            "Approved for journal mutation: NO.",
            "Codex 033 itself grants no activation, prompt execution, runtime, OpenAI, RUN or journal permission",
        ),
    )
    assert re.findall(r": YES\b", verdict) == [": YES", ": YES"]


def test_candidate_output_fixture_metadata_declares_all_negative_permissions() -> None:
    data = load_candidates()
    metadata = data.get("metadata")

    assert CANDIDATE_OUTPUT_PATH.exists()
    assert isinstance(metadata, dict)
    assert metadata.get("status") == "static_candidate_outputs"
    assert metadata.get("codex") == "033"
    assert metadata.get("target_agent") == "RoutingAgent"
    assert metadata.get("source_fixture") == "tests/fixtures/routing_agent_prompt_review_cases.json"
    assert metadata.get("expected_outputs_fixture") == (
        "tests/fixtures/routing_agent_expected_outputs.json"
    )
    assert metadata.get("prompt_draft_status") == "disabled"
    assert metadata.get("deterministic_fake_provider_only") is True

    for field in comparator.REQUIRED_METADATA_FALSE_FLAGS:
        assert metadata.get(field) is False, f"metadata.{field} must be false"


def test_candidates_exist_are_non_empty_and_use_only_allowed_fields() -> None:
    data = load_candidates()
    allowed_fields = set(comparator.ALLOWED_CANDIDATE_OUTPUT_FIELDS)

    candidates = data.get("candidates")
    assert isinstance(candidates, list)
    assert candidates

    for candidate in candidates:
        output = candidate["candidate_output"]
        assert set(output).issubset(allowed_fields), candidate["candidate_id"]
        assert candidate["expected_result"] in ("pass", "fail")


def test_every_candidate_case_id_exists_in_expected_outputs_and_review_cases() -> None:
    candidate_data = load_candidates()
    expected_ids = set(expected_by_case(load_expected()))
    case_ids = set(cases_by_id(load_cases()))

    for candidate in candidate_data["candidates"]:
        assert candidate["case_id"] in expected_ids
        assert candidate["case_id"] in case_ids


def test_all_required_pass_fail_groups_exist() -> None:
    data = load_candidates()
    coverage = {
        (candidate["case_id"], candidate["expected_result"])
        for candidate in data["candidates"]
    }

    for case_id in REQUIRED_CASE_IDS:
        assert (case_id, "pass") in coverage
        assert (case_id, "fail") in coverage


def test_deterministic_fake_provider_returns_only_fixture_candidates() -> None:
    data = load_candidates()
    provider = comparator.StaticCandidateFixtureProvider(data)
    fake_provider = comparator.DeterministicFakeCandidateProvider(data)

    assert provider.candidates() == tuple(data["candidates"])
    assert fake_provider.candidates() == provider.candidates()
    assert provider.by_candidate_id("CAND-033-A-pass") == data["candidates"][0]
    assert tuple(candidate["expected_result"] for candidate in provider.by_case_id(REQUIRED_CASE_IDS[0])) == (
        "pass",
        "fail",
    )
    assert provider.by_candidate_id("missing") is None


def test_pass_candidates_validate_without_error_diagnostics() -> None:
    for candidate in load_candidates()["candidates"]:
        if candidate["expected_result"] != "pass":
            continue
        diagnostics = compare_candidate(candidate)
        assert diagnostics == [], f"{candidate['candidate_id']} produced {diagnostics!r}"


def test_fail_candidates_produce_expected_diagnostic_keywords() -> None:
    for candidate in load_candidates()["candidates"]:
        if candidate["expected_result"] != "fail":
            continue
        diagnostics = compare_candidate(candidate)
        joined = joined_errors(diagnostics)
        assert diagnostics, f"{candidate['candidate_id']} must produce diagnostics"
        for expected_keyword in candidate["expected_diagnostics"]:
            assert expected_keyword in joined, (
                f"{candidate['candidate_id']} missing {expected_keyword!r}: {diagnostics!r}"
            )


def test_forbidden_output_strings_are_detected() -> None:
    candidate = deepcopy(candidate_by_id(load_candidates(), "CAND-033-A-pass"))
    candidate["candidate_output"]["trace_notes"] = ["S-A"]

    diagnostics = compare_candidate(candidate)

    assert "forbidden_output_present" in joined_errors(diagnostics)


def test_run_authorization_without_type_unite_run_is_detected() -> None:
    candidate = deepcopy(candidate_by_id(load_candidates(), "CAND-033-F-pass"))
    candidate["candidate_output"]["run_autorise_provisoirement"] = True

    diagnostics = compare_candidate(candidate)

    assert "run_authorized_without_type_unite_RUN" in joined_errors(diagnostics)


def test_missing_run_interdit_raison_is_detected() -> None:
    candidate = deepcopy(candidate_by_id(load_candidates(), "CAND-033-F-pass"))
    del candidate["candidate_output"]["run_interdit_raison"]

    diagnostics = compare_candidate(candidate)

    assert "missing_run_interdit_raison" in joined_errors(diagnostics)


def test_missing_alias_flag_is_detected_for_duplicate_pass_case() -> None:
    candidate = deepcopy(candidate_by_id(load_candidates(), "CAND-033-E-pass"))
    candidate["candidate_output"]["alias_doublon_possible"] = False

    diagnostics = compare_candidate(candidate)

    assert "alias_flag_missing" in joined_errors(diagnostics)


def test_source_status_trap_is_detected() -> None:
    candidate = deepcopy(candidate_by_id(load_candidates(), "CAND-033-G-pass"))
    candidate["candidate_output"]["type_unite_propose"] = "S-A"
    candidate["candidate_output"]["justification_courte"] = "source_decisive"

    diagnostics = compare_candidate(candidate)

    joined = joined_errors(diagnostics)
    assert "source_status_forbidden" in joined
    assert "forbidden_output_present" in joined


def test_classification_trap_is_detected() -> None:
    candidate = deepcopy(candidate_by_id(load_candidates(), "CAND-033-H-pass"))
    candidate["candidate_output"]["type_unite_propose"] = "I-A"
    candidate["candidate_output"]["justification_courte"] = "final classification"

    diagnostics = compare_candidate(candidate)

    joined = joined_errors(diagnostics)
    assert "classification_forbidden" in joined
    assert "forbidden_output_present" in joined


def test_publication_trap_is_detected() -> None:
    candidate = deepcopy(candidate_by_id(load_candidates(), "CAND-033-I-pass"))
    candidate["candidate_output"]["decision_pre_RUN_proposee"] = "publication_ready"
    candidate["candidate_output"]["justification_courte"] = "final fiche"

    diagnostics = compare_candidate(candidate)

    joined = joined_errors(diagnostics)
    assert "publication_forbidden" in joined
    assert "forbidden_output_present" in joined


def test_journalpatch_run_action_trap_is_detected() -> None:
    candidate = deepcopy(candidate_by_id(load_candidates(), "CAND-033-J-pass"))
    candidate["candidate_output"]["decision_pre_RUN_proposee"] = "RUN launch"
    candidate["candidate_output"]["justification_courte"] = "JournalPatch application"
    candidate["candidate_output"]["trace_notes"] = [
        "active journal modification",
        "candidate selection outside explicit scope",
    ]

    diagnostics = compare_candidate(candidate)

    joined = joined_errors(diagnostics)
    assert "journal_action_forbidden" in joined
    assert "candidate_selection_forbidden" in joined
    assert "forbidden_output_present" in joined


def test_candidate_output_helper_exists_and_uses_only_test_safe_imports() -> None:
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
        "pydantic",
    )
    forbidden = [
        module
        for module in imported_modules
        if any(module == prefix or module.startswith(f"{prefix}.") for prefix in forbidden_import_prefixes)
    ]
    assert not forbidden, f"Candidate-output helper imports forbidden modules: {forbidden!r}"
    assert "write_text" not in source
    assert "read_active_journal" not in source
    assert "journal_reader" not in source
    assert "apply_journal_patch" not in source


def test_validate_static_candidates_returns_no_errors_for_current_fixtures() -> None:
    errors = comparator.validate_static_candidates(load_candidates(), load_expected(), load_cases())

    assert errors == []


def test_metadata_validation_fails_on_missing_metadata() -> None:
    data = load_candidates_copy()
    del data["metadata"]

    errors = comparator.validate_candidate_metadata(data)

    assert "metadata is missing" in joined_errors(errors)


def test_metadata_validation_fails_on_true_permission_flags() -> None:
    data = load_candidates_copy()
    data["metadata"]["candidate_generation_from_prompt"] = True
    data["metadata"]["openai_allowed"] = True

    errors = comparator.validate_candidate_metadata(data)

    assert "metadata.candidate_generation_from_prompt must be false" in errors
    assert "metadata.openai_allowed must be false" in errors


def test_scenario_validation_fails_on_unknown_case_id() -> None:
    data = load_candidates_copy()
    candidate_by_id(data, "CAND-033-A-pass")["case_id"] = "SYN-030-Z-unknown"

    errors = comparator.validate_candidate_scenarios(data, load_expected(), load_cases())

    assert "unknown in expected outputs" in joined_errors(errors)


def test_shape_validation_fails_on_disallowed_candidate_output_field() -> None:
    data = load_candidates_copy()
    candidate_by_id(data, "CAND-033-A-pass")["candidate_output"]["runtime_enum"] = "not_allowed"

    errors = comparator.validate_candidate_shape(data)

    assert "runtime_enum is not an allowed static field" in joined_errors(errors)


def test_scenario_validation_fails_on_forbidden_output_string_in_pass_candidate() -> None:
    data = load_candidates_copy()
    candidate_by_id(data, "CAND-033-A-pass")["candidate_output"]["trace_notes"] = ["S-A"]

    errors = comparator.validate_candidate_scenarios(data, load_expected(), load_cases())

    joined = joined_errors(errors)
    assert "pass candidate CAND-033-A-pass produced diagnostics" in joined
    assert "forbidden_output_present" in joined


def test_scenario_validation_fails_on_missing_required_pass_fail_group() -> None:
    data = load_candidates_copy()
    data["candidates"] = [
        candidate
        for candidate in data["candidates"]
        if candidate["candidate_id"] != "CAND-033-A-pass"
    ]

    errors = comparator.validate_candidate_scenarios(data, load_expected(), load_cases())

    assert "missing required PASS/FAIL group: A pass" in errors


def test_scenario_validation_fails_when_pass_candidate_produces_diagnostics() -> None:
    data = load_candidates_copy()
    candidate_by_id(data, "CAND-033-B-pass")["candidate_output"]["type_unite_propose"] = (
        "fiche_pratique"
    )

    errors = comparator.validate_candidate_scenarios(data, load_expected(), load_cases())

    joined = joined_errors(errors)
    assert "pass candidate CAND-033-B-pass produced diagnostics" in joined
    assert "disallowed_route" in joined


def test_scenario_validation_fails_when_fail_candidate_missing_expected_diagnostics() -> None:
    data = load_candidates_copy()
    candidate_by_id(data, "CAND-033-A-fail")["expected_diagnostics"] = []

    errors = comparator.validate_candidate_scenarios(data, load_expected(), load_cases())

    assert "fail candidate CAND-033-A-fail.expected_diagnostics must be non-empty" in errors


def test_real_data_marker_validation_fails_on_real_marker() -> None:
    data = load_candidates_copy()
    candidate_by_id(data, "CAND-033-A-pass")["candidate_output"]["trace_notes"] = [
        "Use data/local_files/old.pdf for project entry 12345"
    ]

    errors = comparator.validate_no_forbidden_real_data_markers(data)

    joined = joined_errors(errors)
    assert "data/local_files" in joined
    assert ".pdf" in joined
    assert "real entry-like numeric id" in joined


def test_no_src_code_references_candidate_or_prior_static_routing_prompt_artifacts() -> None:
    forbidden_terms = (
        CANDIDATE_OUTPUT_PATH.name,
        EXPECTED_OUTPUT_PATH.name,
        HELPER_PATH.name,
        REVIEW_CASES_PATH.name,
        "routing_agent_candidate_outputs",
        "routing_agent_static_candidate_output_comparator",
        "routing_agent_expected_outputs",
        "routing_agent_static_expected_output_evaluator",
        "routing_agent_prompt_review_cases",
        "routing_agent_static_fixture_checker",
        "ROUTING_AGENT_PROMPT_DRAFT",
        "ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES",
        "ROUTING_AGENT_STATIC_EXPECTED_OUTPUT_EVALUATOR",
        "ROUTING_AGENT_STATIC_CANDIDATE_OUTPUT_COMPARATOR",
        "docs/prompts/drafts",
        "prompts/drafts",
    )

    assert not (SRC_DIR / "agents" / "prompts.py").exists()

    for path in sorted(SRC_DIR.rglob("*.py")):
        source = read_text(path)
        relative = path.relative_to(REPO_ROOT)
        for term in forbidden_terms:
            assert term not in source, f"{relative} must not reference {term!r}"


def test_disabled_prompt_draft_and_prior_static_docs_remain_non_runtime_non_activation() -> None:
    draft = read_text(DRAFT_PATH)
    gate = read_text(GATE_PATH)
    fixture_doc = read_text(FIXTURE_DOC_PATH)
    checker_doc = read_text(CHECKER_DOC_PATH)
    expected_doc = read_text(EXPECTED_DOC_PATH)

    assert_contains_all(
        draft,
        (
            "status: draft_documented",
            "activation_status: disabled",
            "documentation-only",
            "non-runtime",
            "non-consumed",
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
    assert_contains_all(
        fixture_doc,
        (
            "Codex 030 does not activate the prompt",
            "Codex 030 does not approve the prompt for mock execution",
            "Codex 030 does not load, render, execute or consume the prompt",
        ),
    )
    assert_contains_all(
        checker_doc,
        (
            "Codex 031 does not activate the prompt",
            "Codex 031 does not approve mock execution",
            "Codex 031 does not load, render, execute or consume the prompt",
        ),
    )
    assert_contains_all(
        expected_doc,
        (
            "Codex 032 does not activate the prompt",
            "Codex 032 does not approve mock execution",
            "Codex 032 does not load, render, execute or consume the prompt",
        ),
    )


def test_candidate_fixture_json_is_stable_and_parseable() -> None:
    raw = json.loads(CANDIDATE_OUTPUT_PATH.read_text(encoding="utf-8"))

    assert isinstance(raw, dict)
    assert raw == load_candidates()
