from __future__ import annotations

import ast
import importlib.util
import sys
import tomllib
import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DICOIMPRO_DIR = REPO_ROOT / ".dicoimpro"
DOCS_DIR = REPO_ROOT / "docs"
SCRIPTS_DIR = REPO_ROOT / "scripts"
SRC_DIR = REPO_ROOT / "src" / "dico_impro"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

POLICY_PATH = DICOIMPRO_DIR / "WORKFLOW_AUTONOMY_POLICY.example.json"
AUTONOMY_SCRIPT_PATH = SCRIPTS_DIR / "coach_autonomy.py"
WORKFLOW_DOC_PATH = DOCS_DIR / "WORKFLOW_COACH_AUTONOMY_VERIFY_GATE_v0.2.3-auto.md"
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


def valid_gate() -> dict:
    return {
        "evaluated_next_stage": "cadrage",
        "can_advance": True,
        "reflection_required": False,
        "next_prompt_ready": True,
        "next_prompt_type": "stage_prompt",
        "blocking_question": None,
        "reason": "The next stage is ready.",
        "required_user_intervention": False,
        "allowed_to_execute_automatically": False,
    }


def valid_pre_merge_report() -> dict:
    return {
        "merge_mode": "auto_after_verify",
        "pr": {
            "url": "https://github.com/Nyoha12/dicoimpro/pull/99",
            "open": True,
            "draft": False,
            "mergeable": True,
            "base": "main",
            "head_branch": "codex-099-example",
            "head_sha": "abc1234",
            "head_sha_stable": True,
        },
        "scope": {
            "changed_files": ["docs/example.md", "tests/test_example.py"],
            "authorized_paths": ["docs/", "tests/", ".dicoimpro/", "scripts/"],
            "forbidden_paths": ["src/", ".github/workflows/"],
            "secrets_detected": False,
        },
        "checks": {
            "pytest": "passed",
            "diff_check": "passed",
            "ci": "passed",
        },
        "codex_return": {
            "archived": True,
            "valid": True,
            "guardrail_guarantee_present": True,
        },
        "reviews": {
            "request_changes": False,
            "blocking_review": False,
        },
        "contradictions_detected": False,
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


def autonomy_module():
    return load_script_module("coach_autonomy_under_test", AUTONOMY_SCRIPT_PATH)


def policy_under_test() -> dict:
    module = autonomy_module()
    return module.read_json(POLICY_PATH)


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


def assert_decision_shape(decision: dict) -> None:
    assert set(("decision", "allowed", "autonomy_level", "blockers", "warnings", "next_required_action")).issubset(decision)
    assert isinstance(decision["allowed"], bool)
    assert isinstance(decision["blockers"], list)
    assert isinstance(decision["warnings"], list)


def test_autonomy_policy_script_and_workflow_doc_exist():
    assert POLICY_PATH.exists()
    assert AUTONOMY_SCRIPT_PATH.exists()
    assert WORKFLOW_DOC_PATH.exists()


def test_coach_autonomy_imports_only_standard_library():
    imports = imported_roots(AUTONOMY_SCRIPT_PATH)
    standard_roots = set(sys.stdlib_module_names) | {"__future__"}
    non_standard = sorted(imports.difference(standard_roots))
    assert non_standard == []


def test_coach_autonomy_has_no_forbidden_imports_or_execution_strings():
    imports = imported_roots(AUTONOMY_SCRIPT_PATH)
    forbidden = sorted(imports.intersection(FORBIDDEN_IMPORT_ROOTS))
    assert forbidden == []

    source = read_text(AUTONOMY_SCRIPT_PATH)
    forbidden_fragments = (
        "gh pr merge",
        "git merge",
        "git push",
        "subprocess.run",
        "os.system",
        "requests",
        "httpx",
        "GitHub API calls",
    )
    for fragment in forbidden_fragments:
        assert fragment not in source


def test_autonomy_policy_validates_and_has_expected_defaults():
    module = autonomy_module()
    policy = policy_under_test()
    assert module.validate_autonomy_policy(policy) == []

    for level in (
        "stop_human",
        "auto_local",
        "auto_external_with_budget",
        "auto_merge_after_verify",
    ):
        assert level in policy["autonomy_levels"]
    assert policy["merge_mode"] == "manual"
    assert "manual" in policy["allowed_merge_modes"]
    assert "auto_after_verify" in policy["allowed_merge_modes"]
    assert policy["max_reflections_per_stage"] == 3


def test_gate_with_required_user_intervention_true_stops_human():
    module = autonomy_module()
    gate = valid_gate()
    gate["required_user_intervention"] = True
    decision = module.evaluate_gate_autonomy(gate, policy_under_test())
    assert_decision_shape(decision)
    assert decision["decision"] == "stop_human"
    assert decision["allowed"] is False
    assert any("required_user_intervention" in blocker for blocker in decision["blockers"])


def test_gate_with_can_advance_false_stops_human_when_substantive():
    module = autonomy_module()
    gate = valid_gate()
    gate["can_advance"] = False
    gate["reason"] = "Human decision required to approve a scope change."
    decision = module.evaluate_gate_autonomy(gate, policy_under_test())
    assert decision["decision"] == "stop_human"
    assert decision["allowed"] is False
    assert any("substantive decision" in blocker for blocker in decision["blockers"])


def test_gate_ready_without_human_intervention_can_continue():
    module = autonomy_module()
    decision = module.evaluate_gate_autonomy(valid_gate(), policy_under_test())
    assert_decision_shape(decision)
    assert decision["decision"] == "auto_continue_allowed"
    assert decision["allowed"] is True
    assert decision["autonomy_level"] == "auto_local"


def test_auto_reflection_allowed_below_limit():
    module = autonomy_module()
    gate = valid_gate()
    gate["reflection_required"] = True
    gate["can_advance"] = False
    gate["blocking_question"] = "Clarify the local evidence summary."
    decision = module.can_auto_reflect(gate, policy_under_test(), reflection_count=1)
    assert decision["decision"] == "auto_reflection_allowed"
    assert decision["allowed"] is True


def test_auto_reflection_blocked_at_limit():
    module = autonomy_module()
    gate = valid_gate()
    gate["reflection_required"] = True
    decision = module.can_auto_reflect(gate, policy_under_test(), reflection_count=3)
    assert decision["decision"] == "stop_human"
    assert decision["allowed"] is False
    assert any("max_reflections_per_stage" in blocker for blocker in decision["blockers"])


def test_auto_reflection_blocked_for_substantive_human_decision():
    module = autonomy_module()
    gate = valid_gate()
    gate["reflection_required"] = True
    gate["blocking_question"] = "Should a human approve this scope change?"
    decision = module.can_auto_reflect(gate, policy_under_test(), reflection_count=1)
    assert decision["decision"] == "stop_human"
    assert any("substantive human decision" in blocker for blocker in decision["blockers"])


def test_api_budget_passes_when_under_budget_and_blocks_when_exceeded():
    module = autonomy_module()
    policy = policy_under_test()

    allowed = module.evaluate_api_budget(
        policy,
        {
            "explicit_launch_authorization": True,
            "gpt_calls": 1,
            "codex_handoffs": 1,
            "total_external_calls": 2,
            "usd_spent": 0.5,
        },
    )
    assert allowed["decision"] == "api_budget_ok"
    assert allowed["allowed"] is True

    blocked = module.evaluate_api_budget(
        policy,
        {
            "explicit_launch_authorization": True,
            "gpt_calls": 11,
            "codex_handoffs": 1,
            "total_external_calls": 12,
            "usd_spent": 0.5,
        },
    )
    assert blocked["decision"] == "api_budget_exceeded"
    assert blocked["allowed"] is False


def test_pre_merge_report_with_manual_merge_mode_blocks_auto_merge():
    module = autonomy_module()
    report = valid_pre_merge_report()
    report["merge_mode"] = "manual"
    decision = module.decide_auto_merge(report, policy_under_test())
    assert decision["decision"] == "auto_merge_blocked"
    assert decision["allowed"] is False
    assert any("manual" in blocker for blocker in decision["blockers"])


def test_pre_merge_report_with_auto_after_verify_and_green_checks_allows_auto_merge_decision():
    module = autonomy_module()
    decision = module.decide_auto_merge(valid_pre_merge_report(), policy_under_test())
    assert_decision_shape(decision)
    assert decision["decision"] == "auto_merge_allowed"
    assert decision["allowed"] is True
    assert decision["autonomy_level"] == "auto_merge_after_verify"


def assert_auto_merge_blocks(mutator, expected_text: str) -> None:
    module = autonomy_module()
    report = valid_pre_merge_report()
    mutator(report)
    decision = module.decide_auto_merge(report, policy_under_test())
    assert_decision_shape(decision)
    assert decision["decision"] == "auto_merge_blocked"
    assert decision["allowed"] is False
    assert any(expected_text in blocker for blocker in decision["blockers"])


def test_pre_merge_report_blocks_on_pr_state_scope_checks_reviews_and_contradictions():
    cases = (
        (lambda report: report["pr"].update({"draft": True}), "draft"),
        (lambda report: report["pr"].update({"mergeable": False}), "not mergeable"),
        (lambda report: report["pr"].update({"base": "develop"}), "base branch"),
        (lambda report: report["pr"].update({"head_sha_stable": False}), "head SHA"),
        (lambda report: report["scope"]["changed_files"].append("src/dico_impro/example.py"), "forbidden paths"),
        (lambda report: report["scope"].update({"secrets_detected": True}), "secret"),
        (lambda report: report["checks"].update({"pytest": "failed"}), "pytest"),
        (lambda report: report["checks"].update({"diff_check": "failed"}), "git diff --check"),
        (lambda report: report["checks"].update({"ci": "failed"}), "CI"),
        (lambda report: report["codex_return"].update({"archived": False}), "not archived"),
        (lambda report: report["codex_return"].update({"valid": False}), "invalid"),
        (
            lambda report: report["codex_return"].update({"guardrail_guarantee_present": False}),
            "guardrail guarantee",
        ),
        (lambda report: report["reviews"].update({"request_changes": True}), "REQUEST_CHANGES"),
        (lambda report: report.update({"contradictions_detected": True}), "contradiction"),
    )
    for mutator, expected_text in cases:
        assert_auto_merge_blocks(mutator, expected_text)


def test_workflow_doc_states_required_autonomy_boundaries():
    workflow = normalize_text(read_text(WORKFLOW_DOC_PATH))
    required_phrases = (
        "merge is manual by default",
        "auto-merge is allowed only after full verify gate",
        "codex 039 does not perform real merge",
        "does not call github api",
        "does not run git",
        "does not run gh",
        "codex sdk",
        "codex cli",
        "risk cannot be classified, stop_human",
    )
    for phrase in required_phrases:
        assert phrase in workflow, f"Workflow doc is missing: {phrase}"


def test_coach_guidance_contains_program_autonomy_and_verification_policy():
    guidance = normalize_text(read_text(COACH_GUIDANCE_PATH))
    required_phrases = (
        "program autonomy and verification policy",
        "stop_human",
        "auto_local",
        "auto_external_with_budget",
        "auto_merge_after_verify",
        "merge is manual by default",
        "auto-merge possible only with auto_after_verify",
        "repository scripts in codex 039 only decide, they do not merge",
    )
    for phrase in required_phrases:
        assert phrase in guidance, f"Coach guidance is missing: {phrase}"


def test_readme_and_post_015_review_reference_codex_039_and_workflow_doc():
    readme = normalize_text(read_text(README_PATH))
    review = normalize_text(read_text(POST_015_REVIEW_PATH))

    assert "workflow_coach_autonomy_verify_gate_v0.2.3-auto.md" in readme
    assert "codex 039" in readme
    assert "autonomy policy and pre-merge verify gate" in readme
    assert "without real merge" in readme

    assert "codex 039" in review
    assert "535 tests passing" in review
    assert "autonomy policy and pre-merge verify gate" in review
    assert "policy possibility, not an implemented merge action" in review


def test_no_src_references_autonomy_script_or_workflow_doc():
    forbidden_terms = (
        "coach_autonomy.py",
        "coach_autonomy",
        "WORKFLOW_COACH_AUTONOMY_VERIFY_GATE",
    )
    for path in SRC_DIR.rglob("*.py"):
        source = read_text(path)
        for term in forbidden_terms:
            assert term not in source, f"{path} must not reference autonomy gate: {term}"


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
