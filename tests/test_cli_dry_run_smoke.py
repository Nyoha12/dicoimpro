from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dico_impro.exports.json_exporter import BASE_EXPORT_FILES, MASTER_FILE_NAME
from helpers.runtime_guards import (
    assert_no_forbidden_fragments,
    guard_cli_runtime_boundaries,
    invoke_cli,
    load_json_exports,
    write_explicit_scope,
)


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
FORBIDDEN_PAYLOAD_FRAGMENTS = (
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
    "active_journal",
    ".xlsx",
    ".csv",
    "candidate",
)


def test_cli_dry_run_smoke_is_fake_only_end_to_end(
    tmp_path: Path,
    monkeypatch: Any,
    capsys: Any,
) -> None:
    scope_path = tmp_path / "scope.json"
    output_dir = tmp_path / "exports"
    write_explicit_scope(scope_path, batch_id=SCOPE_BATCH_ID, entries=SCOPE_ENTRIES)
    guard_cli_runtime_boundaries(tmp_path, monkeypatch, context="CLI dry-run smoke")

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

    parsed = load_json_exports(output_dir)
    assert set(parsed) == actual_files, "Every generated output file must be valid JSON."

    assert_batch_exports_match_temporary_scope(parsed)
    assert_core_exports_are_fake_only(parsed)
    assert_no_forbidden_fragments(
        parsed,
        FORBIDDEN_PAYLOAD_FRAGMENTS,
        "Generated dry-run smoke JSON",
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
