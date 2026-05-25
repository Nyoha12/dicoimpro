from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
import re
import sys
from pathlib import Path


COACH_GUIDANCE_RELATIVE_PATH = Path(".dicoimpro") / "COACH_GUIDANCE.md"
STAGE_SCHEMA_RELATIVE_PATH = Path(".dicoimpro") / "STAGE_OUTPUT_SCHEMA.md"
LOCAL_STATE_RELATIVE_PATH = Path(".dicoimpro") / "WORKFLOW_STATE.local.json"
EXAMPLE_STATE_RELATIVE_PATH = Path(".dicoimpro") / "WORKFLOW_STATE.example.json"
RUNS_RELATIVE_PATH = Path(".dicoimpro") / "runs"

REQUIRED_FRONT_MATTER_FIELDS = (
    "run_id",
    "stage",
    "created_at",
    "input_refs",
    "repo_context_refs",
    "previous_stage_ref",
    "can_advance",
    "reflection_required",
    "next_stage",
    "next_prompt_type",
    "next_prompt_path_suggested",
    "blocking_question",
    "guardrail_risk_level",
)

REQUIRED_BODY_SECTIONS = (
    "Stage objective",
    "Inputs used",
    "Repository context summary",
    "Current-stage analysis summary",
    "Resolved points",
    "Unresolved points",
    "Guardrail and scope check",
    "Transition gate",
    "Next prompt",
)

