from __future__ import annotations

from dataclasses import dataclass

from dico_impro.agents.adapters.base import AgentAdapter
from dico_impro.agents.evaluation import AgentEvaluationRecord, build_agent_evaluation_record
from dico_impro.agents.quality_gates import QualityGateResult, evaluate_agent_result
from dico_impro.agents.tracing import AgentTraceMetadata, build_agent_trace_metadata
from dico_impro.contracts import AgentContract, AgentResult, AgentTask


@dataclass(frozen=True)
class AgentExecutionOutcome:
    task: AgentTask
    result: AgentResult
    quality_gate_result: QualityGateResult
    trace_metadata: AgentTraceMetadata
    evaluation_record: AgentEvaluationRecord


def run_agent_task_with_evaluation(
    task: AgentTask,
    contract: AgentContract,
    adapter: AgentAdapter,
    adapter_type: str,
    *,
    retry_count: int = 0,
    duration_ms: int = 0,
) -> AgentExecutionOutcome:
    if retry_count < 0:
        raise ValueError("retry_count cannot be negative")
    if duration_ms < 0:
        raise ValueError("duration_ms cannot be negative")

    result = adapter.run_task(task, contract)
    quality_gate_result = evaluate_agent_result(result)
    trace_metadata = build_agent_trace_metadata(
        task,
        result,
        contract,
        adapter_type=adapter_type,
        duration_ms=duration_ms,
        retry_count=retry_count,
    )
    evaluation_record = build_agent_evaluation_record(
        task,
        result,
        quality_gate_result,
        trace_metadata,
    )

    return AgentExecutionOutcome(
        task=task,
        result=result,
        quality_gate_result=quality_gate_result,
        trace_metadata=trace_metadata,
        evaluation_record=evaluation_record,
    )


__all__ = ["AgentExecutionOutcome", "run_agent_task_with_evaluation"]
