from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


RUNS_RELATIVE_PATH = Path(".dicoimpro") / "runs"
POLICY_RELATIVE_PATH = Path(".dicoimpro") / "WORKFLOW_AUTONOMY_POLICY.example.json"
LOOP_STATE_FILENAME = "loop_state.json"
LOOP_SUMMARY_FILENAME = "loop_summary.md"
SCHEMA_VERSION = "coach_loop_state.v1"
DEFAULT_AUTHORIZED_PATHS = ("docs/", "tests/", ".dicoimpro/", "scripts/")
DEFAULT_FORBIDDEN_PATHS = ("src/", ".github/workflows/")

REQUIRED_LOOP_STATE_KEYS = (
    "schema_version",
    "run_id",
    "stage",
    "status",
    "created_or_updated_by",
    "context_path",
    "model_prompt_path",
    "stage_note_path",
    "transition_gate",
    "autonomy_decision",
    "reflection_count_current_stage",
    "max_reflections_per_stage",
    "gpt_call_count",
    "external_call_count",
    "handoff_path",
    "codex_return_path",
    "pr_url",
    "pre_merge_report_path",
    "merge_decision",
    "post_merge_report_path",
    "blockers",
    "warnings",
    "next_required_action",
)


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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _validate_path_segment(value: str, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    path = Path(value)
    if path.name != value or value in {".", ".."}:
        raise ValueError(f"{label} must be a single safe path segment")


def _repo_relative_path(repo_root: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    absolute = path if path.is_absolute() else repo_root / path
    try:
        return absolute.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _load_script_module(module_name: str, script_name: str):
    repo_root = repo_root_from_path()
    module_path = repo_root / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load script module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_coach_state_module():
    return _load_script_module("coach_state_for_loop", "coach_state.py")


def load_context_module():
    return _load_script_module("coach_collect_context_for_loop", "coach_collect_context.py")


def load_step_module():
    return _load_script_module("coach_step_for_loop", "coach_step.py")


def load_handoff_module():
    return _load_script_module("coach_codex_handoff_for_loop", "coach_codex_handoff.py")


def load_autonomy_module():
    return _load_script_module("coach_autonomy_for_loop", "coach_autonomy.py")


def load_pr_verify_module():
    return _load_script_module("coach_pr_verify_for_loop", "coach_pr_verify.py")


def run_folder(repo_root: Path, run_id: str) -> Path:
    _validate_path_segment(run_id, "run_id")
    folder = repo_root / RUNS_RELATIVE_PATH / run_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def loop_state_path(repo_root: Path, run_id: str) -> Path:
    return run_folder(repo_root, run_id) / LOOP_STATE_FILENAME


def loop_summary_path(repo_root: Path, run_id: str) -> Path:
    return run_folder(repo_root, run_id) / LOOP_SUMMARY_FILENAME


def load_policy(repo_root: Path) -> dict:
    autonomy = load_autonomy_module()
    policy = autonomy.load_autonomy_policy(repo_root)
    errors = autonomy.validate_autonomy_policy(policy)
    if errors:
        raise ValueError("Autonomy policy is invalid: " + "; ".join(errors))
    return policy


def initial_loop_state(run_id: str, stage: str, policy: dict | None = None) -> dict:
    _validate_path_segment(run_id, "run_id")
    _validate_path_segment(stage, "stage")
    max_reflections = 3
    if isinstance(policy, dict):
        value = policy.get("max_reflections_per_stage")
        if isinstance(value, int):
            max_reflections = value

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "stage": stage,
        "status": "initialized",
        "created_or_updated_by": "scripts/coach_loop.py",
        "context_path": None,
        "model_prompt_path": None,
        "stage_note_path": None,
        "transition_gate": {},
        "autonomy_decision": {},
        "reflection_count_current_stage": 0,
        "max_reflections_per_stage": max_reflections,
        "gpt_call_count": 0,
        "external_call_count": 0,
        "handoff_path": None,
        "codex_return_path": None,
        "pr_url": None,
        "pre_merge_report_path": None,
        "merge_decision": {},
        "post_merge_report_path": None,
        "blockers": [],
        "warnings": [],
        "next_required_action": "Start or resume the local coach loop.",
    }


def validate_loop_state_shape(state: dict) -> list[str]:
    if not isinstance(state, dict):
        return ["loop state must be a JSON object"]
    errors: list[str] = []
    for key in REQUIRED_LOOP_STATE_KEYS:
        if key not in state:
            errors.append(f"loop state is missing required key: {key}")
    if state.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"loop state schema_version must be {SCHEMA_VERSION}")
    for key in ("blockers", "warnings"):
        if key in state and not isinstance(state[key], list):
            errors.append(f"loop state {key} must be a list")
    for key in ("transition_gate", "autonomy_decision", "merge_decision"):
        if key in state and not isinstance(state[key], dict):
            errors.append(f"loop state {key} must be an object")
    return errors


