from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


RUNS_RELATIVE_PATH = Path(".dicoimpro") / "runs"
COACH_GUIDANCE_RELATIVE_PATH = Path(".dicoimpro") / "COACH_GUIDANCE.md"
STAGE_SCHEMA_RELATIVE_PATH = Path(".dicoimpro") / "STAGE_OUTPUT_SCHEMA.md"

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

BOOLEAN_TRANSITION_GATE_FIELDS = (
    "can_advance",
    "reflection_required",
    "next_prompt_ready",
    "required_user_intervention",
    "allowed_to_execute_automatically",
)

DEFAULT_HANDOFF_INDEX = "02"
DEFAULT_RETURN_INDEX = "05"

PR_URL_RE = re.compile(
    r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/pull/[0-9]+"
)
COMMIT_HASH_RE = re.compile(r"\b[0-9a-f]{7,40}\b", re.IGNORECASE)


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

    raise ValueError("Could not find repository root containing .dicoimpro")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"Required file does not exist: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


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


def extract_front_matter(note_text: str) -> dict:
    if not note_text.startswith("---\n"):
        return {}

    end = note_text.find("\n---", 4)
    if end == -1:
        raise ValueError("YAML front matter closing marker is missing")
    front_matter_text = note_text[4:end]
    return _parse_simple_key_values(front_matter_text.splitlines())


def _transition_gate_lines(note_text: str) -> list[str] | None:
    lines = note_text.splitlines()
    for index, line in enumerate(lines):
        if not re.match(r"^\s*transition_gate:\s*$", line):
            continue

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
    return None


def extract_transition_gate(note_text: str) -> dict:
    gate_lines = _transition_gate_lines(note_text)
    if gate_lines is None:
        return {}
    if not gate_lines:
        raise ValueError("transition_gate block is malformed: expected indented fields")

    gate = _parse_simple_key_values(gate_lines)
    if not gate:
        raise ValueError("transition_gate block is malformed: no key-value fields found")
    return gate


def extract_next_prompt_block(note_text: str) -> str:
    match = re.search(r"(?ms)^next_prompt:\s*(?P<body>.*?)(?:\n^#{1,6}\s+|\Z)", note_text)
    if not match:
        raise ValueError("next_prompt block is missing")

    body = match.group("body").strip()
    if not body:
        raise ValueError("next_prompt block is empty")
    return body


def extract_next_prompt_type(note_text: str) -> str | None:
    gate = extract_transition_gate(note_text)
    gate_prompt_type = gate.get("next_prompt_type")
    if isinstance(gate_prompt_type, str) and gate_prompt_type.strip():
        return gate_prompt_type.strip()

    front_matter = extract_front_matter(note_text)
    front_matter_prompt_type = front_matter.get("next_prompt_type")
    if isinstance(front_matter_prompt_type, str) and front_matter_prompt_type.strip():
        return front_matter_prompt_type.strip()

    for line in note_text.splitlines():
        if re.match(r"^\s*next_prompt_type\s*:", line):
            _, value = line.split(":", 1)
            parsed = _parse_scalar(value)
            if isinstance(parsed, str) and parsed.strip():
                return parsed.strip()
    return None


def _transition_gate_errors(gate: dict) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_TRANSITION_GATE_FIELDS:
        if field not in gate:
            errors.append(f"transition_gate is missing required field: {field}")

    for field in BOOLEAN_TRANSITION_GATE_FIELDS:
        if field in gate and not isinstance(gate[field], bool):
            errors.append(f"transition_gate.{field} must be a boolean")

    prompt_type = gate.get("next_prompt_type")
    if prompt_type not in {"stage_prompt", "reflection_prompt", "codex_prompt", "none"}:
        errors.append(
            "transition_gate.next_prompt_type must be one of: "
            "stage_prompt, reflection_prompt, codex_prompt, none"
        )

    if gate.get("allowed_to_execute_automatically") is not False:
        errors.append("transition_gate.allowed_to_execute_automatically must remain false")

    return errors


def validate_handoff_source(
    note_text: str,
    allow_reflection: bool = False,
    allow_blocked_gate: bool = False,
) -> list[str]:
    errors: list[str] = []

    try:
        extract_front_matter(note_text)
    except ValueError as exc:
        errors.append(str(exc))

    try:
        next_prompt = extract_next_prompt_block(note_text)
    except ValueError as exc:
        errors.append(str(exc))
        next_prompt = ""

    if not next_prompt.strip():
        errors.append("next_prompt must be non-empty")

    try:
        prompt_type = extract_next_prompt_type(note_text)
    except ValueError as exc:
        errors.append(str(exc))
        prompt_type = None

    allowed_types = {"codex_prompt", "stage_prompt"}
    if allow_reflection:
        allowed_types.add("reflection_prompt")
    if prompt_type not in allowed_types:
        allowed = ", ".join(sorted(allowed_types))
        errors.append(f"next_prompt_type must be one of {allowed} for Codex handoff")

    try:
        gate = extract_transition_gate(note_text)
    except ValueError as exc:
        errors.append(str(exc))
        gate = {}

    if gate:
        errors.extend(_transition_gate_errors(gate))
        if gate.get("next_prompt_ready") is not True:
            errors.append("transition_gate.next_prompt_ready must be true")
        if gate.get("can_advance") is False and not allow_blocked_gate:
            errors.append(
                "transition_gate.can_advance is false; use --allow-blocked-gate to package it"
            )

    return errors


