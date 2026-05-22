from __future__ import annotations

import builtins
from dataclasses import dataclass
import inspect
import json
from pathlib import Path
import socket
from typing import Any

import pytest

from dico_impro.exports import JsonExportReport, export_dry_run_result_json
from dico_impro.exports import json_exporter
from dico_impro.orchestration import DryRunResult, ExplicitScope, run_dry_run


EXPECTED_BASE_FILES = {
    "master.json",
    "batch_report.json",
    "batch_state.json",
    "agent_results.json",
    "quality_gates.json",
    "evaluation_records.json",
}


def make_dry_run_result() -> DryRunResult:
    scope = ExplicitScope.model_validate(
        {
            "batch_id": "BATCH_EXPORT",
            "entries": [
                {"id_entree_original": "026", "titre_original_exact": "First"},
                {"id_entree_original": "031", "titre_original_exact": "Second"},
            ],
        }
    )
    return run_dry_run(scope, created_at="2026-05-21T00:00:00Z")


def load_json_files(output_dir: Path) -> dict[str, Any]:
    return {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(output_dir.iterdir())
    }


def test_exporter_creates_expected_json_files_in_tmp_path(tmp_path):
    output_dir = tmp_path / "dry_run_exports"

    report = export_dry_run_result_json(make_dry_run_result(), output_dir)

    assert isinstance(report, JsonExportReport)
    assert report.output_dir == output_dir
    assert {path.parent for path in report.created_files.values()} == {output_dir}
    assert {path.name for path in report.created_files.values()} == EXPECTED_BASE_FILES
    assert {path.name for path in output_dir.iterdir()} == EXPECTED_BASE_FILES

    parsed = load_json_files(output_dir)
    assert set(parsed) == EXPECTED_BASE_FILES

    batch_report = parsed["batch_report.json"]
    assert batch_report["batch_id"] == "BATCH_EXPORT"
    assert batch_report["entries_total"] == 2
    assert batch_report["entries_processed"] == 2
    assert batch_report["entries_skipped"] == 0
    assert batch_report["entries_blocked"] == 0

    master = parsed["master.json"]
    assert master["batch_id"] == "BATCH_EXPORT"
    assert master["files"] == {
        "agent_results": "agent_results.json",
        "batch_report": "batch_report.json",
        "batch_state": "batch_state.json",
        "evaluation_records": "evaluation_records.json",
        "quality_gates": "quality_gates.json",
    }
    assert master["counts"] == {
        "agent_results": 2,
        "evaluation_records": 2,
        "quality_gates": 2,
        "tasks": 2,
    }
    assert "journal_patch" not in master["files"]
    assert "audit_queue" not in master["files"]


def test_exporter_creates_output_directory_if_missing(tmp_path):
    output_dir = tmp_path / "missing" / "exports"
    assert not output_dir.exists()

    report = export_dry_run_result_json(make_dry_run_result(), output_dir)

    assert output_dir.is_dir()
    assert report.created_files["master"] == output_dir / "master.json"


def test_exporter_refuses_output_path_that_exists_as_file(tmp_path):
    output_path = tmp_path / "not_a_directory"
    output_path.write_text("existing file", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        export_dry_run_result_json(make_dry_run_result(), output_path)

    assert output_path.read_text(encoding="utf-8") == "existing file"


def test_exporter_requires_existing_dry_run_result(tmp_path):
    output_dir = tmp_path / "bad_input"

    with pytest.raises(TypeError):
        export_dry_run_result_json(object(), output_dir)  # type: ignore[arg-type]

    assert not output_dir.exists()


def test_exporter_includes_future_optional_payloads_only_when_present(tmp_path):
    @dataclass(frozen=True)
    class FutureDryRunResult(DryRunResult):
        journal_patch: dict[str, str] | None = None
        audit_queue: list[dict[str, str]] | None = None

    result = make_dry_run_result()
    future_result = FutureDryRunResult(
        batch_state=result.batch_state,
        batch_report=result.batch_report,
        tasks=result.tasks,
        agent_results=result.agent_results,
        quality_gate_results=result.quality_gate_results,
        evaluation_records=result.evaluation_records,
        journal_patch={"patch_id": "PATCH_001"},
        audit_queue=None,
    )

    output_dir = tmp_path / "future_exports"
    export_dry_run_result_json(future_result, output_dir)

    parsed = load_json_files(output_dir)
    assert "journal_patch.json" in parsed
    assert "audit_queue.json" not in parsed
    assert parsed["journal_patch.json"] == {"patch_id": "PATCH_001"}
    assert parsed["master.json"]["files"]["journal_patch"] == "journal_patch.json"
    assert "audit_queue" not in parsed["master.json"]["files"]


def test_exporter_has_no_forbidden_integrations_or_formats():
    source = inspect.getsource(json_exporter)
    lowered_source = source.lower()

    for forbidden in ("openai", "requests", "httpx", "urllib", "socket"):
        assert forbidden not in lowered_source
    for forbidden in ("active_journal", "local_files", ".pdf", ".xlsx", ".csv"):
        assert forbidden not in lowered_source
    assert "JournalPatch" not in source


def test_exporter_does_not_access_project_data_or_network(tmp_path, monkeypatch):
    result = make_dry_run_result()
    repo_root = Path(__file__).resolve().parents[1]
    forbidden_roots = (
        repo_root / "data" / "local_files",
        repo_root / "data" / "active_journal",
    )

    def assert_not_forbidden_path(pathish: object) -> None:
        if not isinstance(pathish, (str, Path)):
            return
        path = Path(pathish)
        if not path.is_absolute():
            path = repo_root / path
        absolute_path = path.absolute()
        for forbidden_root in forbidden_roots:
            absolute_root = forbidden_root.absolute()
            if absolute_path == absolute_root or absolute_root in absolute_path.parents:
                raise AssertionError(f"forbidden project data access: {absolute_path}")

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
        raise AssertionError("network access is forbidden during JSON export")

    monkeypatch.setattr(builtins, "open", guarded_builtin_open)
    monkeypatch.setattr(Path, "open", guarded_path_open)
    monkeypatch.setattr(Path, "exists", guarded_path_exists)
    monkeypatch.setattr(Path, "is_dir", guarded_path_is_dir)
    monkeypatch.setattr(Path, "is_file", guarded_path_is_file)
    monkeypatch.setattr(Path, "mkdir", guarded_path_mkdir)
    monkeypatch.setattr(socket, "socket", fail_network_call)
    monkeypatch.setattr(socket, "create_connection", fail_network_call)

    output_dir = tmp_path / "guarded_exports"
    export_dry_run_result_json(result, output_dir)

    assert (output_dir / "master.json").exists()