def load_loop_state(repo_root: Path, run_id: str, stage: str | None = None) -> dict:
    path = loop_state_path(repo_root, run_id)
    if path.exists():
        state = read_json(path)
        errors = validate_loop_state_shape(state)
        if errors:
            raise ValueError("Loop state is invalid: " + "; ".join(errors))
        return state
    policy = load_policy(repo_root)
    return initial_loop_state(run_id, stage or "pre_cadrage", policy)


def save_loop_state(repo_root: Path, state: dict) -> Path:
    errors = validate_loop_state_shape(state)
    if errors:
        raise ValueError("Cannot write loop state: " + "; ".join(errors))
    output_path = loop_state_path(repo_root, state["run_id"])
    write_json(output_path, state)
    return output_path


def _set_status(
    state: dict,
    status: str,
    next_required_action: str,
    blockers: list[str] | None = None,
    warnings: list[str] | None = None,
) -> dict:
    state["status"] = status
    state["next_required_action"] = next_required_action
    state["blockers"] = blockers or []
    if warnings is not None:
        state["warnings"] = warnings
    return state


def stop_human(state: dict, blockers: list[str], next_required_action: str) -> dict:
    return _set_status(state, "stop_human", next_required_action, blockers)


def summarize_state_markdown(state: dict) -> str:
    blockers = state.get("blockers") or []
    warnings = state.get("warnings") or []
    lines = [
        "# Coach Loop Summary",
        "",
        "```text",
        f"schema_version: {state.get('schema_version')}",
        f"run_id: {state.get('run_id')}",
        f"stage: {state.get('stage')}",
        f"status: {state.get('status')}",
        f"context_path: {state.get('context_path')}",
        f"model_prompt_path: {state.get('model_prompt_path')}",
        f"stage_note_path: {state.get('stage_note_path')}",
        f"handoff_path: {state.get('handoff_path')}",
        f"codex_return_path: {state.get('codex_return_path')}",
        f"pr_url: {state.get('pr_url')}",
        f"pre_merge_report_path: {state.get('pre_merge_report_path')}",
        f"post_merge_report_path: {state.get('post_merge_report_path')}",
        f"gpt_call_count: {state.get('gpt_call_count')}",
        f"external_call_count: {state.get('external_call_count')}",
        f"next_required_action: {state.get('next_required_action')}",
        "```",
        "",
        "## Blockers",
        "",
        "\n".join(f"- {blocker}" for blocker in blockers) if blockers else "None.",
        "",
        "## Warnings",
        "",
        "\n".join(f"- {warning}" for warning in warnings) if warnings else "None.",
    ]
    return "\n".join(lines) + "\n"


def write_loop_summary(repo_root: Path, state: dict) -> Path:
    output_path = loop_summary_path(repo_root, state["run_id"])
    write_text(output_path, summarize_state_markdown(state))
    return output_path


def _api_budget_decision(policy: dict, state: dict, add_gpt_calls: int) -> dict:
    autonomy = load_autonomy_module()
    gpt_calls = int(state.get("gpt_call_count", 0)) + add_gpt_calls
    external_calls = int(state.get("external_call_count", 0)) + add_gpt_calls
    return autonomy.evaluate_api_budget(
        policy,
        {
            "explicit_launch_authorization": True,
            "gpt_calls": gpt_calls,
            "codex_handoffs": 0,
            "total_external_calls": external_calls,
            "usd_spent": 0.0,
        },
    )


