from __future__ import annotations

import ast
import re
import unicodedata
from pathlib import Path

from helpers import routing_agent_disabled_prompt_draft_boundary_checker as checker


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
DOC_PATH = DOCS_DIR / "ROUTING_AGENT_DISABLED_PROMPT_DRAFT_ACCESS_BOUNDARY_v0.2.3-auto.md"
DRAFT_PATH = DOCS_DIR / "prompts" / "drafts" / "ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md"
HELPER_PATH = (
    REPO_ROOT
    / "tests"
    / "helpers"
    / "routing_agent_disabled_prompt_draft_boundary_checker.py"
)
SRC_DIR = REPO_ROOT / "src" / "dico_impro"


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


def joined_errors(errors: list[str]) -> str:
    return "\n".join(errors)


def imported_modules(path: Path) -> tuple[str, ...]:
    tree = ast.parse(read_text(path))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.append(node.module)
    return tuple(modules)


def test_access_boundary_doc_exists_and_declares_docs_tests_only_scope() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "Status: Codex 034 disabled prompt draft access boundary",
            "disabled prompt draft access boundary",
            "documentation/tests only",
            "docs/tests-only",
            "plain markdown inspection only",
            "documentation/test-only",
            "non-runtime",
            "non-consuming",
            "non-rendering",
            "non-execution",
            "non-activation",
            "non-approval",
            "non-LLM",
            "not a prompt evaluator runtime",
            "not a mock execution harness",
            "not model-output scoring",
        ),
    )


def test_access_boundary_doc_states_allowed_and_forbidden_distinction() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "Codex 034 does not activate the prompt",
            "Codex 034 does not approve mock execution",
            "Codex 034 does not approve runtime",
            "Codex 034 does not render, execute or consume the prompt",
            "Codex 034 only permits test-only markdown inspection",
            "Codex 034 does not claim RoutingAgent works",
            "Codex 034 does not evaluate model behavior",
            "Reading the markdown file as documentation is allowed in tests; consuming the markdown as an executable prompt is forbidden.",
            "read the draft markdown file in tests",
            "inspect textual markers",
            "verify lifecycle/status vocabulary",
            "verify explicit denial flags or phrases",
            "verify required sections exist",
            "verify no forbidden runtime references are introduced",
            "verify no production code references the draft",
            "rendering the prompt",
            "building prompt messages",
            "creating chat/completion payloads",
            "using the text as task instructions for an agent",
            "passing it to an adapter",
            "passing it to a fake generator",
            "passing it to CLI",
            "passing it to OpenAI",
            "using it to generate candidate outputs",
            "scoring model output against it",
            "converting it into a runtime PromptPackage",
            "treating it as approved for mock or runtime use",
        ),
    )


def test_access_boundary_doc_references_prior_sources_and_codex_sequence() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "docs/prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md",
            "docs/ROUTING_AGENT_STATIC_CANDIDATE_OUTPUT_COMPARATOR_v0.2.3-auto.md",
            "docs/ROUTING_AGENT_STATIC_EXPECTED_OUTPUT_EVALUATOR_v0.2.3-auto.md",
            "docs/ROUTING_AGENT_STATIC_FIXTURE_CHECKER_v0.2.3-auto.md",
            "docs/ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES_v0.2.3-auto.md",
            "docs/ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md",
            "docs/ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md",
            "docs/ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md",
            "docs/AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md",
            "docs/PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md",
            "docs/PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md",
            "docs/REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md",
            "tests/fixtures/routing_agent_prompt_review_cases.json",
            "tests/fixtures/routing_agent_expected_outputs.json",
            "tests/fixtures/routing_agent_candidate_outputs.json",
            "tests/helpers/routing_agent_static_fixture_checker.py",
            "tests/helpers/routing_agent_static_expected_output_evaluator.py",
            "tests/helpers/routing_agent_static_candidate_output_comparator.py",
            "Codex 028 created a disabled documentation-only prompt draft",
            "Codex 029 added a review gate",
            "Codex 030 added synthetic review fixtures",
            "Codex 031 added static fixture checking",
            "Codex 032 added expected outputs",
            "Codex 033 added candidate outputs and comparator diagnostics",
            "Codex 034 now defines the safe test-only access boundary",
            "Codex 034 does not consume the prompt",
        ),
    )


