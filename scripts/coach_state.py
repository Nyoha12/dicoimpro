from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path


EXAMPLE_STATE_RELATIVE_PATH = Path(".dicoimpro") / "WORKFLOW_STATE.example.json"
LOCAL_STATE_RELATIVE_PATH = Path(".dicoimpro") / "WORKFLOW_STATE.local.json"
RUNS_RELATIVE_PATH = Path(".dicoimpro") / "runs"

REQUIRED_STATE_KEYS = (
    "project",
    "protocol_version",
    "last_merged_codex",
    "main_tests",
    "current_run_id",
    "current_stage",
    "stage_status",
    "reflection_count_current_stage",
    "max_reflections",
    "can_advance",
    "last_stage_note",
    "next_prompt_path",
    "repo_context_packet_path",
    "guardrails",
    "workflow_permissions",
)

SENSITIVE_GUARDRAILS = (
    "prompt_activation_allowed",
    "prompt_rendering_allowed",
    "prompt_execution_allowed",
    "openai_runtime_allowed",
    "codex_sdk_allowed",
    "run_allowed",
    "journal_write_allowed",
    "journal_patch_allowed",
    "real_data_allowed",
    "publication_allowed",
)

SENSITIVE_WORKFLOW_PERMISSIONS = (
    "auto_merge_allowed",
    "auto_pr_allowed",
    "autonomous_loop_allowed",
)

REQUIRED_TRANSITION_GATE_KEYS = (
    "evaluated_next_stage",
    "can_advance",
    "reflection_required",
    "next_prompt_ready",
    "next_prompt_type",
    "blocking_question",
    "reason",
    "required_user_intervention",
    "allowed_to_execute_automatically",
)

ALLOWED_NEXT_PROMPT_TYPES = (
    "stage_prompt",
    "reflection_prompt",
    "codex_prompt",
    "none",
)


def repo_root_from_path(path: Path | None = None) -> Path:
    start = Path.cwd() if path is None else Path(path)
    start = start.resolve()
    if start.is_file():
        start = start.parent

    for candidate in (start, *start.parents):
        if (candidate / EXAMPLE_STATE_RELATIVE_PATH).exists():
            return candidate
        if (candidate / "pyproject.toml").exists() and (candidate / ".dicoimpro").exists():
            return candidate

    raise ValueError(
        "Could not find repository root containing .dicoimpro/WORKFLOW_STATE.example.json"
    )


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


def load_example_state(repo_root: Path) -> dict:
    return read_json(repo_root / EXAMPLE_STATE_RELATIVE_PATH)


