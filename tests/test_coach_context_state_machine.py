from __future__ import annotations

import ast
import importlib.util
import json
import shutil
import subprocess
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

GITIGNORE_PATH = DICOIMPRO_DIR / ".gitignore"
WORKFLOW_STATE_PATH = DICOIMPRO_DIR / "WORKFLOW_STATE.example.json"
COACH_STATE_PATH = SCRIPTS_DIR / "coach_state.py"
COACH_CONTEXT_PATH = SCRIPTS_DIR / "coach_collect_context.py"
WORKFLOW_DOC_PATH = DOCS_DIR / "WORKFLOW_COACH_CONTEXT_STATE_MACHINE_v0.2.3-auto.md"
README_PATH = DOCS_DIR / "README.md"
POST_015_REVIEW_PATH = DOCS_DIR / "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md"

FORBIDDEN_SCRIPT_IMPORTS = {
    "codex",
    "dico_impro",
    "github",
    "httpx",
    "openai",
    "pydantic",
    "requests",
    "src",
}

REQUIRED_CONTEXT_SECTIONS = (
    "Context packet metadata",
    "Repository identity",
    "Current branch",
    "Current HEAD",
    "Last commit",
    "Recent commits",
    "Git status",
    "Diff stat",
    "Changed files",
    "Last merged Codex from state if available",
    "Main test count from state if available",
    "Guardrail snapshot",
    "Notes for next GPT-5.5 Thinking stage",
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


def assert_imports_standard_library_only(path: Path) -> None:
    allowed = set(sys.stdlib_module_names)
    allowed.add("__future__")
    imports = imported_roots(path)
    non_standard = sorted(imports.difference(allowed))
    assert non_standard == [], f"{path.name} imports non-stdlib modules: {non_standard!r}"


def git_status_for(pathspec: str) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--", pathspec],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def copy_minimal_repo_like_folder(destination: Path) -> None:
    dicoimpro = destination / ".dicoimpro"
    runs = dicoimpro / "runs"
    runs.mkdir(parents=True)
    shutil.copy2(WORKFLOW_STATE_PATH, dicoimpro / "WORKFLOW_STATE.example.json")
    (runs / ".gitkeep").write_text("", encoding="utf-8")


def valid_transition_gate(**overrides: object) -> dict:
    gate = {
        "evaluated_next_stage": "cadrage",
        "can_advance": True,
        "reflection_required": False,
        "next_prompt_ready": True,
        "next_prompt_type": "stage_prompt",
        "blocking_question": None,
        "reason": "The next stage has enough context.",
        "required_user_intervention": False,
        "allowed_to_execute_automatically": False,
    }
    gate.update(overrides)
    return gate


def test_gitignore_and_scaffold_files_exist():
    assert GITIGNORE_PATH.exists()
    gitignore = read_text(GITIGNORE_PATH).splitlines()
    assert "WORKFLOW_STATE.local.json" in gitignore
    assert "runs/*" in gitignore
    assert "!runs/.gitkeep" in gitignore

    assert COACH_STATE_PATH.exists()
    assert COACH_CONTEXT_PATH.exists()
    assert WORKFLOW_DOC_PATH.exists()


def test_scripts_import_only_standard_library_and_no_forbidden_runtime_modules():
    for path in (COACH_STATE_PATH, COACH_CONTEXT_PATH):
        assert_imports_standard_library_only(path)
        imports = imported_roots(path)
        forbidden = sorted(imports.intersection(FORBIDDEN_SCRIPT_IMPORTS))
        assert forbidden == [], f"{path.name} imports forbidden modules: {forbidden!r}"


def test_coach_state_loads_and_validates_example_state():
    coach_state = load_script_module("coach_state_under_test", COACH_STATE_PATH)
    state = coach_state.load_example_state(REPO_ROOT)

    assert state == json.loads(read_text(WORKFLOW_STATE_PATH))
    assert coach_state.validate_state_shape(state) == []
    assert coach_state.validate_sensitive_permissions_false(state) == []


def test_coach_state_initializes_local_state_and_run_folder_in_temp_repo():
    coach_state = load_script_module("coach_state_temp_under_test", COACH_STATE_PATH)
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_like = Path(temp_dir) / "repo"
        copy_minimal_repo_like_folder(repo_like)

        local_state_path = coach_state.initialize_local_state(
            repo_like,
            run_id="codex_036_temp",
        )
        assert local_state_path == repo_like / ".dicoimpro" / "WORKFLOW_STATE.local.json"

        local_state = json.loads(local_state_path.read_text(encoding="utf-8"))
        assert local_state["current_run_id"] == "codex_036_temp"
        assert (
            local_state["repo_context_packet_path"]
            == ".dicoimpro/runs/codex_036_temp/00_context.md"
        )

        run_folder = coach_state.ensure_run_folder(repo_like, "codex_036_temp")
        assert run_folder.exists()
        assert run_folder.is_dir()


def test_transition_gate_validation_and_advance_decision():
    coach_state = load_script_module("coach_state_gate_under_test", COACH_STATE_PATH)

    assert coach_state.validate_transition_gate(valid_transition_gate()) == []
    for can_advance in (False, True):
        for next_prompt_ready in (False, True):
            gate = valid_transition_gate(
                can_advance=can_advance,
                next_prompt_ready=next_prompt_ready,
            )
            assert coach_state.can_advance_from_transition_gate(gate) is (
                can_advance and next_prompt_ready
            )


def test_update_state_from_transition_gate_refuses_blocked_gate():
    coach_state = load_script_module("coach_state_blocked_under_test", COACH_STATE_PATH)
    state = coach_state.load_example_state(REPO_ROOT)
    blocked_gate = valid_transition_gate(can_advance=False)

    try:
        coach_state.update_state_from_transition_gate(
            state,
            blocked_gate,
            ".dicoimpro/runs/codex_036_example/01_note.md",
        )
    except ValueError as exc:
        assert "can_advance is false" in str(exc)
    else:
        raise AssertionError("Blocked transition_gate must refuse to advance")


def test_update_state_from_transition_gate_increments_reflection_count():
    coach_state = load_script_module("coach_state_reflection_under_test", COACH_STATE_PATH)
    state = coach_state.load_example_state(REPO_ROOT)
    before = state["reflection_count_current_stage"]
    reflection_gate = valid_transition_gate(
        evaluated_next_stage="reflection_before_cadrage",
        next_prompt_type="reflection_prompt",
        reflection_required=True,
        blocking_question="What detail blocks the next stage?",
    )

    updated = coach_state.update_state_from_transition_gate(
        state,
        reflection_gate,
        ".dicoimpro/runs/codex_036_example/01_reflection.md",
    )

    assert updated["reflection_count_current_stage"] == before + 1
    assert updated["current_stage"] == "reflection_before_cadrage"
    assert updated["last_stage_note"] == ".dicoimpro/runs/codex_036_example/01_reflection.md"


def test_context_markdown_includes_required_sections():
    coach_context = load_script_module("coach_context_render_under_test", COACH_CONTEXT_PATH)
    packet = coach_context.build_context_packet(REPO_ROOT, "codex_036_test")
    markdown = coach_context.render_context_markdown(packet)

    for index, section in enumerate(REQUIRED_CONTEXT_SECTIONS, start=1):
        assert f"## {index}. {section}" in markdown


def test_context_packet_builds_from_current_repo_without_network():
    coach_context = load_script_module("coach_context_build_under_test", COACH_CONTEXT_PATH)
    packet = coach_context.build_context_packet(REPO_ROOT, "codex_036_test")

    assert packet["run_id"] == "codex_036_test"
    assert packet["repository"]["name"].casefold() == "dicoimpro"
    assert set(packet["git"]) == {
        "branch",
        "diff_name_only",
        "diff_stat",
        "head",
        "last_commit",
        "recent_commits",
        "status_short",
    }


def test_context_packet_writes_to_run_folder_in_temp_repo():
    coach_context = load_script_module("coach_context_write_under_test", COACH_CONTEXT_PATH)
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_like = Path(temp_dir) / "repo"
        copy_minimal_repo_like_folder(repo_like)

        output_path = coach_context.write_context_packet(repo_like, "codex_036_temp")
        assert output_path == repo_like / ".dicoimpro" / "runs" / "codex_036_temp" / "00_context.md"
        assert output_path.exists()
        assert "## 1. Context packet metadata" in output_path.read_text(encoding="utf-8")


def test_workflow_doc_records_non_runtime_boundaries():
    workflow = normalize_text(read_text(WORKFLOW_DOC_PATH))
    required_phrases = (
        "codex 036 turns the codex 035 output architecture into local files",
        "state machine does not decide maturity arbitrarily",
        "only follows transition_gate",
        "context collector refreshes repo context at each stage",
        "context packets are filtered to avoid token overload",
        "generated local state is ignored by git",
        "does not implement api calls",
        "codex sdk",
        "codex cli",
        "autonomous loop",
        "prompt execution",
        "run",
        "journal",
        "journalpatch",
    )
    for phrase in required_phrases:
        assert phrase in workflow, f"Workflow doc is missing: {phrase}"


def test_readme_and_post_015_review_reference_codex_036_and_workflow_doc():
    readme = normalize_text(read_text(README_PATH))
    review = normalize_text(read_text(POST_015_REVIEW_PATH))

    assert "workflow_coach_context_state_machine_v0.2.3-auto.md" in readme
    assert "codex 036" in readme
    assert "coach context collector and state machine" in readme

    assert "codex 036" in review
    assert "478 tests passing" in review
    assert "scripts under `scripts/`" in review or "scripts sous `scripts/`" in review


def test_no_src_files_are_modified_or_reference_coach_loop_files():
    src_status = git_status_for("src")
    assert src_status == [], f"Codex 036 must not modify src/. Found: {src_status!r}"

    forbidden_terms = (
        ".dicoimpro",
        "COACH_GUIDANCE",
        "STAGE_OUTPUT_SCHEMA",
        "WORKFLOW_STATE",
        "WORKFLOW_COACH_CONTEXT_STATE_MACHINE",
        "coach_collect_context",
        "coach_state",
        "coach loop",
        "GPT-5.5 Thinking",
    )
    for path in SRC_DIR.rglob("*.py"):
        source = read_text(path)
        for term in forbidden_terms:
            assert term not in source, f"{path} must not reference coach scaffold: {term}"


def test_no_openai_codex_dependency_or_github_workflow_is_added():
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
        "Codex 036 must not add GitHub workflow files. "
        f"Found: {workflow_status!r}"
    )
