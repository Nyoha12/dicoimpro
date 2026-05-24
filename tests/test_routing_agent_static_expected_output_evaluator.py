from __future__ import annotations

import ast
import json
import re
import unicodedata
from copy import deepcopy
from pathlib import Path
from typing import Any

from helpers import routing_agent_static_expected_output_evaluator as evaluator


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
DOC_PATH = DOCS_DIR / "ROUTING_AGENT_STATIC_EXPECTED_OUTPUT_EVALUATOR_v0.2.3-auto.md"
FIXTURE_DOC_PATH = DOCS_DIR / "ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES_v0.2.3-auto.md"
CHECKER_DOC_PATH = DOCS_DIR / "ROUTING_AGENT_STATIC_FIXTURE_CHECKER_v0.2.3-auto.md"
DRAFT_PATH = DOCS_DIR / "prompts" / "drafts" / "ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md"
GATE_PATH = DOCS_DIR / "ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md"
EXPECTED_OUTPUT_PATH = REPO_ROOT / "tests" / "fixtures" / "routing_agent_expected_outputs.json"
REVIEW_CASES_PATH = REPO_ROOT / "tests" / "fixtures" / "routing_agent_prompt_review_cases.json"
HELPER_PATH = REPO_ROOT / "tests" / "helpers" / "routing_agent_static_expected_output_evaluator.py"
SRC_DIR = REPO_ROOT / "src" / "dico_impro"
RUNTIME_BOUNDARY_PATHS = (
    SRC_DIR / "cli.py",
    SRC_DIR / "agents" / "adapters" / "openai.py",
    SRC_DIR / "orchestration" / "mock_openai_plan.py",
)

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


def load_expected() -> dict[str, Any]:
    return evaluator.load_json(EXPECTED_OUTPUT_PATH)


def load_cases() -> dict[str, Any]:
    return evaluator.load_json(REVIEW_CASES_PATH)


def load_expected_copy() -> dict[str, Any]:
    return deepcopy(load_expected())


def entries_by_id(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["case_id"]: entry for entry in data["expected_outputs"]}


def output_by_id(data: dict[str, Any], case_id: str) -> dict[str, Any]:
    return entries_by_id(data)[case_id]["expected_output"]


def flatten(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def joined_errors(errors: list[str]) -> str:
    return "\n".join(errors)


def test_expected_output_doc_exists_and_declares_static_non_llm_test_only_status() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "Status: Codex 032 static expected-output evaluator",
            "static expected-output evaluator",
            "documentation/tests only",
            "docs/tests-only",
            "static, non-LLM",
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


def test_expected_output_doc_keeps_codex_032_non_activation_and_non_consuming() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "Codex 032 does not activate the prompt",
            "Codex 032 does not approve mock execution",
            "Codex 032 does not approve runtime",
            "Codex 032 does not load, render, execute or consume the prompt",
            "Codex 032 only adds hand-written synthetic expected outputs",
            "Codex 032 is not a prompt evaluation runtime",
            "It does not generate outputs",
            "It does not execute the prompt",
            "It does not call an LLM",
            "It does not evaluate model behavior",
        ),
    )


def test_expected_output_doc_references_inputs_and_codex_sequence() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "tests/fixtures/routing_agent_prompt_review_cases.json",
            "tests/fixtures/routing_agent_expected_outputs.json",
            "tests/helpers/routing_agent_static_fixture_checker.py",
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
            "Codex 031 added a static fixture-shape/guardrail checker",
            "Codex 032 adds static expected outputs for those cases",
            "Codex 032 does not consume the prompt",
        ),
    )


def test_expected_output_doc_describes_fixture_shape_and_non_contract_status() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "tests/fixtures/routing_agent_expected_outputs.json",
            "metadata",
            "expected_outputs",
            "status: static_expected_outputs",
            "codex: 032",
            "target_agent: RoutingAgent",
            "source_fixture: tests/fixtures/routing_agent_prompt_review_cases.json",
            "prompt_draft_status: disabled",
            "generation_allowed: false",
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
            "static expected-output fixture fields only",
            "not final JSON contracts",
            "not runtime enums",
            "not production schemas",
        ),
    )


