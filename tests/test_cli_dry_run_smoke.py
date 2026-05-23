from __future__ import annotations

import builtins
import inspect
import json
from pathlib import Path
import socket
from typing import Any

from dico_impro import cli
from dico_impro.agents import prompt_contracts
from dico_impro.agents.adapters.openai import OpenAIAdapter
from dico_impro.exports.json_exporter import BASE_EXPORT_FILES, MASTER_FILE_NAME
import dico_impro.orchestration.mock_openai_plan as mock_openai_plan


SCOPE_BATCH_ID = "BATCH_CLI_DRY_RUN_SMOKE"
SCOPE_ENTRIES = (
    {
        "id_entree_original": "SMOKE_SCOPE_ENTRY_001",
        "titre_original_exact": "Temporary smoke scope entry one",
        "fake_scenario": "success_valid",
    },
    {
        "id_entree_original": "SMOKE_SCOPE_ENTRY_002",
        "titre_original_exact": "Temporary smoke scope entry two",
        "fake_scenario": "success_valid",
    },
)
SCOPE_ENTRY_IDS = [entry["id_entree_original"] for entry in SCOPE_ENTRIES]
EXPECTED_CORE_EXPORT_FILES = {MASTER_FILE_NAME, *BASE_EXPORT_FILES.values()}


def write_temporary_scope(path: Path) -> None:
    path.write_text(
        json.dumps({"batch_id": SCOPE_BATCH_ID, "entries": list(SCOPE_ENTRIES)}),
        encoding="utf-8",
    )


def invoke_cli(argv: list[str], capsys: Any) -> tuple[int, str, str]:
    try:
        exit_code = cli.main(argv)
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def test_cli_dry_run_smoke_is_fake_only_end_to_end(
    tmp_path: Path,
    monkeypatch: Any,
    capsys: Any,
) -> None:
    scope_path = tmp_path / "scope.json"
    output_dir = tmp_path / "exports"
    write_temporary_scope(scope_path)
    assert_cli_plan_batch_source_has_no_network_or_openai_integration()
    guard_cli_dry_run_runtime_boundaries(tmp_path, monkeypatch)

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

    assert exit_code == 0, (
        "CLI dry-run smoke must exit successfully. "
        f"stdout={stdout!r} stderr={stderr!r}"
    )
    assert stderr == "", f"CLI dry-run smoke must not write stderr on success: {stderr!r}"

    summary = json.loads(stdout)
    assert summary["ok"] is True, f"CLI summary must report ok=true: {summary!r}"
    assert summary["batch_id"] == SCOPE_BATCH_ID, (
        "CLI summary batch_id must come from the temporary scope JSON."
    )
    assert summary["output_dir"] == str(output_dir), (
        "CLI summary output_dir must be the pytest tmp_path output directory."
    )

    actual_files = {path.name for path in output_dir.iterdir()}
    assert EXPECTED_CORE_EXPORT_FILES.issubset(actual_files), (
        "CLI dry-run smoke must create the current core JSON exports. "
        f"Missing: {sorted(EXPECTED_CORE_EXPORT_FILES.difference(actual_files))!r}"
    )
    assert set(summary["created_files"]) == actual_files, (
        "CLI summary created_files must match the files written to the output directory."
    )
    assert all(file_name.endswith(".json") for file_name in actual_files), (
        f"CLI dry-run smoke must only create JSON files. Found: {sorted(actual_files)!r}"
    )
    assert not any(file_name.endswith((".xlsx", ".csv")) for file_name in actual_files), (
        f"CLI dry-run smoke must not create XLSX or CSV exports. Found: {sorted(actual_files)!r}"
    )

    parsed = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(output_dir.iterdir())
    }
    assert set(parsed) == actual_files, "Every generated output file must be valid JSON."

    assert_batch_exports_match_temporary_scope(parsed)
    assert_core_exports_are_fake_only(parsed)
    assert_no_forbidden_payload_fragments(parsed)