def _record_gpt_call(state: dict) -> None:
    state["gpt_call_count"] = int(state.get("gpt_call_count", 0)) + 1
    state["external_call_count"] = int(state.get("external_call_count", 0)) + 1


def _run_gpt_stage(
    repo_root: Path,
    state: dict,
    stage: str,
    user_instruction: str | None,
    previous_note: Path | None,
    model: str,
    policy: dict,
) -> tuple[dict, str | None]:
    budget = _api_budget_decision(policy, state, 1)
    if not budget.get("allowed"):
        state["autonomy_decision"] = budget
        stop_human(state, budget.get("blockers", []), "Stop for API budget review.")
        return state, None

    step = load_step_module()
    prompt = step.build_stage_prompt(repo_root, state["run_id"], stage, previous_note, user_instruction)
    prompt_path = step.write_stage_prompt(repo_root, state["run_id"], stage, prompt)
    state["model_prompt_path"] = _repo_relative_path(repo_root, prompt_path)

    note_text = step.execute_openai_response(prompt, model)
    _record_gpt_call(state)
    note_path = step.write_stage_note(repo_root, state["run_id"], stage, note_text)
    state["stage"] = stage
    state["stage_note_path"] = _repo_relative_path(repo_root, note_path)
    return state, note_text


def _front_matter_risk_unknown(note_text: str) -> bool:
    step = load_step_module()
    try:
        front_matter = step.extract_yaml_front_matter(note_text)
    except ValueError:
        return False
    risk = front_matter.get("guardrail_risk_level")
    return isinstance(risk, str) and risk.casefold() == "unknown"


def _validate_note_and_gate(state: dict, note_text: str) -> tuple[list[str], dict]:
    step = load_step_module()
    errors = step.validate_stage_note_text(note_text)
    if errors:
        return errors, {}
    if _front_matter_risk_unknown(note_text):
        return ["guardrail_risk_level is unknown"], {}
    try:
        gate = step.extract_transition_gate(note_text)
    except ValueError as exc:
        return [str(exc)], {}
    state["transition_gate"] = gate
    return [], gate


def _evaluate_gate(state: dict, gate: dict, policy: dict) -> dict:
    autonomy = load_autonomy_module()
    decision = autonomy.evaluate_gate_autonomy(gate, policy)
    state["autonomy_decision"] = decision
    return decision


def _reflection_stage_from_gate(current_stage: str, gate: dict) -> str:
    next_stage = gate.get("evaluated_next_stage")
    if isinstance(next_stage, str) and next_stage.strip():
        return f"reflection_before_{next_stage}"
    return f"reflection_before_{current_stage}"


def _try_reflections(
    repo_root: Path,
    state: dict,
    note_text: str,
    gate: dict,
    policy: dict,
    model: str,
) -> tuple[dict, str | None, dict | None]:
    autonomy = load_autonomy_module()
    step = load_step_module()
    max_reflections = int(state.get("max_reflections_per_stage", 3))

    while gate.get("can_advance") is False:
        count = int(state.get("reflection_count_current_stage", 0))
        reflection = autonomy.can_auto_reflect(
            gate,
            policy,
            count,
            gate.get("blocking_question"),
        )
        state["autonomy_decision"] = reflection
        if not reflection.get("allowed"):
            return stop_human(
                state,
                reflection.get("blockers", []),
                "Stop for human review of the unresolved blockage.",
            ), None, None
        if count >= max_reflections:
            return stop_human(
                state,
                ["max_reflections_per_stage is reached"],
                "Stop for human review of the unresolved blockage.",
            ), None, None

        try:
            reflection_prompt = step.extract_next_prompt_block(note_text)
        except ValueError as exc:
            return stop_human(
                state,
                [str(exc)],
                "Stop because the reflection prompt could not be extracted.",
            ), None, None

        reflection_stage = _reflection_stage_from_gate(state["stage"], gate)
        state["reflection_count_current_stage"] = count + 1
        state, note_text = _run_gpt_stage(
            repo_root,
            state,
            reflection_stage,
            reflection_prompt,
            Path(state["stage_note_path"]) if state.get("stage_note_path") else None,
            model,
            policy,
        )
        if note_text is None:
            return state, None, None
        errors, gate = _validate_note_and_gate(state, note_text)
        if errors:
            return stop_human(state, errors, "Stop because reflection note validation failed."), None, None

    return state, note_text, gate


