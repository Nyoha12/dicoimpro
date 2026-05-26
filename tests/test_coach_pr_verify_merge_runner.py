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

PR_VERIFY_SCRIPT_PATH = SCRIPTS_DIR / "coach_pr_verify.py"
WORKFLOW_DOC_PATH = DOCS_DIR / "WORKFLOW_COACH_PR_VERIFY_MERGE_RUNNER_v0.2.3-auto.md"
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
}

VALID_PR_URL = "https://github.com/Nyoha12/dicoimpro/pull/40"
VALID_CODEX_RETURN = """PR URL: https://github.com/Nyoha12/dicoimpro/pull/40
Commit hash: abc1234
Files changed:
- scripts/coach_pr_verify.py
- tests/test_coach_pr_verify_merge_runner.py
Commands run:
- python -m pytest
- git diff --check
pytest result: 555 passed
git diff --check result: clean
Guardrail guarantee: no src/ modified, no OpenAI/GPT call, no Codex SDK/CLI, no autonomous full loop.
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


def pr_verify_module():
    return load_script_module("coach_pr_verify_under_test", PR_VERIFY_SCRIPT_PATH)


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


class FakeRunner:
    def __init__(
        self,
        *,
        changed_files: list[str] | None = None,
        diff_text: str = "diff --git a/docs/example.md b/docs/example.md\n+safe=true\n",
        merge_return_code: int = 0,
        post_pytest_return_code: int = 0,
        metadata_updates: dict | None = None,
        status_rollup: list[dict] | None = None,
    ) -> None:
        self.calls: list[list[str]] = []
        self.changed_files = changed_files or [
            "scripts/coach_pr_verify.py",
            "tests/test_coach_pr_verify_merge_runner.py",
            "docs/WORKFLOW_COACH_PR_VERIFY_MERGE_RUNNER_v0.2.3-auto.md",
        ]
        self.diff_text = diff_text
        self.merge_return_code = merge_return_code
        self.post_pytest_return_code = post_pytest_return_code
        self.metadata_updates = metadata_updates or {}
        self.status_rollup = status_rollup if status_rollup is not None else [
            {"name": "tests", "conclusion": "SUCCESS"}
        ]

    def __call__(self, args: list[str], cwd: Path, timeout: int = 60, env: dict | None = None) -> dict:
        self.calls.append(args)
        if args[:3] == ["gh", "pr", "view"] and args[-1] != "files":
            payload = {
                "number": 40,
                "state": "OPEN",
                "isDraft": False,
                "mergeable": "MERGEABLE",
                "baseRefName": "main",
                "headRefName": "codex-040-coach-pr-verify-merge-runner",
                "headRefOid": "abc1234",
                "reviewDecision": "APPROVED",
                "statusCheckRollup": self.status_rollup,
            }
            payload.update(self.metadata_updates)
            return ok_json(args, payload)
        if args[:3] == ["gh", "pr", "view"] and args[-1] == "files":
            return ok_json(args, {"files": [{"path": path} for path in self.changed_files]})
        if args[:3] == ["gh", "pr", "diff"]:
            return ok(args, stdout=self.diff_text)
        if args[:3] == ["gh", "pr", "merge"]:
            if self.merge_return_code == 0:
                return ok(args, stdout="merged")
            return failed(args, stderr="merge rejected", return_code=self.merge_return_code)
        if args[:2] == ["git", "checkout"]:
            return ok(args, stdout="checked out main")
        if args[:2] == ["git", "pull"]:
            return ok(args, stdout="already up to date")
        if args[-3:] == ["-m", "pytest"] or args[-2:] == ["-m", "pytest"]:
            if self.post_pytest_return_code == 0:
                return ok(args, stdout="555 passed")
            return failed(args, stderr="tests failed", return_code=self.post_pytest_return_code)
        return ok(args)


def ok(args: list[str], stdout: str = "") -> dict:
    return {"args": args, "return_code": 0, "stdout": stdout, "stderr": "", "timed_out": False}


def ok_json(args: list[str], payload: dict) -> dict:
    return ok(args, stdout=json.dumps(payload))


def failed(args: list[str], stderr: str, return_code: int = 1) -> dict:
    return {
        "args": args,
        "return_code": return_code,
        "stdout": "",
        "stderr": stderr,
        "timed_out": False,
    }


def write_codex_return(temp_dir: str) -> Path:
    path = Path(temp_dir) / "codex_return.md"
    path.write_text(VALID_CODEX_RETURN, encoding="utf-8")
    return path


def valid_report(module) -> dict:
    with tempfile.TemporaryDirectory() as temp_dir:
        return module.build_pre_merge_report(
            VALID_PR_URL,
            "auto_after_verify",
            "codex_040_example",
            write_codex_return(temp_dir),
            ["docs/", "tests/", ".dicoimpro/", "scripts/"],
            ["src/", ".github/workflows/"],
            runner=FakeRunner(),
        )


def test_pr_verify_script_and_workflow_doc_exist():
    assert PR_VERIFY_SCRIPT_PATH.exists()
    assert WORKFLOW_DOC_PATH.exists()


def test_pr_verify_script_imports_only_standard_library():
    imports = imported_roots(PR_VERIFY_SCRIPT_PATH)
    standard_roots = set(sys.stdlib_module_names) | {"__future__"}
    non_standard = sorted(imports.difference(standard_roots))
    assert non_standard == []


def test_pr_verify_script_has_no_forbidden_imports_and_no_shell_true():
    imports = imported_roots(PR_VERIFY_SCRIPT_PATH)
    forbidden = sorted(imports.intersection(FORBIDDEN_IMPORT_ROOTS))
    assert forbidden == []

    source = read_text(PR_VERIFY_SCRIPT_PATH)
    assert "shell=True" not in source


def test_parse_pr_url_extracts_owner_repo_and_number():
    module = pr_verify_module()
    parsed = module.parse_pr_url(VALID_PR_URL)
    assert parsed["owner"] == "Nyoha12"
    assert parsed["repo"] == "dicoimpro"
    assert parsed["number"] == 40
    assert parsed["repo_full_name"] == "Nyoha12/dicoimpro"


def test_default_report_build_never_runs_merge_command():
    module = pr_verify_module()
    runner = FakeRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        module.build_pre_merge_report(
            VALID_PR_URL,
            "manual",
            "codex_040_example",
            write_codex_return(temp_dir),
            ["docs/", "tests/", ".dicoimpro/", "scripts/"],
            ["src/", ".github/workflows/"],
            runner=runner,
        )
    assert not any(call[:3] == ["gh", "pr", "merge"] for call in runner.calls)


def test_merge_requires_execute_flag_auto_mode_and_allowed_decision():
    module = pr_verify_module()
    report = valid_report(module)
    allowed = module.decide_report_with_autonomy(report, REPO_ROOT)

    runner = FakeRunner()
    no_execute = module.execute_merge_if_allowed(report, allowed, REPO_ROOT, runner=runner)
    assert no_execute["executed"] is False
    assert any("--execute-merge" in blocker for blocker in no_execute["blockers"])
    assert runner.calls == []

    manual_report = dict(report)
    manual_report["merge_mode"] = "manual"
    manual = module.execute_merge_if_allowed(manual_report, allowed, REPO_ROOT, runner=runner, execute=True)
    assert manual["executed"] is False
    assert any("merge_mode" in blocker for blocker in manual["blockers"])

    blocked_decision = {
        "decision": "auto_merge_blocked",
        "allowed": False,
        "autonomy_level": "stop_human",
        "blockers": ["pytest did not pass"],
        "warnings": [],
        "next_required_action": "stop",
    }
    blocked = module.execute_merge_if_allowed(
        report,
        blocked_decision,
        REPO_ROOT,
        runner=runner,
        execute=True,
    )
    assert blocked["executed"] is False
    assert any("autonomy decision is blocked" in blocker for blocker in blocked["blockers"])


def test_merge_command_uses_match_head_commit_and_never_pushes_main():
    module = pr_verify_module()
    report = valid_report(module)
    decision = module.decide_report_with_autonomy(report, REPO_ROOT)
    runner = FakeRunner()
    result = module.execute_merge_if_allowed(report, decision, REPO_ROOT, runner=runner, execute=True)

    assert result["executed"] is True
    merge_calls = [call for call in runner.calls if call[:3] == ["gh", "pr", "merge"]]
    assert len(merge_calls) == 1
    merge_call = merge_calls[0]
    assert "--match-head-commit" in merge_call
    assert "abc1234" in merge_call
    assert not any(call[:2] == ["git", "push"] for call in runner.calls)


def test_post_merge_validation_runs_only_after_successful_merge_and_reports_failure():
    module = pr_verify_module()
    report = valid_report(module)
    decision = module.decide_report_with_autonomy(report, REPO_ROOT)

    blocked_runner = FakeRunner(merge_return_code=1)
    merge_result = module.execute_merge_if_allowed(
        report,
        decision,
        REPO_ROOT,
        runner=blocked_runner,
        execute=True,
    )
    assert merge_result["executed"] is False
    assert not any(call[0] == "git" for call in blocked_runner.calls)

    success_runner = FakeRunner()
    merge_result = module.execute_merge_if_allowed(
        report,
        decision,
        REPO_ROOT,
        runner=success_runner,
        execute=True,
    )
    assert merge_result["executed"] is True
    post = module.run_post_merge_validation(REPO_ROOT, "codex_040_example", runner=success_runner)
    assert post["passed"] is True
    assert any(call[:2] == ["git", "checkout"] for call in success_runner.calls)
    assert any(call[-2:] == ["-m", "pytest"] for call in success_runner.calls)

    failing_runner = FakeRunner(post_pytest_return_code=1)
    failed_post = module.run_post_merge_validation(REPO_ROOT, "codex_040_example", runner=failing_runner)
    assert failed_post["decision"] == "stop_human"
    assert failed_post["return_code"] == 1
    assert failed_post["passed"] is False
    assert failed_post["no_destructive_auto_repair"] is True


def test_build_pre_merge_report_shape_matches_autonomy_policy():
    module = pr_verify_module()
    report = valid_report(module)

    for key in (
        "merge_mode",
        "pr",
        "scope",
        "checks",
        "codex_return",
        "reviews",
        "contradictions_detected",
    ):
        assert key in report

    assert report["merge_mode"] == "auto_after_verify"
    assert report["pr"]["url"] == VALID_PR_URL
    assert report["checks"]["pytest"] == "passed"
    assert report["checks"]["diff_check"] == "passed"
    assert report["codex_return"]["archived"] is True
    assert report["codex_return"]["valid"] is True
    assert report["codex_return"]["guardrail_guarantee_present"] is True


def test_report_blocks_forbidden_paths_and_detects_secret_like_strings():
    module = pr_verify_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        report = module.build_pre_merge_report(
            VALID_PR_URL,
            "auto_after_verify",
            "codex_040_example",
            write_codex_return(temp_dir),
            ["docs/", "tests/", ".dicoimpro/", "scripts/"],
            ["src/", ".github/workflows/"],
            runner=FakeRunner(
                changed_files=["src/dico_impro/example.py"],
                diff_text="+api_key = 'abc123456789'",
            ),
        )

    assert report["scope"]["secrets_detected"] is True
    assert report["scope"]["forbidden_touched"] == ["src/dico_impro/example.py"]
    decision = module.decide_report_with_autonomy(report, REPO_ROOT)
    assert decision["allowed"] is False
    assert any("forbidden paths" in blocker for blocker in decision["blockers"])
    assert any("secret" in blocker for blocker in decision["blockers"])


def test_report_blocks_missing_codex_return_and_accepts_valid_archive():
    module = pr_verify_module()
    missing_report = module.build_pre_merge_report(
        VALID_PR_URL,
        "auto_after_verify",
        "codex_040_example",
        None,
        ["docs/", "tests/", ".dicoimpro/", "scripts/"],
        ["src/", ".github/workflows/"],
        runner=FakeRunner(),
    )
    assert missing_report["codex_return"]["archived"] is False
    decision = module.decide_report_with_autonomy(missing_report, REPO_ROOT)
    assert decision["allowed"] is False
    assert any("not archived" in blocker for blocker in decision["blockers"])

    valid = valid_report(module)
    assert valid["codex_return"]["archived"] is True
    assert valid["codex_return"]["valid"] is True


def test_decisions_block_manual_and_allow_green_auto_after_verify():
    module = pr_verify_module()
    report = valid_report(module)

    manual = dict(report)
    manual["merge_mode"] = "manual"
    manual_decision = module.decide_report_with_autonomy(manual, REPO_ROOT)
    assert manual_decision["allowed"] is False
    assert any("manual" in blocker for blocker in manual_decision["blockers"])

    decision = module.decide_report_with_autonomy(report, REPO_ROOT)
    assert decision["decision"] == "auto_merge_allowed"
    assert decision["allowed"] is True
    assert decision["autonomy_level"] == "auto_merge_after_verify"


def test_changed_files_within_scope_catches_src_when_forbidden():
    module = pr_verify_module()
    result = module.changed_files_within_scope(
        ["src/dico_impro/runtime.py", "docs/example.md"],
        ["docs/", "tests/", ".dicoimpro/", "scripts/"],
        ["src/", ".github/workflows/"],
    )
    assert result["within_authorized_scope"] is False
    assert result["forbidden_touched"] == ["src/dico_impro/runtime.py"]
    assert "src/dico_impro/runtime.py" in result["unauthorized_files"]


def test_summarize_verify_result_lists_blockers():
    module = pr_verify_module()
    report = valid_report(module)
    decision = {
        "decision": "auto_merge_blocked",
        "allowed": False,
        "autonomy_level": "stop_human",
        "blockers": ["pytest did not pass"],
        "warnings": [],
        "next_required_action": "stop",
    }
    summary = module.summarize_verify_result(report, decision)
    assert "Blockers: pytest did not pass" in summary


def test_cli_exposes_expected_commands():
    source = read_text(PR_VERIFY_SCRIPT_PATH)
    for command in ("verify", "decide-report", "summarize-report", "validate-boundary"):
        assert f'"{command}"' in source


def test_workflow_doc_states_required_merge_boundaries():
    workflow = normalize_text(read_text(WORKFLOW_DOC_PATH))
    required_phrases = (
        "merge is never default",
        "--execute-merge required",
        "match-head-commit required",
        "post-merge tests must run",
        "external codex implementing this mission must not merge pr #40",
        "does not call openai/gpt/codex sdk/codex cli",
        "does not implement autonomous full loop",
    )
    for phrase in required_phrases:
        assert phrase in workflow, f"Workflow doc is missing: {phrase}"


def test_coach_guidance_contains_guarded_pr_verify_boundary():
    guidance = normalize_text(read_text(COACH_GUIDANCE_PATH))
    required_phrases = (
        "guarded pr verification and merge execution boundary",
        "merge is possible only through explicit verify runner",
        "merge never happens by default",
        "--execute-merge and merge_mode auto_after_verify are required",
        "fresh verify gate and stable head sha are required",
        "post-merge tests are required",
        "post-merge failure stops human",
        "no destructive auto-repair",
    )
    for phrase in required_phrases:
        assert phrase in guidance, f"Coach guidance is missing: {phrase}"


def test_readme_and_post_015_review_reference_codex_040_and_workflow_doc():
    readme = normalize_text(read_text(README_PATH))
    review = normalize_text(read_text(POST_015_REVIEW_PATH))

    assert "workflow_coach_pr_verify_merge_runner_v0.2.3-auto.md" in readme
    assert "codex 040" in readme
    assert "guarded pr verification and optional auto-merge runner" in readme
    assert "with --execute-merge plus auto_after_verify" in readme

    assert "codex 040" in review
    assert "555 tests passing" in review
    assert "scripts/coach_pr_verify.py is the only newly authorized real merge-capable workflow script" in review
    assert "external codex implementing this repository change must not merge pr #40" in review


def test_no_src_references_pr_verify_script_or_workflow_doc():
    forbidden_terms = (
        "coach_pr_verify.py",
        "coach_pr_verify",
        "WORKFLOW_COACH_PR_VERIFY_MERGE_RUNNER",
    )
    for path in SRC_DIR.rglob("*.py"):
        source = read_text(path)
        for term in forbidden_terms:
            assert term not in source, f"{path} must not reference PR verify runner: {term}"


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
