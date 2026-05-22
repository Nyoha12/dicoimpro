from __future__ import annotations

from dico_impro.agents import FakeAgentAdapter, FakeScenario, validate_agent_result_payload
from dico_impro.contracts import AgentContract, AgentResult, AgentTask


def make_contract() -> AgentContract:
    return AgentContract.model_validate(
        {
            "object_type": "AgentContract",
            "schema_version": "v0.2.3-auto",
            "created_by": "tests",
            "agent_name": "RoutingAgent",
            "agent_version": "v0.2.3-auto",
            "mission": "Produce a bounded local test object.",
            "allowed_inputs": ["EntryState"],
            "required_output_schema": "RoutingDecision",
            "forbidden_actions": ["write_active_journal", "launch_RUN"],
            "quality_gates": ["schema_validation"],
            "handoff_targets": [],
        }
    )


def make_task(scenario: FakeScenario | str = FakeScenario.SUCCESS_VALID) -> AgentTask:
    return AgentTask.model_validate(
        {
            "object_type": "AgentTask",
            "schema_version": "v0.2.3-auto",
            "created_by": "tests",
            "task_id": "TASK_BATCH_001_026_ROUTING",
            "batch_id": "BATCH_001",
            "id_entree_original": "026",
            "titre_original_exact": "Entry title",
            "task_type": "routing",
            "agent_name": "RoutingAgent",
            "input_payload": {"fake_scenario": str(scenario)},
            "allowed_files": [],
            "forbidden_files": ["legacy_pdf", "active_journal"],
            "expected_schema": "RoutingDecision",
        }
    )


def result_for(scenario: FakeScenario = FakeScenario.SUCCESS_VALID) -> AgentResult:
    return FakeAgentAdapter().run_task(make_task(scenario), make_contract())


def with_payload(result: AgentResult, payload: dict[str, object]) -> AgentResult:
    return AgentResult.model_validate({**result.model_dump(), "payload": payload})


def test_payload_validation_accepts_current_fake_routing_decision_payload():
    result = result_for(FakeScenario.SUCCESS_VALID)

    validation = validate_agent_result_payload(result)

    assert validation.ok is True
    assert validation.reasons == ()


def test_payload_validation_rejects_missing_payload_object_type():
    result = result_for()
    payload = dict(result.payload)
    payload.pop("object_type")

    validation = validate_agent_result_payload(with_payload(result, payload))

    assert validation.ok is False
    assert validation.reasons == ("payload missing object_type",)


def test_payload_validation_rejects_missing_payload_schema_version():
    result = result_for()
    payload = dict(result.payload)
    payload.pop("schema_version")

    validation = validate_agent_result_payload(with_payload(result, payload))

    assert validation.ok is False
    assert validation.reasons == ("payload missing schema_version",)


def test_payload_validation_rejects_object_type_mismatch():
    result = result_for()
    payload = {**result.payload, "object_type": "OtherDecision"}

    validation = validate_agent_result_payload(with_payload(result, payload))

    assert validation.ok is False
    assert validation.reasons == ("payload object_type does not match result.schema_name",)


def test_payload_validation_rejects_schema_version_mismatch():
    result = result_for()
    payload = {**result.payload, "schema_version": "v0.2.2-auto"}

    validation = validate_agent_result_payload(with_payload(result, payload))

    assert validation.ok is False
    assert validation.reasons == (
        "payload schema_version does not match result.schema_version",
    )
