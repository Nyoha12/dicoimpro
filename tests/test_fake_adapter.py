import builtins
from pathlib import Path

import pytest
from pydantic import ValidationError

from dico_impro.agents import (
    FakeAdapterError,
    FakeAgentAdapter,
    FakeScenario,
    QualityGateClassification,
    classify_agent_result,
)
from dico_impro.agents.adapters.base import AgentAdapter
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


SCENARIO_EXPECTATIONS = {
    FakeScenario.SUCCESS_VALID: (ValidationStatus.SCHEMA_VALID, QualityGateClassification.OK),
    FakeScenario.SUCCESS_WITH_WARNING: (
        ValidationStatus.SCHEMA_VALID,
        QualityGateClassification.PRUDENCE,
    ),
    FakeScenario.SCHEMA_INVALID: (
        ValidationStatus.SCHEMA_INVALID,
        QualityGateClassification.RECOVERABLE,
    ),
    FakeScenario.NON_PARSEABLE_OUTPUT: (
        ValidationStatus.SCHEMA_INVALID,
        QualityGateClassification.RECOVERABLE,
    ),
    FakeScenario.PROTOCOL_VIOLATION: (
        ValidationStatus.AUDIT_HUMAIN_REQUIS,
        QualityGateClassification.BLOCKING,
    ),
    FakeScenario.SOURCE_CONFUSION: (
        ValidationStatus.AUDIT_HUMAIN_REQUIS,
        QualityGateClassification.BLOCKING,
    ),
    FakeScenario.PUBLICATION_BLOCKING: (
        ValidationStatus.NON_PUBLIABLE_EN_L_ETAT,
        QualityGateClassification.BLOCKING,
    ),
    FakeScenario.RUN_002_REQUIRED: (
        ValidationStatus.RUN_002_AUTO_REQUIS,
        QualityGateClassification.PRUDENCE,
    ),
}


def test_fake_adapter_matches_agent_adapter_protocol():
    assert isinstance(FakeAgentAdapter(), AgentAdapter)


@pytest.mark.parametrize("scenario", list(FakeScenario))
def test_fake_adapter_returns_valid_agent_result_for_every_scenario(scenario: FakeScenario):
    adapter = FakeAgentAdapter()
    result = adapter.run_task(make_task(scenario), make_contract())
    expected_status, expected_classification = SCENARIO_EXPECTATIONS[scenario]

    assert isinstance(result, AgentResult)
    assert result.object_type == "AgentResult"
    assert result.schema_version == "v0.2.3-auto"
    assert result.created_by == "FakeAgentAdapter"
    assert result.validation_status == expected_status
    assert result.payload["object_type"] == "RoutingDecision"
    assert result.payload["schema_version"] == "v0.2.3-auto"
    assert result.payload["scenario"] == scenario.value
    assert classify_agent_result(result) == expected_classification


def test_every_fake_scenario_is_covered_by_expectations():
    assert set(SCENARIO_EXPECTATIONS) == set(FakeScenario)


def test_fake_adapter_does_not_read_local_files(monkeypatch: pytest.MonkeyPatch):
    def fail_open(*args: object, **kwargs: object) -> None:
        raise AssertionError("FakeAgentAdapter must not open files")

    monkeypatch.setattr(builtins, "open", fail_open)
    monkeypatch.setattr(Path, "open", fail_open)

    result = FakeAgentAdapter().run_task(make_task(), make_contract())

    assert result.validation_status == ValidationStatus.SCHEMA_VALID


def test_fake_adapter_rejects_agent_name_mismatch():
    task = make_task()
    contract = AgentContract.model_validate(
        {
            **make_contract().model_dump(),
            "agent_name": "ClassificationAgent",
            "required_output_schema": "RoutingDecision",
        }
    )

    with pytest.raises(FakeAdapterError):
        FakeAgentAdapter().run_task(task, contract)


def test_fake_adapter_rejects_expected_schema_mismatch():
    task = AgentTask.model_validate({**make_task().model_dump(), "expected_schema": "BatchReport"})

    with pytest.raises(FakeAdapterError):
        FakeAgentAdapter().run_task(task, make_contract())


def test_agent_result_rejects_missing_object_type_or_schema_version():
    valid_result = FakeAgentAdapter().run_task(make_task(), make_contract()).model_dump()

    missing_object_type = dict(valid_result)
    missing_object_type.pop("object_type")
    with pytest.raises(ValidationError):
        AgentResult.model_validate(missing_object_type)

    missing_schema_version = dict(valid_result)
    missing_schema_version.pop("schema_version")
    with pytest.raises(ValidationError):
        AgentResult.model_validate(missing_schema_version)
