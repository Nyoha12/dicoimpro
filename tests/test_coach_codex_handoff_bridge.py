from __future__ import annotations

import ast
import importlib.util
import sys
import tempfile
import tomllib
import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DICOIMPRO_DIR = REPO_ROOT / ".dicoimpro"
DOCS_DIR = REPO_ROOT / "docs"
SCRIPTS_DIR = REPO_ROOT / "scripts"
SRC_DIR = REPO_ROOT / "src" / "dico_impro"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

HANDOFF_SCRIPT_PATH = SCRIPTS_DIR / "coach_codex_handoff.py"
WORKFLOW_DOC_PATH = DOCS_DIR / "WORKFLOW_COACH_CODEX_HANDOFF_BRIDGE_v0.2.3-auto.md"
README_PATH = DOCS_DIR / "README.md"
POST_015_REVIEW_PATH = DOCS_DIR / "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md"
COACH_GUIDANCE_PATH = DICOIMPRO_DIR / "COACH_GUIDANCE.md"

FORBIDDEN_IMPORT_ROOTS = {
    "codex",
    "dico_impro",
    "github",
    "httpx",
    "openai",
    "pydantic",
    "requests",
    "src",
    "subprocess",
}


VALID_CODEX_NOTE = """---
run_id: codex_038_example
stage: codex_prompt
created_at: 2026-05-26T00:00:00Z
input_refs: []
repo_context_refs: []
previous_stage_ref: null
can_advance: true
reflection_required: false
next_stage: codex_return
next_prompt_type: codex_prompt
next_prompt_path_suggested: .dicoimpro/runs/codex_038_example/02_codex_handoff.md
blocking_question: null
guardrail_risk_level: low
---

## 1. Stage objective

Prepare a bounded Codex task.

## 8. Transition gate

```yaml
transition_gate:
  evaluated_next_stage: codex_return
  can_advance: true
  reflection_required: false
  next_prompt_ready: true
  next_prompt_type: codex_prompt
  blocking_question: null
  reason: "The Codex task is ready."
  required_user_intervention: false
  allowed_to_execute_automatically: false
```

## 9. Next prompt

next_prompt_type: codex_prompt

next_prompt:
Implement docs/tests/scripts-only local handoff tooling. Modify only authorized files.
"""


