import pytest
from pydantic import ValidationError

from dico_impro.contracts import BatchReport, BatchState, BatchStatus


def valid_batch_state_data() -> dict[str, object]:
    return {
        "created_by": "tests",
        "batch_id": "BATCH_001",
        "created_at": "2026-05-21T00:00:00Z",
        "status": BatchStatus.PLANNED,
        "steps_completed": [],
        "entries_scope": ["026"],
        "artifacts": [],
        "errors_recoverable": [],
        "errors_blocking": [],
        "replay_command": None,
    }


def valid_batch_report_data() -> dict[str, object]:
    return {
        "created_by": "tests",
        "batch_id": "BATCH_001",
        "protocol_version": "v0.2.3",
        "automation_layer": "v0.2.3-auto",
        "entries_total": 1,
        "entries_processed": 1,
        "entries_skipped": 0,
        "entries_blocked": 0,
        "run_002_requested": 0,
        "publication_blocked": 0,
        "audit_queue_count": 0,
        "journal_patch_id": None,
        "artifacts": ["master.json"],
        "summary_human": "Batch report for contract tests.",
        "warnings": [],
    }


def test_valid_batch_state_is_accepted():
    state = BatchState.model_validate(valid_batch_state_data())

    assert state.object_type == "BatchState"
    assert state.schema_version == "v0.2.3-auto"
    assert state.status == BatchStatus.PLANNED


def test_valid_batch_report_is_accepted():
    report = BatchReport.model_validate(valid_batch_report_data())

    assert report.object_type == "BatchReport"
    assert report.batch_id == "BATCH_001"
    assert report.entries_total == 1


def test_batch_state_rejects_missing_required_field():
    data = valid_batch_state_data()
    data.pop("created_at")

    with pytest.raises(ValidationError):
        BatchState.model_validate(data)


def test_batch_state_rejects_extra_field():
    data = valid_batch_state_data()
    data["extra"] = "forbidden"

    with pytest.raises(ValidationError):
        BatchState.model_validate(data)


def test_batch_state_rejects_invalid_enum():
    data = valid_batch_state_data()
    data["status"] = "done"

    with pytest.raises(ValidationError):
        BatchState.model_validate(data)


def test_batch_report_rejects_incoherent_object_type():
    data = valid_batch_report_data()
    data["object_type"] = "BatchState"

    with pytest.raises(ValidationError):
        BatchReport.model_validate(data)


def test_batch_report_rejects_missing_batch_id():
    data = valid_batch_report_data()
    data.pop("batch_id")

    with pytest.raises(ValidationError):
        BatchReport.model_validate(data)


def test_batch_report_rejects_incoherent_counts():
    data = valid_batch_report_data()
    data["entries_skipped"] = 1

    with pytest.raises(ValidationError):
        BatchReport.model_validate(data)
