from dico_impro.agents import (
    FakeAgentAdapter,
    FakeScenario,
    QualityGateClassification,
    classify_agent_result,
    evaluate_agent_result,
)
from dico_impro.contracts import AgentContract, AgentResult, AgentTask, ValidationStatus


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


def result_for(scenario: FakeScenario) -> AgentResult:
    return FakeAgentAdapter().run_task(make_task(scenario), make_contract())


def result_with_payload(payload: dict[str, object]) -> AgentResult:
    result = result_for(FakeScenario.SUCCESS_VALID)
    return AgentResult.model_validate({**result.model_dump(), "payload": payload})


def test_quality_gate_classifies_ok_result():
    assert (
        classify_agent_result(result_for(FakeScenario.SUCCESS_VALID))
        == QualityGateClassification.OK
    )


def test_quality_gate_classifies_recoverable_errors():
    assert (
        classify_agent_result(result_for(FakeScenario.SCHEMA_INVALID))
        == QualityGateClassification.RECOVERABLE
    )
    assert (
        classify_agent_result(result_for(FakeScenario.NON_PARSEABLE_OUTPUT))
        == QualityGateClassification.RECOVERABLE
    )


def test_quality_gate_classifies_blocking_errors():
    assert (
        classify_agent_result(result_for(FakeScenario.PROTOCOL_VIOLATION))
        == QualityGateClassification.BLOCKING
    )
    assert (
        classify_agent_result(result_for(FakeScenario.SOURCE_CONFUSION))
        == QualityGateClassification.BLOCKING
    )
    assert (
        classify_agent_result(result_for(FakeScenario.PUBLICATION_BLOCKING))
        == QualityGateClassification.BLOCKING
    )


def test_quality_gate_classifies_prudence_results():
    assert (
        classify_agent_result(result_for(FakeScenario.SUCCESS_WITH_WARNING))
        == QualityGateClassification.PRUDENCE
    )
    assert (
        classify_agent_result(result_for(FakeScenario.RUN_002_REQUIRED))
        == QualityGateClassification.PRUDENCE
    )


def test_evaluate_agent_result_blocks_missing_payload_object_type():
    result = result_for(FakeScenario.SUCCESS_VALID)
    broken_payload = dict(result.payload)
    broken_payload.pop("object_type")
    broken = result_with_payload(broken_payload)

    evaluation = evaluate_agent_result(broken)

    assert evaluation.classification == QualityGateClassification.BLOCKING
    assert evaluation.reasons == ("payload missing object_type",)


def test_evaluate_agent_result_blocks_missing_payload_schema_version():
    result = result_for(FakeScenario.SUCCESS_VALID)
    broken_payload = dict(result.payload)
    broken_payload.pop("schema_version")
    broken = result_with_payload(broken_payload)

    evaluation = evaluate_agent_result(broken)

    assert evaluation.classification == QualityGateClassification.BLOCKING
    assert evaluation.reasons == ("payload missing schema_version",)


def test_evaluate_agent_result_blocks_payload_object_type_mismatch():
    result = result_for(FakeScenario.SUCCESS_VALID)
    broken_payload = {**result.payload, "object_type": "OtherSchema"}
    broken = result_with_payload(broken_payload)

    evaluation = evaluate_agent_result(broken)

    assert evaluation.classification == QualityGateClassification.BLOCKING
    assert evaluation.reasons == ("payload object_type does not match result.schema_name",)


def test_evaluate_agent_result_blocks_payload_schema_version_mismatch():
    result = result_for(FakeScenario.SUCCESS_VALID)
    broken_payload = {**result.payload, "schema_version": "v0.0.0-test"}
    broken = result_with_payload(broken_payload)

    evaluation = evaluate_agent_result(broken)

    assert evaluation.classification == QualityGateClassification.BLOCKING
    assert evaluation.reasons == (
        "payload schema_version does not match result.schema_version",
    )


def test_quality_gate_uses_validation_status_when_no_error_type_is_present():
    result = result_for(FakeScenario.SUCCESS_VALID)
    payload = dict(result.payload)
    payload.pop("error_type", None)
    changed = AgentResult.model_validate(
        {
            **result.model_dump(),
            "payload": payload,
            "validation_status": ValidationStatus.RUN_002_AUTO_REQUIS,
            "warnings": [],
            "audit_notes": [],
        }
    )

    assert classify_agent_result(changed) == QualityGateClassification.PRUDENCE