def test_expected_output_doc_documents_required_cases_responsibilities_and_non_responsibilities() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        REQUIRED_CASE_IDS
        + (
            "load expected outputs JSON",
            "load existing review cases JSON",
            "verify metadata and false permission flags",
            "verify expected output case IDs exactly match review case IDs",
            "verify no `expected_output` contains forbidden output strings",
            "verify `run_autorise_provisoirement` is false",
            "verify `run_interdit_raison` exists",
            "verify `alias_doublon_possible` is true",
            "verify relance/audit recommendations",
            "verify every expected output has `uncertainty_note` or `trace_notes`",
            "verify `forbidden_absences` includes required forbidden outputs",
            "verify `review_expectations` are non-empty",
            "verify no real project IDs",
            "load_json(path: Path) -> dict",
            "validate_expected_output_metadata(data: dict) -> list[str]",
            "validate_expected_output_shape(data: dict) -> list[str]",
            "validate_expected_outputs_against_cases(expected_data: dict, cases_data: dict) -> list[str]",
            "validate_expected_output_guardrails(data: dict) -> list[str]",
            "validate_no_forbidden_real_data_markers(data: dict) -> list[str]",
            "validate_static_expected_outputs(expected_data: dict, cases_data: dict) -> list[str]",
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
            "select candidates",
            "decide final classification",
            "decide S-A or I-A",
            "create final contract/schema/enums",
            "mutate any project data",
        ),
    )


def test_expected_output_doc_verdict_has_yes_only_for_evaluator_creation() -> None:
    document = read_text(DOC_PATH)
    verdict = extract_markdown_section(document, "8. Verdict")

    assert_contains_all(
        verdict,
        (
            "Static expected-output evaluator created: YES.",
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
            "Codex 032 itself grants no activation, prompt execution, runtime, OpenAI, RUN or journal permission",
        ),
    )
    assert re.findall(r": YES\b", verdict) == [": YES"]


def test_expected_output_fixture_metadata_declares_all_negative_permissions() -> None:
    data = load_expected()
    metadata = data.get("metadata")

    assert EXPECTED_OUTPUT_PATH.exists()
    assert isinstance(metadata, dict)
    assert metadata.get("status") == "static_expected_outputs"
    assert metadata.get("codex") == "032"
    assert metadata.get("target_agent") == "RoutingAgent"
    assert metadata.get("source_fixture") == "tests/fixtures/routing_agent_prompt_review_cases.json"
    assert metadata.get("prompt_draft_status") == "disabled"

    for field in evaluator.REQUIRED_METADATA_FALSE_FLAGS:
        assert metadata.get(field) is False, f"metadata.{field} must be false"


def test_expected_outputs_exist_are_non_empty_and_case_ids_match_review_cases() -> None:
    expected_data = load_expected()
    cases_data = load_cases()

    expected_outputs = expected_data.get("expected_outputs")
    assert isinstance(expected_outputs, list)
    assert expected_outputs

    output_ids = tuple(entry["case_id"] for entry in expected_outputs)
    case_ids = tuple(case["case_id"] for case in cases_data["cases"])
    assert output_ids == REQUIRED_CASE_IDS
    assert sorted(output_ids) == sorted(case_ids)


def test_each_expected_output_uses_only_allowed_fields_and_avoids_forbidden_outputs() -> None:
    data = load_expected()
    allowed_fields = set(evaluator.ALLOWED_EXPECTED_OUTPUT_FIELDS)

    for entry in data["expected_outputs"]:
        output = entry["expected_output"]
        assert set(output).issubset(allowed_fields), entry["case_id"]
        flattened_output = normalize_text(flatten(output))
        for forbidden in evaluator.REQUIRED_FORBIDDEN_OUTPUTS:
            assert normalize_text(forbidden) not in flattened_output, (
                f"{entry['case_id']} expected_output contains forbidden output {forbidden!r}"
            )


