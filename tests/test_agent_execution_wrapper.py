from __future__ import annotations

import builtins
from dataclasses import FrozenInstanceError
import inspect
from pathlib import Path

import pytest

from dico_impro.agents import (
    AgentEvaluationRecord,
    AgentExecutionOutcome,
    AgentTraceMetadata,
    FakeAgentAdapter,
    OpenAIAdapter,
    OpenAIAdapterDisabledError,
    QualityGateClassification,
    run_agent_task_with_evaluation,
)
import dico_impro.agents.execution as execution_module
from dico_impro.contracts import AgentContract, AgentResult, AgentTask


def make_contract() -> AgentContract:
    return AgentContract.model_validate(
        {
            "object_type": "AgentContract",
            "schema_version": "v0.2.3-auto",
            "created_by": "tests",
            "agent_name": "RoutingAgent",
            "agent_version": "v0.2.3-auto",
            "mission": "Produce a bounded structured mock object.",
            "allowed_inputs": ["EntryState"],
            "required_output_schema": "RoutingDecision",
            "forbidden_actions": ["write_outputs", "external_model_call"],
            "quality_gates": ["schema_validation"],
            "handoff_targets": [],
        }
    )


def make_task(input_payload: dict[str, object] | None = None) -> AgentTask:
    return AgentTask.model_validate(
        {
            "object_type": "AgentTask",
            "schema_version": "v0.2.3-auto",
            "created_by": "tests",
            "task_id": "TASK_BATCH_001_026_ROUTING",
            "batch_id": "BATCH_001",
            "id_entree_original": "026",
            "titre_original_exact": "Entry title",
            "task_type": "routing",
            "agent_name": "RoutingAgent",
            "input_payload": input_payload or {"fake_scenario": "success_valid"},
            "allowed_files": [],
            "forbidden_files": ["local_fixture_forbidden"],
            "expected_schema": "RoutingDecision",
        }
    )


class MissingPayloadObjectTypeAdapter(FakeAgentAdapter):
    def run_task(self, task: AgentTask, contract: AgentContract) -> AgentResult:
        result = super().run_task(task, contract)
        payload = dict(result.payload)
        payload.pop("object_type")
        return AgentResult.model_validate({**result.model_dump(), "payload": payload})


class CountingAdapter:
    def __init__(self) -> None:
        self.calls = 0

    def run_task(self, task: AgentTask, contract: AgentContract) -> AgentResult:
        self.calls += 1
        return FakeAgentAdapter().run_task(task, contract)


class ExplodingAdapter:
    def run_task(self, task: AgentTask, contract: AgentContract) -> AgentResult:
        raise RuntimeError("adapter failure")


class DeterministicMockClient:
    def __init__(self, *, payload: dict[str, object] | None = None) -> None:
        self.calls: list[tuple[AgentTask, AgentContract]] = []
        self.payload = payload or {
            "object_type": "RoutingDecision",
            "schema_version": "v0.2.3-auto",
            "scenario": "success_valid",
            "status": "ok",
        }

    def run_task(self, *, task: AgentTask, contract: AgentContract) -> dict[str, object]:
        self.calls.append((task, contract))
        return {
            "result_id": f"MOCK_RESULT_{task.task_id}",
            "payload": self.payload,
            "warnings": [],
            "audit_notes": [],
            "raw_model_trace_ref": f"mock_trace:{task.task_id}:deterministic",
            "validation_status": "schema_valid",
        }


class FailingClient:
    def __init__(self) -> None:
        self.calls = 0

    def run_task(self, *, task: AgentTask, contract: AgentContract) -> dict[str, object]:
        self.calls += 1
        raise AssertionError("disabled OpenAIAdapter must not call the injected client")


def test_wrapper_returns_frozen_outcome_for_fake_adapter():
    task = make_task()
    contract = make_contract()

    outcome = run_agent_task_with_evaluation(
        task,
        contract,
        FakeAgentAdapter(),
        adapter_type="fake",
    )

    assert isinstance(outcome, AgentExecutionOutcome)
    assert outcome.task == task
    assert outcome.result.created_by == "FakeAgentAdapter"
    assert outcome.quality_gate_result.classification == QualityGateClassification.OK
    assert isinstance(outcome.trace_metadata, AgentTraceMetadata)
    assert isinstance(outcome.evaluation_record, AgentEvaluationRecord)

    with pytest.raises(FrozenInstanceError):
        outcome.result = outcome.result


