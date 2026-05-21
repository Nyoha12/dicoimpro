import pytest
from pydantic import ValidationError

from dico_impro.contracts import AuditGravite, AuditQueueRecord, EntryState, GoldenSetCase


def valid_entry_state_data() -> dict[str, object]:
    return {
        "created_by": "tests",
        "batch_id": "BATCH_001",
        "id_entree_original": "026",
        "titre_original_exact": "Entry title",
        "source_base_ref": None,
        "triage_ref": None,
        "journal_ref": "active_journal",
        "statut_journal_connu": "RUN_002_fait",
        "dernier_RUN_connu": "RUN_002",
        "a_ne_pas_retraiter_nouveau": True,
        "est_archive_non_active": False,
        "notes_etat": [],
        "alertes_initiales": ["do_not_reprocess_as_new"],
    }


def valid_audit_queue_record_data() -> dict[str, object]:
    return {
        "created_by": "tests",
        "batch_id": "BATCH_001",
        "id_entree_original": "026",
        "titre_original_exact": "Entry title",
        "audit_id": "AUDIT_026_001",
        "audit_gravite": AuditGravite.ORANGE,
        "audit_reason": ["source_check_required"],
        "blocking_for_publication": True,
        "blocking_for_processing": False,
        "recommended_action": "Review source status.",
        "linked_objects": ["RESULT_TASK_BATCH_001_026_ROUTING"],
    }


def valid_golden_set_case_data() -> dict[str, object]:
    return {
        "created_by": "tests",
        "case_id": "GOLDEN_032_RESERVE",
        "id_entree_original": "032",
        "titre_original_exact": None,
        "purpose": "Verify reserve status is not treated as a completed RUN.",
        "input_fixture_refs": ["post005_026_030_032.yaml"],
        "expected_must": ["journal_read"],
        "expected_must_not": ["treat_as_run_done"],
        "expected_alerts": ["reserve_not_run_done"],
        "expected_publication_status": "publication_bloquee",
        "notes": None,
    }


def test_valid_entry_state_is_accepted():
    state = EntryState.model_validate(valid_entry_state_data())

    assert state.object_type == "EntryState"
    assert state.batch_id == "BATCH_001"
    assert state.id_entree_original == "026"


def test_valid_audit_queue_record_is_accepted():
    record = AuditQueueRecord.model_validate(valid_audit_queue_record_data())

    assert record.object_type == "AuditQueueRecord"
    assert record.audit_gravite == AuditGravite.ORANGE
    assert record.blocking_for_publication is True


def test_valid_golden_set_case_is_accepted():
    case = GoldenSetCase.model_validate(valid_golden_set_case_data())

    assert case.object_type == "GoldenSetCase"
    assert case.schema_version == "v0.2.3-auto"
    assert case.expected_publication_status == "publication_bloquee"


def test_entry_state_rejects_missing_required_field():
    data = valid_entry_state_data()
    data.pop("titre_original_exact")

    with pytest.raises(ValidationError):
        EntryState.model_validate(data)


def test_entry_state_rejects_extra_field():
    data = valid_entry_state_data()
    data["extra"] = "forbidden"

    with pytest.raises(ValidationError):
        EntryState.model_validate(data)


def test_audit_queue_record_rejects_invalid_enum():
    data = valid_audit_queue_record_data()
    data["audit_gravite"] = "blue"

    with pytest.raises(ValidationError):
        AuditQueueRecord.model_validate(data)


def test_audit_queue_record_rejects_incoherent_object_type():
    data = valid_audit_queue_record_data()
    data["object_type"] = "EntryState"

    with pytest.raises(ValidationError):
        AuditQueueRecord.model_validate(data)


def test_audit_queue_record_rejects_missing_batch_id():
    data = valid_audit_queue_record_data()
    data.pop("batch_id")

    with pytest.raises(ValidationError):
        AuditQueueRecord.model_validate(data)


def test_golden_set_case_rejects_non_ascii_publication_status_value():
    data = valid_golden_set_case_data()
    data["expected_publication_status"] = "publication_bloqu\u00e9e"

    with pytest.raises(ValidationError):
        GoldenSetCase.model_validate(data)
