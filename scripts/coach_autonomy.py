from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path


POLICY_RELATIVE_PATH = Path(".dicoimpro") / "WORKFLOW_AUTONOMY_POLICY.example.json"
REQUIRED_POLICY_KEYS = (
    "schema_version",
    "autonomy_levels",
    "default_autonomy_level",
    "merge_mode",
    "allowed_merge_modes",
    "max_reflections_per_stage",
    "api_budget",
    "sensitive_path_patterns",
    "forbidden_path_patterns",
    "requires_human_intervention",
    "pre_merge_verify_required",
    "post_merge_verify_required",
    "auto_merge_policy_statement",
)
REQUIRED_AUTONOMY_LEVELS = (
    "stop_human",
    "auto_local",
    "auto_external_with_budget",
    "auto_merge_after_verify",
)
REQUIRED_MERGE_MODES = ("manual", "auto_after_verify")
DECISION_KEYS = (
    "decision",
    "allowed",
    "autonomy_level",
    "blockers",
    "warnings",
    "next_required_action",
)
OK_STATUSES = {"passed", "pass", "ok", "success", "successful"}
CI_OK_STATUSES = OK_STATUSES | {"not_required", "not required", "skipped_by_policy"}


def repo_root_from_path(path: Path | None = None) -> Path:
    start = Path.cwd() if path is None else Path(path)
    start = start.resolve()
    if start.is_file():
        start = start.parent

    for candidate in (start, *start.parents):
        if (candidate / POLICY_RELATIVE_PATH).exists():
            return candidate
        if (candidate / "pyproject.toml").exists() and (candidate / ".dicoimpro").exists():
            return candidate

    raise ValueError("Could not find repository root containing .dicoimpro")