def test_wrapper_result_gate_trace_and_record_are_coherent():
    task = make_task()
    contract = make_contract()

    outcome = run_agent_task_with_evaluation(
        task,
        contract,
        FakeAgentAdapter(),
        adapter_type="custom-fake",
        retry_count=2,
        duration_ms=37,
    )

    assert outcome.result.task_id == task.task_id
    assert outcome.result.agent_name == task.agent_name
    assert outcome.result.schema_name == contract.required_output_schema
    assert outcome.quality_gate_result.is_ok is True
    assert outcome.trace_metadata.task_id == task.task_id
    assert outcome.trace_metadata.result_id == outcome.result.result_id
    assert outcome.trace_metadata.agent_name == outcome.result.agent_name
    assert outcome.trace_metadata.adapter_type == "custom-fake"
    assert outcome.trace_metadata.retry_count == 2
    assert outcome.trace_metadata.duration_ms == 37
    assert outcome.trace_metadata.raw_trace_ref == outcome.result.raw_model_trace_ref
    assert outcome.evaluation_record.task_id == task.task_id
    assert outcome.evaluation_record.result_id == outcome.result.result_id
    assert outcome.evaluation_record.quality_gate_classification == (
        outcome.quality_gate_result.classification
    )
    assert outcome.evaluation_record.trace_metadata == outcome.trace_metadata
    assert outcome.evaluation_record.payload_validation_ok is True


def test_invalid_payload_through_wrapper_becomes_blocking():
    outcome = run_agent_task_with_evaluation(
        make_task(),
        make_contract(),
        MissingPayloadObjectTypeAdapter(),
        adapter_type="fake",
    )

    assert outcome.quality_gate_result.classification == QualityGateClassification.BLOCKING
    assert outcome.quality_gate_result.reasons == ("payload missing object_type",)
    assert outcome.evaluation_record.quality_gate_classification == (
        QualityGateClassification.BLOCKING
    )
    assert outcome.evaluation_record.payload_validation_ok is False
    assert outcome.evaluation_record.payload_validation_reasons == (
        "payload missing object_type",
    )


def test_wrapper_rejects_negative_runtime_counters_before_adapter_call():
    adapter = CountingAdapter()

    with pytest.raises(ValueError, match="retry_count"):
        run_agent_task_with_evaluation(
            make_task(),
            make_contract(),
            adapter,
            adapter_type="fake",
            retry_count=-1,
        )

    with pytest.raises(ValueError, match="duration_ms"):
        run_agent_task_with_evaluation(
            make_task(),
            make_contract(),
            adapter,
            adapter_type="fake",
            duration_ms=-1,
        )

    assert adapter.calls == 0


def test_wrapper_propagates_adapter_errors():
    with pytest.raises(RuntimeError, match="adapter failure"):
        run_agent_task_with_evaluation(
            make_task(),
            make_contract(),
            ExplodingAdapter(),
            adapter_type="failing",
        )


def test_disabled_openai_adapter_raises_before_client_use_through_wrapper():
    client = FailingClient()

    with pytest.raises(OpenAIAdapterDisabledError, match="disabled"):
        run_agent_task_with_evaluation(
            make_task(),
            make_contract(),
            OpenAIAdapter(client=client),
            adapter_type="openai",
        )

    assert client.calls == 0


def test_enabled_openai_adapter_with_mock_client_returns_valid_outcome():
    client = DeterministicMockClient()

    outcome = run_agent_task_with_evaluation(
        make_task(),
        make_contract(),
        OpenAIAdapter(enabled=True, client=client),
        adapter_type="openai",
        retry_count=1,
        duration_ms=12,
    )

    assert outcome.result.created_by == "OpenAIAdapter"
    assert outcome.result.result_id == "MOCK_RESULT_TASK_BATCH_001_026_ROUTING"
    assert outcome.quality_gate_result.classification == QualityGateClassification.OK
    assert outcome.trace_metadata.adapter_type == "openai"
    assert outcome.trace_metadata.retry_count == 1
    assert outcome.trace_metadata.duration_ms == 12
    assert outcome.trace_metadata.raw_trace_ref == (
        "mock_trace:TASK_BATCH_001_026_ROUTING:deterministic"
    )
    assert outcome.evaluation_record.agent_name == "RoutingAgent"
    assert outcome.evaluation_record.payload_validation_ok is True
    assert outcome.evaluation_record.trace_metadata == outcome.trace_metadata
    assert client.calls == [(make_task(), make_contract())]


def test_wrapper_opens_no_files(monkeypatch: pytest.MonkeyPatch):
    def fail_open(*args: object, **kwargs: object) -> None:
        raise AssertionError("execution wrapper must not open files")

    monkeypatch.setattr(builtins, "open", fail_open)
    monkeypatch.setattr(Path, "open", fail_open)

    outcome = run_agent_task_with_evaluation(
        make_task(),
        make_contract(),
        FakeAgentAdapter(),
        adapter_type="fake",
    )

    assert outcome.quality_gate_result.is_ok is True


def test_execution_wrapper_source_has_no_network_or_openai_sdk_imports():
    source = inspect.getsource(execution_module).lower()

    assert "import openai" not in source
    for forbidden in ("requests", "httpx", "urllib", "socket"):
        assert forbidden not in source