def test_access_boundary_doc_documents_checker_responsibilities_and_markers() -> None:
    document = read_text(DOC_PATH)

    assert_contains_all(
        document,
        (
            "tests/helpers/routing_agent_disabled_prompt_draft_boundary_checker.py",
            "read the disabled prompt draft markdown as text",
            "validate required status markers",
            "validate required denial markers",
            "validate required non-runtime/non-consuming/non-activation language",
            "validate that the draft does not declare itself approved",
            "validate that no source file under `src/` references the prompt draft path",
            "validate that no `src/` file contains runtime prompt-loading names",
            "validate that tests/helper code imports only the Python standard library",
            "return human-readable errors",
            "validate_draft_access_metadata(text: str) -> list[str]",
            "validate_disabled_status_markers(text: str) -> list[str]",
            "validate_denial_markers(text: str) -> list[str]",
            "validate_no_approval_markers(text: str) -> list[str]",
            "validate_no_src_prompt_references(repo_root: Path) -> list[str]",
            "validate_helper_import_boundaries(helper_path: Path) -> list[str]",
            "validate_disabled_prompt_draft_access_boundary(repo_root: Path) -> list[str]",
            "Use only Python standard library",
            "Do not use pydantic",
            "Do not import from `src/dico_impro`",
            "Do not create production contracts",
            "Do not create a reusable runtime prompt loader",
            "draft_documented",
            "disabled",
            "documentation-only",
            "non-runtime",
            "non-consumed",
            "non-activation",
            "non-approval",
            "not approved for mock execution",
            "not approved for runtime",
            "not approved for OpenAI",
            "not approved for RUN",
            "not final contracts",
            "not runtime enums",
            "positive approval language",
        ),
    )


def test_access_boundary_doc_verdict_denies_activation_runtime_and_prompt_use() -> None:
    document = read_text(DOC_PATH)
    verdict = extract_markdown_section(document, "7. Verdict")

    assert_contains_all(
        verdict,
        (
            "Disabled prompt draft access boundary created: YES.",
            "Plain markdown inspection in tests allowed: YES.",
            "Prompt consumed as executable prompt: NO.",
            "Prompt rendered: NO.",
            "Prompt executed: NO.",
            "Model output scored: NO.",
            "Approved for mock execution: NO.",
            "Approved for runtime: NO.",
            "Approved for CLI consumption: NO.",
            "Approved for OpenAI: NO.",
            "Approved for RUN: NO.",
            "Approved for final contracts/enums: NO.",
            "Approved for journal mutation: NO.",
        ),
    )
    assert re.findall(r": YES\b", verdict) == [": YES", ": YES"]


def test_boundary_checker_exists_and_uses_only_test_safe_imports() -> None:
    source = read_text(HELPER_PATH)
    modules = imported_modules(HELPER_PATH)

    assert checker.validate_helper_import_boundaries(HELPER_PATH) == []
    assert "import dico_impro" not in source
    assert "from dico_impro" not in source
    assert "from src" not in source
    assert "import openai" not in source
    assert "import requests" not in source

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
        for module in modules
        if any(module == prefix or module.startswith(f"{prefix}.") for prefix in forbidden_import_prefixes)
    ]
    assert not forbidden, f"Boundary helper imports forbidden modules: {forbidden!r}"


def test_disabled_prompt_draft_contains_required_status_and_denial_markers() -> None:
    draft = read_text(DRAFT_PATH)

    assert checker.validate_draft_access_metadata(draft) == []
    assert checker.validate_disabled_status_markers(draft) == []
    assert checker.validate_denial_markers(draft) == []
    assert checker.validate_no_approval_markers(draft) == []


def test_no_src_code_references_disabled_prompt_draft_or_static_review_artifacts() -> None:
    forbidden_terms = (
        "docs/prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md",
        "ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md",
        "routing_agent_prompt_review_cases.json",
        "routing_agent_expected_outputs.json",
        "routing_agent_candidate_outputs.json",
        "routing_agent_static_fixture_checker",
        "routing_agent_static_expected_output_evaluator",
        "routing_agent_static_candidate_output_comparator",
        "routing_agent_disabled_prompt_draft_boundary_checker",
        "render_prompt",
        "load_prompt",
        "execute_prompt",
        "consume_prompt",
        "prompt_loader",
        "prompt_registry",
        "ROUTING_AGENT_PROMPT_DRAFT",
    )

    assert not (SRC_DIR / "agents" / "prompts.py").exists()
    assert checker.validate_no_src_prompt_references(REPO_ROOT) == []

    for path in sorted(SRC_DIR.rglob("*.py")):
        source = read_text(path)
        relative = path.relative_to(REPO_ROOT)
        for term in forbidden_terms:
            assert term not in source, f"{relative} must not reference {term!r}"