def read_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise ValueError(f"JSON file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON file is malformed: {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return data


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def load_autonomy_policy(repo_root: Path) -> dict:
    return read_json(repo_root / POLICY_RELATIVE_PATH)


def validate_autonomy_policy(policy: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(policy, dict):
        return ["policy must be a JSON object"]

    for key in REQUIRED_POLICY_KEYS:
        if key not in policy:
            errors.append(f"policy is missing required key: {key}")

    levels = policy.get("autonomy_levels")
    if not isinstance(levels, list):
        errors.append("policy.autonomy_levels must be a list")
        levels = []
    for level in REQUIRED_AUTONOMY_LEVELS:
        if level not in levels:
            errors.append(f"policy.autonomy_levels must include: {level}")

    default_level = policy.get("default_autonomy_level")
    if default_level not in levels:
        errors.append("policy.default_autonomy_level must be one of autonomy_levels")

    merge_mode = policy.get("merge_mode")
    allowed_merge_modes = policy.get("allowed_merge_modes")
    if not isinstance(allowed_merge_modes, list):
        errors.append("policy.allowed_merge_modes must be a list")
        allowed_merge_modes = []
    for mode in REQUIRED_MERGE_MODES:
        if mode not in allowed_merge_modes:
            errors.append(f"policy.allowed_merge_modes must include: {mode}")
    if merge_mode != "manual":
        errors.append("policy.merge_mode must default to manual")
    if merge_mode not in allowed_merge_modes:
        errors.append("policy.merge_mode must be one of allowed_merge_modes")

    max_reflections = policy.get("max_reflections_per_stage")
    if not isinstance(max_reflections, int) or max_reflections != 3:
        errors.append("policy.max_reflections_per_stage must default to 3")

    api_budget = policy.get("api_budget")
    if not isinstance(api_budget, dict):
        errors.append("policy.api_budget must be an object")
    else:
        for key in (
            "max_gpt_calls_per_run",
            "max_codex_handoffs_per_run",
            "max_total_external_calls_per_run",
            "max_usd_per_run",
            "requires_explicit_launch_authorization",
        ):
            if key not in api_budget:
                errors.append(f"policy.api_budget is missing required key: {key}")

    for key in ("sensitive_path_patterns", "forbidden_path_patterns"):
        if not isinstance(policy.get(key), list):
            errors.append(f"policy.{key} must be a list")

    triggers = policy.get("requires_human_intervention", {}).get("triggers")
    if not isinstance(triggers, list) or not triggers:
        errors.append("policy.requires_human_intervention.triggers must be a non-empty list")

    pre_merge_fields = policy.get("pre_merge_verify_required", {}).get("fields")
    if not isinstance(pre_merge_fields, list) or not pre_merge_fields:
        errors.append("policy.pre_merge_verify_required.fields must be a non-empty list")

    post_merge_fields = policy.get("post_merge_verify_required", {}).get("fields")
    if not isinstance(post_merge_fields, list) or not post_merge_fields:
        errors.append("policy.post_merge_verify_required.fields must be a non-empty list")

    statement = policy.get("auto_merge_policy_statement")
    if not isinstance(statement, str) or "verify gate" not in statement.casefold():
        errors.append("policy.auto_merge_policy_statement must mention verify gate")

    return errors


def normalize_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().casefold() in {"1", "true", "yes", "y", "ok", "passed"}
    if isinstance(value, (int, float)):
        return value != 0
    return False


def _decision(
    decision: str,
    allowed: bool,
    autonomy_level: str,
    blockers: list[str] | None = None,
    warnings: list[str] | None = None,
    next_required_action: str = "",
) -> dict:
    return {
        "decision": decision,
        "allowed": allowed,
        "autonomy_level": autonomy_level,
        "blockers": blockers or [],
        "warnings": warnings or [],
        "next_required_action": next_required_action,
    }


def _normalized_text(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).casefold().split())


def _is_substantive_human_decision(text: object, context: dict | None = None) -> bool:
    if context and normalize_bool(context.get("substantive_decision_required")):
        return True
    normalized = _normalized_text(text)
    if not normalized:
        return False
    markers = (
        "approve",
        "approval",
        "authorize",
        "authorization",
        "choose",
        "decision",
        "human decision",
        "scope change",
        "risk acceptance",
        "budget",
        "secret",
        "token",
        "production",
        "merge",
        "publish",
    )
    return any(marker in normalized for marker in markers)


def human_intervention_required(
    gate: dict,
    policy: dict,
    context: dict | None = None,
) -> dict:
    blockers: list[str] = []
    warnings: list[str] = []
    context = context or {}

    if not isinstance(gate, dict):
        blockers.append("transition_gate is missing or malformed")
    else:
        if normalize_bool(gate.get("required_user_intervention")):
            blockers.append("transition_gate.required_user_intervention is true")
        if gate.get("can_advance") is False and _is_substantive_human_decision(
            gate.get("reason") or gate.get("blocking_question"),
            context,
        ):
            blockers.append("transition_gate.can_advance is false for a substantive decision")

    context_blockers = (
        ("objective_absent_or_ambiguous", "run objective is absent or ambiguous"),
        ("scope_change_proposed", "scope change is proposed"),
        ("contradictions_detected", "contradiction is detected"),
        (
            "sensitive_files_touched_without_authorization",
            "sensitive files are touched without explicit authorization",
        ),
        ("dependencies_modified_without_authorization", "dependencies are modified without authorization"),
        ("github_workflows_modified", "workflow files are modified"),
        ("secrets_detected", "secrets, API keys, or tokens are detected"),
        ("tests_failed", "tests fail"),
        ("diff_check_failed", "git diff --check fails"),
        ("api_budget_exceeded", "API budget is exceeded"),
    )
    for key, message in context_blockers:
        if normalize_bool(context.get(key)):
            blockers.append(message)

    if normalize_bool(context.get("docs_tests_scripts_only")) and normalize_bool(
        context.get("src_touched")
    ):
        blockers.append("src/ is touched while the run is docs/tests/scripts only")

    if context.get("gpt_note_valid") is False:
        blockers.append("GPT note is invalid")
    if context.get("codex_return_valid") is False:
        blockers.append("Codex return is invalid")
    if context.get("pr_mergeable") is False:
        blockers.append("PR is not mergeable")
    if _normalized_text(context.get("ci")) in {"failed", "red", "failure"}:
        blockers.append("CI is red")
    if normalize_bool(context.get("review_request_changes")):
        blockers.append("a review asks for changes")
    if context.get("risk_classified") is False or _normalized_text(context.get("risk")) == "unknown":
        blockers.append("risk cannot be classified")

    if blockers:
        return _decision(
            "stop_human",
            False,
            "stop_human",
            blockers,
            warnings,
            "Ask for a human decision before continuing.",
        )

    return _decision(
        "human_intervention_not_required",
        True,
        "auto_local",
        [],
        warnings,
        "Continue according to the next eligible autonomy level.",
    )


def evaluate_gate_autonomy(
    gate: dict,
    policy: dict,
    context: dict | None = None,
) -> dict:
    human = human_intervention_required(gate, policy, context)
    if not human["allowed"]:
        return human

    if gate.get("can_advance") is True and gate.get("next_prompt_ready") is True:
        return _decision(
            "auto_continue_allowed",
            True,
            "auto_local",
            [],
            [],
            "Continue locally to the next prepared stage.",
        )

    return _decision(
        "stop_human",
        False,
        "stop_human",
        ["transition_gate does not allow automatic continuation"],
        [],
        "Ask for a human decision or a valid reflection prompt.",
    )


def can_auto_reflect(
    gate: dict,
    policy: dict,
    reflection_count: int,
    blocking_question: str | None = None,
) -> dict:
    blockers: list[str] = []
    limit = policy.get("max_reflections_per_stage", 3)
    question = blocking_question if blocking_question is not None else gate.get("blocking_question")

    if not normalize_bool(gate.get("reflection_required")):
        blockers.append("reflection_required is not true")
    if normalize_bool(gate.get("required_user_intervention")):
        blockers.append("required_user_intervention is true")
    if _is_substantive_human_decision(question):
        blockers.append("blocking question is a substantive human decision")
    if not isinstance(reflection_count, int) or reflection_count < 0:
        blockers.append("reflection_count must be a non-negative integer")
    elif reflection_count >= limit:
        blockers.append("max_reflections_per_stage is reached")

    if blockers:
        return _decision(
            "stop_human",
            False,
            "stop_human",
            blockers,
            [],
            "Summarize the unresolved blockage for a human.",
        )

    return _decision(
        "auto_reflection_allowed",
        True,
        "auto_external_with_budget",
        [],
        [],
        "Prepare the next reflection only if external budget and launch authorization allow it.",
    )


def evaluate_api_budget(policy: dict, usage: dict) -> dict:
    budget = policy.get("api_budget", {})
    blockers: list[str] = []
    warnings: list[str] = []

    gpt_calls = usage.get("gpt_calls", 0)
    codex_handoffs = usage.get("codex_handoffs", 0)
    total_external = usage.get("total_external_calls", gpt_calls + codex_handoffs)
    usd_spent = usage.get("usd_spent", 0.0)

    if budget.get("requires_explicit_launch_authorization") is True:
        if total_external > 0 and not normalize_bool(usage.get("explicit_launch_authorization")):
            blockers.append("external calls require explicit launch authorization")

    limits = (
        ("gpt_calls", gpt_calls, budget.get("max_gpt_calls_per_run")),
        ("codex_handoffs", codex_handoffs, budget.get("max_codex_handoffs_per_run")),
        ("total_external_calls", total_external, budget.get("max_total_external_calls_per_run")),
        ("usd_spent", usd_spent, budget.get("max_usd_per_run")),
    )
    for label, actual, maximum in limits:
        if maximum is not None and actual > maximum:
            blockers.append(f"{label} exceeds budget: {actual} > {maximum}")

    if blockers:
        return _decision(
            "api_budget_exceeded",
            False,
            "stop_human",
            blockers,
            warnings,
            "Stop for human budget review.",
        )

    return _decision(
        "api_budget_ok",
        True,
        "auto_external_with_budget",
        [],
        warnings,
        "External budget is available if the run was explicitly authorized.",
    )


def _status_ok(value: object, allowed: set[str]) -> bool:
    return _normalized_text(value) in allowed


def _path_matches(path: str, pattern: str) -> bool:
    normalized_path = path.replace("\\", "/")
    normalized_pattern = pattern.replace("\\", "/")
    if normalized_pattern.endswith("/"):
        return normalized_path == normalized_pattern[:-1] or normalized_path.startswith(normalized_pattern)
    return fnmatch.fnmatch(normalized_path, normalized_pattern)


def _changed_files_within_authorized_scope(changed_files: list[str], authorized_paths: list[str]) -> bool:
    if not changed_files:
        return False
    if not authorized_paths:
        return False
    return all(
        any(_path_matches(path, authorized_path) for authorized_path in authorized_paths)
        for path in changed_files
    )


def _forbidden_files_touched(changed_files: list[str], forbidden_paths: list[str]) -> list[str]:
    return [
        path
        for path in changed_files
        if any(_path_matches(path, forbidden_path) for forbidden_path in forbidden_paths)
    ]


def _head_branch_authorized(branch: object, pr: dict) -> bool:
    if normalize_bool(pr.get("head_branch_authorized")):
        return True
    if not isinstance(branch, str) or not branch.strip():
        return False
    return branch.startswith(("codex-", "coach-")) and branch != "main"


def validate_pre_merge_report(report: dict, policy: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(report, dict):
        return ["pre-merge report must be a JSON object"]

    for key in ("merge_mode", "pr", "scope", "checks", "codex_return", "reviews"):
        if key not in report:
            errors.append(f"pre-merge report is missing required key: {key}")

    for key in ("pr", "scope", "checks", "codex_return", "reviews"):
        if key in report and not isinstance(report[key], dict):
            errors.append(f"pre-merge report.{key} must be an object")

    pr = report.get("pr") if isinstance(report.get("pr"), dict) else {}
    for key in ("url", "open", "draft", "mergeable", "base", "head_branch", "head_sha", "head_sha_stable"):
        if key not in pr:
            errors.append(f"pre-merge report.pr is missing required key: {key}")

    scope = report.get("scope") if isinstance(report.get("scope"), dict) else {}
    for key in ("changed_files", "authorized_paths", "forbidden_paths", "secrets_detected"):
        if key not in scope:
            errors.append(f"pre-merge report.scope is missing required key: {key}")
    for key in ("changed_files", "authorized_paths", "forbidden_paths"):
        if key in scope and not isinstance(scope[key], list):
            errors.append(f"pre-merge report.scope.{key} must be a list")

    checks = report.get("checks") if isinstance(report.get("checks"), dict) else {}
    for key in ("pytest", "diff_check", "ci"):
        if key not in checks:
            errors.append(f"pre-merge report.checks is missing required key: {key}")

    codex_return = report.get("codex_return") if isinstance(report.get("codex_return"), dict) else {}
    for key in ("archived", "valid", "guardrail_guarantee_present"):
        if key not in codex_return:
            errors.append(f"pre-merge report.codex_return is missing required key: {key}")

    reviews = report.get("reviews") if isinstance(report.get("reviews"), dict) else {}
    for key in ("request_changes", "blocking_review"):
        if key not in reviews:
            errors.append(f"pre-merge report.reviews is missing required key: {key}")

    merge_mode = report.get("merge_mode")
    if merge_mode not in policy.get("allowed_merge_modes", []):
        errors.append("pre-merge report.merge_mode must be an allowed merge mode")

    return errors


def decide_auto_merge(report: dict, policy: dict) -> dict:
    blockers = validate_pre_merge_report(report, policy)
    warnings: list[str] = []
    if blockers:
        return _decision(
            "stop_human",
            False,
            "stop_human",
            blockers,
            warnings,
            "Fix or complete the supplied pre-merge report.",
        )

    merge_mode = report["merge_mode"]
    pr = report["pr"]
    scope = report["scope"]
    checks = report["checks"]
    codex_return = report["codex_return"]
    reviews = report["reviews"]

    if merge_mode != "auto_after_verify":
        blockers.append("merge_mode is manual; auto-merge is not authorized")

    if not pr.get("url"):
        blockers.append("PR is not detected")
    if pr.get("open") is not True:
        blockers.append("PR is not open")
    if pr.get("draft") is not False:
        blockers.append("PR is draft")
    if pr.get("mergeable") is not True:
        blockers.append("PR is not mergeable")
    if pr.get("base") != policy.get("pre_merge_verify_required", {}).get("required_base_branch", "main"):
        blockers.append("base branch is not main")
    if not _head_branch_authorized(pr.get("head_branch"), pr):
        blockers.append("head branch is not authorized")
    if not (pr.get("head_sha") and (pr.get("head_sha_stable") is True or pr.get("head_sha_verified") is True)):
        blockers.append("head SHA is not stable or explicitly verified")

    changed_files = scope.get("changed_files", [])
    authorized_paths = scope.get("authorized_paths", [])
    forbidden_paths = list(scope.get("forbidden_paths", [])) + list(
        policy.get("forbidden_path_patterns", [])
    )
    if not _changed_files_within_authorized_scope(changed_files, authorized_paths):
        blockers.append("changed files are outside authorized scope")
    forbidden_touched = _forbidden_files_touched(changed_files, forbidden_paths)
    if forbidden_touched:
        blockers.append("forbidden paths are touched: " + ", ".join(sorted(forbidden_touched)))
    if scope.get("secrets_detected") is not False:
        blockers.append("secret is detected")

    if codex_return.get("archived") is not True:
        blockers.append("Codex return is not archived")
    if codex_return.get("valid") is not True:
        blockers.append("Codex return is invalid")
    if codex_return.get("guardrail_guarantee_present") is not True:
        blockers.append("guardrail guarantee is missing")

    if not _status_ok(checks.get("pytest"), OK_STATUSES):
        blockers.append("pytest did not pass")
    if not _status_ok(checks.get("diff_check"), OK_STATUSES):
        blockers.append("git diff --check did not pass")
    if not _status_ok(checks.get("ci"), CI_OK_STATUSES):
        blockers.append("CI did not pass")

    if reviews.get("blocking_review") is not False:
        blockers.append("blocking review exists")
    if reviews.get("request_changes") is not False:
        blockers.append("REQUEST_CHANGES review exists")
    if report.get("contradictions_detected") is not False:
        blockers.append("contradiction is detected")
    if report.get("run_config", {}).get("auto_merge_authorized") is False:
        blockers.append("run config does not authorize auto-merge")

    if blockers:
        return _decision(
            "auto_merge_blocked",
            False,
            "stop_human",
            blockers,
            warnings,
            "Stop before merge and resolve blockers with a human.",
        )

    return _decision(
        "auto_merge_allowed",
        True,
        "auto_merge_after_verify",
        [],
        warnings,
        "A future authorized implementation may merge; this script never performs the merge.",
    )


def summarize_decision(decision: dict) -> str:
    missing = [key for key in DECISION_KEYS if key not in decision]
    if missing:
        return "Malformed decision missing keys: " + ", ".join(missing)
    status = "allowed" if decision["allowed"] else "blocked"
    blockers = decision.get("blockers") or []
    if blockers:
        return f"{decision['decision']} ({status}): {decision['next_required_action']} Blockers: {'; '.join(blockers)}"
    return f"{decision['decision']} ({status}): {decision['next_required_action']}"


def _print_errors(errors: list[str]) -> None:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)


def _print_json(data: dict) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def _summary_text(policy: dict) -> str:
    levels = ", ".join(policy.get("autonomy_levels", []))
    merge_mode = policy.get("merge_mode")
    max_reflections = policy.get("max_reflections_per_stage")
    return (
        "Coach autonomy policy: "
        f"levels={levels}; default_merge_mode={merge_mode}; "
        "auto-merge requires merge_mode auto_after_verify and complete verify gate; "
        f"max_reflections_per_stage={max_reflections}; "
        "this script decides only and performs no merge."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local coach autonomy decision utilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate-policy", help="Validate the example autonomy policy.")

    decide_gate_parser = subparsers.add_parser(
        "decide-gate",
        help="Decide whether a transition_gate can continue automatically.",
    )
    decide_gate_parser.add_argument("--gate-json", required=True)

    reflect_parser = subparsers.add_parser(
        "can-reflect",
        help="Decide whether auto-reflection is allowed.",
    )
    reflect_parser.add_argument("--gate-json", required=True)
    reflect_parser.add_argument("--reflection-count", required=True, type=int)

    verify_parser = subparsers.add_parser(
        "verify-merge",
        help="Decide whether auto-merge would be allowed from a supplied report.",
    )
    verify_parser.add_argument("--report-json", required=True)

    subparsers.add_parser("summarize-policy", help="Print a short policy summary.")

    args = parser.parse_args(argv)

    try:
        repo_root = repo_root_from_path()
        policy = load_autonomy_policy(repo_root)
        policy_errors = validate_autonomy_policy(policy)
        if args.command == "validate-policy":
            if policy_errors:
                _print_errors(policy_errors)
                return 1
            print(f"OK: {repo_root / POLICY_RELATIVE_PATH}")
            return 0
        if policy_errors:
            raise ValueError("Autonomy policy is invalid: " + "; ".join(policy_errors))

        if args.command == "decide-gate":
            gate_path = Path(args.gate_json)
            if not gate_path.is_absolute():
                gate_path = repo_root / gate_path
            _print_json(evaluate_gate_autonomy(read_json(gate_path), policy))
            return 0

        if args.command == "can-reflect":
            gate_path = Path(args.gate_json)
            if not gate_path.is_absolute():
                gate_path = repo_root / gate_path
            gate = read_json(gate_path)
            _print_json(can_auto_reflect(gate, policy, args.reflection_count))
            return 0

        if args.command == "verify-merge":
            report_path = Path(args.report_json)
            if not report_path.is_absolute():
                report_path = repo_root / report_path
            _print_json(decide_auto_merge(read_json(report_path), policy))
            return 0

        if args.command == "summarize-policy":
            print(_summary_text(policy))
            return 0
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