REQUIRED_TRANSITION_GATE_FIELDS = (
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

STAGE_FILE_INDEXES = {
    "context": "00",
    "pre_cadrage": "01",
    "cadrage": "02",
    "decision": "03",
    "codex_prompt": "04",
    "codex_return": "05",
    "post_codex_review": "06",
    "pr_review": "07",
    "post_merge_review": "08",
    "reflection_before_cadrage": "21",
    "reflection_before_decision": "22",
    "reflection_before_codex_prompt": "23",
    "reflection_before_post_codex_review": "24",
    "reflection_before_pr_review": "25",
    "reflection_before_post_merge_review": "26",
}


def repo_root_from_path(path: Path | None = None) -> Path:
    start = Path.cwd() if path is None else Path(path)
    start = start.resolve()
    if start.is_file():
        start = start.parent

    for candidate in (start, *start.parents):
        if (candidate / COACH_GUIDANCE_RELATIVE_PATH).exists():
            return candidate
        if (candidate / "pyproject.toml").exists() and (candidate / ".dicoimpro").exists():
            return candidate

    raise ValueError("Could not find repository root containing .dicoimpro/COACH_GUIDANCE.md")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"Required file does not exist: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def load_state(repo_root: Path) -> dict:
    state_path = repo_root / LOCAL_STATE_RELATIVE_PATH
    if not state_path.exists():
        state_path = repo_root / EXAMPLE_STATE_RELATIVE_PATH
    try:
        data = json.loads(read_text(state_path))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Workflow state is malformed JSON: {state_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Workflow state must be a JSON object: {state_path}")
    return data


def stage_file_index(stage: str) -> str:
    return STAGE_FILE_INDEXES.get(stage, "99")


def _validate_path_segment(value: str, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    path = Path(value)
    if path.name != value or value in {".", ".."}:
        raise ValueError(f"{label} must be a single safe path segment")


def _optional_file_text(path: Path) -> str:
    if path.exists():
        return read_text(path)
    return "Not present."


def build_stage_prompt(
    repo_root: Path,
    run_id: str,
    stage: str,
    previous_note: Path | None,
    user_instruction: str | None,
) -> str:
    _validate_path_segment(run_id, "run_id")
    _validate_path_segment(stage, "stage")

    guidance_path = repo_root / COACH_GUIDANCE_RELATIVE_PATH
    schema_path = repo_root / STAGE_SCHEMA_RELATIVE_PATH
    state = load_state(repo_root)
    context_path = repo_root / RUNS_RELATIVE_PATH / run_id / "00_context.md"

    previous_note_text = "Not provided."
    if previous_note is not None:
        previous_note_path = previous_note
        if not previous_note_path.is_absolute():
            previous_note_path = repo_root / previous_note_path
        previous_note_text = read_text(previous_note_path)

    instruction_text = user_instruction if user_instruction else "No extra user instruction."

    return (
        "# GPT-5.5 Thinking Stage Request\n\n"
        "You are GPT-5.5 Thinking acting as the dicoimpro coach. Use "
        "COACH_GUIDANCE and STAGE_OUTPUT_SCHEMA exactly as controlling local "
        "workflow references. Produce one valid stage note for the requested stage.\n\n"
        "Do not expose private chain-of-thought. Write a shareable reasoning summary "
        "only. Decide readiness inside the same output. If the next stage is ready, "
        "produce a stage_prompt. If it is not ready, produce a targeted "
        "reflection_prompt. Do not invent repository facts absent from the context "
        "packet, workflow state, or previous stage note.\n\n"
        "Do not authorize prompt activation, prompt rendering, prompt execution, "
        "OpenAI runtime inside dicoimpro application code, Codex SDK, Codex CLI, "
        "autonomous loop, RUN, journal read/write, JournalPatch, real data "
        "processing, publication, PR automation, merge automation, XLSX/CSV export, "
        "old PDF usage, or production behavior change.\n\n"
        "Your output must include YAML front matter, all required body sections, "
        "a transition_gate block, and a next_prompt block. The transition_gate must "
        "include every required field from STAGE_OUTPUT_SCHEMA. next_prompt_type must "
        "be one of: stage_prompt, reflection_prompt, codex_prompt, none.\n\n"
        "## Requested Stage\n\n"
        f"stage: {stage}\n"
        f"run_id: {run_id}\n\n"
        "## Extra User Instruction\n\n"
        f"{instruction_text}\n\n"
        "## COACH_GUIDANCE\n\n"
        f"{read_text(guidance_path)}\n\n"
        "## STAGE_OUTPUT_SCHEMA\n\n"
        f"{read_text(schema_path)}\n\n"
        "## Workflow State JSON\n\n"
        "```json\n"
        f"{json.dumps(state, indent=2, sort_keys=True)}\n"
        "```\n\n"
        "## Context Packet\n\n"
        f"{_optional_file_text(context_path)}\n\n"
        "## Previous Stage Note\n\n"
        f"{previous_note_text}\n"
    )


def write_stage_prompt(repo_root: Path, run_id: str, stage: str, prompt: str) -> Path:
    _validate_path_segment(run_id, "run_id")
    _validate_path_segment(stage, "stage")
    prompt_path = (
        repo_root
        / RUNS_RELATIVE_PATH
        / run_id
        / f"{stage_file_index(stage)}_{stage}.model_prompt.md"
    )
    write_text(prompt_path, prompt)
    return prompt_path


def lazy_openai_client():
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required when --execute-api is used")

    try:
        openai_module = importlib.import_module("openai")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The openai package is required when --execute-api is used"
        ) from exc

    try:
        openai_client = getattr(openai_module, "OpenAI")
    except AttributeError as exc:
        raise RuntimeError("The installed openai package does not expose OpenAI") from exc

    return openai_client()


def _response_text_from_output(response: object) -> str | None:
    output = getattr(response, "output", None)
    if output is None:
        return None

    collected: list[str] = []
    for item in output:
        content_items = getattr(item, "content", None)
        if content_items is None and isinstance(item, dict):
            content_items = item.get("content")
        if content_items is None:
            continue
        for content in content_items:
            text = getattr(content, "text", None)
            if text is None and isinstance(content, dict):
                text = content.get("text")
            if isinstance(text, str):
                collected.append(text)

    if collected:
        return "\n".join(collected)
    return None


def execute_openai_response(prompt: str, model: str) -> str:
    client = lazy_openai_client()
    response = client.responses.create(model=model, input=prompt)

    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text:
        return output_text

    traversed_text = _response_text_from_output(response)
    if traversed_text:
        return traversed_text

    return "WARNING: response text could not be extracted structurally.\n\n" + str(response)


def _parse_scalar(value: str):
    stripped = value.strip()
    if stripped in {"", "null", "Null", "NULL", "~"}:
        return None
    if stripped in {"true", "True", "TRUE"}:
        return True
    if stripped in {"false", "False", "FALSE"}:
        return False
    if stripped == "[]":
        return []
    if stripped.startswith('"') and stripped.endswith('"') and len(stripped) >= 2:
        return stripped[1:-1]
    if stripped.startswith("'") and stripped.endswith("'") and len(stripped) >= 2:
        return stripped[1:-1]
    return stripped


def _parse_simple_key_values(lines: list[str]) -> dict:
    parsed: dict = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("```"):
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        if not key:
            continue
        parsed[key] = _parse_scalar(value)
    return parsed


def extract_yaml_front_matter(note_text: str) -> dict:
    if not note_text.startswith("---\n"):
        raise ValueError("Stage note must start with YAML front matter")
    end = note_text.find("\n---", 4)
    if end == -1:
        raise ValueError("Stage note YAML front matter closing marker is missing")
    front_matter_text = note_text[4:end]
    return _parse_simple_key_values(front_matter_text.splitlines())


def _normalized_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _body_has_section(note_text: str, section: str) -> bool:
    pattern = re.compile(rf"^#+\s+(?:\d+\.\s+)?{re.escape(section)}\s*$", re.IGNORECASE)
    return any(pattern.match(line.strip()) for line in note_text.splitlines())


def _transition_gate_lines(note_text: str) -> list[str]:
    lines = note_text.splitlines()
    for index, line in enumerate(lines):
        if re.match(r"^\s*transition_gate:\s*$", line):
            gate_lines: list[str] = []
            for candidate in lines[index + 1 :]:
                if candidate.strip().startswith("```"):
                    continue
                if not candidate.strip():
                    if gate_lines:
                        break
                    continue
                if candidate.startswith((" ", "\t")):
                    gate_lines.append(candidate)
                    continue
                break
            return gate_lines
    return []


def extract_transition_gate(note_text: str) -> dict:
    gate_lines = _transition_gate_lines(note_text)
    if not gate_lines:
        raise ValueError("transition_gate block is missing")
    gate = _parse_simple_key_values(gate_lines)
    missing = [field for field in REQUIRED_TRANSITION_GATE_FIELDS if field not in gate]
    if missing:
        raise ValueError(f"transition_gate is missing required fields: {missing}")

    errors = _validate_transition_gate_with_coach_state(gate)
    if errors:
        raise ValueError("transition_gate is malformed: " + "; ".join(errors))
    return gate


def extract_next_prompt_block(note_text: str) -> str:
    match = re.search(r"(?ms)^next_prompt:\s*(?P<body>.*?)(?:\n^#{1,6}\s+|\Z)", note_text)
    if not match:
        raise ValueError("next_prompt block is missing")
    body = match.group("body").strip()
    if not body:
        raise ValueError("next_prompt block is empty")
    return body


def validate_stage_note_text(note_text: str) -> list[str]:
    errors: list[str] = []
    try:
        front_matter = extract_yaml_front_matter(note_text)
    except ValueError as exc:
        errors.append(str(exc))
        front_matter = {}

    for field in REQUIRED_FRONT_MATTER_FIELDS:
        if field not in front_matter:
            errors.append(f"YAML front matter is missing required field: {field}")

    for section in REQUIRED_BODY_SECTIONS:
        if not _body_has_section(note_text, section):
            errors.append(f"Stage note is missing required body section: {section}")

    try:
        gate = extract_transition_gate(note_text)
    except ValueError as exc:
        errors.append(str(exc))
        gate = {}

    next_prompt_type = gate.get("next_prompt_type") or front_matter.get("next_prompt_type")
    if next_prompt_type not in ALLOWED_NEXT_PROMPT_TYPES:
        errors.append(
            "next_prompt_type must be one of: " + ", ".join(ALLOWED_NEXT_PROMPT_TYPES)
        )

    try:
        extract_next_prompt_block(note_text)
    except ValueError as exc:
        errors.append(str(exc))

    return errors


def write_stage_note(repo_root: Path, run_id: str, stage: str, note_text: str) -> Path:
    _validate_path_segment(run_id, "run_id")
    _validate_path_segment(stage, "stage")
    note_path = repo_root / RUNS_RELATIVE_PATH / run_id / f"{stage_file_index(stage)}_{stage}.md"
    write_text(note_path, note_text)
    return note_path


def _load_coach_state_module():
    module_path = Path(__file__).resolve().parent / "coach_state.py"
    spec = importlib.util.spec_from_file_location("coach_state_for_step", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load coach_state.py from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate_transition_gate_with_coach_state(gate: dict) -> list[str]:
    coach_state = _load_coach_state_module()
    return coach_state.validate_transition_gate(gate)


def _repo_relative_path(repo_root: Path, path: Path) -> str:
    absolute = path if path.is_absolute() else repo_root / path
    try:
        return absolute.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def update_local_state_from_note(repo_root: Path, note_path: Path) -> Path:
    absolute_note_path = note_path if note_path.is_absolute() else repo_root / note_path
    note_text = read_text(absolute_note_path)
    gate = extract_transition_gate(note_text)
    state = load_state(repo_root)

    coach_state = _load_coach_state_module()
    updated = coach_state.update_state_from_transition_gate(
        state,
        gate,
        _repo_relative_path(repo_root, absolute_note_path),
    )
    local_state_path = repo_root / LOCAL_STATE_RELATIVE_PATH
    coach_state.write_json(local_state_path, updated)
    return local_state_path


def _print_errors(errors: list[str]) -> None:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local GPT-5.5 Thinking coach stage runner.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare", help="Prepare a stage prompt only.")
    prepare_parser.add_argument("--stage", required=True)
    prepare_parser.add_argument("--run-id", required=True)
    prepare_parser.add_argument("--previous-note")
    prepare_parser.add_argument("--user-instruction")

    run_parser = subparsers.add_parser("run", help="Execute an explicit API stage run.")
    run_parser.add_argument("--stage", required=True)
    run_parser.add_argument("--run-id", required=True)
    run_parser.add_argument("--previous-note")
    run_parser.add_argument("--user-instruction")
    run_parser.add_argument("--model", default="gpt-5.5")
    run_parser.add_argument("--execute-api", action="store_true")
    run_parser.add_argument("--update-state", action="store_true")

    validate_parser = subparsers.add_parser("validate-note", help="Validate a local stage note.")
    validate_parser.add_argument("--note-path", required=True)

    extract_parser = subparsers.add_parser("extract-gate", help="Print transition_gate as JSON.")
    extract_parser.add_argument("--note-path", required=True)

    args = parser.parse_args(argv)

    try:
        repo_root = repo_root_from_path()
        if args.command == "prepare":
            previous_note = Path(args.previous_note) if args.previous_note else None
            prompt = build_stage_prompt(
                repo_root,
                args.run_id,
                args.stage,
                previous_note,
                args.user_instruction,
            )
            prompt_path = write_stage_prompt(repo_root, args.run_id, args.stage, prompt)
            print(prompt_path)
            return 0

        if args.command == "run":
            if not args.execute_api:
                print(
                    "ERROR: run requires --execute-api. Use prepare to write a prompt without API.",
                    file=sys.stderr,
                )
                return 1
            previous_note = Path(args.previous_note) if args.previous_note else None
            prompt = build_stage_prompt(
                repo_root,
                args.run_id,
                args.stage,
                previous_note,
                args.user_instruction,
            )
            prompt_path = write_stage_prompt(repo_root, args.run_id, args.stage, prompt)
            note_text = execute_openai_response(prompt, args.model)
            note_path = write_stage_note(repo_root, args.run_id, args.stage, note_text)
            errors = validate_stage_note_text(note_text)
            if errors:
                _print_errors(errors)
                print(f"Prompt written: {prompt_path}", file=sys.stderr)
                print(f"Note written: {note_path}", file=sys.stderr)
                return 1
            if args.update_state:
                update_local_state_from_note(repo_root, note_path)
            print(note_path)
            return 0

        if args.command == "validate-note":
            note_path = Path(args.note_path)
            if not note_path.is_absolute():
                note_path = repo_root / note_path
            errors = validate_stage_note_text(read_text(note_path))
            if errors:
                _print_errors(errors)
                return 1
            print(f"OK: {note_path}")
            return 0

        if args.command == "extract-gate":
            note_path = Path(args.note_path)
            if not note_path.is_absolute():
                note_path = repo_root / note_path
            gate = extract_transition_gate(read_text(note_path))
            print(json.dumps(gate, indent=2, sort_keys=True))
            return 0
    except (RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
