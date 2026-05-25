from __future__ import annotations

import json
import subprocess
import tomllib
import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DICOIMPRO_DIR = REPO_ROOT / ".dicoimpro"
DOCS_DIR = REPO_ROOT / "docs"
SRC_DIR = REPO_ROOT / "src" / "dico_impro"

COACH_GUIDANCE_PATH = DICOIMPRO_DIR / "COACH_GUIDANCE.md"
STAGE_OUTPUT_SCHEMA_PATH = DICOIMPRO_DIR / "STAGE_OUTPUT_SCHEMA.md"
WORKFLOW_STATE_PATH = DICOIMPRO_DIR / "WORKFLOW_STATE.example.json"
RUNS_GITKEEP_PATH = DICOIMPRO_DIR / "runs" / ".gitkeep"
WORKFLOW_DOC_PATH = DOCS_DIR / "WORKFLOW_GPT_CODEX_COACH_LOOP_v0.2.3-auto.md"
README_PATH = DOCS_DIR / "README.md"
POST_015_REVIEW_PATH = DOCS_DIR / "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

EXPECTED_STAGES = (
    "context",
    "pre_cadrage",
    "cadrage",
    "decision",
    "codex_prompt",
    "codex_return",
    "post_codex_review",
    "pr_review",
    "post_merge_review",
    "reflection_before_cadrage",
    "reflection_before_decision",
    "reflection_before_codex_prompt",
    "reflection_before_post_codex_review",
    "reflection_before_pr_review",
    "reflection_before_post_merge_review",
)

SENSITIVE_GUARDRAILS = (
    "prompt_activation_allowed",
    "prompt_rendering_allowed",
    "prompt_execution_allowed",
    "openai_runtime_allowed",
    "codex_sdk_allowed",
    "run_allowed",
    "journal_write_allowed",
    "journal_patch_allowed",
    "real_data_allowed",
    "publication_allowed",
)