VALID_CODEX_RETURN = """PR URL: https://github.com/example/dicoimpro/pull/38
Commit hash: abc1234
Files changed:
- scripts/coach_codex_handoff.py
- tests/test_coach_codex_handoff_bridge.py
Commands run:
- python -m pytest
- git diff --check
pytest result: 514 passed
git diff --check result: clean
Guardrail guarantee: no src/ modified, no OpenAI call, no Codex SDK/CLI, no autonomous loop.
Not merged.
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


def assert_raises_value_error(callback, expected_text: str) -> None:
    try:
        callback()
    except ValueError as exc:
        assert expected_text in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def write_temp_note(repo_like: Path, note_text: str = VALID_CODEX_NOTE) -> Path:
    run_folder = repo_like / ".dicoimpro" / "runs" / "codex_038_example"
    run_folder.mkdir(parents=True)
    note_path = run_folder / "01_pre_cadrage.md"
    note_path.write_text(note_text, encoding="utf-8")
    return note_path


def test_handoff_script_and_workflow_doc_exist():
    assert HANDOFF_SCRIPT_PATH.exists()
    assert WORKFLOW_DOC_PATH.exists()


def test_handoff_script_imports_only_standard_library():
    imports = imported_roots(HANDOFF_SCRIPT_PATH)
    standard_roots = set(sys.stdlib_module_names) | {"__future__"}
    non_standard = sorted(imports.difference(standard_roots))
    assert non_standard == []


def test_handoff_script_has_no_forbidden_imports_or_subprocess_calls():
    imports = imported_roots(HANDOFF_SCRIPT_PATH)
    forbidden = sorted(imports.intersection(FORBIDDEN_IMPORT_ROOTS))
    assert forbidden == []

    tree = ast.parse(read_text(HANDOFF_SCRIPT_PATH), filename=str(HANDOFF_SCRIPT_PATH))
    subprocess_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
    ]
    assert subprocess_calls == []


def test_cli_exposes_expected_commands():
    source = read_text(HANDOFF_SCRIPT_PATH)
    for command in ("build", "validate-source", "archive-return", "validate-return", "extract-pr"):
        assert f'"{command}"' in source


def test_valid_source_note_with_codex_prompt_passes():
    handoff = load_script_module("coach_codex_handoff_valid_under_test", HANDOFF_SCRIPT_PATH)
    assert handoff.validate_handoff_source(VALID_CODEX_NOTE) == []


def test_source_note_missing_next_prompt_fails():
    handoff = load_script_module("coach_codex_handoff_missing_prompt_under_test", HANDOFF_SCRIPT_PATH)
    note = VALID_CODEX_NOTE.replace("\nnext_prompt:\n", "\nnext_prompt_missing:\n", 1)
    errors = handoff.validate_handoff_source(note)
    assert any("next_prompt block" in error for error in errors)


def test_reflection_prompt_requires_explicit_allowance():
    handoff = load_script_module("coach_codex_handoff_reflection_under_test", HANDOFF_SCRIPT_PATH)
    note = VALID_CODEX_NOTE.replace("codex_prompt", "reflection_prompt")

    errors = handoff.validate_handoff_source(note)
    assert any("next_prompt_type" in error for error in errors)
    assert handoff.validate_handoff_source(note, allow_reflection=True) == []


def test_transition_gate_next_prompt_ready_false_fails():
    handoff = load_script_module("coach_codex_handoff_ready_gate_under_test", HANDOFF_SCRIPT_PATH)
    note = VALID_CODEX_NOTE.replace("  next_prompt_ready: true", "  next_prompt_ready: false")
    errors = handoff.validate_handoff_source(note)
    assert any("next_prompt_ready must be true" in error for error in errors)


def test_transition_gate_can_advance_false_requires_allow_blocked_gate():
    handoff = load_script_module("coach_codex_handoff_blocked_gate_under_test", HANDOFF_SCRIPT_PATH)
    note = VALID_CODEX_NOTE.replace("can_advance: true", "can_advance: false")
    note = note.replace("  can_advance: true", "  can_advance: false")

    errors = handoff.validate_handoff_source(note)
    assert any("can_advance is false" in error for error in errors)
    assert handoff.validate_handoff_source(note, allow_blocked_gate=True) == []


def test_build_codex_handoff_includes_required_sections_and_finalization():
    handoff = load_script_module("coach_codex_handoff_build_under_test", HANDOFF_SCRIPT_PATH)
    packet = handoff.build_codex_handoff(
        VALID_CODEX_NOTE,
        "codex_038_example",
        ".dicoimpro/runs/codex_038_example/01_pre_cadrage.md",
        "02",
    )
    normalized_packet = normalize_text(packet)

    for heading in (
        "Handoff metadata",
        "Source coach note",
        "Intended Codex mission",
        "Prompt to paste into Codex",
        "Required Codex finalization behavior",
        "Forbidden scope",
        "Expected files",
        "Expected commands",
        "Expected final summary",
        "PR review boundary",
    ):
        assert f"## {heading}" in packet

    required_phrases = (
        "run tests",
        "git diff --check",
        "verify only authorized files changed",
        "stage only authorized files",
        "commit",
        "push branch",
        "create pr",
        "pr url",
        "commit hash",
        "pytest result",
        "guardrail guarantee",
        "never merge",
        "never push to main",
        "forbidden scope",
        "no production code under `src/`",
    )
    for phrase in required_phrases:
        assert phrase in normalized_packet


def test_write_codex_handoff_writes_under_run_folder_and_refuses_overwrite():
    handoff = load_script_module("coach_codex_handoff_write_under_test", HANDOFF_SCRIPT_PATH)
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_like = Path(temp_dir) / "repo"
        note_path = write_temp_note(repo_like)

        output_path = handoff.write_codex_handoff(repo_like, "codex_038_example", note_path)
        assert output_path == repo_like / ".dicoimpro" / "runs" / "codex_038_example" / "02_codex_handoff.md"
        assert output_path.exists()

        assert_raises_value_error(
            lambda: handoff.write_codex_handoff(repo_like, "codex_038_example", note_path),
            "--overwrite",
        )


def test_archive_codex_return_writes_under_run_folder_and_refuses_overwrite():
    handoff = load_script_module("coach_codex_handoff_archive_under_test", HANDOFF_SCRIPT_PATH)
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_like = Path(temp_dir) / "repo"
        (repo_like / ".dicoimpro" / "runs" / "codex_038_example").mkdir(parents=True)

        output_path = handoff.archive_codex_return(
            repo_like,
            "codex_038_example",
            VALID_CODEX_RETURN,
        )
        assert output_path == repo_like / ".dicoimpro" / "runs" / "codex_038_example" / "05_codex_return.md"
        assert output_path.exists()

        assert_raises_value_error(
            lambda: handoff.archive_codex_return(
                repo_like,
                "codex_038_example",
                VALID_CODEX_RETURN,
            ),
            "--overwrite",
        )


def test_validate_codex_return_text_accepts_valid_return():
    handoff = load_script_module("coach_codex_handoff_return_valid_under_test", HANDOFF_SCRIPT_PATH)
    assert handoff.validate_codex_return_text(VALID_CODEX_RETURN) == []


def test_validate_codex_return_text_rejects_merge_completed_claim():
    handoff = load_script_module("coach_codex_handoff_return_merge_under_test", HANDOFF_SCRIPT_PATH)
    invalid_return = VALID_CODEX_RETURN.replace("Not merged.", "Merge completed.")
    errors = handoff.validate_codex_return_text(invalid_return)
    assert any("merge completed" in error for error in errors)


def test_extract_pr_url_extracts_github_pr_urls():
    handoff = load_script_module("coach_codex_handoff_extract_pr_under_test", HANDOFF_SCRIPT_PATH)
    assert handoff.extract_pr_url(VALID_CODEX_RETURN) == "https://github.com/example/dicoimpro/pull/38"
    assert handoff.extract_pr_url("No pull request here.") is None


def test_workflow_doc_states_manual_boundaries():
    workflow = normalize_text(read_text(WORKFLOW_DOC_PATH))
    required_phrases = (
        "does not call codex sdk",
        "does not call codex cli",
        "does not execute codex",
        "does not call openai",
        "does not run an autonomous loop",
        "repository scripts do not create prs or merge",
        "merge remains human-controlled",
        "manual handoff tooling only",
    )
    for phrase in required_phrases:
        assert phrase in workflow, f"Workflow doc is missing: {phrase}"


def test_coach_guidance_contains_manual_codex_handoff_boundary():
    guidance = normalize_text(read_text(COACH_GUIDANCE_PATH))
    required_phrases = (
        "manual codex handoff boundary",
        "gpt coach may produce a codex_prompt for codex",
        "repository scripts may package this prompt for manual handoff",
        "must not execute codex sdk/cli",
        "must not create/merge prs",
        "merge remains human-controlled after review",
        "no run/journal/journalpatch/real data/src runtime behavior change",
    )
    for phrase in required_phrases:
        assert phrase in guidance, f"Coach guidance is missing: {phrase}"


def test_readme_references_codex_038_and_workflow_doc():
    readme = normalize_text(read_text(README_PATH))
    assert "workflow_coach_codex_handoff_bridge_v0.2.3-auto.md" in readme
    assert "codex 038" in readme
    assert "manual codex handoff bridge" in readme
    assert "without codex sdk/cli" in readme


def test_post_015_review_references_codex_038():
    review = normalize_text(read_text(POST_015_REVIEW_PATH))
    assert "codex 038" in review
    assert "513 tests passing" in review
    assert "manual codex handoff bridge" in review
    assert "repository scripts do not call codex sdk/cli" in review


def test_no_src_references_handoff_bridge_or_workflow_doc():
    forbidden_terms = (
        "coach_codex_handoff.py",
        "coach_codex_handoff",
        "WORKFLOW_COACH_CODEX_HANDOFF_BRIDGE",
    )
    for path in SRC_DIR.rglob("*.py"):
        source = read_text(path)
        for term in forbidden_terms:
            assert term not in source, f"{path} must not reference handoff bridge: {term}"


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
    assert not (REPO_ROOT / ".github" / "workflows").exists()
