from __future__ import annotations

import inspect

from dico_impro.agents import AgentEvaluationRecord, QualityGateClassification
import dico_impro.agents.evaluation as evaluation_module
import dico_impro.agents.payload_validation as payload_validation_module
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


def test_evaluation_modules_have_no_openai_or_network_integration():
    source = "\n".join(
        [
            inspect.getsource(payload_validation_module),
            inspect.getsource(evaluation_module),
            inspect.getsource(dry_run_module),
        ]
    )
    lowered_source = source.lower()

    for forbidden in ("openai", "requests", "httpx", "urllib", "socket"):
        assert forbidden not in lowered_source
