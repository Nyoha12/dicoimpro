from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from dico_impro.agents import (
    AgentEvaluationRecord,
    AgentRegistry,
    FakeAgentAdapter,
    QualityGateClassification,
    QualityGateResult,
    build_agent_evaluation_record,
    build_agent_trace_metadata,
    evaluate_agent_result,
)
from dico_impro.contracts import AgentResult, AgentTask, BatchReport, BatchState, BatchStatus
from dico_impro.contracts.common import SCHEMA_VERSION
from dico_impro.orchestration.scope import ExplicitScope
from dico_impro.orchestration.task_builder import (
    DEFAULT_DRY_RUN_AGENT_NAME,
    build_agent_tasks,
    build_dry_run_agent_contract,
)


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
        result = resolved_adapter.run_task(task, contract)
        gate_result = evaluate_agent_result(result)
        trace_metadata = build_agent_trace_metadata(
            task,
            result,
            contract,
            adapter_type=registered.adapter_type,
            duration_ms=0,
            retry_count=0,
        )
        results.append(result)
        gate_results.append(gate_result)
        evaluation_records.append(
            build_agent_evaluation_record(task, result, gate_result, trace_metadata)
        )

    batch_state = _build_batch_state(scope, tuple(gate_results), created_at=created_at)
    batch_report = _build_batch_report(scope, tuple(gate_results))

    return DryRunResult(
        batch_state=batch_state,
        batch_report=batch_report,
        tasks=tasks,
        agent_results=tuple(results),
        quality_gate_results=tuple(gate_results),
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
            "created_by": "dico_impro.orchestration.dry_run",
            "batch_id": scope.batch_id,
            "created_at": created_at or _utc_timestamp(),
            "status": _status_for(gate_results),
            "steps_completed": [
                "explicit_scope_validated",
                "agent_tasks_built",
                "fake_agent_tasks_executed",
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
            "created_by": "dico_impro.orchestration.dry_run",
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
            "summary_human": "In-memory dry-run completed for explicit scope only.",
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


__all__ = ["DryRunResult", "build_default_registry", "run_dry_run"]
