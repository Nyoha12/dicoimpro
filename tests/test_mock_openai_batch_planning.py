from __future__ import annotations

import builtins
import inspect
import json
from pathlib import Path
import socket

import pytest

from dico_impro.agents import OpenAIAdapter, QualityGateClassification
from dico_impro.contracts import AgentContract, AgentTask, BatchStatus
from dico_impro.contracts.common import SCHEMA_VERSION
from dico_impro.exports import export_dry_run_result_json
from dico_impro.orchestration import (
    DryRunResult,
    ExplicitScope,
    build_default_registry,
    build_mock_openai_planning_registry,
    plan_batch_with_mock_openai,
    run_dry_run,
)
import dico_impro.orchestration.mock_openai_plan as mock_openai_plan_module
from dico_impro.orchestration.task_builder import DEFAULT_DRY_RUN_AGENT_NAME


def make_scope(*, batch_id: str = "BATCH_MOCK_OPENAI") -> ExplicitScope:
    return ExplicitScope.model_validate(
        {
            "batch_id": batch_id,
            "entries": [{"id_entree_original": "026", "titre_original_exact": "First"}],
        }
    )


def valid_payload() -> dict[str, object]:
    return {
        "object_type": "RoutingDecision",
        "schema_version": SCHEMA_VERSION,
        "scenario": "success_valid",
        "status": "ok",
    }


def blocking_payload(error_type: str) -> dict[str, object]:
    return {
        "object_type": "RoutingDecision",
        "schema_version": SCHEMA_VERSION,
        "scenario": error_type,
        "status": "error",
        "error_type": error_type,
    }


class DeterministicMockOpenAIClient:
    def __init__(self, *payloads: dict[str, object]) -> None:
        self.payloads = list(payloads) or [valid_payload()]
        self.calls: list[tuple[AgentTask, AgentContract]] = []

    def run_task(self, *, task: AgentTask, contract: AgentContract) -> dict[str, object]:
        self.calls.append((task, contract))
        payload_index = min(len(self.calls) - 1, len(self.payloads) - 1)
        return {
            "result_id": f"MOCK_OPENAI_RESULT_{task.task_id}",
            "payload": dict(self.payloads[payload_index]),
            "warnings": [],
            "audit_notes": [],
            "raw_model_trace_ref": f"mock_openai_trace:{task.task_id}:{payload_index}",
            "validation_status": "schema_valid",
        }


def test_mock_openai_planning_succeeds_with_valid_mock_payload():
    client = DeterministicMockOpenAIClient(valid_payload())

    result = plan_batch_with_mock_openai(
        make_scope(),
        client,
        created_at="2026-05-21T00:00:00Z",
    )

    assert isinstance(result, DryRunResult)
    assert result.batch_state.status == BatchStatus.COMPLETED_CLEAN
    assert result.batch_report.entries_total == 1
    assert result.batch_report.entries_processed == 1
    assert result.batch_report.entries_blocked == 0
    assert result.batch_report.entries_skipped == 0
    assert len(result.tasks) == 1
    assert len(result.agent_results) == 1
    assert len(result.quality_gate_results) == 1
    assert len(result.evaluation_records) == 1
    assert result.quality_gate_results[0].classification == QualityGateClassification.OK

    trace_metadata = result.evaluation_records[0].trace_metadata
    assert trace_metadata.adapter_type == "openai"
    assert trace_metadata.retry_count == 0
    assert trace_metadata.duration_ms == 0
    assert trace_metadata.raw_trace_ref == (
        f"mock_openai_trace:{result.tasks[0].task_id}:0"
    )

    assert len(client.calls) == 1
    called_task, called_contract = client.calls[0]
    assert called_task == result.tasks[0]
    assert called_contract.agent_name == DEFAULT_DRY_RUN_AGENT_NAME
    assert called_contract.required_output_schema == "RoutingDecision"


def test_invalid_mock_openai_payload_becomes_blocking_through_report():
    client = DeterministicMockOpenAIClient(
        {
            "schema_version": SCHEMA_VERSION,
            "scenario": "missing_object_type",
            "status": "ok",
        }
    )

    result = plan_batch_with_mock_openai(
        make_scope(batch_id="BATCH_MOCK_OPENAI_INVALID"),
        client,
        created_at="2026-05-21T00:00:00Z",
    )

    assert result.quality_gate_results[0].classification == QualityGateClassification.BLOCKING
    assert result.quality_gate_results[0].reasons == ("payload missing object_type",)
    assert result.batch_state.status == BatchStatus.FAILED_BLOCKING
    assert result.batch_state.errors_blocking == ["payload missing object_type"]
    assert result.batch_report.entries_total == 1
    assert result.batch_report.entries_processed == 0
    assert result.batch_report.entries_blocked == 1
    assert result.evaluation_records[0].payload_validation_ok is False
    assert result.evaluation_records[0].trace_metadata.adapter_type == "openai"
    assert len(client.calls) == 1


