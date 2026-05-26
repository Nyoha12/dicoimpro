from __future__ import annotations

import ast
import importlib.util
import json
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

LOOP_SCRIPT_PATH = SCRIPTS_DIR / "coach_loop.py"
RUNBOOK_PATH = DOCS_DIR / "RUNBOOK_COACH_LOOP_USAGE_v0.2.3-auto.md"
WORKFLOW_DOC_PATH = DOCS_DIR / "WORKFLOW_COACH_LOOP_RUNNER_v0.2.3-auto.md"
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


def loop_module():
    return load_script_module("coach_loop_hardening_under_test", LOOP_SCRIPT_PATH)


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


class FakeAutonomy:
    def load_autonomy_policy(self, repo_root):
        return {
            "max_reflections_per_stage": 3,
            "merge_mode": "manual",
            "allowed_merge_modes": ["manual", "auto_after_verify"],
        }

    def validate_autonomy_policy(self, policy):
        return []


def make_state_repo(module) -> tempfile.TemporaryDirectory:
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    (root / ".dicoimpro" / "runs").mkdir(parents=True)
    return temp


def create_prompt_prepared_state(module, repo_root: Path, run_id: str) -> dict:
    run_dir = repo_root / ".dicoimpro" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    context_path = run_dir / "00_context.md"
    prompt_path = run_dir / "01_pre_cadrage.model_prompt.md"
    context_path.write_text("# context\n", encoding="utf-8")
    prompt_path.write_text("# prompt\n", encoding="utf-8")

    state = module.initial_loop_state(run_id, "pre_cadrage")
    state["status"] = "prompt_prepared"
    state["context_path"] = context_path.relative_to(repo_root).as_posix()
    state["model_prompt_path"] = prompt_path.relative_to(repo_root).as_posix()
    state["next_required_action"] = "Review the prepared prompt."
    module.save_loop_state(repo_root, state)
    return state


def test_runbook_exists_and_cli_exposes_hardening_commands():
    assert RUNBOOK_PATH.exists()
    source = read_text(LOOP_SCRIPT_PATH)
    for command in ("doctor", "validate-run", "explain-next"):
        assert f'"{command}"' in source


def test_coach_loop_imports_only_standard_library_and_no_forbidden_imports():
    imports = imported_roots(LOOP_SCRIPT_PATH)
    standard_roots = set(sys.stdlib_module_names) | {"__future__"}
    assert sorted(imports.difference(standard_roots)) == []
    assert sorted(imports.intersection(FORBIDDEN_IMPORT_ROOTS)) == []


def test_doctor_report_returns_ok_true_in_normal_repository_context():
    module = loop_module()
    report = module.doctor_report(REPO_ROOT)
    assert report["ok"] is True
    assert report["checked"]
    assert report["blockers"] == []
    assert "warnings" in report
    assert report["next_required_action"]


def test_doctor_report_shape_and_no_external_service_methods_are_called():
    module = loop_module()
    calls: list[str] = []

    def loader(name):
        def _load():
            calls.append(name)
            return object()

        return _load

    module.load_autonomy_module = lambda: FakeAutonomy()
    module.load_coach_state_module = loader("coach_state")
    module.load_context_module = loader("context")
    module.load_step_module = loader("step")
    module.load_handoff_module = loader("handoff")
    module.load_pr_verify_module = loader("pr_verify")

    with tempfile.TemporaryDirectory() as temp_dir:
        repo_root = Path(temp_dir)
        for relative_path in module.REQUIRED_WORKFLOW_RELATIVE_PATHS:
            path = repo_root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            content = "{}\n" if relative_path == module.POLICY_RELATIVE_PATH else "\n"
            path.write_text(content, encoding="utf-8")
        (repo_root / ".dicoimpro" / ".gitignore").write_text(
            "WORKFLOW_STATE.local.json\nruns/*\n!runs/.gitkeep\n",
            encoding="utf-8",
        )
        report = module.doctor_report(repo_root)

    assert report["ok"] is True
    assert sorted(calls) == ["coach_state", "context", "handoff", "pr_verify", "step"]
    assert report["checked"]
    assert report["blockers"] == []
    assert "next_required_action" in report