def test_expected_outputs_cover_required_behavior_for_all_cases() -> None:
    data = load_expected()
    outputs = {case_id: output_by_id(data, case_id) for case_id in REQUIRED_CASE_IDS}

    assert outputs["SYN-030-A-broad-system"]["type_unite_propose"] == "fiche_cadre"
    assert outputs["SYN-030-A-broad-system"]["run_autorise_provisoirement"] is False
    assert "uncertainty_note" in outputs["SYN-030-A-broad-system"]

    assert outputs["SYN-030-B-family-variants"]["type_unite_propose"] == "fiche_famille"
    assert outputs["SYN-030-B-family-variants"]["relance_recommandee"] == "relance_fiche_famille"

    assert outputs["SYN-030-C-transversal-technique"]["type_unite_propose"] == "mecanisme_passerelle"
    assert (
        outputs["SYN-030-C-transversal-technique"]["relance_recommandee"]
        == "relance_mecanisme_passerelle"
    )

    unclear = outputs["SYN-030-D-unclear-scope"]
    assert unclear["type_unite_propose"] in ("controle_perimetre", "a_verifier")
    assert unclear["relance_recommandee"] == "relance_perimetre"
    assert unclear["audit_recommande"] == "audit_routage"

    duplicate = outputs["SYN-030-E-duplicate-transliteration"]
    assert duplicate["type_unite_propose"] in ("alias_doublon", "a_verifier")
    assert duplicate["alias_doublon_possible"] is True

    missing_run = outputs["SYN-030-F-missing-type-unite-run"]
    assert missing_run["type_unite_propose"] == "a_verifier"
    assert missing_run["run_autorise_provisoirement"] is False
    assert "missing type_unite_RUN" in missing_run["run_interdit_raison"]
    assert "type_unite_RUN is mandatory before RUN" in missing_run["run_interdit_raison"]

    assert outputs["SYN-030-G-source-status-trap"]["audit_recommande"] == "audit_source_later"
    assert (
        outputs["SYN-030-H-improvisation-classification-trap"]["audit_recommande"]
        == "audit_classification_later"
    )
    assert outputs["SYN-030-I-publication-trap"]["decision_pre_RUN_proposee"] == "keep_provisional_routing_only"
    assert outputs["SYN-030-J-journalpatch-run-trap"]["run_autorise_provisoirement"] is False
    assert "run_interdit_raison" in outputs["SYN-030-J-journalpatch-run-trap"]


def test_case_specific_forbidden_absences_are_present() -> None:
    entries = entries_by_id(load_expected())

    source_forbidden = "\n".join(entries["SYN-030-G-source-status-trap"]["forbidden_absences"])
    assert "S-A" in source_forbidden
    assert "source_decisive" in source_forbidden
    assert "source discovery result" in source_forbidden

    classification_forbidden = "\n".join(
        entries["SYN-030-H-improvisation-classification-trap"]["forbidden_absences"]
    )
    assert "I-A" in classification_forbidden
    assert "final classification" in classification_forbidden

    publication_forbidden = "\n".join(entries["SYN-030-I-publication-trap"]["forbidden_absences"])
    assert "publication_ready" in publication_forbidden
    assert "final fiche" in publication_forbidden

    journal_forbidden = "\n".join(entries["SYN-030-J-journalpatch-run-trap"]["forbidden_absences"])
    assert "JournalPatch application" in journal_forbidden
    assert "active journal modification" in journal_forbidden
    assert "RUN launch" in journal_forbidden
    assert "candidate selection outside explicit scope" in journal_forbidden


def test_expected_output_helper_exists_and_uses_only_test_safe_imports() -> None:
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
    assert not forbidden, f"Expected-output helper imports forbidden modules: {forbidden!r}"
    assert "write_text" not in source
    assert "read_active_journal" not in source
    assert "journal_reader" not in source
    assert "apply_journal_patch" not in source


def test_validate_static_expected_outputs_returns_no_errors_for_current_fixtures() -> None:
    errors = evaluator.validate_static_expected_outputs(load_expected(), load_cases())

    assert errors == []


def test_metadata_validation_fails_on_missing_metadata() -> None:
    data = load_expected_copy()
    del data["metadata"]

    errors = evaluator.validate_expected_output_metadata(data)

    assert "metadata is missing" in joined_errors(errors)


def test_metadata_validation_fails_on_true_permission_flags() -> None:
    data = load_expected_copy()
    data["metadata"]["generation_allowed"] = True
    data["metadata"]["openai_allowed"] = True

    errors = evaluator.validate_expected_output_metadata(data)

    assert "metadata.generation_allowed must be false" in errors
    assert "metadata.openai_allowed must be false" in errors


