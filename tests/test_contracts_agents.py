import pytest
from pydantic import ValidationError

from dico_impro.contracts import AgentContract, AgentResult, AgentTask, ValidationStatus


def valid_agent_contract_data() -> dict[str, object]:
    return {
        "object_type": "AgentContract",
        "schema_version": "v0.2.3-auto",
        "created_by": "tests",
        "agent_name": "RoutingAgent",
        "agent_version": "v0.2.3-auto",
        "mission": "Produce a bounded routing object.",
        "allowed_inputs": ["EntryState"],
        "required_output_schema": "RoutingDecision",
        "forbidden_actions": ["write_active_journal"],
        "quality_gates": ["schema_validation"],
        "handoff_targets": [],
    }


def valid_agent_task_data() -> dict[str, object]:
    return {
        "object_type": "AgentTask",
        "schema_version": "v0.2.3-auto",
        "created_by": "tests",
        "task_id": "TASK_BATCH_001_026_ROUTING",
        "batch_id": "BATCH_001",
        "id_entree_original": "026",
        "titre_original_exact": "Entry title",
        "task_type": "routing",
        "agent_name": "RoutingAgent",
        "input_payload": {"id_entree_original": "026"},
        "allowed_files": ["manifest"],
        "forbidden_files": ["legacy_pdf"],
        "expected_schema": "RoutingDecision",
    }


def valid_agent_result_data() -> dict[str, object]:
    return {
        "object_type": "AgentResult",
        "schema_version": "v0.2.3-auto",
        "created_by": "tests",
        "result_id": "RESULT_TASK_BATCH_001_026_ROUTING",
        "task_id": "TASK_BATCH_001_026_ROUTING",
        "batch_id": "BATCH_001",
        "agent_name": "RoutingAgent",
        "schema_name": "RoutingDecision",
        "payload": {"object_type": "RoutingDecision"},
        "warnings": [],
        "audit_notes": [],
        "raw_model_trace_ref": None,
        "validation_status": ValidationStatus.SCHEMA_VALID,
    }


def test_valid_agent_contract_is_accepted():
    contract = AgentContract.model_validate(valid_agent_contract_data())

    assert contract.object_type == "AgentContract"
    assert contract.schema_version == "v0.2.3-auto"
    assert contract.created_by == "tests"


def test_valid_agent_task_is_accepted():
    task = AgentTask.model_validate(valid_agent_task_data())

    assert task.object_type == "AgentTask"
    assert task.batch_id == "BATCH_001"
    assert task.id_entree_original == "026"


def test_valid_agent_result_is_accepted():
    result = AgentResult.model_validate(valid_agent_result_data())

    assert result.object_type == "AgentResult"
    assert result.validation_status == ValidationStatus.SCHEMA_VALID


def test_agent_contract_rejects_missing_required_field():
    data = valid_agent_contract_data()
    data.pop("required_output_schema")

    with pytest.raises(ValidationError):
        AgentContract.model_validate(data)


def test_agent_contract_rejects_missing_schema_version():
    data = valid_agent_contract_data()
    data.pop("schema_version")

    with pytest.raises(ValidationError):
        AgentContract.model_validate(data)


def test_agent_contract_rejects_missing_object_type():
    data = valid_agent_contract_data()
    data.pop("object_type")

    with pytest.raises(ValidationError):
        AgentContract.model_validate(data)


def test_agent_task_rejects_extra_field():
    data = valid_agent_task_data()
    data["unexpected"] = "forbidden"

    with pytest.raises(ValidationError):
        AgentTask.model_validate(data)


def test_agent_result_rejects_invalid_enum():
    data = valid_agent_result_data()
    data["validation_status"] = "validated"

    with pytest.raises(ValidationError):
        AgentResult.model_validate(data)


def test_agent_task_rejects_incoherent_object_type():
    data = valid_agent_task_data()
    data["object_type"] = "AgentResult"

    with pytest.raises(ValidationError):
        AgentTask.model_validate(data)


def test_agent_task_rejects_missing_batch_id():
    data = valid_agent_task_data()
    data.pop("batch_id")

    with pytest.raises(ValidationError):
        AgentTask.model_validate(data)
