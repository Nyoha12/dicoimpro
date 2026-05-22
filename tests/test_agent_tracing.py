from __future__ import annotations

import builtins
from pathlib import Path

import pytest

from dico_impro.agents import (
    AgentTraceMetadata,
    FakeAgentAdapter,
    build_agent_trace_metadata,
    canonical_payload_hash,
)
from dico_impro.contracts import AgentContract, AgentResult, AgentTask


def make_contract() -> AgentContract:
    return AgentContract.model_validate(
        {
            "object_type": "AgentContract",
            "schema_version": "v0.2.3-auto",
            "created_by": "tests",
            "agent_name": "RoutingAgent",
            "agent_version": "v0.2.3-auto",
            "mission": "Produce a bounded local test object.",
            "allowed_inputs": ["EntryState"],
            "required_output_schema": "RoutingDecision",
            "forbidden_actions": ["write_active_journal", "launch_RUN"],
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
            "forbidden_files": ["legacy_pdf", "active_journal"],
            "expected_schema": "RoutingDecision",
        }
    )


def make_result(
    task: AgentTask,
    contract: AgentContract,
    payload: dict[str, object] | None = None,
) -> AgentResult:
    result = FakeAgentAdapter().run_task(task, contract)
    if payload is None:
        return result
    return AgentResult.model_validate({**result.model_dump(), "payload": payload})


def make_trace(
    task: AgentTask | None = None,
    result: AgentResult | None = None,
) -> AgentTraceMetadata:
    contract = make_contract()
    resolved_task = task or make_task()
    resolved_result = result or make_result(resolved_task, contract)
    return build_agent_trace_metadata(
        resolved_task,
        resolved_result,
        contract,
        adapter_type="fake",
        duration_ms=0,
        retry_count=0,
    )


def test_canonical_payload_hash_is_stable_for_equivalent_json_payloads():
    left = {"b": [2, {"y": "yes", "x": "ex"}], "a": 1}
    right = {"a": 1, "b": [2, {"x": "ex", "y": "yes"}]}

    assert canonical_payload_hash(left) == canonical_payload_hash(right)


def test_same_task_and_result_produce_same_trace_hashes_across_calls():
    task = make_task()
    contract = make_contract()
    result = make_result(task, contract)

    first = make_trace(task, result)
    second = make_trace(task, result)

    assert first == second
    assert first.input_hash == second.input_hash
    assert first.output_hash == second.output_hash
    assert len(first.input_hash) == 64
    assert len(first.output_hash) == 64


def test_changing_input_payload_changes_input_hash_only():
    original_task = make_task({"fake_scenario": "success_valid", "entry": "026"})
    changed_task = make_task({"fake_scenario": "success_valid", "entry": "031"})
    contract = make_contract()
    original_result = make_result(original_task, contract)
    changed_result = AgentResult.model_validate(
        {**original_result.model_dump(), "task_id": changed_task.task_id}
    )

    original = make_trace(original_task, original_result)
    changed = make_trace(changed_task, changed_result)

    assert original.input_hash != changed.input_hash
    assert original.output_hash == changed.output_hash


def test_changing_result_payload_changes_output_hash_only():
    task = make_task()
    contract = make_contract()
    original_result = make_result(task, contract)
    changed_payload = {**original_result.payload, "status": "changed"}
    changed_result = make_result(task, contract, changed_payload)

    original = make_trace(task, original_result)
    changed = make_trace(task, changed_result)

    assert original.input_hash == changed.input_hash
    assert original.output_hash != changed.output_hash


def test_fake_trace_metadata_surfaces_adapter_runtime_and_trace_ref():
    task = make_task()
    contract = make_contract()
    result = make_result(task, contract)

    trace = make_trace(task, result)

    assert trace.task_id == task.task_id
    assert trace.result_id == result.result_id
    assert trace.agent_name == result.agent_name
    assert trace.agent_version == contract.agent_version
    assert trace.adapter_type == "fake"
    assert trace.contract_version == contract.schema_version
    assert trace.retry_count == 0
    assert trace.duration_ms == 0
    assert trace.raw_trace_ref == result.raw_model_trace_ref


def test_trace_metadata_does_not_open_files(monkeypatch: pytest.MonkeyPatch):
    def fail_open(*args: object, **kwargs: object) -> None:
        raise AssertionError("trace metadata must not open files")

    monkeypatch.setattr(builtins, "open", fail_open)
    monkeypatch.setattr(Path, "open", fail_open)

    trace = make_trace()

    assert trace.adapter_type == "fake"