def test_validate_run_report_validates_prompt_prepared_state_and_missing_paths():
    module = loop_module()
    with make_state_repo(module) as temp_dir:
        repo_root = Path(temp_dir)
        create_prompt_prepared_state(module, repo_root, "codex_042_valid")
        report = module.validate_run_report(repo_root, "codex_042_valid")
        assert report["ok"] is True
        assert report["status"] == "prompt_prepared"
        assert report["missing_paths"] == []

        state = module.read_json(module.loop_state_path(repo_root, "codex_042_valid"))
        state["context_path"] = ".dicoimpro/runs/codex_042_valid/missing_context.md"
        module.write_json(module.loop_state_path(repo_root, "codex_042_valid"), state)
        missing = module.validate_run_report(repo_root, "codex_042_valid")
        assert missing["ok"] is False
        assert missing["missing_paths"]
        assert any("referenced local paths are missing" in blocker for blocker in missing["blockers"])


def test_validate_run_report_handles_missing_loop_state_safely():
    module = loop_module()
    with make_state_repo(module) as temp_dir:
        report = module.validate_run_report(Path(temp_dir), "codex_042_missing")
        assert report["ok"] is False
        assert report["status"] is None
        assert any("loop_state.json is missing" in blocker for blocker in report["blockers"])


def test_explain_next_action_covers_required_statuses():
    module = loop_module()
    prompt = module.explain_next_action({"status": "prompt_prepared", "blockers": []})
    handoff = module.explain_next_action({"status": "handoff_ready", "blockers": []})
    stopped = module.explain_next_action({"status": "stop_human", "blockers": ["tests failed"]})
    pr_detected = module.explain_next_action({"status": "pr_detected", "blockers": []})
    post_validated = module.explain_next_action({"status": "post_merge_validated", "blockers": []})

    assert "Prompt prepared" in prompt
    assert "Codex remains manual" in handoff
    assert "tests failed" in stopped
    assert "verify-pr" in pr_detected
    assert "--execute-merge plus auto_after_verify" in pr_detected
    assert "Post-merge validation" in post_validated
    assert "continue anyway" not in normalize_text(stopped)
    assert "ignore blockers" not in normalize_text(stopped)


def test_explain_next_action_covers_merge_statuses_and_unknown_status():
    module = loop_module()
    pre_merge = module.explain_next_action({"status": "pre_merge_verified", "blockers": []})
    merged = module.explain_next_action({"status": "merged", "blockers": []})
    unknown = module.explain_next_action({"status": "unexpected", "blockers": []})

    assert "Merge is never default" in pre_merge
    assert "--execute-merge plus auto_after_verify" in pre_merge
    assert "post-merge validation" in normalize_text(merged)
    assert "Unknown loop status" in unknown


def test_runbook_states_operational_boundaries():
    runbook = normalize_text(read_text(RUNBOOK_PATH))
    required_phrases = (
        "default is local and non-destructive",
        "api requires --execute-api",
        "codex remains manual handoff",
        "merge is never default",
        "merge requires --execute-merge",
        "merge_mode auto_after_verify",
        "unknown risk means stop_human",
        "generated .dicoimpro/runs/* artifacts are local and ignored",
        "no run/journal/journalpatch/real data",
        "no src runtime behavior change",
    )
    for phrase in required_phrases:
        assert phrase in runbook, f"Runbook is missing: {phrase}"


def test_docs_guidance_readme_and_review_reference_codex_042():
    workflow = normalize_text(read_text(WORKFLOW_DOC_PATH))
    guidance = normalize_text(read_text(COACH_GUIDANCE_PATH))
    readme = normalize_text(read_text(README_PATH))
    review = normalize_text(read_text(POST_015_REVIEW_PATH))

    assert "doctor" in workflow
    assert "validate-run" in workflow
    assert "explain-next" in workflow
    assert "do not call gpt, openai, codex, gh, git, pytest, network, or merge" in workflow

    assert "runner hardening and operational diagnostics" in guidance
    assert "diagnostics are local-only" in guidance
    assert "must not bypass stop_human" in guidance
    assert "must not weaken the api, codex, pr verification, or merge boundaries" in guidance

    assert "runbook_coach_loop_usage_v0.2.3-auto.md" in readme
    assert "codex 042" in readme
    assert "hardening and operational runbook" in readme

    assert "codex 042" in review
    assert "597 tests passing" in review
    assert "diagnostics local-only" in review
    assert "aucun nouveau chemin runtime" in review


def test_no_src_references_loop_runner_and_no_new_dependency_or_workflow():
    for path in SRC_DIR.rglob("*.py"):
        source = read_text(path)
        assert "coach_loop.py" not in source

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
