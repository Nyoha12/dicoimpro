from __future__ import annotations

import ast
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unicodedata
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
DICOIMPRO_DIR = REPO_ROOT / ".dicoimpro"
DOCS_DIR = REPO_ROOT / "docs"
SCRIPTS_DIR = REPO_ROOT / "scripts"
SRC_DIR = REPO_ROOT / "src" / "dico_impro"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

COACH_STEP_PATH = SCRIPTS_DIR / "coach_step.py"
COACH_STATE_PATH = SCRIPTS_DIR / "coach_state.py"
WORKFLOW_DOC_PATH = DOCS_DIR / "WORKFLOW_COACH_GPT_STAGE_RUNNER_v0.2.3-auto.md"
README_PATH = DOCS_DIR / "README.md"
POST_015_REVIEW_PATH = DOCS_DIR / "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md"
COACH_GUIDANCE_PATH = DICOIMPRO_DIR / "COACH_GUIDANCE.md"
STAGE_SCHEMA_PATH = DICOIMPRO_DIR / "STAGE_OUTPUT_SCHEMA.md"
WORKFLOW_STATE_PATH = DICOIMPRO_DIR / "WORKFLOW_STATE.example.json"

FORBIDDEN_IMPORT_ROOTS = {
    "codex",
    "dico_impro",
    "github",
    "httpx",
    "openai",
    "pydantic",
    "requests",
    "src",
}


VALID_SAMPLE_NOTE = """---
run_id: codex_037_example
stage: pre_cadrage
created_at: 2026-05-26T00:00:00Z
input_refs: []
repo_context_refs: []
previous_stage_ref: null
can_advance: true
reflection_required: false
next_stage: cadrage
next_prompt_type: stage_prompt
next_prompt_path_suggested: .dicoimpro/runs/codex_037_example/02_cadrage_prompt.md
blocking_question: null
guardrail_risk_level: low
---

## 1. Stage objective

Frame the next bounded stage.

## 2. Inputs used

Local context packet and workflow state.

## 3. Repository context summary

The repository context is sufficient for the next stage.

## 4. Current-stage analysis summary

Shareable summary only.

## 5. Resolved points

The state and context are available.

## 6. Unresolved points

None.

## 7. Guardrail and scope check

No runtime activation is authorized.

## 8. Transition gate

```yaml
transition_gate:
  evaluated_next_stage: cadrage
  can_advance: true
  reflection_required: false
  next_prompt_ready: true
  next_prompt_type: stage_prompt
  blocking_question: null
  reason: "The next stage has enough context."
  required_user_intervention: false
  allowed_to_execute_automatically: false
```

## 9. Next prompt

next_prompt_type: stage_prompt

next_prompt:
Ask GPT-5.5 Thinking to produce the cadrage note from the local context.
"""


def read_text(path: Path) -> str:
    assert path.exists(), f"Required file is missing: {path}"
    return path.read_text(encoding="utf-8")


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return " ".join(without_accents.casefold().split())


def load_script_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(read_text(path), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                roots.add(node.module.split(".", 1)[0])
            elif node.level:
                roots.add("<relative>")
    return roots


def copy_minimal_repo_like_folder(destination: Path) -> None:
    dicoimpro = destination / ".dicoimpro"
    runs = dicoimpro / "runs" / "codex_037_temp"
    runs.mkdir(parents=True)
    shutil.copy2(COACH_GUIDANCE_PATH, dicoimpro / "COACH_GUIDANCE.md")
    shutil.copy2(STAGE_SCHEMA_PATH, dicoimpro / "STAGE_OUTPUT_SCHEMA.md")
    shutil.copy2(WORKFLOW_STATE_PATH, dicoimpro / "WORKFLOW_STATE.example.json")
    (runs / "00_context.md").write_text("# Context\n\nLocal test context.\n", encoding="utf-8")


def git_status_for(pathspec: str) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--", pathspec],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def test_coach_step_script_and_workflow_doc_exist():
    assert COACH_STEP_PATH.exists()
    assert WORKFLOW_DOC_PATH.exists()


def test_coach_step_has_no_forbidden_top_level_imports():
    imports = imported_roots(COACH_STEP_PATH)
    forbidden = sorted(imports.intersection(FORBIDDEN_IMPORT_ROOTS))
    assert forbidden == [], f"coach_step.py imports forbidden modules: {forbidden!r}"


def test_coach_step_uses_lazy_dynamic_openai_import_only():
    source = read_text(COACH_STEP_PATH)
    tree = ast.parse(source, filename=str(COACH_STEP_PATH))

    direct_openai_imports = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        and any(
            name == "openai" or name.startswith("openai.")
            for name in (
                [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""]
            )
        )
    ]
    assert direct_openai_imports == []
    assert 'import_module("openai")' in source
    assert "def lazy_openai_client" in source
    assert "def execute_openai_response" in source


