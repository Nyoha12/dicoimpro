import pytest

from dico_impro.agents import (
    AgentContractMismatchError,
    AgentDisabledError,
    AgentNotFoundError,
    AgentRegistry,
)
from dico_impro.contracts import AgentContract, AgentTask


def valid_contract_data(
    *, agent_name: str = "RoutingAgent", output_schema: str = "RoutingDecision"
) -> dict[str, object]:
    return {
        "object_type": "AgentContract",
        "schema_version": "v0.2.3-auto",
        "created_by": "tests",
        "agent_name": agent_name,
        "agent_version": "v0.2.3-auto",
        "mission": "Produce a bounded local test object.",
        "allowed_inputs": ["EntryState"],
        "required_output_schema": output_schema,
        "forbidden_actions": ["write_active_journal", "launch_RUN"],
        "quality_gates": ["schema_validation"],
        "handoff_targets": [],
    }


def valid_task_data(
    *, agent_name: str = "RoutingAgent", expected_schema: str = "RoutingDecision"
) -> dict[str, object]:
    return {
        "object_type": "AgentTask",
        "schema_version": "v0.2.3-auto",
        "created_by": "tests",
        "task_id": "TASK_BATCH_001_026_ROUTING",
        "batch_id": "BATCH_001",
        "id_entree_original": "026",
        "titre_original_exact": "Entry title",
        "task_type": "routing",
        "agent_name": agent_name,
        "input_payload": {"fake_scenario": "success_valid"},
        "allowed_files": [],
        "forbidden_files": ["legacy_pdf", "active_journal"],
        "expected_schema": expected_schema,
    }


def make_contract(
    *, agent_name: str = "RoutingAgent", output_schema: str = "RoutingDecision"
) -> AgentContract:
    return AgentContract.model_validate(
        valid_contract_data(agent_name=agent_name, output_schema=output_schema)
    )


def make_task(
    *, agent_name: str = "RoutingAgent", expected_schema: str = "RoutingDecision"
) -> AgentTask:
    return AgentTask.model_validate(
        valid_task_data(agent_name=agent_name, expected_schema=expected_schema)
    )


def test_registry_accepts_valid_contract():
    registry = AgentRegistry()
    contract = make_contract()

    registered = registry.register(contract)

    assert registered.contract == contract
    assert registry.get_contract("RoutingAgent") == contract


def test_registry_rejects_missing_agent():
    registry = AgentRegistry()

    with pytest.raises(AgentNotFoundError):
        registry.get_contract("MissingAgent")


def test_registry_rejects_disabled_agent():
    registry = AgentRegistry()
    registry.register(make_contract(), enabled=False)

    with pytest.raises(AgentDisabledError):
        registry.get_contract("RoutingAgent")


def test_registry_only_registers_valid_contract_instances():
    registry = AgentRegistry()

    with pytest.raises(TypeError):
        registry.register(valid_contract_data())  # type: ignore[arg-type]


def test_registry_rejects_unknown_output_schema():
    registry = AgentRegistry()

    with pytest.raises(AgentContractMismatchError):
        registry.register(make_contract(output_schema="UnknownSchema"))


def test_registry_validates_task_agent_and_schema_coherence():
    registry = AgentRegistry()
    contract = make_contract()
    task = make_task()
    registry.register(contract)

    assert registry.validate_task(task) == contract


def test_registry_rejects_task_schema_mismatch():
    registry = AgentRegistry()
    registry.register(make_contract())
    task = make_task(expected_schema="ClassificationResult")

    with pytest.raises(AgentContractMismatchError):
        registry.validate_task(task)