SENSITIVE_WORKFLOW_PERMISSIONS = (
    "auto_merge_allowed",
    "auto_pr_allowed",
    "autonomous_loop_allowed",
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


def run_git_status(pathspec: str) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--", pathspec],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def test_coach_loop_scaffold_files_exist():
    for path in (
        COACH_GUIDANCE_PATH,
        STAGE_OUTPUT_SCHEMA_PATH,
        WORKFLOW_STATE_PATH,
        RUNS_GITKEEP_PATH,
        WORKFLOW_DOC_PATH,
    ):
        assert path.exists(), f"Missing coach loop scaffold file: {path}"


def test_coach_guidance_defines_roles_reflection_and_transition_rules():
    guidance = read_text(COACH_GUIDANCE_PATH)
    normalized = normalize_text(guidance)

    assert "gpt-5.5 thinking is the local coach and strategist" in normalized
    assert "codex is the executor" in normalized
    assert "reflection is optional, targeted, and unlimited" in normalized
    assert (
        "maturity assessment and next prompt generation happen inside the current "
        "gpt stage output"
    ) in normalized
    assert "no separate mandatory gpt call only to decide maturity" in normalized
    assert "no separate mandatory gpt call only to generate the next prompt" in normalized
    assert "must never advance if `transition_gate.can_advance` is false" in normalized
    assert "must never advance if `transition_gate.next_prompt_ready` is false" in normalized


def test_coach_guidance_contains_core_dicoimpro_guardrails():
    guidance = normalize_text(read_text(COACH_GUIDANCE_PATH))

    required_guardrails = (
        "no prompt activation",
        "no prompt rendering, execution, or consumption",
        "no openai runtime activation inside dicoimpro application code",
        "no run",
        "no journal read/write",
        "no journalpatch application",
        "no real data processing",
        "no publication",
        "no old pdf as an active or decisive source",
    )

    for guardrail in required_guardrails:
        assert guardrail in guidance, f"Missing guardrail: {guardrail}"


def test_stage_output_schema_defines_front_matter_and_transition_gate_fields():
    schema = read_text(STAGE_OUTPUT_SCHEMA_PATH)
    normalized = normalize_text(schema)

    required_front_matter = (
        "run_id",
        "stage",
        "created_at",
        "input_refs",
        "repo_context_refs",
        "previous_stage_ref",
        "can_advance",
        "reflection_required",
        "next_stage",
        "next_prompt_type",
        "next_prompt_path_suggested",
        "blocking_question",
        "guardrail_risk_level",
    )
    required_transition_gate = (
        "evaluated_next_stage",
        "can_advance",
        "reflection_required",
        "next_prompt_ready",
        "next_prompt_type",
        "blocking_question",
        "reason",
        "required_user_intervention",
        "allowed_to_execute_automatically",
    )

    for field in required_front_matter:
        assert f"`{field}`" in schema or f"{field}:" in schema, (
            f"Missing front matter field: {field}"
        )
    for field in required_transition_gate:
        assert f"{field}:" in schema or f"`{field}`" in schema, (
            f"Missing transition_gate field: {field}"
        )

    assert "the `next_prompt` block is mandatory" in normalized
    assert "`stage_prompt`" in schema
    assert "`reflection_prompt`" in schema


def test_stage_output_schema_defines_all_expected_stages_and_reflection_output():
    schema = read_text(STAGE_OUTPUT_SCHEMA_PATH)
    normalized = normalize_text(schema)

    for stage in EXPECTED_STAGES:
        assert f"`{stage}`" in schema, f"Missing stage in schema: {stage}"

    reflection_fields = (
        "target_stage",
        "reflection_index",
        "trigger",
        "blocking_question",
        "analysis_summary",
        "conclusion",
        "updated_transition_gate",
    )
    assert "### reflection" in normalized
    for field in reflection_fields:
        assert f"`{field}`" in schema, f"Missing reflection output field: {field}"


def test_workflow_state_example_parses_and_sensitive_permissions_are_false():
    state = json.loads(read_text(WORKFLOW_STATE_PATH))

    assert state["project"] == "dicoimpro"
    assert state["protocol_version"] == "v0.2.3-auto"
    assert state["last_merged_codex"] == "034"
    assert state["main_tests"] == "466 passed"

    for key in SENSITIVE_GUARDRAILS:
        assert state["guardrails"][key] is False, f"Guardrail must be false: {key}"
    for key in SENSITIVE_WORKFLOW_PERMISSIONS:
        assert state["workflow_permissions"][key] is False, (
            f"Workflow permission must be false: {key}"
        )


def test_workflow_doc_contains_loop_context_model_and_non_implementation_boundaries():
    workflow = normalize_text(read_text(WORKFLOW_DOC_PATH))

    assert "repo context + last merged pr" in workflow
    assert "gpt-5.5 thinking pre_cadrage" in workflow
    assert "codex execution" in workflow
    assert "codex return to gpt-5.5 thinking" in workflow
    assert "repository context packet model" in workflow
    assert "repo context is refreshed at each stage through context packets" in workflow
    assert "context packets must be filtered to avoid token overload" in workflow
    assert "no api call implementation" in workflow
    assert "no codex sdk implementation" in workflow
    assert "no autonomous loop" in workflow
    assert "no production code or runtime behavior change" in workflow


def test_readme_and_post_015_review_reference_codex_035_and_workflow_doc():
    readme = normalize_text(read_text(README_PATH))
    review = normalize_text(read_text(POST_015_REVIEW_PATH))

    assert "codex 035" in readme
    assert "workflow_gpt_codex_coach_loop_v0.2.3-auto.md" in readme
    assert "no api/codex sdk/autonomous loop implemented" in readme or (
        "sans api implementation" in readme
        and "sans codex sdk implementation" in readme
        and "sans autonomous loop" in readme
    )

    assert "codex 035" in review
    assert "466 tests passing" in review
    assert "workflow architecture documentation/tests only" in review
    assert "n'autorise pas openai runtime" in review


def test_no_src_files_are_modified_or_reference_coach_loop_scaffold():
    src_status = run_git_status("src")
    assert src_status == [], f"Codex 035 must not modify src/. Found: {src_status!r}"

    forbidden_terms = (
        ".dicoimpro",
        "COACH_GUIDANCE",
        "STAGE_OUTPUT_SCHEMA",
        "WORKFLOW_STATE",
        "coach loop",
        "GPT-5.5 Thinking",
    )
    for path in SRC_DIR.rglob("*.py"):
        source = read_text(path)
        for term in forbidden_terms:
            assert term not in source, f"{path} must not reference coach loop scaffold: {term}"


def test_no_github_workflow_files_are_added_for_this_codex():
    workflow_status = run_git_status(".github/workflows")
    assert workflow_status == [], (
        "Codex 035 must not add or modify .github/workflows files. "
        f"Found: {workflow_status!r}"
    )


def test_no_codex_sdk_or_openai_api_dependency_is_added():
    pyproject = tomllib.loads(read_text(PYPROJECT_PATH))
    dependency_groups = [
        pyproject.get("project", {}).get("dependencies", []),
        *pyproject.get("project", {}).get("optional-dependencies", {}).values(),
    ]
    dependencies = [dependency.casefold() for group in dependency_groups for dependency in group]

    assert not any("openai" in dependency for dependency in dependencies), (
        f"OpenAI API dependency must not be added. Found dependencies: {dependencies!r}"
    )
    assert not any("codex" in dependency for dependency in dependencies), (
        f"Codex SDK dependency must not be added. Found dependencies: {dependencies!r}"
    )
