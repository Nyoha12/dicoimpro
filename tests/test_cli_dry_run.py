from __future__ import annotations

import builtins
import inspect
import json
from pathlib import Path
import socket
from typing import Any

from dico_impro import cli


EXPECTED_EXPORT_FILES = {
    "master.json",
    "batch_state.json",
    "batch_report.json",
    "agent_results.json",
    "quality_gates.json",
}

EXPECTED_SUMMARY_FIELDS = {
    "ok",
    "batch_id",
    "output_dir",
    "created_files",
    "entries_total",
    "entries_processed",
    "entries_skipped",
    "entries_blocked",
}


def write_scope(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "batch_id": "BATCH_CLI",
                "entries": [
                    {"id_entree_original": "026", "titre_original_exact": "First"},
                    {"id_entree_original": "031", "titre_original_exact": "Second"},
                ],
            }
        ),
        encoding="utf-8",
    )


def invoke_cli(argv: list[str], capsys: Any) -> tuple[int, str, str]:
    try:
        exit_code = cli.main(argv)
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def test_plan_batch_dry_run_creates_json_files_and_prints_summary(tmp_path, capsys):
    scope_path = tmp_path / "scope.json"
    output_dir = tmp_path / "exports"
    write_scope(scope_path)

    exit_code, stdout, stderr = invoke_cli(
        [
            "plan-batch",
            "--dry-run",
            "--scope",
            str(scope_path),
            "--output-dir",
            str(output_dir),
        ],
        capsys,
    )

    assert exit_code == 0
    assert stderr == ""
    summary = json.loads(stdout)
    assert set(summary) == EXPECTED_SUMMARY_FIELDS
    assert summary["ok"] is True
    assert summary["batch_id"] == "BATCH_CLI"
    assert summary["output_dir"] == str(output_dir)
    assert set(summary["created_files"]) == EXPECTED_EXPORT_FILES
    assert summary["entries_total"] == 2
    assert summary["entries_processed"] == 2
    assert summary["entries_skipped"] == 0
    assert summary["entries_blocked"] == 0
    assert {path.name for path in output_dir.iterdir()} == EXPECTED_EXPORT_FILES


def test_plan_batch_fails_without_dry_run(tmp_path, capsys):
    scope_path = tmp_path / "scope.json"
    output_dir = tmp_path / "exports"
    write_scope(scope_path)

    exit_code, stdout, stderr = invoke_cli(
        [
            "plan-batch",
            "--scope",
            str(scope_path),
            "--output-dir",
            str(output_dir),
        ],
        capsys,
    )

    assert exit_code != 0
    assert stdout == ""
    assert "--dry-run" in stderr
    assert not output_dir.exists()


def test_plan_batch_fails_with_missing_scope_file(tmp_path, capsys):
    missing_scope = tmp_path / "missing_scope.json"
    output_dir = tmp_path / "exports"

    exit_code, stdout, stderr = invoke_cli(
        [
            "plan-batch",
            "--dry-run",
            "--scope",
            str(missing_scope),
            "--output-dir",
            str(output_dir),
        ],
        capsys,
    )

    assert exit_code != 0
    assert stdout == ""
    assert json.loads(stderr)["error"] == "scope_file_missing"
    assert not output_dir.exists()


def test_plan_batch_fails_with_invalid_scope_json(tmp_path, capsys):
    scope_path = tmp_path / "scope.json"
    output_dir = tmp_path / "exports"
    scope_path.write_text(
        json.dumps({"batch_id": "BATCH_CLI", "entries": []}),
        encoding="utf-8",
    )

    exit_code, stdout, stderr = invoke_cli(
        [
            "plan-batch",
            "--dry-run",
            "--scope",
            str(scope_path),
            "--output-dir",
            str(output_dir),
        ],
        capsys,
    )

    assert exit_code != 0
    assert stdout == ""
    assert json.loads(stderr)["error"] == "dry_run_failed"
    assert not output_dir.exists()


def test_plan_batch_fails_when_output_dir_is_existing_file(tmp_path, capsys):
    scope_path = tmp_path / "scope.json"
    output_path = tmp_path / "not_a_directory"
    write_scope(scope_path)
    output_path.write_text("existing file", encoding="utf-8")

    exit_code, stdout, stderr = invoke_cli(
        [
            "plan-batch",
            "--dry-run",
            "--scope",
            str(scope_path),
            "--output-dir",
            str(output_path),
        ],
        capsys,
    )

    assert exit_code != 0
    assert stdout == ""
    assert json.loads(stderr)["error"] == "output_path_not_directory"
    assert output_path.read_text(encoding="utf-8") == "existing file"


def test_plan_batch_does_not_access_project_data_or_network(tmp_path, monkeypatch, capsys):
    scope_path = tmp_path / "scope.json"
    output_dir = tmp_path / "exports"
    write_scope(scope_path)

    forbidden_fragments = ("data/local_files", "data/active_journal")

    def assert_not_forbidden_path(pathish: object) -> None:
        if not isinstance(pathish, (str, Path)):
            return
        normalized = str(pathish).replace("\\", "/")
        if any(fragment in normalized for fragment in forbidden_fragments):
            raise AssertionError(f"forbidden project data access: {pathish}")

    original_builtin_open = builtins.open
    original_path_open = Path.open
    original_path_exists = Path.exists
    original_path_is_dir = Path.is_dir
    original_path_is_file = Path.is_file
    original_path_mkdir = Path.mkdir

    def guarded_builtin_open(file: object, *args: object, **kwargs: object) -> Any:
        assert_not_forbidden_path(file)
        return original_builtin_open(file, *args, **kwargs)

    def guarded_path_open(self: Path, *args: object, **kwargs: object) -> Any:
        assert_not_forbidden_path(self)
        return original_path_open(self, *args, **kwargs)

    def guarded_path_exists(self: Path) -> bool:
        assert_not_forbidden_path(self)
        return original_path_exists(self)

    def guarded_path_is_dir(self: Path) -> bool:
        assert_not_forbidden_path(self)
        return original_path_is_dir(self)

    def guarded_path_is_file(self: Path) -> bool:
        assert_not_forbidden_path(self)
        return original_path_is_file(self)

    def guarded_path_mkdir(self: Path, *args: object, **kwargs: object) -> None:
        assert_not_forbidden_path(self)
        return original_path_mkdir(self, *args, **kwargs)

    def fail_network_call(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access is forbidden during CLI dry-run")

    monkeypatch.setattr(builtins, "open", guarded_builtin_open)
    monkeypatch.setattr(Path, "open", guarded_path_open)
    monkeypatch.setattr(Path, "exists", guarded_path_exists)
    monkeypatch.setattr(Path, "is_dir", guarded_path_is_dir)
    monkeypatch.setattr(Path, "is_file", guarded_path_is_file)
    monkeypatch.setattr(Path, "mkdir", guarded_path_mkdir)
    monkeypatch.setattr(socket, "socket", fail_network_call)
    monkeypatch.setattr(socket, "create_connection", fail_network_call)

    exit_code, stdout, stderr = invoke_cli(
        [
            "plan-batch",
            "--dry-run",
            "--scope",
            str(scope_path),
            "--output-dir",
            str(output_dir),
        ],
        capsys,
    )

    assert exit_code == 0
    assert stderr == ""
    assert json.loads(stdout)["ok"] is True
    assert (output_dir / "master.json").exists()


def test_plan_batch_command_has_no_openai_or_network_integration():
    source = inspect.getsource(cli.cmd_plan_batch)
    lowered_source = source.lower()

    for forbidden in ("openai", "requests", "httpx", "urllib", "socket"):
        assert forbidden not in lowered_source
