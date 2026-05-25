from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


LOCAL_STATE_RELATIVE_PATH = Path(".dicoimpro") / "WORKFLOW_STATE.local.json"
EXAMPLE_STATE_RELATIVE_PATH = Path(".dicoimpro") / "WORKFLOW_STATE.example.json"
RUNS_RELATIVE_PATH = Path(".dicoimpro") / "runs"

GIT_COMMANDS = {
    "status_short": ["git", "status", "--short"],
    "branch": ["git", "branch", "--show-current"],
    "head": ["git", "rev-parse", "HEAD"],
    "last_commit": ["git", "log", "-1", "--oneline"],
    "diff_stat": ["git", "diff", "--stat"],
    "diff_name_only": ["git", "diff", "--name-only"],
    "recent_commits": ["git", "log", "--oneline", "-5"],
}

REQUIRED_CONTEXT_SECTIONS = (
    "Context packet metadata",
    "Repository identity",
    "Current branch",
    "Current HEAD",
    "Last commit",
    "Recent commits",
    "Git status",
    "Diff stat",
    "Changed files",
    "Last merged Codex from state if available",
    "Main test count from state if available",
    "Guardrail snapshot",
    "Notes for next GPT-5.5 Thinking stage",
)


def repo_root_from_path(path: Path | None = None) -> Path:
    start = Path.cwd() if path is None else Path(path)
    start = start.resolve()
    if start.is_file():
        start = start.parent
    for candidate in (start, *start.parents):
        if (candidate / ".dicoimpro").exists() or (candidate / ".git").exists():
            return candidate
    return start


def run_command(args: list[str], cwd: Path, timeout: int = 15) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return 127, "", f"Command not found: {args[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"Command timed out after {timeout} seconds: {' '.join(args)}"

    return result.returncode, result.stdout.strip(), result.stderr.strip()


def collect_git_context(repo_root: Path) -> dict:
    context = {}
    for name, args in GIT_COMMANDS.items():
        return_code, stdout, stderr = run_command(args, repo_root)
        context[name] = {
            "args": args,
            "return_code": return_code,
            "stdout": stdout,
            "stderr": stderr,
        }
    return context


def _read_json_object(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    if isinstance(data, dict):
        return data
    return None


def load_state_if_present(repo_root: Path) -> dict | None:
    local_state = _read_json_object(repo_root / LOCAL_STATE_RELATIVE_PATH)
    if local_state is not None:
        return local_state
    return _read_json_object(repo_root / EXAMPLE_STATE_RELATIVE_PATH)


def build_context_packet(repo_root: Path, run_id: str) -> dict:
    state = load_state_if_present(repo_root)
    return {
        "run_id": run_id,
        "packet_path": f".dicoimpro/runs/{run_id}/00_context.md",
        "repository": {
            "name": repo_root.name,
            "path": str(repo_root),
        },
        "git": collect_git_context(repo_root),
        "state": state,
        "sections": list(REQUIRED_CONTEXT_SECTIONS),
    }


def _command_output(command_result: dict) -> str:
    stdout = command_result.get("stdout") or ""
    stderr = command_result.get("stderr") or ""
    return_code = command_result.get("return_code")

    lines = []
    if stdout:
        lines.append(stdout)
    if stderr:
        lines.append(f"[stderr] {stderr}")
    if return_code not in (0, None):
        lines.append(f"[exit {return_code}]")
    if not lines:
        return "None."
    return "\n".join(lines)


def _fenced(value: str) -> str:
    return f"```text\n{value}\n```"


def _guardrail_snapshot(state: dict | None) -> str:
    if not state:
        return "State file not present."
    guardrails = state.get("guardrails")
    if not isinstance(guardrails, dict):
        return "State guardrails are missing or malformed."
    lines = [f"- {key}: {guardrails[key]}" for key in sorted(guardrails)]
    return "\n".join(lines) if lines else "No guardrails recorded."


def render_context_markdown(packet: dict) -> str:
    git_context = packet["git"]
    state = packet.get("state")
    last_merged_codex = None
    main_tests = None
    if isinstance(state, dict):
        last_merged_codex = state.get("last_merged_codex")
        main_tests = state.get("main_tests")

    changed_files = _command_output(git_context["diff_name_only"])
    if changed_files == "None.":
        changed_files = "No changed files reported by git diff --name-only."

    sections = [
        "# Coach Context Packet",
        "## 1. Context packet metadata",
        _fenced(
            "\n".join(
                (
                    f"run_id: {packet['run_id']}",
                    f"packet_path: {packet['packet_path']}",
                    "generated_by: scripts/coach_collect_context.py",
                    "network_used: false",
                    "models_called: false",
                )
            )
        ),
        "## 2. Repository identity",
        _fenced(
            "\n".join(
                (
                    f"name: {packet['repository']['name']}",
                    f"path: {packet['repository']['path']}",
                )
            )
        ),
        "## 3. Current branch",
        _fenced(_command_output(git_context["branch"])),
        "## 4. Current HEAD",
        _fenced(_command_output(git_context["head"])),
        "## 5. Last commit",
        _fenced(_command_output(git_context["last_commit"])),
        "## 6. Recent commits",
        _fenced(_command_output(git_context["recent_commits"])),
        "## 7. Git status",
        _fenced(_command_output(git_context["status_short"])),
        "## 8. Diff stat",
        _fenced(_command_output(git_context["diff_stat"])),
        "## 9. Changed files",
        _fenced(changed_files),
        "## 10. Last merged Codex from state if available",
        _fenced(str(last_merged_codex) if last_merged_codex is not None else "Not available."),
        "## 11. Main test count from state if available",
        _fenced(str(main_tests) if main_tests is not None else "Not available."),
        "## 12. Guardrail snapshot",
        _guardrail_snapshot(state),
        "## 13. Notes for next GPT-5.5 Thinking stage",
        (
            "This packet is filtered local repository context only. It does not call "
            "GPT-5.5, OpenAI, Codex SDK, Codex CLI, network, GitHub API, pytest, RUN, "
            "journal, JournalPatch, prompt rendering, prompt execution, or prompt "
            "consumption. Use it as context for a future manually authorized stage, "
            "not as an executable prompt."
        ),
    ]
    return "\n\n".join(sections) + "\n"


def _validate_run_id(run_id: str) -> None:
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id must be a non-empty string")
    run_path = Path(run_id)
    if run_path.name != run_id or run_id in {".", ".."}:
        raise ValueError("run_id must be a single safe path segment")


def write_context_packet(repo_root: Path, run_id: str) -> Path:
    _validate_run_id(run_id)
    packet = build_context_packet(repo_root, run_id)
    run_folder = repo_root / RUNS_RELATIVE_PATH / run_id
    run_folder.mkdir(parents=True, exist_ok=True)
    output_path = run_folder / "00_context.md"
    output_path.write_text(render_context_markdown(packet), encoding="utf-8", newline="\n")
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write a local coach context packet.")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args(argv)

    try:
        repo_root = repo_root_from_path()
        output_path = write_context_packet(repo_root, args.run_id)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