def test_validate_disabled_prompt_draft_access_boundary_returns_no_errors() -> None:
    errors = checker.validate_disabled_prompt_draft_access_boundary(REPO_ROOT)

    assert errors == []


def test_status_marker_validation_fails_on_missing_disabled_marker() -> None:
    text = "status: draft_documented documentation-only non-runtime non-consumed"

    errors = checker.validate_disabled_status_markers(text)

    assert "required marker is missing: disabled" in errors


def test_status_marker_validation_fails_on_missing_non_runtime_marker() -> None:
    text = "status: draft_documented disabled documentation-only non-consumed"

    errors = checker.validate_disabled_status_markers(text)

    assert "required marker is missing: non-runtime" in errors


def test_positive_approval_validation_fails_on_approved_for_runtime_language() -> None:
    errors = checker.validate_no_approval_markers("This prompt is approved for runtime.")

    assert "positive approval marker is forbidden: approved for runtime" in errors


def test_positive_approval_validation_fails_on_approved_for_mock_language() -> None:
    errors = checker.validate_no_approval_markers(
        "This prompt is approved for mock execution."
    )

    assert "positive approval marker is forbidden: approved for mock execution" in errors


def test_positive_approval_validation_fails_on_approved_for_openai_language() -> None:
    errors = checker.validate_no_approval_markers("This prompt is approved for OpenAI.")

    assert "positive approval marker is forbidden: approved for OpenAI" in errors


def test_positive_approval_validation_allows_negative_denial_language() -> None:
    text = (
        "No active prompt exists. This prompt is not approved for runtime. "
        "Approved for OpenAI: NO. Runtime prompt loading is forbidden."
    )

    errors = checker.validate_no_approval_markers(text)

    assert errors == []


def test_src_reference_validation_fails_on_prompt_draft_reference(tmp_path: Path) -> None:
    source_dir = tmp_path / "src" / "dico_impro"
    source_dir.mkdir(parents=True)
    (source_dir / "module.py").write_text(
        'DRAFT = "docs/prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md"\n',
        encoding="utf-8",
    )

    errors = checker.validate_no_src_prompt_references(tmp_path)

    assert "ROUTING_AGENT_PROMPT_DRAFT".casefold() in joined_errors(errors)


def test_src_reference_validation_fails_on_candidate_outputs_reference(tmp_path: Path) -> None:
    source_dir = tmp_path / "src" / "dico_impro"
    source_dir.mkdir(parents=True)
    (source_dir / "module.py").write_text(
        'FIXTURE = "routing_agent_candidate_outputs.json"\n',
        encoding="utf-8",
    )

    errors = checker.validate_no_src_prompt_references(tmp_path)

    assert "routing_agent_candidate_outputs.json" in joined_errors(errors)


def test_src_reference_validation_fails_on_runtime_prompt_loading_name(tmp_path: Path) -> None:
    source_dir = tmp_path / "src" / "dico_impro"
    source_dir.mkdir(parents=True)
    (source_dir / "module.py").write_text(
        "def render_prompt():\n    return ''\n",
        encoding="utf-8",
    )

    errors = checker.validate_no_src_prompt_references(tmp_path)

    assert "render_prompt" in joined_errors(errors)


def test_helper_import_boundary_fails_on_src_dico_impro_import(tmp_path: Path) -> None:
    helper_path = tmp_path / "helper.py"
    helper_path.write_text("from dico_impro.models import Entry\n", encoding="utf-8")

    errors = checker.validate_helper_import_boundaries(helper_path)

    assert "imports forbidden module: dico_impro.models" in joined_errors(errors)


def test_helper_import_boundary_fails_on_openai_or_requests_imports(tmp_path: Path) -> None:
    helper_path = tmp_path / "helper.py"
    helper_path.write_text("import openai\nimport requests\n", encoding="utf-8")

    errors = checker.validate_helper_import_boundaries(helper_path)
    joined = joined_errors(errors)

    assert "imports forbidden module: openai" in joined
    assert "imports forbidden module: requests" in joined
