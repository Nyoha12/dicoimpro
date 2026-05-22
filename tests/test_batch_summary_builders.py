from __future__ import annotations

from dico_impro.agents import QualityGateClassification, QualityGateResult
from dico_impro.contracts import AgentContract, AgentTask, BatchStatus
from dico_impro.contracts.common import SCHEMA_VERSION
from dico_impro.orchestration import (
    ExplicitScope,
    build_batch_report,
    build_batch_state,
    plan_batch_with_mock_openai,
    run_dry_run,
)


CREATED_AT = "2026-05-21T00:00:00Z"
CREATED_BY = "tests.batch_summary"
STEPS_COMPLETED = ("scope_validated", "report_built")
SUMMARY_HUMAN = "Batch summary builder test."


def make_scope(entry_count: int = 2, *, batch_id: str = "BATCH_SUMMARY") -> ExplicitScope:
    return ExplicitScope.model_validate(
        {
            "batch_id": batch_id,
            "entries": [
                {"id_entree_original": f"{index:03d}", "titre_original_exact": f"Entry {index}"}
                for index in range(1, entry_count + 1)
            ],
        }
    )


def make_dry_run_scope() -> ExplicitScope:
    return ExplicitScope.model_validate(
        {
            "batch_id": "BATCH_DRY_RUN_SUMMARY",
            "entries": [
                {
                    "id_entree_original": "026",
                    "titre_original_exact": "Clean",
                    "fake_scenario": "success_valid",
                },
                {
                    "id_entree_original": "031",
                    "titre_original_exact": "Recoverable",
                    "fake_scenario": "schema_invalid",
                },
                {
                    "id_entree_original": "044",
                    "titre_original_exact": "Prudence",
                    "fake_scenario": "run_002_required",
                },
            ],
        }
    )


def build_state_and_report(
    gate_results: tuple[QualityGateResult, ...],
    *,
    scope: ExplicitScope | None = None,
) -> tuple[object, object]:
    resolved_scope = scope or make_scope(len(gate_results))
    state = build_batch_state(
        resolved_scope,
        gate_results,
        created_by=CREATED_BY,
        steps_completed=STEPS_COMPLETED,
        created_at=CREATED_AT,
    )
    report = build_batch_report(
        resolved_scope,
        gate_results,
        created_by=CREATED_BY,
        summary_human=SUMMARY_HUMAN,
    )
    return state, report


def test_shared_builders_create_completed_clean_state_and_report():
    state, report = build_state_and_report(
        (
            QualityGateResult(QualityGateClassification.OK),
            QualityGateResult(QualityGateClassification.OK),
        )
    )

    assert state.status == BatchStatus.COMPLETED_CLEAN
    assert state.created_by == CREATED_BY
    assert state.steps_completed == list(STEPS_COMPLETED)
    assert state.errors_recoverable == []
    assert state.errors_blocking == []
    assert state.artifacts == []
    assert state.replay_command is None
    assert report.entries_total == 2
    assert report.entries_processed == 2
    assert report.entries_skipped == 0
    assert report.entries_blocked == 0
    assert report.run_002_requested == 0
    assert report.publication_blocked == 0
    assert report.audit_queue_count == 0
    assert report.journal_patch_id is None
    assert report.artifacts == []
    assert report.warnings == []


def test_shared_builders_create_failed_blocking_state_and_report():
    state, report = build_state_and_report(
        (
            QualityGateResult(QualityGateClassification.OK),
            QualityGateResult(QualityGateClassification.BLOCKING, ("publication_blocking",)),
        )
    )

    assert state.status == BatchStatus.FAILED_BLOCKING
    assert state.errors_recoverable == []
    assert state.errors_blocking == ["publication_blocking"]
    assert report.entries_total == 2
    assert report.entries_processed == 1
    assert report.entries_skipped == 0
    assert report.entries_blocked == 1
    assert report.publication_blocked == 1
    assert report.audit_queue_count == 1


def test_shared_builders_create_failed_recoverable_state_and_report():
    state, report = build_state_and_report(
        (
            QualityGateResult(QualityGateClassification.OK),
            QualityGateResult(QualityGateClassification.RECOVERABLE, ("schema_invalid",)),
        )
    )

    assert state.status == BatchStatus.FAILED_RECOVERABLE
    assert state.errors_recoverable == ["schema_invalid"]
    assert state.errors_blocking == []
    assert report.entries_total == 2
    assert report.entries_processed == 1
    assert report.entries_skipped == 1
    assert report.entries_blocked == 0
    assert report.audit_queue_count == 1