def _validate_path_segment(value: str, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    path = Path(value)
    if path.name != value or value in {".", ".."}:
        raise ValueError(f"{label} must be a single safe path segment")


def _next_index_after_source(source_note_path: str) -> str:
    source_name = Path(source_note_path).name
    match = re.match(r"^(?P<index>[0-9]{2})_", source_name)
    if match:
        return f"{int(match.group('index')) + 1:02d}"
    return DEFAULT_HANDOFF_INDEX


def _repo_relative_path(repo_root: Path, path: Path) -> str:
    absolute = path if path.is_absolute() else repo_root / path
    try:
        return absolute.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _fenced_text(value: str, language: str = "text") -> str:
    return f"```{language}\n{value.rstrip()}\n```"


def _format_key_values(values: dict) -> str:
    if not values:
        return "Not present."
    lines = [f"{key}: {values[key]}" for key in sorted(values)]
    return "\n".join(lines)


def build_codex_handoff(
    note_text: str,
    run_id: str,
    source_note_path: str,
    handoff_index: str,
) -> str:
    front_matter = extract_front_matter(note_text)
    transition_gate = extract_transition_gate(note_text)
    prompt_type = extract_next_prompt_type(note_text) or "unknown"
    next_prompt = extract_next_prompt_block(note_text)

    forbidden_scope = "\n".join(
        (
            "- No production code under `src/`.",
            "- No OpenAI API call, GPT call, Codex SDK, Codex CLI, or Codex execution from repository scripts.",
            "- No network or GitHub API call from repository scripts.",
            "- No autonomous loop and no automatic PR merge.",
            "- No prompt activation, rendering, execution, or consumption inside `src/`.",
            "- No RUN, real entry processing, candidate selection, active journal read/write, JournalPatch application, XLSX/CSV export, old PDF usage, publication, or behavior change.",
            "- No repository-script creation of PRs, merges, pushes, tags, or releases.",
        )
    )

    finalization = "\n".join(
        (
            "1. Run tests requested by the mission.",
            "2. Run git diff --check.",
            "3. Verify only authorized files changed.",
            "4. Stage only authorized files.",
            "5. Commit only after checks pass.",
            "6. Push branch only after checks pass.",
            "7. Create PR only after checks pass.",
            "8. Include PR URL, commit hash, files changed, commands run, pytest result, diff-check result, and guardrail guarantee.",
            "9. Never merge.",
            "10. Never push to main.",
            "11. Never create tags/releases.",
            "12. If checks fail, do not commit, do not push, and do not create a PR.",
        )
    )

    return (
        "# Codex Handoff Packet\n\n"
        "## Handoff metadata\n\n"
        + _fenced_text(
            "\n".join(
                (
                    f"run_id: {run_id}",
                    f"handoff_index: {handoff_index}",
                    f"source_note_path: {source_note_path}",
                    f"next_prompt_type: {prompt_type}",
                    "generated_by: scripts/coach_codex_handoff.py",
                    "manual_handoff_only: true",
                    "repository_script_creates_pr: false",
                    "repository_script_merges_pr: false",
                    "codex_sdk_called: false",
                    "codex_cli_called: false",
                    "openai_called: false",
                    "network_called: false",
                )
            )
        )
        + "\n\n"
        "## Source coach note\n\n"
        "Front matter:\n\n"
        + _fenced_text(_format_key_values(front_matter), "yaml")
        + "\n\n"
        "Transition gate:\n\n"
        + _fenced_text(_format_key_values(transition_gate), "yaml")
        + "\n\n"
        "## Intended Codex mission\n\n"
        "Use the prompt below as the bounded manual Codex mission. Treat it as a "
        "copy-paste packet prepared from a local coach stage note, not as an "
        "automatic execution request from repository scripts.\n\n"
        "## Prompt to paste into Codex\n\n"
        + _fenced_text(next_prompt)
        + "\n\n"
        "## Required Codex finalization behavior\n\n"
        f"{finalization}\n\n"
        "## Forbidden scope\n\n"
        f"{forbidden_scope}\n\n"
        "## Expected files\n\n"
        "The prompt above is the controlling source for authorized files. If the "
        "prompt does not explicitly authorize a file, do not edit it. For this "
        "coach-loop bridge class of mission, expected changes are limited to "
        "docs, tests, scripts, and `.dicoimpro` workflow guidance; `src/` "
        "production code is forbidden.\n\n"
        "## Expected commands\n\n"
        "Run the smoke commands and pytest commands explicitly requested by the "
        "mission prompt, then run `git diff --check`. Repository scripts in this "
        "handoff bridge must not run Codex, OpenAI, GitHub API, PR creation, PR "
        "merge, or an autonomous loop.\n\n"
        "## Expected final summary\n\n"
        "Return a concise summary containing PR URL, commit hash, files changed, "
        "commands run, pytest result, git diff --check result, and an explicit "
        "guardrail guarantee. If checks failed, state that no PR was created "
        "because checks failed and include the failing command evidence.\n\n"
        "## PR review boundary\n\n"
        "Repository scripts do not create PRs and do not merge PRs. External Codex "
        "execution may create a PR only when the user workflow explicitly asks for "
        "that finalization and all checks pass. Merge remains human-controlled "
        "after GPT review. Never merge, never push to main, and never create "
        "tags/releases.\n"
    )


def _handoff_target_path(repo_root: Path, run_id: str, note_path: Path) -> Path:
    source_note_path = _repo_relative_path(repo_root, note_path)
    index = _next_index_after_source(source_note_path)
    return repo_root / RUNS_RELATIVE_PATH / run_id / f"{index}_codex_handoff.md"


def write_codex_handoff(
    repo_root: Path,
    run_id: str,
    note_path: Path,
    allow_reflection: bool = False,
    allow_blocked_gate: bool = False,
    overwrite: bool = False,
) -> Path:
    _validate_path_segment(run_id, "run_id")
    absolute_note_path = note_path if note_path.is_absolute() else repo_root / note_path
    note_text = read_text(absolute_note_path)
    errors = validate_handoff_source(note_text, allow_reflection, allow_blocked_gate)
    if errors:
        raise ValueError("Source note is not eligible for Codex handoff: " + "; ".join(errors))

    source_note_path = _repo_relative_path(repo_root, absolute_note_path)
    handoff_index = _next_index_after_source(source_note_path)
    handoff = build_codex_handoff(note_text, run_id, source_note_path, handoff_index)
    output_path = _handoff_target_path(repo_root, run_id, absolute_note_path)
    if output_path.exists() and not overwrite:
        raise ValueError(f"Target already exists: {output_path}. Use --overwrite to replace it.")
    write_text(output_path, handoff)
    return output_path


def _latest_handoff_index(run_folder: Path) -> str | None:
    indexes: list[int] = []
    for path in run_folder.glob("[0-9][0-9]_codex_handoff.md"):
        match = re.match(r"^(?P<index>[0-9]{2})_", path.name)
        if match:
            indexes.append(int(match.group("index")))
    if not indexes:
        return None
    return f"{max(indexes) + 1:02d}"


def _return_target_path(repo_root: Path, run_id: str) -> Path:
    run_folder = repo_root / RUNS_RELATIVE_PATH / run_id
    index = _latest_handoff_index(run_folder) or DEFAULT_RETURN_INDEX
    return run_folder / f"{index}_codex_return.md"


def archive_codex_return(
    repo_root: Path,
    run_id: str,
    return_text: str,
    overwrite: bool = False,
) -> Path:
    _validate_path_segment(run_id, "run_id")
    if not isinstance(return_text, str) or not return_text.strip():
        raise ValueError("return_text must be non-empty")

    output_path = _return_target_path(repo_root, run_id)
    if output_path.exists() and not overwrite:
        raise ValueError(f"Target already exists: {output_path}. Use --overwrite to replace it.")
    write_text(output_path, return_text)
    return output_path


def _normalized_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _states_no_pr_because_checks_failed(normalized: str) -> bool:
    patterns = (
        "no pr was created because checks failed",
        "no pr created because checks failed",
        "no pull request was created because checks failed",
        "no pull request created because checks failed",
        "no pr was opened because checks failed",
        "no pull request was opened because checks failed",
    )
    return any(pattern in normalized for pattern in patterns)


def _claims_merge_completed(return_text: str) -> bool:
    denied_markers = (
        "not merged",
        "not merge",
        "never merge",
        "no merge",
        "not been merged",
        "merge remains",
    )
    claim_markers = (
        "merge completed",
        "merge was completed",
        "merge complete",
        "merge done",
        "merged into main",
        "merged the pr",
        "merged the pull request",
        "pr merged",
        "pull request merged",
    )
    for line in return_text.splitlines():
        normalized_line = _normalized_text(line)
        if any(marker in normalized_line for marker in denied_markers):
            continue
        if any(marker in normalized_line for marker in claim_markers):
            return True
    return False


def validate_codex_return_text(return_text: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(return_text, str) or not return_text.strip():
        return ["Codex return text must be non-empty"]

    normalized = _normalized_text(return_text)
    pr_url = extract_pr_url(return_text)
    no_pr_checks_failed = _states_no_pr_because_checks_failed(normalized)

    if pr_url is None and not no_pr_checks_failed:
        errors.append("Codex return must include a PR URL or say no PR was created because checks failed")

    if pr_url is not None and COMMIT_HASH_RE.search(return_text) is None:
        errors.append("Codex return with a PR URL must include a commit hash")

    if "pytest" not in normalized and "test failure" not in normalized and "tests failed" not in normalized:
        errors.append("Codex return must include pytest result or explicit test failure")

    if "git diff --check" not in normalized and "diff-check" not in normalized:
        errors.append("Codex return must include git diff --check result or explicit reason it was not run")

    if "files changed" not in normalized and "changed files" not in normalized:
        errors.append("Codex return must include files changed")

    if "guardrail guarantee" not in normalized:
        errors.append("Codex return must include guardrail guarantee")

    if _claims_merge_completed(return_text):
        errors.append("Codex return must not claim merge completed")

    return errors


def extract_pr_url(return_text: str) -> str | None:
    match = PR_URL_RE.search(return_text)
    if match:
        return match.group(0)
    return None


def _print_errors(errors: list[str]) -> None:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local manual Codex handoff bridge.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build a Codex handoff packet.")
    build_parser.add_argument("--run-id", required=True)
    build_parser.add_argument("--note-path", required=True)
    build_parser.add_argument("--allow-reflection", action="store_true")
    build_parser.add_argument("--allow-blocked-gate", action="store_true")
    build_parser.add_argument("--overwrite", action="store_true")

    validate_source_parser = subparsers.add_parser(
        "validate-source",
        help="Validate source note eligibility for handoff.",
    )
    validate_source_parser.add_argument("--note-path", required=True)
    validate_source_parser.add_argument("--allow-reflection", action="store_true")
    validate_source_parser.add_argument("--allow-blocked-gate", action="store_true")

    archive_parser = subparsers.add_parser(
        "archive-return",
        help="Archive a manually supplied Codex return.",
    )
    archive_parser.add_argument("--run-id", required=True)
    archive_parser.add_argument("--return-path", required=True)
    archive_parser.add_argument("--overwrite", action="store_true")

    validate_return_parser = subparsers.add_parser(
        "validate-return",
        help="Validate an archived or local Codex return.",
    )
    validate_return_parser.add_argument("--return-path", required=True)

    extract_pr_parser = subparsers.add_parser(
        "extract-pr",
        help="Extract the first GitHub PR URL from a Codex return.",
    )
    extract_pr_parser.add_argument("--return-path", required=True)

    args = parser.parse_args(argv)

    try:
        repo_root = repo_root_from_path()
        if args.command == "build":
            output_path = write_codex_handoff(
                repo_root,
                args.run_id,
                Path(args.note_path),
                allow_reflection=args.allow_reflection,
                allow_blocked_gate=args.allow_blocked_gate,
                overwrite=args.overwrite,
            )
            print(output_path)
            return 0

        if args.command == "validate-source":
            note_path = Path(args.note_path)
            if not note_path.is_absolute():
                note_path = repo_root / note_path
            errors = validate_handoff_source(
                read_text(note_path),
                allow_reflection=args.allow_reflection,
                allow_blocked_gate=args.allow_blocked_gate,
            )
            if errors:
                _print_errors(errors)
                return 1
            print(f"OK: {note_path}")
            return 0

        if args.command == "archive-return":
            return_path = Path(args.return_path)
            if not return_path.is_absolute():
                return_path = repo_root / return_path
            output_path = archive_codex_return(
                repo_root,
                args.run_id,
                read_text(return_path),
                overwrite=args.overwrite,
            )
            print(output_path)
            return 0

        if args.command == "validate-return":
            return_path = Path(args.return_path)
            if not return_path.is_absolute():
                return_path = repo_root / return_path
            errors = validate_codex_return_text(read_text(return_path))
            if errors:
                _print_errors(errors)
                return 1
            print(f"OK: {return_path}")
            return 0

        if args.command == "extract-pr":
            return_path = Path(args.return_path)
            if not return_path.is_absolute():
                return_path = repo_root / return_path
            pr_url = extract_pr_url(read_text(return_path))
            if pr_url is None:
                print("ERROR: no GitHub PR URL found", file=sys.stderr)
                return 1
            print(pr_url)
            return 0
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
