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

VALID_PR_URL = "https://github.com/Nyoha12/dicoimpro/pull/41"
VALID_CODEX_RETURN = """PR URL: https://github.com/Nyoha12/dicoimpro/pull/41
Commit hash: abc1234
Files changed:
- scripts/coach_loop.py
Commands run:
- python -m pytest
- git diff --check
pytest result: 576 passed
git diff --check result: clean
Guardrail guarantee: no src/ modified, no OpenAI/GPT call during smoke/tests, no Codex SDK/CLI.
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


def loop_module():
    return load_script_module("coach_loop_under_test", LOOP_SCRIPT_PATH)


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


def make_repo_like() -> tempfile.TemporaryDirectory:
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    (root / ".dicoimpro").mkdir()
    (root / "scripts").mkdir()
    (root / ".dicoimpro" / "WORKFLOW_AUTONOMY_POLICY.example.json").write_text(
        "{}",
        encoding="utf-8",
    )
    return temp


def valid_gate(prompt_type: str = "stage_prompt") -> dict:
    return {
        "evaluated_next_stage": "codex_return" if prompt_type == "codex_prompt" else "cadrage",
        "can_advance": True,
        "reflection_required": False,
        "next_prompt_ready": True,
        "next_prompt_type": prompt_type,
        "blocking_question": None,
        "reason": "ready",
        "required_user_intervention": False,
        "allowed_to_execute_automatically": False,
    }


class FakeContext:
    def __init__(self) -> None:
        self.calls = 0

    def write_context_packet(self, repo_root: Path, run_id: str) -> Path:
        self.calls += 1
        path = repo_root / ".dicoimpro" / "runs" / run_id / "00_context.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# context\n", encoding="utf-8")
        return path


class FakeStep:
    def __init__(
        self,
        gates: list[dict] | None = None,
        validation_errors: list[str] | None = None,
        risk: str = "low",
    ) -> None:
        self.gates = gates or [valid_gate()]
        self.validation_errors = validation_errors or []
        self.risk = risk
        self.api_calls = 0
        self.prompt_builds = 0
        self.note_counter = 0

    def build_stage_prompt(self, repo_root, run_id, stage, previous_note, user_instruction):
        self.prompt_builds += 1
        return f"prompt for {stage}"

    def write_stage_prompt(self, repo_root, run_id, stage, prompt):
        path = repo_root / ".dicoimpro" / "runs" / run_id / f"01_{stage}.model_prompt.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(prompt, encoding="utf-8")
        return path

    def execute_openai_response(self, prompt, model):
        self.api_calls += 1
        self.note_counter += 1
        return f"NOTE{self.note_counter}"

    def write_stage_note(self, repo_root, run_id, stage, note_text):
        path = repo_root / ".dicoimpro" / "runs" / run_id / f"01_{stage}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(note_text, encoding="utf-8")
        return path

    def validate_stage_note_text(self, note_text):
        return list(self.validation_errors)

    def extract_transition_gate(self, note_text):
        index = max(int(note_text.replace("NOTE", "") or "1") - 1, 0)
        return self.gates[min(index, len(self.gates) - 1)]

    def extract_yaml_front_matter(self, note_text):
        return {"guardrail_risk_level": self.risk}

    def extract_next_prompt_block(self, note_text):
        return "reflection prompt"


class FakeAutonomy:
    def __init__(self, max_reflections: int = 3, budget_allowed: bool = True) -> None:
        self.max_reflections = max_reflections
        self.budget_allowed = budget_allowed

    def load_autonomy_policy(self, repo_root):
        return {
            "max_reflections_per_stage": self.max_reflections,
            "allowed_merge_modes": ["manual", "auto_after_verify"],
            "merge_mode": "manual",
        }

    def validate_autonomy_policy(self, policy):
        return []

    def evaluate_gate_autonomy(self, gate, policy, context=None):
        if gate.get("required_user_intervention") is True:
            return decision(False, "stop_human", ["required_user_intervention"])
        if gate.get("can_advance") is False:
            return decision(False, "stop_human", ["transition_gate does not allow automatic continuation"])
        return decision(True, "auto_continue_allowed", [])

    def can_auto_reflect(self, gate, policy, reflection_count, blocking_question=None):
        if reflection_count >= self.max_reflections:
            return decision(False, "stop_human", ["max_reflections_per_stage is reached"])
        if gate.get("required_user_intervention") is True:
            return decision(False, "stop_human", ["required_user_intervention is true"])
        if blocking_question and "approve" in blocking_question.casefold():
            return decision(False, "stop_human", ["blocking question is a substantive human decision"])
        return decision(True, "auto_reflection_allowed", [])

    def evaluate_api_budget(self, policy, usage):
        if self.budget_allowed:
            return decision(True, "api_budget_ok", [], "auto_external_with_budget")
        return decision(False, "api_budget_exceeded", ["API budget is exceeded"])


def decision(allowed: bool, name: str, blockers: list[str], autonomy_level: str | None = None) -> dict:
    return {
        "decision": name,
        "allowed": allowed,
        "autonomy_level": autonomy_level or ("auto_local" if allowed else "stop_human"),
        "blockers": blockers,
        "warnings": [],
        "next_required_action": "continue" if allowed else "stop",
    }


class FakeHandoff:
    def __init__(self, return_errors: list[str] | None = None, pr_url: str | None = VALID_PR_URL) -> None:
        self.return_errors = return_errors or []
        self.pr_url = pr_url
        self.handoff_calls = 0
        self.archive_calls = 0

    def write_codex_handoff(self, repo_root, run_id, note_path):
        self.handoff_calls += 1
        path = repo_root / ".dicoimpro" / "runs" / run_id / "02_codex_handoff.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# handoff\n", encoding="utf-8")
        return path

    def archive_codex_return(self, repo_root, run_id, return_text, overwrite=False):
        self.archive_calls += 1
        path = repo_root / ".dicoimpro" / "runs" / run_id / "05_codex_return.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(return_text, encoding="utf-8")
        return path

    def validate_codex_return_text(self, return_text):
        return list(self.return_errors)

    def extract_pr_url(self, return_text):
        return self.pr_url


class FakePRVerify:
    def __init__(self, decision_allowed: bool = True, post_passed: bool = True) -> None:
        self.decision_allowed = decision_allowed
        self.post_passed = post_passed
        self.merge_calls = 0
        self.post_calls = 0

    def build_pre_merge_report(
        self,
        pr_url,
        merge_mode,
        run_id,
        codex_return_path,
        authorized_paths,
        forbidden_paths,
    ):
        return {
            "merge_mode": merge_mode,
            "pr": {
                "url": pr_url,
                "number": 41,
                "mergeable": True,
                "head_sha": "abc1234",
            },
            "scope": {"changed_files": ["scripts/coach_loop.py"]},
            "checks": {"pytest": "passed", "diff_check": "passed", "ci": "passed"},
        }

    def save_pre_merge_report(self, repo_root, run_id, report, overwrite=False):
        path = repo_root / ".dicoimpro" / "runs" / run_id / "08_pre_merge_report.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report), encoding="utf-8")
        return path

    def decide_report_with_autonomy(self, report, repo_root):
        if self.decision_allowed:
            return {
                "decision": "auto_merge_allowed",
                "allowed": True,
                "autonomy_level": "auto_merge_after_verify",
                "blockers": [],
                "warnings": [],
                "next_required_action": "merge may be delegated",
            }
        return {
            "decision": "auto_merge_blocked",
            "allowed": False,
            "autonomy_level": "stop_human",
            "blockers": ["verify gate red"],
            "warnings": [],
            "next_required_action": "stop",
        }

    def execute_merge_if_allowed(self, report, decision, repo_root, execute=False):
        self.merge_calls += 1
        if execute and decision.get("allowed"):
            return {"executed": True, "blockers": [], "return_code": 0}
        return {"executed": False, "blockers": ["blocked"], "return_code": 1}

    def run_post_merge_validation(self, repo_root, run_id):
        self.post_calls += 1
        return {
            "passed": self.post_passed,
            "return_code": 0 if self.post_passed else 1,
            "decision": "post_merge_validation_passed" if self.post_passed else "stop_human",
            "no_destructive_auto_repair": True,
        }

    def write_post_merge_report(self, repo_root, run_id, report, overwrite=False):
        path = repo_root / ".dicoimpro" / "runs" / run_id / "09_post_merge_report.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report), encoding="utf-8")
        return path


def install_fakes(module, context=None, step=None, autonomy=None, handoff=None, pr_verify=None):
    module.load_context_module = lambda: context or FakeContext()
    module.load_step_module = lambda: step or FakeStep()
    module.load_autonomy_module = lambda: autonomy or FakeAutonomy()
    module.load_handoff_module = lambda: handoff or FakeHandoff()
    module.load_pr_verify_module = lambda: pr_verify or FakePRVerify()


def test_coach_loop_script_and_workflow_doc_exist():
    assert LOOP_SCRIPT_PATH.exists()
    assert WORKFLOW_DOC_PATH.exists()


def test_coach_loop_imports_only_standard_library():
    imports = imported_roots(LOOP_SCRIPT_PATH)
    standard_roots = set(sys.stdlib_module_names) | {"__future__"}
    assert sorted(imports.difference(standard_roots)) == []


def test_coach_loop_has_no_forbidden_imports_or_direct_merge_command():
    imports = imported_roots(LOOP_SCRIPT_PATH)
    assert sorted(imports.intersection(FORBIDDEN_IMPORT_ROOTS)) == []

    source = read_text(LOOP_SCRIPT_PATH)
    assert "gh pr merge" not in source
    assert '"gh", "pr", "merge"' not in source
    assert "Codex SDK" not in source
    assert "Codex CLI" not in source


def test_cli_exposes_expected_commands():
    source = read_text(LOOP_SCRIPT_PATH)
    for command in ("start", "resume-codex", "verify-pr", "status", "summarize"):
        assert f'"{command}"' in source


def test_start_without_execute_api_prepares_prompt_and_does_not_call_api():
    module = loop_module()
    step = FakeStep()
    install_fakes(module, step=step)
    with make_repo_like() as temp_dir:
        state = module.start_run(Path(temp_dir), "codex_041_test", "pre_cadrage")
        assert state["status"] == "prompt_prepared"
        assert state["model_prompt_path"]
        assert step.api_calls == 0
        assert (Path(temp_dir) / ".dicoimpro" / "runs" / "codex_041_test" / "loop_state.json").exists()
        assert (Path(temp_dir) / ".dicoimpro" / "runs" / "codex_041_test" / "loop_summary.md").exists()


def test_start_with_execute_api_delegates_to_coach_step_boundary():
    module = loop_module()
    step = FakeStep()
    install_fakes(module, step=step)
    with make_repo_like() as temp_dir:
        state = module.start_run(
            Path(temp_dir),
            "codex_041_test",
            "pre_cadrage",
            execute_api=True,
        )
        assert step.api_calls == 1
        assert state["status"] == "gpt_note_ready"
        assert state["gpt_call_count"] == 1


def test_invalid_stage_note_causes_stop_human():
    module = loop_module()
    install_fakes(module, step=FakeStep(validation_errors=["missing transition_gate"]))
    with make_repo_like() as temp_dir:
        state = module.start_run(
            Path(temp_dir),
            "codex_041_test",
            "pre_cadrage",
            execute_api=True,
        )
        assert state["status"] == "stop_human"
        assert "missing transition_gate" in state["blockers"]


def test_required_user_intervention_true_causes_stop_human():
    module = loop_module()
    gate = valid_gate()
    gate["required_user_intervention"] = True
    install_fakes(module, step=FakeStep(gates=[gate]))
    with make_repo_like() as temp_dir:
        state = module.start_run(
            Path(temp_dir),
            "codex_041_test",
            "pre_cadrage",
            execute_api=True,
        )
        assert state["status"] == "stop_human"
        assert any("required_user_intervention" in blocker for blocker in state["blockers"])


def test_auto_reflection_allowed_only_below_limit_and_blocks_at_limit():
    module = loop_module()
    blocked_gate = valid_gate("reflection_prompt")
    blocked_gate["can_advance"] = False
    blocked_gate["reflection_required"] = True
    blocked_gate["blocking_question"] = "Clarify local evidence."
    ready_gate = valid_gate()
    step = FakeStep(gates=[blocked_gate, ready_gate])
    install_fakes(module, step=step, autonomy=FakeAutonomy(max_reflections=3))
    with make_repo_like() as temp_dir:
        state = module.start_run(
            Path(temp_dir),
            "codex_041_reflect",
            "pre_cadrage",
            execute_api=True,
        )
        assert state["status"] == "gpt_note_ready"
        assert state["reflection_count_current_stage"] == 1
        assert step.api_calls == 2

    module = loop_module()
    step_at_limit = FakeStep(gates=[blocked_gate])
    install_fakes(module, step=step_at_limit, autonomy=FakeAutonomy(max_reflections=0))
    with make_repo_like() as temp_dir:
        state = module.start_run(
            Path(temp_dir),
            "codex_041_reflect_limit",
            "pre_cadrage",
            execute_api=True,
        )
        assert state["status"] == "stop_human"
        assert any("max_reflections" in blocker for blocker in state["blockers"])


def test_no_gpt_call_occurs_without_execute_api():
    module = loop_module()
    step = FakeStep(gates=[valid_gate("codex_prompt")])
    install_fakes(module, step=step)
    with make_repo_like() as temp_dir:
        state = module.start_run(Path(temp_dir), "codex_041_no_api", "pre_cadrage")
        assert state["status"] == "prompt_prepared"
        assert step.api_calls == 0
        assert state["gpt_call_count"] == 0


def test_handoff_is_built_when_codex_ready_and_runner_never_executes_codex():
    module = loop_module()
    handoff = FakeHandoff()
    install_fakes(module, step=FakeStep(gates=[valid_gate("codex_prompt")]), handoff=handoff)
    with make_repo_like() as temp_dir:
        state = module.start_run(
            Path(temp_dir),
            "codex_041_handoff",
            "codex_prompt",
            execute_api=True,
        )
        assert state["status"] == "handoff_ready"
        assert state["handoff_path"].endswith("02_codex_handoff.md")
        assert handoff.handoff_calls == 1


def test_resume_codex_archives_return_extracts_pr_and_stops_when_invalid():
    module = loop_module()
    handoff = FakeHandoff()
    install_fakes(module, handoff=handoff)
    with make_repo_like() as temp_dir:
        return_path = Path(temp_dir) / "codex_return.md"
        return_path.write_text(VALID_CODEX_RETURN, encoding="utf-8")
        state = module.resume_codex_return(Path(temp_dir), "codex_041_resume", return_path)
        assert state["status"] == "pr_detected"
        assert state["pr_url"] == VALID_PR_URL
        assert handoff.archive_calls == 1

    module = loop_module()
    install_fakes(module, handoff=FakeHandoff(return_errors=["Codex return is invalid"]))
    with make_repo_like() as temp_dir:
        return_path = Path(temp_dir) / "codex_return.md"
        return_path.write_text("invalid", encoding="utf-8")
        state = module.resume_codex_return(Path(temp_dir), "codex_041_resume_bad", return_path)
        assert state["status"] == "stop_human"
        assert "Codex return is invalid" in state["blockers"]


def test_verify_pr_manual_and_missing_execute_never_merge():
    module = loop_module()
    pr_verify = FakePRVerify()
    install_fakes(module, pr_verify=pr_verify)
    with make_repo_like() as temp_dir:
        return_path = Path(temp_dir) / "return.md"
        return_path.write_text(VALID_CODEX_RETURN, encoding="utf-8")
        state = module.verify_pr_flow(
            Path(temp_dir),
            "codex_041_verify",
            pr_url=VALID_PR_URL,
            codex_return_path=return_path,
            merge_mode="manual",
        )
        assert state["status"] == "stop_human"
        assert pr_verify.merge_calls == 0
        assert any("manual" in blocker for blocker in state["blockers"])

    module = loop_module()
    pr_verify = FakePRVerify()
    install_fakes(module, pr_verify=pr_verify)
    with make_repo_like() as temp_dir:
        return_path = Path(temp_dir) / "return.md"
        return_path.write_text(VALID_CODEX_RETURN, encoding="utf-8")
        state = module.verify_pr_flow(
            Path(temp_dir),
            "codex_041_verify_no_execute",
            pr_url=VALID_PR_URL,
            codex_return_path=return_path,
            merge_mode="auto_after_verify",
        )
        assert state["status"] == "stop_human"
        assert pr_verify.merge_calls == 0
        assert any("--execute-merge absent" in blocker for blocker in state["blockers"])


def test_verify_pr_execute_merge_delegates_to_pr_verify_boundary_and_handles_post_failure():
    module = loop_module()
    pr_verify = FakePRVerify()
    install_fakes(module, pr_verify=pr_verify)
    with make_repo_like() as temp_dir:
        return_path = Path(temp_dir) / "return.md"
        return_path.write_text(VALID_CODEX_RETURN, encoding="utf-8")
        state = module.verify_pr_flow(
            Path(temp_dir),
            "codex_041_merge",
            pr_url=VALID_PR_URL,
            codex_return_path=return_path,
            merge_mode="auto_after_verify",
            execute_merge=True,
        )
        assert state["status"] == "post_merge_validated"
        assert pr_verify.merge_calls == 1
        assert pr_verify.post_calls == 1

    module = loop_module()
    failing_pr_verify = FakePRVerify(post_passed=False)
    install_fakes(module, pr_verify=failing_pr_verify)
    with make_repo_like() as temp_dir:
        return_path = Path(temp_dir) / "return.md"
        return_path.write_text(VALID_CODEX_RETURN, encoding="utf-8")
        state = module.verify_pr_flow(
            Path(temp_dir),
            "codex_041_post_fail",
            pr_url=VALID_PR_URL,
            codex_return_path=return_path,
            merge_mode="auto_after_verify",
            execute_merge=True,
        )
        assert state["status"] == "stop_human"
        assert state["post_merge_report_path"]
        assert "do not repair destructively" in state["next_required_action"]


def test_loop_state_contains_required_fields_and_summary_is_written():
    module = loop_module()
    state = module.initial_loop_state("codex_041_state", "pre_cadrage", {"max_reflections_per_stage": 3})
    with make_repo_like() as temp_dir:
        module.save_loop_state(Path(temp_dir), state)
        summary_path = module.write_loop_summary(Path(temp_dir), state)
        assert summary_path.exists()
        loaded = module.load_loop_state(Path(temp_dir), "codex_041_state")
        for key in module.REQUIRED_LOOP_STATE_KEYS:
            assert key in loaded


def test_status_and_summarize_do_not_call_external_services():
    module = loop_module()
    with make_repo_like() as temp_dir:
        state = module.initial_loop_state("codex_041_status", "pre_cadrage", {"max_reflections_per_stage": 3})
        module.save_loop_state(Path(temp_dir), state)
        module.load_context_module = lambda: (_ for _ in ()).throw(AssertionError("external service called"))
        module.load_step_module = lambda: (_ for _ in ()).throw(AssertionError("external service called"))
        module.load_pr_verify_module = lambda: (_ for _ in ()).throw(AssertionError("external service called"))
        loaded = module.load_loop_state(Path(temp_dir), "codex_041_status")
        summary_path = module.write_loop_summary(Path(temp_dir), loaded)
        assert loaded["status"] == "initialized"
        assert summary_path.exists()


def test_workflow_doc_states_runner_boundaries():
    workflow = normalize_text(read_text(WORKFLOW_DOC_PATH))
    required_phrases = (
        "does not call codex sdk",
        "does not call codex cli",
        "does not execute codex",
        "does not call openai directly",
        "gpt calls require --execute-api",
        "merge requires --execute-merge and auto_after_verify",
        "does not implement an unbounded autonomous loop",
    )
    for phrase in required_phrases:
        assert phrase in workflow, f"Workflow doc is missing: {phrase}"


def test_guidance_readme_and_review_reference_codex_041():
    guidance = normalize_text(read_text(COACH_GUIDANCE_PATH))
    readme = normalize_text(read_text(README_PATH))
    review = normalize_text(read_text(POST_015_REVIEW_PATH))

    assert "semi-automatic coach loop runner boundary" in guidance
    assert "gpt is allowed only through explicit --execute-api" in guidance
    assert "codex remains manual handoff" in guidance
    assert "merge is allowed only through the pr verify boundary" in guidance

    assert "workflow_coach_loop_runner_v0.2.3-auto.md" in readme
    assert "codex 041" in readme
    assert "semi-automatic coach-loop runner" in readme

    assert "codex 041" in review
    assert "576 tests passing" in review
    assert "coach_loop.py orchestre uniquement les workflow tools locaux" in review


def test_no_src_references_loop_runner_or_workflow_doc():
    forbidden_terms = (
        "coach_loop.py",
        "coach_loop",
        "WORKFLOW_COACH_LOOP_RUNNER",
    )
    for path in SRC_DIR.rglob("*.py"):
        source = read_text(path)
        for term in forbidden_terms:
            assert term not in source, f"{path} must not reference coach loop runner: {term}"


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