def test_shared_builders_create_completed_with_warnings_state_and_report():
    state, report = build_state_and_report(
        (
            QualityGateResult(QualityGateClassification.OK),
            QualityGateResult(QualityGateClassification.PRUDENCE, ("run_002_required",)),
        )
    )

    assert state.status == BatchStatus.COMPLETED_WITH_WARNINGS
    assert state.errors_recoverable == []
    assert state.errors_blocking == []
    assert report.entries_total == 2
    assert report.entries_processed == 2
    assert report.entries_skipped == 0
    assert report.entries_blocked == 0
    assert report.run_002_requested == 1
    assert report.audit_queue_count == 1
    assert report.warnings == ["run_002_required"]


def test_shared_builders_count_run_002_and_publication_blocked_reasons():
    _, report = build_state_and_report(
        (
            QualityGateResult(QualityGateClassification.PRUDENCE, ("run_002_required",)),
            QualityGateResult(
                QualityGateClassification.PRUDENCE,
                ("run_002_required", "warning"),
            ),
            QualityGateResult(QualityGateClassification.BLOCKING, ("publication_blocking",)),
            QualityGateResult(QualityGateClassification.BLOCKING, ("publication_blocked",)),
        ),
        scope=make_scope(4),
    )

    assert report.entries_total == 4
    assert report.entries_processed == 2
    assert report.entries_skipped == 0
    assert report.entries_blocked == 2
    assert report.run_002_requested == 2
    assert report.publication_blocked == 2
    assert report.audit_queue_count == 4
    assert report.warnings == ["run_002_required", "run_002_required", "warning"]


def test_dry_run_batch_summary_output_unchanged_for_representative_scope():
    result = run_dry_run(make_dry_run_scope(), created_at=CREATED_AT)

    assert result.batch_state.status == BatchStatus.FAILED_RECOVERABLE
    assert result.batch_state.created_by == "dico_impro.orchestration.dry_run"
    assert result.batch_state.steps_completed == [
        "explicit_scope_validated",
        "agent_tasks_built",
        "fake_agent_tasks_executed",
        "quality_gates_evaluated",
        "agent_evaluation_records_built",
        "in_memory_report_built",
    ]
    assert result.batch_report.created_by == "dico_impro.orchestration.dry_run"
    assert result.batch_report.entries_total == 3
    assert result.batch_report.entries_processed == 2
    assert result.batch_report.entries_skipped == 1
    assert result.batch_report.entries_blocked == 0
    assert result.batch_report.run_002_requested == 1
    assert result.batch_report.publication_blocked == 0
    assert result.batch_report.audit_queue_count == 2


def test_mock_openai_batch_summary_output_unchanged_for_representative_scope():
    result = plan_batch_with_mock_openai(
        make_scope(3, batch_id="BATCH_MOCK_SUMMARY"),
        DeterministicMockOpenAIClient(
            valid_payload(),
            typed_payload("schema_invalid"),
            typed_payload("run_002_required"),
        ),
        created_at=CREATED_AT,
    )

    assert result.batch_state.status == BatchStatus.FAILED_RECOVERABLE
    assert result.batch_state.created_by == "dico_impro.orchestration.mock_openai_plan"
    assert result.batch_state.steps_completed == [
        "explicit_scope_validated",
        "mock_openai_planning_registry_built",
        "agent_tasks_built",
        "mock_openai_agent_tasks_executed",
        "quality_gates_evaluated",
        "agent_evaluation_records_built",
        "in_memory_report_built",
    ]
    assert result.batch_report.created_by == "dico_impro.orchestration.mock_openai_plan"
    assert result.batch_report.entries_total == 3
    assert result.batch_report.entries_processed == 2
    assert result.batch_report.entries_skipped == 1
    assert result.batch_report.entries_blocked == 0
    assert result.batch_report.run_002_requested == 1
    assert result.batch_report.publication_blocked == 0
    assert result.batch_report.audit_queue_count == 2


def valid_payload() -> dict[str, object]:
    return {
        "object_type": "RoutingDecision",
        "schema_version": SCHEMA_VERSION,
        "scenario": "success_valid",
        "status": "ok",
    }


def typed_payload(error_type: str) -> dict[str, object]:
    return {
        "object_type": "RoutingDecision",
        "schema_version": SCHEMA_VERSION,
        "scenario": error_type,
        "status": "error",
        "error_type": error_type,
    }


class DeterministicMockOpenAIClient:
    def __init__(self, *payloads: dict[str, object]) -> None:
        self.payloads = list(payloads) or [valid_payload()]
        self.calls: list[tuple[AgentTask, AgentContract]] = []

    def run_task(self, *, task: AgentTask, contract: AgentContract) -> dict[str, object]:
        self.calls.append((task, contract))
        payload_index = min(len(self.calls) - 1, len(self.payloads) - 1)
        return {
            "result_id": f"MOCK_OPENAI_RESULT_{task.task_id}",
            "payload": dict(self.payloads[payload_index]),
            "warnings": [],
            "audit_notes": [],
            "raw_model_trace_ref": f"mock_openai_trace:{task.task_id}:{payload_index}",
            "validation_status": "schema_valid",
        }
