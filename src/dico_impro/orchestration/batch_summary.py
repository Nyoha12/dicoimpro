from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone

from dico_impro.agents import QualityGateClassification, QualityGateResult
from dico_impro.contracts import BatchReport, BatchState, BatchStatus
from dico_impro.contracts.common import SCHEMA_VERSION
from dico_impro.orchestration.scope import ExplicitScope


def build_batch_state(
    scope: ExplicitScope,
    gate_results: tuple[QualityGateResult, ...],
    *,
    created_by: str,
    steps_completed: Sequence[str],
    created_at: str | None = None,
) -> BatchState:
    return BatchState.model_validate(
        {
            "object_type": "BatchState",
            "schema_version": SCHEMA_VERSION,
            "created_by": created_by,
            "batch_id": scope.batch_id,
            "created_at": created_at or _utc_timestamp(),
            "status": _status_for(gate_results),
            "steps_completed": list(steps_completed),
            "entries_scope": scope.entry_ids,
            "artifacts": [],
            "errors_recoverable": _reasons_for(
                gate_results, QualityGateClassification.RECOVERABLE
            ),
            "errors_blocking": _reasons_for(gate_results, QualityGateClassification.BLOCKING),
            "replay_command": None,
        }
    )


def build_batch_report(
    scope: ExplicitScope,
    gate_results: tuple[QualityGateResult, ...],
    *,
    created_by: str,
    summary_human: str,
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
            "created_by": created_by,
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
            "summary_human": summary_human,
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


__all__ = ["build_batch_report", "build_batch_state"]