@pytest.mark.parametrize("error_type", ["source_confusion", "protocol_violation"])
def test_mock_openai_source_or_protocol_payload_becomes_blocking(error_type: str):
    client = DeterministicMockOpenAIClient(blocking_payload(error_type))

    result = plan_batch_with_mock_openai(
        make_scope(batch_id=f"BATCH_MOCK_OPENAI_{error_type.upper()}"),
        client,
        created_at="2026-05-21T00:00:00Z",
    )

    assert result.quality_gate_results[0].classification == QualityGateClassification.BLOCKING
    assert result.quality_gate_results[0].reasons == (error_type,)
    assert result.batch_state.status == BatchStatus.FAILED_BLOCKING
    assert result.batch_state.errors_blocking == [error_type]
    assert result.batch_report.entries_processed == 0
    assert result.batch_report.entries_blocked == 1
    assert len(client.calls) == 1


def test_plan_batch_with_mock_openai_requires_explicit_scope():
    client = DeterministicMockOpenAIClient()

    with pytest.raises(TypeError, match="ExplicitScope"):
        plan_batch_with_mock_openai(  # type: ignore[arg-type]
            {"batch_id": "BATCH_BAD", "entries": [{"id_entree_original": "026"}]},
            client,
        )

    assert client.calls == []


def test_plan_batch_with_mock_openai_requires_injected_client():
    with pytest.raises(TypeError, match="injected client"):
        plan_batch_with_mock_openai(make_scope(), None)


def test_mock_openai_registry_isolated_from_default_dry_run_registry():
    default_registered = build_default_registry().get(DEFAULT_DRY_RUN_AGENT_NAME)
    mock_registered = build_mock_openai_planning_registry().get(DEFAULT_DRY_RUN_AGENT_NAME)

    assert default_registered.adapter_type == "fake"
    assert mock_registered.adapter_type == "openai"
    assert default_registered.contract == mock_registered.contract


def test_run_dry_run_still_rejects_openai_adapter_before_client_call():
    client = DeterministicMockOpenAIClient()

    with pytest.raises(TypeError, match="FakeAgentAdapter"):
        run_dry_run(make_scope(), adapter=OpenAIAdapter(enabled=True, client=client))

    assert client.calls == []


def test_json_exporter_can_export_mock_openai_planning_result(tmp_path):
    client = DeterministicMockOpenAIClient(valid_payload())
    result = plan_batch_with_mock_openai(
        make_scope(batch_id="BATCH_MOCK_OPENAI_EXPORT"),
        client,
        created_at="2026-05-21T00:00:00Z",
    )

    export_dry_run_result_json(result, tmp_path)

    batch_report = json.loads((tmp_path / "batch_report.json").read_text(encoding="utf-8"))
    evaluation_records = json.loads(
        (tmp_path / "evaluation_records.json").read_text(encoding="utf-8")
    )
    master = json.loads((tmp_path / "master.json").read_text(encoding="utf-8"))

    assert batch_report["batch_id"] == "BATCH_MOCK_OPENAI_EXPORT"
    assert batch_report["entries_processed"] == 1
    assert evaluation_records[0]["trace_metadata"]["adapter_type"] == "openai"
    assert evaluation_records[0]["trace_metadata"]["raw_trace_ref"].startswith(
        "mock_openai_trace:"
    )
    assert master["source_object_type"] == "DryRunResult"
    assert master["counts"] == {
        "agent_results": 1,
        "evaluation_records": 1,
        "quality_gates": 1,
        "tasks": 1,
    }


def test_mock_openai_planner_does_not_access_files_or_network(monkeypatch: pytest.MonkeyPatch):
    def fail_file_access(*args: object, **kwargs: object) -> None:
        raise AssertionError("mock OpenAI planning must not access files")

    def fail_network_call(*args: object, **kwargs: object) -> None:
        raise AssertionError("mock OpenAI planning must not access network")

    monkeypatch.setattr(builtins, "open", fail_file_access)
    monkeypatch.setattr(Path, "open", fail_file_access)
    monkeypatch.setattr(Path, "read_text", fail_file_access)
    monkeypatch.setattr(Path, "write_text", fail_file_access)
    monkeypatch.setattr(socket, "socket", fail_network_call)
    monkeypatch.setattr(socket, "create_connection", fail_network_call)

    result = plan_batch_with_mock_openai(
        make_scope(batch_id="BATCH_MOCK_OPENAI_NO_IO"),
        DeterministicMockOpenAIClient(valid_payload()),
        created_at="2026-05-21T00:00:00Z",
    )

    assert result.batch_report.entries_processed == 1


def test_mock_openai_planner_source_has_no_forbidden_integrations():
    source = inspect.getsource(mock_openai_plan_module)
    lowered_source = source.lower()

    assert "import openai" not in lowered_source
    assert "__import__('openai'" not in lowered_source
    assert '__import__("openai"' not in lowered_source
    for forbidden in ("requests", "httpx", "urllib", "socket"):
        assert forbidden not in lowered_source
    for forbidden in (
        "data/local_files",
        "active_journal",
        ".pdf",
        ".xlsx",
        ".csv",
        "journalpatch",
        "prompt_contracts",
        "promptpackage",
        "prompts.py",
        "sourcediscoveryagent",
    ):
        assert forbidden not in lowered_source
