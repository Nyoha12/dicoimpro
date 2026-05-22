from __future__ import annotations

from dataclasses import dataclass

from dico_impro.agents.payload_validation import validate_agent_result_payload
from dico_impro.agents.quality_gates import QualityGateClassification, QualityGateResult
from dico_impro.contracts import AgentResult, AgentTask, ValidationStatus


@dataclass(frozen=True)
class AgentEvaluationRecord:
    id_entree_original: str | None
    task_id: str
    result_id: str
    agent_name: str
    schema_name: str
    validation_status: ValidationStatus
    quality_gate_classification: QualityGateClassification
    quality_gate_reasons: tuple[str, ...]
    payload_validation_ok: bool
    payload_validation_reasons: tuple[str, ...]


def build_agent_evaluation_record(
    task: AgentTask,
    result: AgentResult,
    quality_gate_result: QualityGateResult,
) -> AgentEvaluationRecord:
    if task.task_id != result.task_id:
        raise ValueError("task/result task_id mismatch")

    payload_validation = validate_agent_result_payload(result)
    return AgentEvaluationRecord(
        id_entree_original=task.id_entree_original,
        task_id=task.task_id,
        result_id=result.result_id,
        agent_name=result.agent_name,
        schema_name=result.schema_name,
        validation_status=result.validation_status,
        quality_gate_classification=quality_gate_result.classification,
        quality_gate_reasons=tuple(quality_gate_result.reasons),
        payload_validation_ok=payload_validation.ok,
        payload_validation_reasons=payload_validation.reasons,
    )


__all__ = ["AgentEvaluationRecord", "build_agent_evaluation_record"]