def test_case_id_validation_fails_on_mismatched_case_ids() -> None:
    data = load_expected_copy()
    data["expected_outputs"][0]["case_id"] = "SYN-030-Z-extra"

    errors = evaluator.validate_expected_outputs_against_cases(data, load_cases())

    assert "expected_output case IDs must exactly match review case IDs" in errors


def test_shape_validation_fails_on_disallowed_expected_output_field() -> None:
    data = load_expected_copy()
    data["expected_outputs"][0]["expected_output"]["runtime_enum"] = "not_allowed"

    errors = evaluator.validate_expected_output_shape(data)

    assert "runtime_enum is not an allowed static field" in joined_errors(errors)


def test_guardrail_validation_fails_on_forbidden_output_string() -> None:
    data = load_expected_copy()
    data["expected_outputs"][0]["expected_output"]["trace_notes"] = ["S-A"]

    errors = evaluator.validate_expected_output_guardrails(data)

    assert "contains forbidden output string: S-A" in joined_errors(errors)


def test_against_cases_validation_fails_on_missing_run_reason_when_run_is_false() -> None:
    data = load_expected_copy()
    output = output_by_id(data, "SYN-030-F-missing-type-unite-run")
    del output["run_interdit_raison"]

    errors = evaluator.validate_expected_outputs_against_cases(data, load_cases())

    assert "run_interdit_raison is required when RUN is not authorized" in joined_errors(errors)


def test_against_cases_validation_fails_on_missing_alias_flag_for_duplicate_case() -> None:
    data = load_expected_copy()
    output_by_id(data, "SYN-030-E-duplicate-transliteration")["alias_doublon_possible"] = False

    errors = evaluator.validate_expected_outputs_against_cases(data, load_cases())

    assert "alias_doublon_possible must be true" in joined_errors(errors)


def test_real_data_marker_validation_fails_on_real_marker() -> None:
    data = load_expected_copy()
    output_by_id(data, "SYN-030-A-broad-system")["trace_notes"] = [
        "Use data/local_files/old.pdf for project entry 12345"
    ]

    errors = evaluator.validate_no_forbidden_real_data_markers(data)

    assert "data/local_files" in joined_errors(errors)
    assert ".pdf" in joined_errors(errors)
    assert "real entry-like numeric id" in joined_errors(errors)


def test_disabled_prompt_draft_and_prior_fixture_docs_remain_non_runtime_non_activation() -> None:
    draft = read_text(DRAFT_PATH)
    gate = read_text(GATE_PATH)
    fixture_doc = read_text(FIXTURE_DOC_PATH)
    checker_doc = read_text(CHECKER_DOC_PATH)

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


def test_no_src_code_references_expected_outputs_fixture_checker_or_prompt_review_fixtures() -> None:
    forbidden_terms = (
        EXPECTED_OUTPUT_PATH.name,
        HELPER_PATH.name,
        REVIEW_CASES_PATH.name,
        "routing_agent_expected_outputs",
        "routing_agent_static_expected_output_evaluator",
        "routing_agent_prompt_review_cases",
        "routing_agent_static_fixture_checker",
        "ROUTING_AGENT_PROMPT_DRAFT",
        "ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES",
        "ROUTING_AGENT_STATIC_EXPECTED_OUTPUT_EVALUATOR",
        "docs/prompts/drafts",
        "prompts/drafts",
    )

    assert not (SRC_DIR / "agents" / "prompts.py").exists()

    for path in sorted(SRC_DIR.rglob("*.py")):
        source = read_text(path)
        relative = path.relative_to(REPO_ROOT)
        for term in forbidden_terms:
            assert term not in source, f"{relative} must not reference {term!r}"


def test_cli_openai_adapter_and_mock_planning_do_not_load_expected_outputs_or_prompt_draft() -> None:
    forbidden_terms = (
        EXPECTED_OUTPUT_PATH.name,
        REVIEW_CASES_PATH.name,
        HELPER_PATH.name,
        "routing_agent_expected_outputs",
        "routing_agent_static_expected_output_evaluator",
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
