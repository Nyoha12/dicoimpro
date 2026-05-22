from __future__ import annotations

import builtins
import json
from pathlib import Path
import socket
from typing import Any

import pytest

from dico_impro.agents import FakeScenario
from dico_impro.contracts import BatchStatus
from dico_impro.orchestration import ExplicitScope, run_dry_run


GOLDEN_SET_DIR = Path(__file__).parent / "fixtures" / "golden_set"
FIXED_CREATED_AT = "2026-05-21T00:00:00Z"

GOLDEN_CASES: dict[str, dict[str, object]] = {
    "scope_success_valid.json": {
        "scenario": FakeScenario.SUCCESS_VALID,
        "status": BatchStatus.COMPLETED_CLEAN,
        "entries_processed": 1,
        "entries_skipped": 0,
        "entries_blocked": 0,
        "run_002_requested": 0,
        "publication_blocked": 0,
    },
    "scope_success_with_warning.json": {
        "scenario": FakeScenario.SUCCESS_WITH_WARNING,
        "status": BatchStatus.COMPLETED_WITH_WARNINGS,
        "entries_processed": 1,
        "entries_skipped": 0,
        "entries_blocked": 0,
        "run_002_requested": 0,
        "publication_blocked": 0,
    },
    "scope_schema_invalid.json": {
        "scenario": FakeScenario.SCHEMA_INVALID,
        "status": BatchStatus.FAILED_RECOVERABLE,
        "entries_processed": 0,
        "entries_skipped": 1,
        "entries_blocked": 0,
        "run_002_requested": 0,
        "publication_blocked": 0,
    },
    "scope_non_parseable_output.json": {
        "scenario": FakeScenario.NON_PARSEABLE_OUTPUT,
        "status": BatchStatus.FAILED_RECOVERABLE,
        "entries_processed": 0,
        "entries_skipped": 1,
        "entries_blocked": 0,
        "run_002_requested": 0,
        "publication_blocked": 0,
    },
    "scope_protocol_violation.json": {
        "scenario": FakeScenario.PROTOCOL_VIOLATION,
        "status": BatchStatus.FAILED_BLOCKING,
        "entries_processed": 0,
        "entries_skipped": 0,
        "entries_blocked": 1,
        "run_002_requested": 0,
        "publication_blocked": 0,
    },
    "scope_source_confusion.json": {
        "scenario": FakeScenario.SOURCE_CONFUSION,
        "status": BatchStatus.FAILED_BLOCKING,
        "entries_processed": 0,
        "entries_skipped": 0,
        "entries_blocked": 1,
        "run_002_requested": 0,
        "publication_blocked": 0,
    },
    "scope_publication_blocking.json": {
        "scenario": FakeScenario.PUBLICATION_BLOCKING,
        "status": BatchStatus.FAILED_BLOCKING,
        "entries_processed": 0,
        "entries_skipped": 0,
        "entries_blocked": 1,
        "run_002_requested": 0,
        "publication_blocked": 1,
    },
    "scope_run_002_required.json": {
        "scenario": FakeScenario.RUN_002_REQUIRED,
        "status": BatchStatus.COMPLETED_WITH_WARNINGS,
        "entries_processed": 1,
        "entries_skipped": 0,
        "entries_blocked": 0,
        "run_002_requested": 1,
        "publication_blocked": 0,
    },
}


def load_golden_scope(fixture_name: str) -> ExplicitScope:
    fixture_path = (GOLDEN_SET_DIR / fixture_name).resolve()
    assert fixture_path.parent == GOLDEN_SET_DIR.resolve()
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    return ExplicitScope.model_validate(payload)


@pytest.mark.parametrize("fixture_name", sorted(GOLDEN_CASES))
def test_golden_set_fixtures_are_explicit_single_entry_scopes(fixture_name: str):
    scope = load_golden_scope(fixture_name)
    expected = GOLDEN_CASES[fixture_name]
    scenario = expected["scenario"]

    assert len(scope.entries) == 1
    assert scope.entries[0].id_entree_original.startswith("GOLDEN_ENTRY_")
    assert scope.entries[0].fake_scenario == scenario.value


def test_golden_set_directory_contains_only_expected_fixtures():
    assert {path.name for path in GOLDEN_SET_DIR.glob("*.json")} == set(GOLDEN_CASES)


@pytest.mark.parametrize("fixture_name", sorted(GOLDEN_CASES))
def test_golden_set_prudence_and_error_behavior(fixture_name: str):
    scope = load_golden_scope(fixture_name)
    expected = GOLDEN_CASES[fixture_name]
    scenario = expected["scenario"]

    result = run_dry_run(scope, created_at=FIXED_CREATED_AT)

    assert result.batch_state.status == expected["status"]
    assert result.batch_state.entries_scope == [scope.entries[0].id_entree_original]
    assert result.batch_state.artifacts == []

    report = result.batch_report
    assert report.entries_total == 1
    assert report.entries_processed == expected["entries_processed"]
    assert report.entries_skipped == expected["entries_skipped"]
    assert report.entries_blocked == expected["entries_blocked"]
    assert report.run_002_requested == expected["run_002_requested"]
    assert report.publication_blocked == expected["publication_blocked"]
    assert report.artifacts == []
    assert report.journal_patch_id is None

    assert len(result.tasks) == 1
    assert len(result.agent_results) == 1
    assert len(result.quality_gate_results) == 1
    assert result.tasks[0].allowed_files == []
    assert result.tasks[0].input_payload["fake_scenario"] == scenario.value
    assert result.agent_results[0].payload["scenario"] == scenario.value


def test_golden_set_dry_run_is_in_memory(monkeypatch: pytest.MonkeyPatch):
    scopes = [load_golden_scope(fixture_name) for fixture_name in sorted(GOLDEN_CASES)]

    def fail_file_access(*args: object, **kwargs: object) -> Any:
        raise AssertionError("golden-set dry-run must not access files")

    def fail_network_call(*args: object, **kwargs: object) -> Any:
        raise AssertionError("golden-set dry-run must not access the network")

    monkeypatch.setattr(builtins, "open", fail_file_access)
    monkeypatch.setattr(Path, "open", fail_file_access)
    monkeypatch.setattr(Path, "read_text", fail_file_access)
    monkeypatch.setattr(Path, "write_text", fail_file_access)
    monkeypatch.setattr(socket, "socket", fail_network_call)
    monkeypatch.setattr(socket, "create_connection", fail_network_call)

    for scope in scopes:
        result = run_dry_run(scope, created_at=FIXED_CREATED_AT)
        assert result.batch_report.entries_total == 1
