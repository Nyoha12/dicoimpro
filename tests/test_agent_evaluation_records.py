from __future__ import annotations

import inspect

from dico_impro.agents import AgentEvaluationRecord, FakeAgentAdapter, QualityGateClassification
import dico_impro.agents.evaluation as evaluation_module
import dico_impro.agents.payload_validation as payload_validation_module
import dico_impro.agents.tracing as tracing_module
from dico_impro.orchestration import ExplicitScope, run_dry_run
import dico_impro.orchestration.dry_run as dry_run_module


def make_scope() -> ExplicitScope:
    return ExplicitScope.model_validate(
        {
            "batch_id": "BATCH_EVALUATION",
            "entries": [
                {"id_entree_original": "026", "titre_original_exact": "First"},
                {
                    "id_entree_original": "031",
                    "titre_original_exact": "Second",
                    "fake_scenario": "run_002_required",
                },
            ],
        }
    )


def test_dry_run_produces_one_evaluation_record_per_explicit_scope_entry():
    result = run_dry_run(make_scope(), created_at="2026-05-21T00:00:00Z")

    assert len(result.evaluation_records) == len(result.tasks) == 2
    assert all(isinstance(record, AgentEvaluationRecord) for record in result.evaluation_records)
    assert [record.id_entree_original for record in result.evaluation_records] == ["026", "031"]
    assert [record.task_id for record in result.evaluation_records] == [
        result.tasks[0].task_id,
        result.tasks[1].task_id,
    ]
    assert [record.result_id for record in result.evaluation_records] == [
        result.agent_results[0].result_id,
        result.agent_results[1].result_id,
    ]
    assert all(record.trace_metadata is not None for record in result.evaluation_records)


def test_evaluation_records_include_quality_gate_classification_and_payload_validation():
    result = run_dry_run(make_scope(), created_at="2026-05-21T00:00:00Z")

    first, second = result.evaluation_records

    assert first.id_entree_original == "026"
    assert first.quality_gate_classification == QualityGateClassification.OK
    assert first.quality_gate_reasons == ()
    assert first.payload_validation_ok is True
    assert first.payload_validation_reasons == ()

    assert second.id_entree_original == "031"
    assert second.quality_gate_classification == QualityGateClassification.PRUDENCE
    assert second.quality_gate_reasons == ("run_002_required",)
    assert second.payload_validation_ok is True
    assert second.payload_validation_reasons == ()


def test_evaluation_records_include_one_fake_trace_metadata_object_each():
    result = run_dry_run(make_scope(), created_at="2026-05-21T00:00:00Z")

    for record, task, agent_result in zip(
        result.evaluation_records,
        result.tasks,
        result.agent_results,
        strict=True,
    ):
        trace = record.trace_metadata
        assert trace.task_id == task.task_id
        assert trace.result_id == agent_result.result_id
        assert trace.agent_name == agent_result.agent_name
        assert trace.adapter_type == "fake"
        assert trace.retry_count == 0
        assert trace.duration_ms >= 0
        assert trace.raw_trace_ref == agent_result.raw_model_trace_ref
        assert len(trace.input_hash) == 64
        assert len(trace.output_hash) == 64


def test_evaluation_record_classification_is_blocking_when_payload_validation_fails():
    class MissingPayloadObjectTypeAdapter(FakeAgentAdapter):
        def run_task(self, task, contract):
            result = super().run_task(task, contract)
            payload = dict(result.payload)
            payload.pop("object_type")
            return type(result).model_validate({**result.model_dump(), "payload": payload})

    scope = ExplicitScope.model_validate(
        {
            "batch_id": "BATCH_EVALUATION_INVALID",
            "entries": [{"id_entree_original": "026", "titre_original_exact": "First"}],
        }
    )

    result = run_dry_run(
        scope,
        adapter=MissingPayloadObjectTypeAdapter(),
        created_at="2026-05-21T00:00:00Z",
    )

    record = result.evaluation_records[0]
    assert record.quality_gate_classification == QualityGateClassification.BLOCKING
    assert record.quality_gate_reasons == ("payload missing object_type",)
    assert record.payload_validation_ok is False
    assert record.payload_validation_reasons == ("payload missing object_type",)


def test_evaluation_modules_have_no_openai_or_network_integration():
    source = "\n".join(
        [
            inspect.getsource(payload_validation_module),
            inspect.getsource(evaluation_module),
            inspect.getsource(tracing_module),
            inspect.getsource(dry_run_module),
        ]
    )
    lowered_source = source.lower()

    for forbidden in ("openai", "requests", "httpx", "urllib", "socket"):
        assert forbidden not in lowered_source