def guard_cli_dry_run_runtime_boundaries(tmp_path: Path, monkeypatch: Any) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tmp_root = tmp_path.absolute()
    forbidden_roots = (
        repo_root / "data" / "local_files",
        repo_root / "data" / "active_journal",
        repo_root / "tests" / "fixtures" / "prompt_packages",
    )
    forbidden_files = (repo_root / "src" / "dico_impro" / "agents" / "prompts.py",)

    def is_relative_to(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
        except ValueError:
            return False
        return True

    def normalize_path(pathish: object) -> Path | None:
        if not isinstance(pathish, (str, Path)):
            return None
        path = Path(pathish)
        if not path.is_absolute():
            path = repo_root / path
        return path.absolute()

    def assert_allowed_path(pathish: object) -> None:
        path = normalize_path(pathish)
        if path is None:
            return
        for forbidden_root in forbidden_roots:
            if is_relative_to(path, forbidden_root.absolute()):
                raise AssertionError(f"CLI dry-run smoke touched forbidden path: {path}")
        if any(path == forbidden_file.absolute() for forbidden_file in forbidden_files):
            raise AssertionError(f"CLI dry-run smoke touched forbidden file: {path}")
        assert is_relative_to(path, tmp_root), (
            "CLI dry-run smoke must only use pytest tmp_path files at runtime. "
            f"Touched: {path}"
        )

    original_builtin_open = builtins.open
    original_path_open = Path.open
    original_path_exists = Path.exists
    original_path_is_dir = Path.is_dir
    original_path_is_file = Path.is_file
    original_path_mkdir = Path.mkdir
    original_path_iterdir = Path.iterdir
    original_path_glob = Path.glob

    def guarded_builtin_open(file: object, *args: object, **kwargs: object) -> Any:
        assert_allowed_path(file)
        return original_builtin_open(file, *args, **kwargs)

    def guarded_path_open(self: Path, *args: object, **kwargs: object) -> Any:
        assert_allowed_path(self)
        return original_path_open(self, *args, **kwargs)

    def guarded_path_exists(self: Path) -> bool:
        assert_allowed_path(self)
        return original_path_exists(self)

    def guarded_path_is_dir(self: Path) -> bool:
        assert_allowed_path(self)
        return original_path_is_dir(self)

    def guarded_path_is_file(self: Path) -> bool:
        assert_allowed_path(self)
        return original_path_is_file(self)

    def guarded_path_mkdir(self: Path, *args: object, **kwargs: object) -> None:
        assert_allowed_path(self)
        return original_path_mkdir(self, *args, **kwargs)

    def guarded_path_iterdir(self: Path) -> Any:
        assert_allowed_path(self)
        return original_path_iterdir(self)

    def guarded_path_glob(self: Path, pattern: str) -> Any:
        assert_allowed_path(self)
        return original_path_glob(self, pattern)

    def fail_network_call(*args: object, **kwargs: object) -> None:
        raise AssertionError("CLI dry-run smoke must not access the network")

    def fail_openai_adapter_use(*args: object, **kwargs: object) -> None:
        raise AssertionError("CLI dry-run smoke must not use OpenAIAdapter")

    def fail_prompt_package_consumption(cls: object, *args: object, **kwargs: object) -> None:
        raise AssertionError("CLI dry-run smoke must not consume PromptPackage metadata")

    monkeypatch.setattr(builtins, "open", guarded_builtin_open)
    monkeypatch.setattr(Path, "open", guarded_path_open)
    monkeypatch.setattr(Path, "exists", guarded_path_exists)
    monkeypatch.setattr(Path, "is_dir", guarded_path_is_dir)
    monkeypatch.setattr(Path, "is_file", guarded_path_is_file)
    monkeypatch.setattr(Path, "mkdir", guarded_path_mkdir)
    monkeypatch.setattr(Path, "iterdir", guarded_path_iterdir)
    monkeypatch.setattr(Path, "glob", guarded_path_glob)
    monkeypatch.setattr(socket, "socket", fail_network_call)
    monkeypatch.setattr(socket, "create_connection", fail_network_call)
    monkeypatch.setattr(OpenAIAdapter, "__init__", fail_openai_adapter_use)
    monkeypatch.setattr(OpenAIAdapter, "run_task", fail_openai_adapter_use)
    monkeypatch.setattr(mock_openai_plan, "OpenAIAdapter", OpenAIAdapter)
    monkeypatch.setattr(
        prompt_contracts.PromptPackage,
        "model_validate",
        classmethod(fail_prompt_package_consumption),
    )
    monkeypatch.setattr(
        prompt_contracts.PromptPackage,
        "__init__",
        fail_prompt_package_consumption,
    )


def assert_batch_exports_match_temporary_scope(parsed: dict[str, Any]) -> None:
    batch_state = parsed["batch_state.json"]
    batch_report = parsed["batch_report.json"]
    agent_results = parsed["agent_results.json"]
    quality_gates = parsed["quality_gates.json"]

    assert batch_state["batch_id"] == SCOPE_BATCH_ID, (
        "batch_state.json batch_id must come from the temporary scope JSON."
    )
    assert batch_state["entries_scope"] == SCOPE_ENTRY_IDS, (
        "batch_state.json entries_scope must exactly match the temporary scope entries."
    )
    assert batch_state["artifacts"] == [], "Dry-run smoke must not record output artifacts."
    assert batch_state["errors_recoverable"] == [], (
        "Smoke scope uses success_valid entries and must not produce recoverable errors."
    )
    assert batch_state["errors_blocking"] == [], (
        "Smoke scope uses success_valid entries and must not produce blocking errors."
    )
    assert batch_state["replay_command"] is None, (
        "Dry-run smoke must not produce a replay or RUN command."
    )

    assert batch_report["batch_id"] == SCOPE_BATCH_ID, (
        "batch_report.json batch_id must come from the temporary scope JSON."
    )
    assert batch_report["entries_total"] == len(SCOPE_ENTRY_IDS), (
        "batch_report.json entries_total must count the temporary scope entries."
    )
    assert batch_report["entries_processed"] == len(SCOPE_ENTRY_IDS), (
        "All success_valid temporary entries must be processed by the fake dry-run."
    )
    assert batch_report["entries_skipped"] == 0, "Smoke dry-run must not skip entries."
    assert batch_report["entries_blocked"] == 0, "Smoke dry-run must not block entries."
    assert batch_report["run_002_requested"] == 0, "Smoke dry-run must not request RUN_002."
    assert batch_report["publication_blocked"] == 0, (
        "Smoke dry-run must not block publication."
    )
    assert batch_report["journal_patch_id"] is None, (
        "Smoke dry-run must not create or apply a journal patch."
    )
    assert batch_report["artifacts"] == [], "Smoke dry-run must not emit non-JSON artifacts."

    assert len(agent_results) == len(SCOPE_ENTRY_IDS), (
        "agent_results.json must include one fake result per temporary scope entry."
    )
    assert len(quality_gates) == len(SCOPE_ENTRY_IDS), (
        "quality_gates.json must include one gate result per temporary scope entry."
    )
    assert [gate["classification"] for gate in quality_gates] == ["ok", "ok"], (
        "Smoke scope success_valid entries must pass quality gates."
    )


def assert_core_exports_are_fake_only(parsed: dict[str, Any]) -> None:
    agent_results = parsed["agent_results.json"]
    evaluation_records = parsed.get("evaluation_records.json")
    master = parsed["master.json"]

    assert master["batch_id"] == SCOPE_BATCH_ID, (
        "master.json batch_id must come from the temporary scope JSON."
    )
    assert master["counts"]["agent_results"] == len(SCOPE_ENTRY_IDS), (
        "master.json must count one agent result per temporary scope entry."
    )
    assert master["counts"]["quality_gates"] == len(SCOPE_ENTRY_IDS), (
        "master.json must count one quality gate per temporary scope entry."
    )
    assert "journal_patch" not in master["files"], (
        "Smoke dry-run must not emit journal_patch.json."
    )
    assert "audit_queue" not in master["files"], "Smoke dry-run must not emit audit_queue.json."

    assert [result["created_by"] for result in agent_results] == [
        "FakeAgentAdapter",
        "FakeAgentAdapter",
    ], "CLI dry-run smoke must use only FakeAgentAdapter results."
    assert [result["payload"]["scenario"] for result in agent_results] == [
        "success_valid",
        "success_valid",
    ], "CLI dry-run smoke must use only explicit success_valid fake scenarios."
    assert all(
        result["raw_model_trace_ref"].startswith("fake_trace:")
        for result in agent_results
    ), "CLI dry-run smoke must only emit fake trace references."

    if evaluation_records is not None:
        assert evaluation_records, (
            "evaluation_records.json is emitted by current exports and must not be empty."
        )
        assert [record["id_entree_original"] for record in evaluation_records] == (
            SCOPE_ENTRY_IDS
        ), "evaluation_records.json must correspond to temporary scope entries."
        assert [record["quality_gate_classification"] for record in evaluation_records] == [
            "ok",
            "ok",
        ], "evaluation_records.json must record successful fake quality gates."
        assert [record["payload_validation_ok"] for record in evaluation_records] == [
            True,
            True,
        ], "evaluation_records.json must record successful fake payload validation."
        assert [
            record["trace_metadata"]["adapter_type"] for record in evaluation_records
        ] == ["fake", "fake"], (
            "evaluation_records.json trace metadata must remain fake-only."
        )
        assert all(
            record["trace_metadata"]["raw_trace_ref"].startswith("fake_trace:")
            for record in evaluation_records
        ), "evaluation_records.json must only reference fake traces."


def assert_no_forbidden_payload_fragments(parsed: dict[str, Any]) -> None:
    generated_payload = json.dumps(parsed, ensure_ascii=False, sort_keys=True)
    normalized_payload = generated_payload.casefold()
    forbidden_fragments = (
        "OpenAIAdapter",
        "PromptPackage",
        "prompt_body_ref",
        "system prompt",
        "user prompt",
        "prompts.py",
        "SourceDiscoveryAgent",
        "JournalPatch",
        "data/local_files",
        "data/active_journal",
        ".xlsx",
        ".csv",
        "candidate",
    )
    missing = [
        fragment for fragment in forbidden_fragments if fragment.casefold() in normalized_payload
    ]
    assert not missing, (
        "Generated dry-run smoke JSON must not contain forbidden integration or "
        f"project-data fragments: {missing!r}"
    )


def assert_cli_plan_batch_source_has_no_network_or_openai_integration() -> None:
    source = inspect.getsource(cli.cmd_plan_batch)
    lowered_source = source.lower()

    for forbidden in ("openai", "requests", "httpx", "urllib", "socket"):
        assert forbidden not in lowered_source, (
            "cmd_plan_batch must stay free of direct OpenAI or network integration. "
            f"Forbidden source fragment present: {forbidden!r}"
        )
