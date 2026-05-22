from __future__ import annotations

from dataclasses import dataclass

from dico_impro.agents import (
    AgentEvaluationRecord,
    AgentRegistry,
    FakeAgentAdapter,
    QualityGateResult,
    run_agent_task_with_evaluation,
)
from dico_impro.contracts import AgentResult, AgentTask, BatchReport, BatchState
from dico_impro.orchestration.batch_summary import build_batch_report, build_batch_state
from dico_impro.orchestration.scope import ExplicitScope
from dico_impro.orchestration.task_builder import (
    DEFAULT_DRY_RUN_AGENT_NAME,
    build_agent_tasks,
    build_dry_run_agent_contract,
)


DRY_RUN_CREATED_BY = "dico_impro.orchestration.dry_run"
DRY_RUN_STEPS_COMPLETED = (
    "explicit_scope_validated",
    "agent_tasks_built",
    "fake_agent_tasks_executed",
    "quality_gates_evaluated",
    "agent_evaluation_records_built",
    "in_memory_report_built",
)
DRY_RUN_SUMMARY_HUMAN = "In-memory dry-run completed for explicit scope only."


@dataclass(frozen=True)
class DryRunResult:
    batch_state: BatchState
    batch_report: BatchReport
    tasks: tuple[AgentTask, ...]
    agent_results: tuple[AgentResult, ...]
    quality_gate_results: tuple[QualityGateResult, ...]
    evaluation_records: tuple[AgentEvaluationRecord, ...]


def build_default_registry() -> AgentRegistry:
    registry = AgentRegistry()
    registry.register(
        build_dry_run_agent_contract(),
        adapter_type="fake",
        expected_schema="RoutingDecision",
        max_retries=0,
    )
    return registry


def run_dry_run(
    scope: ExplicitScope,
    *,
    registry: AgentRegistry | None = None,
    adapter: FakeAgentAdapter | None = None,
    created_at: str | None = None,
) -> DryRunResult:
    if not isinstance(scope, ExplicitScope):
        raise TypeError("run_dry_run requires an ExplicitScope")

    resolved_registry = registry or build_default_registry()
    resolved_adapter = adapter or FakeAgentAdapter()
    if not isinstance(resolved_adapter, FakeAgentAdapter):
        raise TypeError("dry-run orchestration only supports FakeAgentAdapter")

    tasks = build_agent_tasks(scope, resolved_registry, agent_name=DEFAULT_DRY_RUN_AGENT_NAME)
    results: list[AgentResult] = []
    gate_results: list[QualityGateResult] = []
    evaluation_records: list[AgentEvaluationRecord] = []

    for task in tasks:
        registered = resolved_registry.get(task.agent_name)
        contract = resolved_registry.validate_task(task)
        outcome = run_agent_task_with_evaluation(
            task,
            contract,
            resolved_adapter,
            adapter_type=registered.adapter_type,
            duration_ms=0,
            retry_count=0,
        )
        results.append(outcome.result)
        gate_results.append(outcome.quality_gate_result)
        evaluation_records.append(outcome.evaluation_record)

    gate_results_tuple = tuple(gate_results)
    batch_state = build_batch_state(
        scope,
        gate_results_tuple,
        created_by=DRY_RUN_CREATED_BY,
        steps_completed=DRY_RUN_STEPS_COMPLETED,
        created_at=created_at,
    )
    batch_report = build_batch_report(
        scope,
        gate_results_tuple,
        created_by=DRY_RUN_CREATED_BY,
        summary_human=DRY_RUN_SUMMARY_HUMAN,
    )

    return DryRunResult(
        batch_state=batch_state,
        batch_report=batch_report,
        tasks=tasks,
        agent_results=tuple(results),
        quality_gate_results=gate_results_tuple,
        evaluation_records=tuple(evaluation_records),
    )


__all__ = ["DryRunResult", "build_default_registry", "run_dry_run"]
