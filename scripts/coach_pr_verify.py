from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from typing import Callable


RUNS_RELATIVE_PATH = Path(".dicoimpro") / "runs"
POLICY_RELATIVE_PATH = Path(".dicoimpro") / "WORKFLOW_AUTONOMY_POLICY.example.json"
DEFAULT_PRE_MERGE_INDEX = "08"
DEFAULT_POST_MERGE_INDEX = "09"
DEFAULT_AUTHORIZED_PATHS = ("docs/", "tests/", ".dicoimpro/", "scripts/")
DEFAULT_FORBIDDEN_PATHS = ("src/", ".github/workflows/")

PR_URL_RE = re.compile(
    r"^https://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/"
    r"(?P<repo>[A-Za-z0-9_.-]+)/pull/(?P<number>[0-9]+)(?:[/?#].*)?$"
)
SECRET_PATTERNS = (
    ("api_key_assignment", re.compile(r"(?i)\bapi[_-]?key\b\s*[:=]\s*['\"]?[^'\"\s]+")),
    ("token_assignment", re.compile(r"(?i)\btoken\b\s*[:=]\s*['\"]?[^'\"\s]+")),
    ("secret_assignment", re.compile(r"(?i)\bsecret\b\s*[:=]\s*['\"]?[^'\"\s]+")),
    ("github_pat", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("openai_key_shape", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)


CommandRunner = Callable[[list[str], Path], dict]


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


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"Required file does not exist: {path}") from exc


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


def parse_pr_url(url: str) -> dict:
    match = PR_URL_RE.match(url.strip())
    if not match:
        raise ValueError("PR URL must look like https://github.com/<owner>/<repo>/pull/<number>")
    owner = match.group("owner")
    repo = match.group("repo")
    number = int(match.group("number"))
    return {
        "owner": owner,
        "repo": repo,
        "number": number,
        "repo_full_name": f"{owner}/{repo}",
        "url": f"https://github.com/{owner}/{repo}/pull/{number}",
    }


def run_command(
    args: list[str],
    cwd: Path,
    timeout: int = 60,
    env: dict | None = None,
) -> dict:
    import subprocess

    try:
        completed = subprocess.run(
            args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "args": args,
            "return_code": 124,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or f"Command timed out after {timeout} seconds.",
            "timed_out": True,
        }

    return {
        "args": args,
        "return_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "timed_out": False,
    }


def _command_failed(result: dict) -> bool:
    return int(result.get("return_code", 1)) != 0


def _require_success(result: dict, label: str) -> None:
    if _command_failed(result):
        stderr = str(result.get("stderr") or "").strip()
        stdout = str(result.get("stdout") or "").strip()
        detail = stderr or stdout or "no command output"
        raise ValueError(f"{label} failed: {detail}")


def _call_runner(
    runner: Callable,
    args: list[str],
    cwd: Path,
    timeout: int = 60,
    env: dict | None = None,
) -> dict:
    try:
        return runner(args, cwd, timeout=timeout, env=env)
    except TypeError:
        return runner(args, cwd)


def gh_json(args: list[str], cwd: Path, runner: Callable = run_command) -> dict:
    result = runner(["gh", *args], cwd)
    _require_success(result, "gh JSON command")
    try:
        data = json.loads(result.get("stdout") or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"gh JSON command returned malformed JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("gh JSON command must return an object")
    return data


def _load_script_module(module_name: str, script_name: str):
    repo_root = repo_root_from_path()
    script_path = repo_root / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load script module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_codex_handoff_module():
    return _load_script_module("coach_codex_handoff_for_pr_verify", "coach_codex_handoff.py")


def load_autonomy_module():
    return _load_script_module("coach_autonomy_for_pr_verify", "coach_autonomy.py")


def fetch_pr_metadata(pr_url: str, runner: Callable = run_command) -> dict:
    parsed = parse_pr_url(pr_url)
    data = gh_json(
        [
            "pr",
            "view",
            parsed["url"],
            "--repo",
            parsed["repo_full_name"],
            "--json",
            "number,state,isDraft,mergeable,baseRefName,headRefName,headRefOid,"
            "reviewDecision,statusCheckRollup",
        ],
        repo_root_from_path(),
        runner=runner,
    )
    mergeable_value = data.get("mergeable")
    if isinstance(mergeable_value, str):
        mergeable = mergeable_value.casefold() == "mergeable"
    else:
        mergeable = mergeable_value is True

    head_sha = data.get("headRefOid")
    head_branch = data.get("headRefName")
    return {
        "url": parsed["url"],
        "number": int(data.get("number") or parsed["number"]),
        "open": str(data.get("state") or "").upper() == "OPEN",
        "draft": data.get("isDraft") is True,
        "mergeable": mergeable,
        "base": data.get("baseRefName"),
        "head_branch": head_branch,
        "head_branch_authorized": _head_branch_authorized(head_branch),
        "head_sha": head_sha,
        "head_sha_stable": bool(head_sha),
        "review_decision": data.get("reviewDecision"),
        "status_check_rollup": data.get("statusCheckRollup") or [],
        "repo_full_name": parsed["repo_full_name"],
    }


def fetch_pr_changed_files(pr_url: str, runner: Callable = run_command) -> list[str]:
    parsed = parse_pr_url(pr_url)
    data = gh_json(
        ["pr", "view", parsed["url"], "--repo", parsed["repo_full_name"], "--json", "files"],
        repo_root_from_path(),
        runner=runner,
    )
    files = data.get("files") or []
    if not isinstance(files, list):
        raise ValueError("gh files payload must be a list")

    changed_files: list[str] = []
    for item in files:
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            changed_files.append(item["path"])
        elif isinstance(item, str):
            changed_files.append(item)
    return changed_files


def fetch_pr_diff(pr_url: str, runner: Callable = run_command) -> str:
    parsed = parse_pr_url(pr_url)
    result = runner(
        ["gh", "pr", "diff", parsed["url"], "--repo", parsed["repo_full_name"]],
        repo_root_from_path(),
    )
    _require_success(result, "gh PR diff")
    return str(result.get("stdout") or "")


def detect_secrets_in_text(text: str) -> dict:
    labels: list[str] = []
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            labels.append(label)
    return {
        "secrets_detected": bool(labels),
        "matches": sorted(set(labels)),
    }


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def _path_matches(path: str, pattern: str) -> bool:
    import fnmatch

    normalized_path = _normalize_path(path)
    normalized_pattern = _normalize_path(pattern)
    if normalized_pattern.endswith("/"):
        return normalized_path == normalized_pattern[:-1] or normalized_path.startswith(
            normalized_pattern
        )
    return fnmatch.fnmatch(normalized_path, normalized_pattern)


def changed_files_within_scope(
    changed_files: list[str],
    authorized_paths: list[str],
    forbidden_paths: list[str],
) -> dict:
    forbidden_touched = [
        path
        for path in changed_files
        if any(_path_matches(path, pattern) for pattern in forbidden_paths)
    ]
    unauthorized_files = [
        path
        for path in changed_files
        if not any(_path_matches(path, pattern) for pattern in authorized_paths)
    ]
    return {
        "within_authorized_scope": bool(changed_files) and not unauthorized_files,
        "forbidden_touched": forbidden_touched,
        "unauthorized_files": unauthorized_files,
    }


def _head_branch_authorized(branch: object) -> bool:
    return isinstance(branch, str) and branch.startswith(("codex-", "coach-")) and branch != "main"


def _normalized_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _status_from_return_text(return_text: str, command_name: str) -> str:
    normalized = _normalized_text(return_text)
    if command_name not in normalized:
        return "failed"
    if any(marker in normalized for marker in ("failed", "failure", "error")):
        return "failed"
    if any(marker in normalized for marker in ("passed", "clean", "ok", "success")):
        return "passed"
    return "failed"


def _ci_status_from_rollup(rollup: object) -> str:
    if not rollup:
        return "not_required"
    if not isinstance(rollup, list):
        return "failed"

    for item in rollup:
        if not isinstance(item, dict):
            return "failed"
        conclusion = str(item.get("conclusion") or item.get("state") or "").casefold()
        status = str(item.get("status") or "").casefold()
        if conclusion in {"failure", "failed", "cancelled", "timed_out", "action_required"}:
            return "failed"
        if status in {"queued", "in_progress", "pending", "waiting"}:
            return "failed"
        if conclusion and conclusion not in {"success", "skipped", "neutral", "passed"}:
            return "failed"
    return "passed"


def _codex_return_evidence(codex_return_path: Path | None, expected_pr_url: str) -> dict:
    if codex_return_path is None:
        return {
            "archived": False,
            "valid": False,
            "guardrail_guarantee_present": False,
            "errors": ["Codex return path is required"],
            "pr_url": None,
            "text": "",
        }

    absolute_path = codex_return_path.resolve()
    if not absolute_path.exists():
        return {
            "archived": False,
            "valid": False,
            "guardrail_guarantee_present": False,
            "errors": [f"Codex return file does not exist: {codex_return_path}"],
            "pr_url": None,
            "text": "",
        }

    return_text = read_text(absolute_path)
    handoff = load_codex_handoff_module()
    errors = handoff.validate_codex_return_text(return_text)
    pr_url = handoff.extract_pr_url(return_text)
    if pr_url and pr_url != expected_pr_url:
        errors.append("Codex return PR URL contradicts supplied PR URL")
    normalized = _normalized_text(return_text)
    return {
        "archived": True,
        "valid": errors == [],
        "guardrail_guarantee_present": "guardrail guarantee" in normalized,
        "errors": errors,
        "pr_url": pr_url,
        "text": return_text,
    }


def build_pre_merge_report(
    pr_url: str,
    merge_mode: str,
    run_id: str,
    codex_return_path: Path | None,
    authorized_paths: list[str],
    forbidden_paths: list[str],
    runner: Callable = run_command,
) -> dict:
    metadata = fetch_pr_metadata(pr_url, runner=runner)
    changed_files = fetch_pr_changed_files(pr_url, runner=runner)
    diff_text = fetch_pr_diff(pr_url, runner=runner)
    secret_scan = detect_secrets_in_text(diff_text)
    scope = changed_files_within_scope(changed_files, authorized_paths, forbidden_paths)
    codex_return = _codex_return_evidence(codex_return_path, metadata["url"])
    return_text = codex_return.pop("text")
    review_decision = str(metadata.get("review_decision") or "").upper()

    return {
        "merge_mode": merge_mode,
        "run_id": run_id,
        "pr": {
            "url": metadata["url"],
            "number": metadata["number"],
            "open": metadata["open"],
            "draft": metadata["draft"],
            "mergeable": metadata["mergeable"],
            "base": metadata["base"],
            "head_branch": metadata["head_branch"],
            "head_branch_authorized": metadata["head_branch_authorized"],
            "head_sha": metadata["head_sha"],
            "head_sha_stable": metadata["head_sha_stable"],
            "repo_full_name": metadata["repo_full_name"],
        },
        "scope": {
            "changed_files": changed_files,
            "authorized_paths": authorized_paths,
            "forbidden_paths": forbidden_paths,
            "secrets_detected": secret_scan["secrets_detected"],
            "secret_match_types": secret_scan["matches"],
            "within_authorized_scope": scope["within_authorized_scope"],
            "forbidden_touched": scope["forbidden_touched"],
            "unauthorized_files": scope["unauthorized_files"],
        },
        "checks": {
            "pytest": _status_from_return_text(return_text, "pytest"),
            "diff_check": _status_from_return_text(return_text, "git diff --check"),
            "ci": _ci_status_from_rollup(metadata.get("status_check_rollup")),
        },
        "codex_return": codex_return,
        "reviews": {
            "request_changes": review_decision == "CHANGES_REQUESTED",
            "blocking_review": review_decision == "CHANGES_REQUESTED",
            "review_decision": metadata.get("review_decision"),
        },
        "contradictions_detected": any(
            "contradict" in error.casefold() for error in codex_return.get("errors", [])
        ),
        "run_config": {
            "auto_merge_authorized": merge_mode == "auto_after_verify",
        },
        "evidence": {
            "diff_available": bool(diff_text),
            "metadata_source": "gh CLI",
            "changed_files_source": "gh CLI",
            "diff_source": "gh CLI",
        },
    }


def _report_target_path(repo_root: Path, run_id: str, suffix: str, default_index: str) -> Path:
    if not isinstance(run_id, str) or not run_id.strip() or Path(run_id).name != run_id:
        raise ValueError("run_id must be a single safe path segment")
    return repo_root / RUNS_RELATIVE_PATH / run_id / f"{default_index}_{suffix}.json"


def save_pre_merge_report(
    repo_root: Path,
    run_id: str,
    report: dict,
    overwrite: bool = False,
) -> Path:
    output_path = _report_target_path(repo_root, run_id, "pre_merge_report", DEFAULT_PRE_MERGE_INDEX)
    if output_path.exists() and not overwrite:
        raise ValueError(f"Target already exists: {output_path}. Use --overwrite to replace it.")
    write_json(output_path, report)
    return output_path


def decide_report_with_autonomy(report: dict, repo_root: Path) -> dict:
    autonomy = load_autonomy_module()
    policy = autonomy.load_autonomy_policy(repo_root)
    errors = autonomy.validate_autonomy_policy(policy)
    if errors:
        raise ValueError("Autonomy policy is invalid: " + "; ".join(errors))
    return autonomy.decide_auto_merge(report, policy)


def execute_merge_if_allowed(
    report: dict,
    decision: dict,
    repo_root: Path,
    runner: Callable = run_command,
    execute: bool = False,
) -> dict:
    blockers: list[str] = []
    if not execute:
        blockers.append("--execute-merge is required")
    if report.get("merge_mode") != "auto_after_verify":
        blockers.append("merge_mode must be auto_after_verify")
    if decision.get("allowed") is not True:
        blockers.append("autonomy decision is blocked")
    if decision.get("autonomy_level") != "auto_merge_after_verify":
        blockers.append("autonomy level must be auto_merge_after_verify")
    if decision.get("blockers"):
        blockers.extend(str(blocker) for blocker in decision["blockers"])

    pr = report.get("pr", {})
    head_sha = pr.get("head_sha")
    if not head_sha:
        blockers.append("head SHA is missing")
    if pr.get("mergeable") is not True:
        blockers.append("PR is not mergeable")

    if blockers:
        return {
            "executed": False,
            "return_code": 1,
            "decision": "stop_human",
            "blockers": blockers,
            "next_required_action": "Do not merge; resolve blockers with a human.",
        }

    parsed = parse_pr_url(pr.get("url") or "")
    command = [
        "gh",
        "pr",
        "merge",
        str(pr.get("number") or parsed["number"]),
        "--repo",
        pr.get("repo_full_name") or parsed["repo_full_name"],
        "--merge",
        "--delete-branch",
        "--match-head-commit",
        str(head_sha),
    ]
    result = runner(command, repo_root)
    return {
        "executed": not _command_failed(result),
        "attempted": True,
        "return_code": int(result.get("return_code", 1)),
        "command": command,
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "decision": "merge_executed" if not _command_failed(result) else "stop_human",
        "blockers": [] if not _command_failed(result) else ["merge command failed"],
        "next_required_action": (
            "Run post-merge validation."
            if not _command_failed(result)
            else "Stop for human intervention; do not auto-repair."
        ),
    }


def _post_merge_env(repo_root: Path) -> dict:
    env = dict(os.environ)
    src_path = str(repo_root / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        src_path if not existing_pythonpath else os.pathsep.join((src_path, existing_pythonpath))
    )
    temp_dir = repo_root / ".dicoimpro" / "tmp" / "coach_pr_verify"
    temp_dir.mkdir(parents=True, exist_ok=True)
    env.setdefault("TEMP", str(temp_dir))
    env.setdefault("TMP", str(temp_dir))
    return env


def run_post_merge_validation(
    repo_root: Path,
    run_id: str,
    runner: Callable = run_command,
) -> dict:
    steps: list[dict] = []
    commands = (
        ("git_checkout_main", ["git", "checkout", "main"], 60),
        ("git_pull_main", ["git", "pull", "origin", "main"], 120),
        ("pytest", [sys.executable, "-m", "pytest"], 3600),
    )
    env = _post_merge_env(repo_root)
    for label, command, timeout in commands:
        result = _call_runner(runner, command, repo_root, timeout=timeout, env=env)
        step = {
            "name": label,
            "command": command,
            "return_code": int(result.get("return_code", 1)),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
        }
        steps.append(step)
        if step["return_code"] != 0:
            return {
                "run_id": run_id,
                "passed": False,
                "return_code": 1,
                "decision": "stop_human",
                "steps": steps,
                "next_required_action": (
                    "Post-merge validation failed; stop for human intervention "
                    "and do not auto-repair."
                ),
                "no_destructive_auto_repair": True,
            }

    return {
        "run_id": run_id,
        "passed": True,
        "return_code": 0,
        "decision": "post_merge_validation_passed",
        "steps": steps,
        "next_required_action": "Record the successful post-merge validation.",
        "no_destructive_auto_repair": True,
    }


def write_post_merge_report(
    repo_root: Path,
    run_id: str,
    report: dict,
    overwrite: bool = False,
) -> Path:
    output_path = _report_target_path(
        repo_root,
        run_id,
        "post_merge_report",
        DEFAULT_POST_MERGE_INDEX,
    )
    if output_path.exists() and not overwrite:
        raise ValueError(f"Target already exists: {output_path}. Use --overwrite to replace it.")
    write_json(output_path, report)
    return output_path


def summarize_verify_result(report: dict, decision: dict) -> str:
    pr = report.get("pr", {})
    checks = report.get("checks", {})
    scope = report.get("scope", {})
    blockers = decision.get("blockers") or []
    lines = [
        f"PR: {pr.get('url', 'unknown')}",
        f"Merge mode: {report.get('merge_mode', 'unknown')}",
        f"Decision: {decision.get('decision', 'unknown')}",
        f"Allowed: {decision.get('allowed')}",
        f"Autonomy level: {decision.get('autonomy_level', 'unknown')}",
        "Checks: "
        f"pytest={checks.get('pytest', 'unknown')}, "
        f"diff_check={checks.get('diff_check', 'unknown')}, "
        f"ci={checks.get('ci', 'unknown')}",
        "Changed files: " + ", ".join(scope.get("changed_files") or ["none"]),
    ]
    if blockers:
        lines.append("Blockers: " + "; ".join(str(blocker) for blocker in blockers))
    else:
        lines.append("Blockers: none")
    lines.append("Default behavior: no merge unless --execute-merge is explicitly supplied.")
    return "\n".join(lines)


def _print_json(data: dict) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def _boundary_summary() -> str:
    return (
        "Boundary: merge is never default. A real merge requires --execute-merge, "
        "merge_mode auto_after_verify, a fresh successful verify gate, a stable "
        "head SHA, and --match-head-commit. Post-merge tests run only after an "
        "executed merge. No OpenAI/GPT/Codex SDK/Codex CLI or autonomous full loop "
        "is implemented here."
    )


def _resolve_optional_path(repo_root: Path, value: str | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = repo_root / path
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guarded coach PR verification runner.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify_parser = subparsers.add_parser("verify", help="Build PR report and decision.")
    verify_parser.add_argument("--run-id", required=True)
    verify_parser.add_argument("--pr-url", required=True)
    verify_parser.add_argument("--codex-return-path")
    verify_parser.add_argument("--merge-mode", choices=("manual", "auto_after_verify"), default="manual")
    verify_parser.add_argument("--authorized-path", action="append", dest="authorized_paths")
    verify_parser.add_argument("--forbidden-path", action="append", dest="forbidden_paths")
    verify_parser.add_argument("--execute-merge", action="store_true")
    verify_parser.add_argument("--overwrite", action="store_true")

    decide_parser = subparsers.add_parser(
        "decide-report",
        help="Decide auto-merge from a supplied report without gh/git.",
    )
    decide_parser.add_argument("--report-json", required=True)

    summarize_parser = subparsers.add_parser(
        "summarize-report",
        help="Summarize a supplied report without gh/git.",
    )
    summarize_parser.add_argument("--report-json", required=True)

    subparsers.add_parser("validate-boundary", help="Print explicit merge boundary.")

    args = parser.parse_args(argv)

    try:
        repo_root = repo_root_from_path()

        if args.command == "validate-boundary":
            print(_boundary_summary())
            return 0

        if args.command == "decide-report":
            report_path = Path(args.report_json)
            if not report_path.is_absolute():
                report_path = repo_root / report_path
            _print_json(decide_report_with_autonomy(read_json(report_path), repo_root))
            return 0

        if args.command == "summarize-report":
            report_path = Path(args.report_json)
            if not report_path.is_absolute():
                report_path = repo_root / report_path
            report = read_json(report_path)
            decision = decide_report_with_autonomy(report, repo_root)
            print(summarize_verify_result(report, decision))
            return 0

        if args.command == "verify":
            authorized_paths = args.authorized_paths or list(DEFAULT_AUTHORIZED_PATHS)
            forbidden_paths = args.forbidden_paths or list(DEFAULT_FORBIDDEN_PATHS)
            report = build_pre_merge_report(
                args.pr_url,
                args.merge_mode,
                args.run_id,
                _resolve_optional_path(repo_root, args.codex_return_path),
                authorized_paths,
                forbidden_paths,
            )
            report_path = save_pre_merge_report(
                repo_root,
                args.run_id,
                report,
                overwrite=args.overwrite,
            )
            decision = decide_report_with_autonomy(report, repo_root)
            print(f"Pre-merge report: {report_path}")
            print(summarize_verify_result(report, decision))

            if not args.execute_merge:
                return 0

            merge_result = execute_merge_if_allowed(
                report,
                decision,
                repo_root,
                execute=True,
            )
            _print_json({"merge_result": merge_result})
            if merge_result.get("executed") is not True:
                return 1

            post_merge_report = run_post_merge_validation(repo_root, args.run_id)
            post_merge_path = write_post_merge_report(
                repo_root,
                args.run_id,
                post_merge_report,
                overwrite=args.overwrite,
            )
            print(f"Post-merge report: {post_merge_path}")
            _print_json({"post_merge_report": post_merge_report})
            return 0 if post_merge_report.get("passed") is True else 1
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