def _build_handoff_if_ready(repo_root: Path, state: dict, gate: dict) -> dict:
    if gate.get("next_prompt_type") != "codex_prompt":
        return _set_status(
            state,
            "gpt_note_ready",
            "Review the next prompt and run the next stage explicitly.",
        )
    if gate.get("next_prompt_ready") is not True:
        return stop_human(
            state,
            ["Codex prompt is not marked ready"],
            "Stop until the Codex prompt is ready.",
        )

    handoff = load_handoff_module()
    note_path = Path(state["stage_note_path"])
    try:
        output_path = handoff.write_codex_handoff(repo_root, state["run_id"], note_path)
    except ValueError as exc:
        return stop_human(
            state,
            [str(exc)],
            "Stop because Codex handoff validation failed.",
        )
    state["handoff_path"] = _repo_relative_path(repo_root, output_path)
    return _set_status(
        state,
        "handoff_ready",
        "Paste the handoff packet into Codex manually. Repository scripts never execute Codex.",
    )


def start_run(
    repo_root: Path,
    run_id: str,
    stage: str,
    execute_api: bool = False,
    user_instruction: str | None = None,
    model: str = "gpt-5.5",
    previous_note: Path | None = None,
) -> dict:
    policy = load_policy(repo_root)
    state = load_loop_state(repo_root, run_id, stage)
    state["stage"] = stage
    state["max_reflections_per_stage"] = int(policy.get("max_reflections_per_stage", 3))

    context = load_context_module()
    context_path = context.write_context_packet(repo_root, run_id)
    state["context_path"] = _repo_relative_path(repo_root, context_path)

    step = load_step_module()
    prompt = step.build_stage_prompt(repo_root, run_id, stage, previous_note, user_instruction)
    prompt_path = step.write_stage_prompt(repo_root, run_id, stage, prompt)
    state["model_prompt_path"] = _repo_relative_path(repo_root, prompt_path)

    if not execute_api:
        _set_status(
            state,
            "prompt_prepared",
            "Review the prepared prompt or rerun with --execute-api. No API call was made.",
        )
        save_loop_state(repo_root, state)
        write_loop_summary(repo_root, state)
        return state

    state, note_text = _run_gpt_stage(
        repo_root,
        state,
        stage,
        user_instruction,
        previous_note,
        model,
        policy,
    )
    if note_text is None:
        save_loop_state(repo_root, state)
        write_loop_summary(repo_root, state)
        return state

    errors, gate = _validate_note_and_gate(state, note_text)
    if errors:
        stop_human(state, errors, "Stop because GPT stage note validation failed.")
        save_loop_state(repo_root, state)
        write_loop_summary(repo_root, state)
        return state

    decision = _evaluate_gate(state, gate, policy)
    if not decision.get("allowed"):
        if gate.get("can_advance") is False:
            state, note_text, gate = _try_reflections(repo_root, state, note_text, gate, policy, model)
            if gate is None:
                save_loop_state(repo_root, state)
                write_loop_summary(repo_root, state)
                return state
            decision = _evaluate_gate(state, gate, policy)
        if not decision.get("allowed"):
            stop_human(
                state,
                decision.get("blockers", []),
                decision.get("next_required_action", "Stop for human review."),
            )
            save_loop_state(repo_root, state)
            write_loop_summary(repo_root, state)
            return state

    state = _build_handoff_if_ready(repo_root, state, gate)
    save_loop_state(repo_root, state)
    write_loop_summary(repo_root, state)
    return state


