from __future__ import annotations

from datetime import datetime, timezone

from dico_impro.agents import (
    AgentEvaluationRecord,
    AgentRegistry,
    OpenAIAdapter,
    QualityGateClassification,
    QualityGateResult,
    run_agent_task_with_evaluation,
)
from dico_impro.contracts import AgentResult, BatchReport, BatchState, BatchStatus
from dico_impro.contracts.common import SCHEMA_VERSION
from dico_impro.orchestration.dry_run import DryRunResult
from dico_impro.orchestration.scope import ExplicitScope
from dico_impro.orchestration.task_builder import (
    DEFAULT_DRY_RUN_AGENT_NAME,
    DEFAULT_DRY_RUN_OUTPUT_SCHEMA,
    build_agent_tasks,
    build_dry_run_agent_contract,
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
        batch_state=_build_batch_state(scope, gate_results_tuple, created_at=created_at),
        batch_report=_build_batch_report(scope, gate_results_tuple),
        tasks=tasks,
        agent_results=tuple(results),
        quality_gate_results=gate_results_tuple,
        evaluation_records=tuple(evaluation_records),
    )


def _build_batch_state(
    scope: ExplicitScope,
    gate_results: tuple[QualityGateResult, ...],
    *,
    created_at: str | None,
) -> BatchState:
    return BatchState.model_validate(
        {
            "object_type": "BatchState",
            "schema_version": SCHEMA_VERSION,
            "created_by": "dico_impro.orchestration.mock_openai_plan",
            "batch_id": scope.batch_id,
            "created_at": created_at or _utc_timestamp(),
            "status": _status_for(gate_results),
            "steps_completed": [
                "explicit_scope_validated",
                "mock_openai_planning_registry_built",
                "agent_tasks_built",
                "mock_openai_agent_tasks_executed",
                "quality_gates_evaluated",
                "agent_evaluation_records_built",
                "in_memory_report_built",
            ],
            "entries_scope": scope.entry_ids,
            "artifacts": [],
            "errors_recoverable": _reasons_for(
                gate_results, QualityGateClassification.RECOVERABLE
            ),
            "errors_blocking": _reasons_for(gate_results, QualityGateClassification.BLOCKING),
            "replay_command": None,
        }
    )


def _build_batch_report(
    scope: ExplicitScope,
    gate_results: tuple[QualityGateResult, ...],
) -> BatchReport:
    entries_blocked = _count(gate_results, QualityGateClassification.BLOCKING)
    entries_skipped = _count(gate_results, QualityGateClassification.RECOVERABLE)
    entries_processed = len(gate_results) - entries_blocked - entries_skipped
    run_002_requested = sum(
        1 for gate_result in gate_results if "run_002_required" in gate_result.reasons
    )
    publication_blocked = sum(
        1
        for gate_result in gate_results
        if "publication_blocking" in gate_result.reasons
        or "publication_blocked" in gate_result.reasons
    )
    audit_queue_count = sum(
        1
        for gate_result in gate_results
        if gate_result.classification
        in {
            QualityGateClassification.PRUDENCE,
            QualityGateClassification.RECOVERABLE,
            QualityGateClassification.BLOCKING,
        }
    )

    return BatchReport.model_validate(
        {
            "object_type": "BatchReport",
            "schema_version": SCHEMA_VERSION,
            "created_by": "dico_impro.orchestration.mock_openai_plan",
            "batch_id": scope.batch_id,
            "protocol_version": "v0.2.3",
            "automation_layer": SCHEMA_VERSION,
            "entries_total": len(scope.entries),
            "entries_processed": entries_processed,
            "entries_skipped": entries_skipped,
            "entries_blocked": entries_blocked,
            "run_002_requested": run_002_requested,
            "publication_blocked": publication_blocked,
            "audit_queue_count": audit_queue_count,
            "journal_patch_id": None,
            "artifacts": [],
            "summary_human": "Mock OpenAI in-memory planning completed for explicit scope only.",
            "warnings": _report_warnings(gate_results),
        }
    )


def _status_for(gate_results: tuple[QualityGateResult, ...]) -> BatchStatus:
    classifications = {gate_result.classification for gate_result in gate_results}
    if QualityGateClassification.BLOCKING in classifications:
        return BatchStatus.FAILED_BLOCKING
    if QualityGateClassification.RECOVERABLE in classifications:
        return BatchStatus.FAILED_RECOVERABLE
    if QualityGateClassification.PRUDENCE in classifications:
        return BatchStatus.COMPLETED_WITH_WARNINGS
    return BatchStatus.COMPLETED_CLEAN


def _count(
    gate_results: tuple[QualityGateResult, ...],
    classification: QualityGateClassification,
) -> int:
    return sum(1 for gate_result in gate_results if gate_result.classification == classification)


def _reasons_for(
    gate_results: tuple[QualityGateResult, ...],
    classification: QualityGateClassification,
) -> list[str]:
    reasons: list[str] = []
    for gate_result in gate_results:
        if gate_result.classification == classification:
            reasons.extend(gate_result.reasons)
    return reasons


def _report_warnings(gate_results: tuple[QualityGateResult, ...]) -> list[str]:
    warnings: list[str] = []
    for gate_result in gate_results:
        if gate_result.classification == QualityGateClassification.PRUDENCE:
            warnings.extend(gate_result.reasons or ("prudence",))
    return warnings


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


__all__ = ["build_mock_openai_planning_registry", "plan_batch_with_mock_openai"]