def validate_state_shape(state: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(state, dict):
        return ["state must be a JSON object"]

    for key in REQUIRED_STATE_KEYS:
        if key not in state:
            errors.append(f"state is missing required key: {key}")

    guardrails = state.get("guardrails")
    if not isinstance(guardrails, dict):
        errors.append("state.guardrails must be an object")
    workflow_permissions = state.get("workflow_permissions")
    if not isinstance(workflow_permissions, dict):
        errors.append("state.workflow_permissions must be an object")

    for key in (
        "project",
        "protocol_version",
        "last_merged_codex",
        "main_tests",
        "current_run_id",
        "current_stage",
        "stage_status",
    ):
        if key in state and not isinstance(state[key], str):
            errors.append(f"state.{key} must be a string")

    reflection_count = state.get("reflection_count_current_stage")
    if not isinstance(reflection_count, int) or reflection_count < 0:
        errors.append("state.reflection_count_current_stage must be a non-negative integer")

    max_reflections = state.get("max_reflections")
    if max_reflections is not None and (
        not isinstance(max_reflections, int) or max_reflections < 0
    ):
        errors.append("state.max_reflections must be null or a non-negative integer")

    can_advance = state.get("can_advance")
    if can_advance is not None and not isinstance(can_advance, bool):
        errors.append("state.can_advance must be null or a boolean")

    for key in ("last_stage_note", "next_prompt_path", "repo_context_packet_path"):
        if key in state and state[key] is not None and not isinstance(state[key], str):
            errors.append(f"state.{key} must be null or a string")

    return errors


def validate_sensitive_permissions_false(state: dict) -> list[str]:
    errors: list[str] = []
    guardrails = state.get("guardrails")
    if isinstance(guardrails, dict):
        for key in SENSITIVE_GUARDRAILS:
            if guardrails.get(key) is not False:
                errors.append(f"state.guardrails.{key} must remain false by default")
    else:
        errors.append("state.guardrails must be an object before guardrails can be checked")

    workflow_permissions = state.get("workflow_permissions")
    if isinstance(workflow_permissions, dict):
        for key in SENSITIVE_WORKFLOW_PERMISSIONS:
            if workflow_permissions.get(key) is not False:
                errors.append(f"state.workflow_permissions.{key} must remain false by default")
    else:
        errors.append(
            "state.workflow_permissions must be an object before workflow permissions can be checked"
        )

    return errors


def _validate_run_id(run_id: str) -> None:
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id must be a non-empty string")
    run_path = Path(run_id)
    if run_path.name != run_id or run_id in {".", ".."}:
        raise ValueError("run_id must be a single safe path segment")


def initialize_local_state(
    repo_root: Path,
    run_id: str | None = None,
    overwrite: bool = False,
) -> Path:
    local_path = repo_root / LOCAL_STATE_RELATIVE_PATH
    if local_path.exists() and not overwrite:
        return local_path

    state = load_example_state(repo_root)
    errors = validate_state_shape(state) + validate_sensitive_permissions_false(state)
    if errors:
        raise ValueError("Example state is invalid: " + "; ".join(errors))

    local_state = copy.deepcopy(state)
    if run_id is not None:
        _validate_run_id(run_id)
        local_state["current_run_id"] = run_id
        local_state["repo_context_packet_path"] = (
            f".dicoimpro/runs/{run_id}/00_context.md"
        )

    write_json(local_path, local_state)
    return local_path


def ensure_run_folder(repo_root: Path, run_id: str) -> Path:
    _validate_run_id(run_id)
    run_folder = repo_root / RUNS_RELATIVE_PATH / run_id
    run_folder.mkdir(parents=True, exist_ok=True)
    return run_folder


def validate_transition_gate(gate: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(gate, dict):
        return ["transition_gate must be an object"]

    for key in REQUIRED_TRANSITION_GATE_KEYS:
        if key not in gate:
            errors.append(f"transition_gate is missing required key: {key}")

    prompt_type = gate.get("next_prompt_type")
    if prompt_type not in ALLOWED_NEXT_PROMPT_TYPES:
        errors.append(
            "transition_gate.next_prompt_type must be one of: "
            + ", ".join(ALLOWED_NEXT_PROMPT_TYPES)
        )

    for key in (
        "can_advance",
        "reflection_required",
        "next_prompt_ready",
        "required_user_intervention",
        "allowed_to_execute_automatically",
    ):
        if key in gate and not isinstance(gate[key], bool):
            errors.append(f"transition_gate.{key} must be a boolean")

    if gate.get("allowed_to_execute_automatically") is not False:
        errors.append("transition_gate.allowed_to_execute_automatically must remain false")

    evaluated_next_stage = gate.get("evaluated_next_stage")
    if prompt_type == "none":
        if evaluated_next_stage is not None and not isinstance(evaluated_next_stage, str):
            errors.append("transition_gate.evaluated_next_stage must be null or a string")
    elif not isinstance(evaluated_next_stage, str) or not evaluated_next_stage.strip():
        errors.append("transition_gate.evaluated_next_stage must be a non-empty string")

    blocking_question = gate.get("blocking_question")
    if blocking_question is not None and not isinstance(blocking_question, str):
        errors.append("transition_gate.blocking_question must be null or a string")

    reason = gate.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        errors.append("transition_gate.reason must be a non-empty string")

    return errors


def can_advance_from_transition_gate(gate: dict) -> bool:
    return gate.get("can_advance") is True and gate.get("next_prompt_ready") is True


def next_stage_from_transition_gate(gate: dict) -> str | None:
    if not can_advance_from_transition_gate(gate):
        return None
    next_stage = gate.get("evaluated_next_stage")
    if isinstance(next_stage, str) and next_stage.strip():
        return next_stage
    return None


def update_state_from_transition_gate(state: dict, gate: dict, note_path: str) -> dict:
    state_errors = validate_state_shape(state) + validate_sensitive_permissions_false(state)
    gate_errors = validate_transition_gate(gate)
    errors = state_errors + gate_errors
    if errors:
        raise ValueError("Cannot update workflow state: " + "; ".join(errors))

    if gate["can_advance"] is not True:
        raise ValueError("transition_gate.can_advance is false; refusing to advance")
    if gate["next_prompt_ready"] is not True:
        raise ValueError("transition_gate.next_prompt_ready is false; refusing to advance")
    if not isinstance(note_path, str) or not note_path.strip():
        raise ValueError("note_path must be a non-empty string")

    updated = copy.deepcopy(state)
    updated["can_advance"] = True
    updated["last_stage_note"] = note_path
    updated["stage_status"] = "ready"

    next_stage = next_stage_from_transition_gate(gate)
    if next_stage is not None:
        updated["current_stage"] = next_stage

    next_prompt_path = gate.get("next_prompt_path") or gate.get("next_prompt_path_suggested")
    if next_prompt_path is not None:
        if not isinstance(next_prompt_path, str):
            raise ValueError("transition_gate.next_prompt_path must be a string when present")
        updated["next_prompt_path"] = next_prompt_path

    if gate.get("next_prompt_type") == "reflection_prompt":
        updated["reflection_count_current_stage"] += 1

    return updated


def _state_path_for_validation(repo_root: Path) -> Path:
    local_path = repo_root / LOCAL_STATE_RELATIVE_PATH
    if local_path.exists():
        return local_path
    return repo_root / EXAMPLE_STATE_RELATIVE_PATH


def _print_errors(errors: list[str]) -> None:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local coach workflow state utilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create local workflow state.")
    init_parser.add_argument("--run-id", required=True)
    init_parser.add_argument("--overwrite", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate workflow state.")
    validate_parser.set_defaults(validate=True)

    ensure_parser = subparsers.add_parser("ensure-run", help="Create a local run folder.")
    ensure_parser.add_argument("--run-id", required=True)

    args = parser.parse_args(argv)

    try:
        repo_root = repo_root_from_path()
        if args.command == "init":
            path = initialize_local_state(repo_root, args.run_id, args.overwrite)
            print(path)
            return 0
        if args.command == "validate":
            path = _state_path_for_validation(repo_root)
            state = read_json(path)
            errors = validate_state_shape(state) + validate_sensitive_permissions_false(state)
            if errors:
                _print_errors(errors)
                return 1
            print(f"OK: {path}")
            return 0
        if args.command == "ensure-run":
            path = ensure_run_folder(repo_root, args.run_id)
            print(path)
            return 0
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