def resume_codex_return(
    repo_root: Path,
    run_id: str,
    return_path: Path,
    verify_pr: bool = False,
    merge_mode: str = "manual",
    execute_merge: bool = False,
    overwrite: bool = False,
) -> dict:
    state = load_loop_state(repo_root, run_id)
    handoff = load_handoff_module()
    absolute_return_path = return_path if return_path.is_absolute() else repo_root / return_path
    try:
        archived_path = handoff.archive_codex_return(
            repo_root,
            run_id,
            read_text(absolute_return_path),
            overwrite=overwrite,
        )
    except ValueError as exc:
        stop_human(state, [str(exc)], "Stop because Codex return could not be archived.")
        save_loop_state(repo_root, state)
        write_loop_summary(repo_root, state)
        return state

    return_text = read_text(archived_path)
    errors = handoff.validate_codex_return_text(return_text)
    state["codex_return_path"] = _repo_relative_path(repo_root, archived_path)
    if errors:
        stop_human(state, errors, "Stop because Codex return validation failed.")
        save_loop_state(repo_root, state)
        write_loop_summary(repo_root, state)
        return state

    pr_url = handoff.extract_pr_url(return_text)
    if not pr_url:
        stop_human(
            state,
            ["PR URL missing after Codex return"],
            "Stop until the Codex return includes a PR URL.",
        )
        save_loop_state(repo_root, state)
        write_loop_summary(repo_root, state)
        return state

    state["pr_url"] = pr_url
    _set_status(
        state,
        "pr_detected",
        "Review the PR manually or run verify-pr.",
    )
    save_loop_state(repo_root, state)

    if verify_pr:
        return verify_pr_flow(
            repo_root,
            run_id,
            pr_url=pr_url,
            codex_return_path=archived_path,
            merge_mode=merge_mode,
            execute_merge=execute_merge,
            overwrite=overwrite,
        )

    write_loop_summary(repo_root, state)
    return state


def verify_pr_flow(
    repo_root: Path,
    run_id: str,
    pr_url: str | None = None,
    codex_return_path: Path | None = None,
    merge_mode: str = "manual",
    execute_merge: bool = False,
    overwrite: bool = False,
) -> dict:
    state = load_loop_state(repo_root, run_id)
    pr_url = pr_url or state.get("pr_url")
    if not pr_url:
        stop_human(state, ["PR URL is missing"], "Stop until a PR URL is supplied.")
        save_loop_state(repo_root, state)
        write_loop_summary(repo_root, state)
        return state

    if codex_return_path is None and state.get("codex_return_path"):
        codex_return_path = repo_root / state["codex_return_path"]
    if codex_return_path is None:
        stop_human(
            state,
            ["Codex return path is missing"],
            "Stop until an archived Codex return is supplied.",
        )
        save_loop_state(repo_root, state)
        write_loop_summary(repo_root, state)
        return state

    pr_verify = load_pr_verify_module()
    report = pr_verify.build_pre_merge_report(
        pr_url,
        merge_mode,
        run_id,
        codex_return_path,
        list(DEFAULT_AUTHORIZED_PATHS),
        list(DEFAULT_FORBIDDEN_PATHS),
    )
    report_path = pr_verify.save_pre_merge_report(repo_root, run_id, report, overwrite=overwrite)
    decision = pr_verify.decide_report_with_autonomy(report, repo_root)
    state["pr_url"] = pr_url
    state["codex_return_path"] = _repo_relative_path(repo_root, codex_return_path)
    state["pre_merge_report_path"] = _repo_relative_path(repo_root, report_path)
    state["merge_decision"] = decision

    blockers = list(decision.get("blockers", []))
    if merge_mode == "manual":
        blockers.append("merge_mode manual blocks automatic merge")
    if not execute_merge:
        blockers.append("--execute-merge absent; default behavior is no merge")

    if blockers:
        stop_human(
            state,
            blockers,
            "Stop before merge; review blockers or rerun with explicit authorization.",
        )
        save_loop_state(repo_root, state)
        write_loop_summary(repo_root, state)
        return state

    merge_result = pr_verify.execute_merge_if_allowed(
        report,
        decision,
        repo_root,
        execute=True,
    )
    state["merge_decision"] = {
        "decision": decision,
        "merge_result": merge_result,
    }
    if merge_result.get("executed") is not True:
        stop_human(
            state,
            merge_result.get("blockers", ["merge delegation did not execute"]),
            "Stop because guarded merge delegation failed.",
        )
        save_loop_state(repo_root, state)
        write_loop_summary(repo_root, state)
        return state

    post_merge = pr_verify.run_post_merge_validation(repo_root, run_id)
    post_merge_path = pr_verify.write_post_merge_report(
        repo_root,
        run_id,
        post_merge,
        overwrite=overwrite,
    )
    state["post_merge_report_path"] = _repo_relative_path(repo_root, post_merge_path)
    if post_merge.get("passed") is not True:
        stop_human(
            state,
            ["post-merge validation failed"],
            "Stop for human intervention; do not repair destructively.",
        )
    else:
        _set_status(
            state,
            "post_merge_validated",
            "Post-merge validation passed and was recorded.",
        )
    save_loop_state(repo_root, state)
    write_loop_summary(repo_root, state)
    return state


