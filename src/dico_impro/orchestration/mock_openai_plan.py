from __future__ import annotations

from dico_impro.agents import (
    AgentEvaluationRecord,
    AgentRegistry,
    OpenAIAdapter,
    QualityGateResult,
    run_agent_task_with_evaluation,
)
from dico_impro.contracts import AgentResult
from dico_impro.orchestration.batch_summary import build_batch_report, build_batch_state
from dico_impro.orchestration.dry_run import DryRunResult
from dico_impro.orchestration.scope import ExplicitScope
from dico_impro.orchestration.task_builder import (
    DEFAULT_DRY_RUN_AGENT_NAME,
    DEFAULT_DRY_RUN_OUTPUT_SCHEMA,
    build_agent_tasks,
    build_dry_run_agent_contract,
)


MOCK_OPENAI_CREATED_BY = "dico_impro.orchestration.mock_openai_plan"
MOCK_OPENAI_STEPS_COMPLETED = (
    "explicit_scope_validated",
    "mock_openai_planning_registry_built",
    "agent_tasks_built",
    "mock_openai_agent_tasks_executed",
    "quality_gates_evaluated",
    "agent_evaluation_records_built",
    "in_memory_report_built",
)
MOCK_OPENAI_SUMMARY_HUMAN = (
    "Mock OpenAI in-memory planning completed for explicit scope only."
)


def build_mock_openai_planning_registry() -> AgentRegistry:
    registry = AgentRegistry()
    registry.register(
        build_dry_run_agent_contract(),
        adapter_type="openai",
        expected_schema=DEFAULT_DRY_RUN_OUTPUT_SCHEMA,
        max_retries=0,
    )
    return registry


def plan_batch_with_mock_openai(
    scope: ExplicitScope,
    client: object,
    *,
    created_at: str | None = None,
) -> DryRunResult:
    if not isinstance(scope, ExplicitScope):
        raise TypeError("plan_batch_with_mock_openai requires an ExplicitScope")
    if client is None:
        raise TypeError("plan_batch_with_mock_openai requires an injected client")

    registry = build_mock_openai_planning_registry()
    adapter = OpenAIAdapter(enabled=True, client=client)
    tasks = build_agent_tasks(scope, registry, agent_name=DEFAULT_DRY_RUN_AGENT_NAME)

    results: list[AgentResult] = []
    gate_results: list[QualityGateResult] = []
    evaluation_records: list[AgentEvaluationRecord] = []

    for task in tasks:
        registered = registry.get(task.agent_name)
        contract = registry.validate_task(task)
        outcome = run_agent_task_with_evaluation(
            task,
            contract,
            adapter,
            adapter_type=registered.adapter_type,
            duration_ms=0,
            retry_count=0,
        )
        results.append(outcome.result)
        gate_results.append(outcome.quality_gate_result)
        evaluation_records.append(outcome.evaluation_record)

    gate_results_tuple = tuple(gate_results)
    return DryRunResult(
        batch_state=build_batch_state(
            scope,
            gate_results_tuple,
            created_by=MOCK_OPENAI_CREATED_BY,
            steps_completed=MOCK_OPENAI_STEPS_COMPLETED,
            created_at=created_at,
        ),
        batch_report=build_batch_report(
            scope,
            gate_results_tuple,
            created_by=MOCK_OPENAI_CREATED_BY,
            summary_human=MOCK_OPENAI_SUMMARY_HUMAN,
        ),
        tasks=tasks,
        agent_results=tuple(results),
        quality_gate_results=gate_results_tuple,
        evaluation_records=tuple(evaluation_records),
    )


__all__ = ["build_mock_openai_planning_registry", "plan_batch_with_mock_openai"]