def test_coach_step_exposes_expected_cli_commands():
    result = subprocess.run(
        [sys.executable, str(COACH_STEP_PATH), "--help"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    help_text = result.stdout
    for command in ("prepare", "run", "validate-note", "extract-gate"):
        assert command in help_text


def test_prepare_mode_writes_prompt_without_calling_api():
    coach_step = load_script_module("coach_step_prepare_under_test", COACH_STEP_PATH)
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_like = Path(temp_dir) / "repo"
        copy_minimal_repo_like_folder(repo_like)

        prompt = coach_step.build_stage_prompt(
            repo_like,
            "codex_037_temp",
            "pre_cadrage",
            previous_note=None,
            user_instruction="Focus on the next local scaffold stage.",
        )
        prompt_path = coach_step.write_stage_prompt(
            repo_like,
            "codex_037_temp",
            "pre_cadrage",
            prompt,
        )

        assert prompt_path.exists()
        written = prompt_path.read_text(encoding="utf-8")
        assert "COACH_GUIDANCE" in written
        assert "STAGE_OUTPUT_SCHEMA" in written
        assert "YAML front matter" in written
        assert "transition_gate" in written
        assert "next_prompt" in written
        assert "shareable reasoning summary" in written
        assert "private chain-of-thought" in written
        assert "Do not invent repository facts absent from the context" in written


def test_api_mode_without_openai_api_key_fails_clearly_without_network_call():
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_like = Path(temp_dir) / "repo"
        copy_minimal_repo_like_folder(repo_like)
        env = os.environ.copy()
        env.pop("OPENAI_API_KEY", None)

        result = subprocess.run(
            [
                sys.executable,
                str(COACH_STEP_PATH),
                "run",
                "--stage",
                "pre_cadrage",
                "--run-id",
                "codex_037_temp",
                "--execute-api",
            ],
            cwd=repo_like,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        assert result.returncode == 1
        assert "OPENAI_API_KEY is required" in result.stderr


def test_api_mode_without_openai_package_fails_when_lazy_import_is_attempted():
    coach_step = load_script_module("coach_step_missing_openai_under_test", COACH_STEP_PATH)

    with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
        with mock.patch.object(
            coach_step.importlib,
            "import_module",
            side_effect=ModuleNotFoundError("openai"),
        ):
            try:
                coach_step.lazy_openai_client()
            except RuntimeError as exc:
                assert "openai package is required" in str(exc)
            else:
                raise AssertionError("Missing openai package must fail clearly")


def test_validate_stage_note_text_accepts_valid_sample_note():
    coach_step = load_script_module("coach_step_validate_under_test", COACH_STEP_PATH)
    assert coach_step.validate_stage_note_text(VALID_SAMPLE_NOTE) == []


def test_validate_stage_note_text_rejects_missing_yaml_front_matter():
    coach_step = load_script_module("coach_step_no_yaml_under_test", COACH_STEP_PATH)
    note = VALID_SAMPLE_NOTE.replace("---\n", "", 1)
    errors = coach_step.validate_stage_note_text(note)
    assert any("YAML front matter" in error for error in errors)


def test_validate_stage_note_text_rejects_missing_transition_gate():
    coach_step = load_script_module("coach_step_no_gate_under_test", COACH_STEP_PATH)
    note = VALID_SAMPLE_NOTE.replace("transition_gate:", "transition_gate_missing:", 1)
    errors = coach_step.validate_stage_note_text(note)
    assert any("transition_gate" in error for error in errors)


def test_validate_stage_note_text_rejects_missing_next_prompt():
    coach_step = load_script_module("coach_step_no_prompt_under_test", COACH_STEP_PATH)
    note = VALID_SAMPLE_NOTE.replace("next_prompt:", "next_prompt_missing:", 1)
    errors = coach_step.validate_stage_note_text(note)
    assert any("next_prompt block" in error for error in errors)


def test_extract_transition_gate_returns_expected_dict():
    coach_step = load_script_module("coach_step_gate_under_test", COACH_STEP_PATH)
    gate = coach_step.extract_transition_gate(VALID_SAMPLE_NOTE)

    assert gate == {
        "allowed_to_execute_automatically": False,
        "blocking_question": None,
        "can_advance": True,
        "evaluated_next_stage": "cadrage",
        "next_prompt_ready": True,
        "next_prompt_type": "stage_prompt",
        "reason": "The next stage has enough context.",
        "reflection_required": False,
        "required_user_intervention": False,
    }


def test_extract_transition_gate_rejects_malformed_gate():
    coach_step = load_script_module("coach_step_bad_gate_under_test", COACH_STEP_PATH)
    note = VALID_SAMPLE_NOTE.replace("  reason:", "  missing_reason:", 1)

    try:
        coach_step.extract_transition_gate(note)
    except ValueError as exc:
        assert "transition_gate" in str(exc)
    else:
        raise AssertionError("Malformed transition_gate must be rejected")


def test_update_state_path_uses_transition_gate_and_refuses_blocked_gates():
    coach_step = load_script_module("coach_step_update_under_test", COACH_STEP_PATH)
    blocked_note = (
        VALID_SAMPLE_NOTE
        .replace("can_advance: true", "can_advance: false")
        .replace("reflection_required: false", "reflection_required: true")
        .replace("next_prompt_type: stage_prompt", "next_prompt_type: reflection_prompt")
        .replace("blocking_question: null", "blocking_question: What blocks the next stage?")
        .replace("  can_advance: true", "  can_advance: false")
        .replace("  reflection_required: false", "  reflection_required: true")
        .replace("  next_prompt_type: stage_prompt", "  next_prompt_type: reflection_prompt")
        .replace("  blocking_question: null", "  blocking_question: What blocks the next stage?")
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        repo_like = Path(temp_dir) / "repo"
        copy_minimal_repo_like_folder(repo_like)
        note_path = repo_like / ".dicoimpro" / "runs" / "codex_037_temp" / "01_pre_cadrage.md"
        note_path.write_text(blocked_note, encoding="utf-8")

        try:
            coach_step.update_local_state_from_note(repo_like, note_path)
        except ValueError as exc:
            assert "can_advance is false" in str(exc)
        else:
            raise AssertionError("Blocked transition_gate must refuse state update")


def test_workflow_doc_records_api_and_runtime_boundaries():
    workflow = normalize_text(read_text(WORKFLOW_DOC_PATH))
    required_phrases = (
        "codex 037 introduces an explicit local gpt coach api path",
        "not dicoimpro application runtime",
        "not routingagent execution",
        "not prompt activation inside `src/`",
        "api is never called by default",
        "--execute-api",
        "openai_api_key",
        "tests never call the api",
        "openai sdk import is lazy/dynamic",
        "no api key is committed, printed, logged, or stored",
        "does not call codex sdk or codex cli",
        "does not run an autonomous loop",
        "does not run run, journal, journalpatch or real data processing",
        "state machine still follows transition_gate",
        "does not invent maturity decisions",
        "repository scripts do not automate pr creation or merge",
    )
    for phrase in required_phrases:
        assert phrase in workflow, f"Workflow doc is missing: {phrase}"


def test_coach_guidance_contains_local_gpt_coach_api_boundary():
    guidance = normalize_text(read_text(COACH_GUIDANCE_PATH))
    required_phrases = (
        "local gpt coach api boundary",
        "authorized only by an explicit workflow command",
        "outside the dicoimpro application runtime",
        "context packets",
        "stage_output_schema",
        "must not activate prompts in `src/`",
        "must not authorize run",
        "journalpatch",
        "real data processing",
        "shareable stage notes",
        "not private chain-of-thought dumps",
    )
    for phrase in required_phrases:
        assert phrase in guidance, f"Coach guidance is missing: {phrase}"


def test_readme_and_post_015_review_reference_codex_037_and_workflow_doc():
    readme = normalize_text(read_text(README_PATH))
    review = normalize_text(read_text(POST_015_REVIEW_PATH))

    assert "workflow_coach_gpt_stage_runner_v0.2.3-auto.md" in readme
    assert "codex 037" in readme
    assert "gpt-5.5 thinking stage runner" in readme
    assert "no api calls by default" in readme

    assert "codex 037" in review
    assert "493 tests passing" in review
    assert "workflow tooling only" in review
    assert "openai runtime dans l'application dicoimpro reste interdit" in review


def test_no_src_files_are_modified_or_reference_coach_step_or_local_gpt_api():
    src_status = git_status_for("src")
    assert src_status == [], f"Codex 037 must not modify src/. Found: {src_status!r}"

    forbidden_terms = (
        "coach_step.py",
        "coach_step",
        "WORKFLOW_COACH_GPT_STAGE_RUNNER",
        "local GPT coach API",
        "GPT coach API",
    )
    for path in SRC_DIR.rglob("*.py"):
        source = read_text(path)
        for term in forbidden_terms:
            assert term not in source, f"{path} must not reference coach GPT runner: {term}"


def test_no_openai_or_codex_dependency_and_no_github_workflow_added():
    pyproject = tomllib.loads(read_text(PYPROJECT_PATH))
    dependency_groups = [
        pyproject.get("project", {}).get("dependencies", []),
        *pyproject.get("project", {}).get("optional-dependencies", {}).values(),
    ]
    dependencies = [
        dependency.casefold()
        for group in dependency_groups
        for dependency in group
    ]

    assert not any("openai" in dependency for dependency in dependencies)
    assert not any("codex" in dependency for dependency in dependencies)

    workflow_status = git_status_for(".github/workflows")
    assert workflow_status == [], (
        "Codex 037 must not add GitHub workflow files. "
        f"Found: {workflow_status!r}"
    )