def print_state_summary(state: dict) -> None:
    print(json.dumps(state, indent=2, sort_keys=True))


def _resolve_optional_path(repo_root: Path, value: str | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = repo_root / path
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Semi-automatic local coach-loop runner.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start or prepare a local coach run.")
    start_parser.add_argument("--run-id", required=True)
    start_parser.add_argument("--stage", required=True)
    start_parser.add_argument("--execute-api", action="store_true")
    start_parser.add_argument("--user-instruction")
    start_parser.add_argument("--previous-note")
    start_parser.add_argument("--model", default="gpt-5.5")

    resume_parser = subparsers.add_parser("resume-codex", help="Archive a manual Codex return.")
    resume_parser.add_argument("--run-id", required=True)
    resume_parser.add_argument("--return-path", required=True)
    resume_parser.add_argument("--verify-pr", action="store_true")
    resume_parser.add_argument("--merge-mode", choices=("manual", "auto_after_verify"), default="manual")
    resume_parser.add_argument("--execute-merge", action="store_true")
    resume_parser.add_argument("--overwrite", action="store_true")

    verify_parser = subparsers.add_parser("verify-pr", help="Verify a PR from supplied or stored state.")
    verify_parser.add_argument("--run-id", required=True)
    verify_parser.add_argument("--pr-url")
    verify_parser.add_argument("--codex-return-path")
    verify_parser.add_argument("--merge-mode", choices=("manual", "auto_after_verify"), default="manual")
    verify_parser.add_argument("--execute-merge", action="store_true")
    verify_parser.add_argument("--overwrite", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print current loop state.")
    status_parser.add_argument("--run-id", required=True)

    summarize_parser = subparsers.add_parser("summarize", help="Write loop summary.")
    summarize_parser.add_argument("--run-id", required=True)

    args = parser.parse_args(argv)

    try:
        repo_root = repo_root_from_path()
        if args.command == "start":
            state = start_run(
                repo_root,
                args.run_id,
                args.stage,
                execute_api=args.execute_api,
                user_instruction=args.user_instruction,
                model=args.model,
                previous_note=_resolve_optional_path(repo_root, args.previous_note),
            )
            print_state_summary(state)
            return 0 if state.get("status") != "stop_human" else 1

        if args.command == "resume-codex":
            state = resume_codex_return(
                repo_root,
                args.run_id,
                _resolve_optional_path(repo_root, args.return_path) or Path(args.return_path),
                verify_pr=args.verify_pr,
                merge_mode=args.merge_mode,
                execute_merge=args.execute_merge,
                overwrite=args.overwrite,
            )
            print_state_summary(state)
            return 0 if state.get("status") != "stop_human" else 1

        if args.command == "verify-pr":
            state = verify_pr_flow(
                repo_root,
                args.run_id,
                pr_url=args.pr_url,
                codex_return_path=_resolve_optional_path(repo_root, args.codex_return_path),
                merge_mode=args.merge_mode,
                execute_merge=args.execute_merge,
                overwrite=args.overwrite,
            )
            print_state_summary(state)
            return 0 if state.get("status") != "stop_human" else 1

        if args.command == "status":
            print_state_summary(load_loop_state(repo_root, args.run_id))
            return 0

        if args.command == "summarize":
            state = load_loop_state(repo_root, args.run_id)
            output_path = write_loop_summary(repo_root, state)
            print(output_path)
            return 0
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
