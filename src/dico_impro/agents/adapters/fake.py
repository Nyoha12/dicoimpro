from __future__ import annotations

from enum import StrEnum

from dico_impro.contracts import AgentContract, AgentResult, AgentTask, ValidationStatus


class FakeAdapterError(ValueError):
    """Raised when the fake adapter is used with incoherent local inputs."""


class FakeScenario(StrEnum):
    SUCCESS_VALID = "success_valid"
    SUCCESS_WITH_WARNING = "success_with_warning"
    SCHEMA_INVALID = "schema_invalid"
    NON_PARSEABLE_OUTPUT = "non_parseable_output"
    PROTOCOL_VIOLATION = "protocol_violation"
    SOURCE_CONFUSION = "source_confusion"
    PUBLICATION_BLOCKING = "publication_blocking"
    RUN_002_REQUIRED = "run_002_required"


class FakeAgentAdapter:
    """Local adapter returning deterministic AgentResult objects.

    It does not read project files, write outputs, or perform network calls.
    Scenario selection is explicit through the constructor or task.input_payload.
    """

    def __init__(self, default_scenario: FakeScenario | str = FakeScenario.SUCCESS_VALID) -> None:
        self.default_scenario = FakeScenario(default_scenario)

    def run_task(self, task: AgentTask, contract: AgentContract) -> AgentResult:
        self._validate_inputs(task, contract)
        scenario = self._scenario_for_task(task)
        payload = self._payload_for(task, scenario)

        warnings: list[str] = []
        audit_notes: list[str] = []
        validation_status = ValidationStatus.SCHEMA_VALID

        if scenario == FakeScenario.SUCCESS_WITH_WARNING:
            warnings.append("fake warning emitted by local adapter")
        elif scenario == FakeScenario.SCHEMA_INVALID:
            validation_status = ValidationStatus.SCHEMA_INVALID
            audit_notes.append("fake schema validation failure")
        elif scenario == FakeScenario.NON_PARSEABLE_OUTPUT:
            validation_status = ValidationStatus.SCHEMA_INVALID
            audit_notes.append("fake non-parseable output converted to AgentResult")
        elif scenario == FakeScenario.PROTOCOL_VIOLATION:
            validation_status = ValidationStatus.AUDIT_HUMAIN_REQUIS
            audit_notes.append("fake protocol violation")
        elif scenario == FakeScenario.SOURCE_CONFUSION:
            validation_status = ValidationStatus.AUDIT_HUMAIN_REQUIS
            audit_notes.append("fake source/platform confusion")
        elif scenario == FakeScenario.PUBLICATION_BLOCKING:
            validation_status = ValidationStatus.NON_PUBLIABLE_EN_L_ETAT
            audit_notes.append("fake publication blocking condition")
        elif scenario == FakeScenario.RUN_002_REQUIRED:
            validation_status = ValidationStatus.RUN_002_AUTO_REQUIS
            audit_notes.append("fake RUN_002 requirement")

        return AgentResult(
            object_type="AgentResult",
            schema_version=task.schema_version,
            created_by="FakeAgentAdapter",
            result_id=f"RESULT_{task.task_id}",
            task_id=task.task_id,
            batch_id=task.batch_id,
            agent_name=contract.agent_name,
            schema_name=contract.required_output_schema,
            payload=payload,
            warnings=warnings,
            audit_notes=audit_notes,
            raw_model_trace_ref=f"fake_trace:{task.task_id}:{scenario.value}",
            validation_status=validation_status,
        )

    def _validate_inputs(self, task: AgentTask, contract: AgentContract) -> None:
        if task.agent_name != contract.agent_name:
            raise FakeAdapterError("task.agent_name does not match contract.agent_name")
        if task.expected_schema != contract.required_output_schema:
            raise FakeAdapterError(
                "task.expected_schema does not match contract.required_output_schema"
            )

    def _scenario_for_task(self, task: AgentTask) -> FakeScenario:
        requested = task.input_payload.get("fake_scenario", self.default_scenario)
        try:
            return FakeScenario(requested)
        except ValueError as exc:
            raise FakeAdapterError(f"unknown fake scenario: {requested}") from exc

    def _payload_for(self, task: AgentTask, scenario: FakeScenario) -> dict[str, object]:
        payload: dict[str, object] = {
            "object_type": task.expected_schema,
            "schema_version": task.schema_version,
            "scenario": scenario.value,
            "status": "ok",
        }
        if scenario == FakeScenario.SUCCESS_WITH_WARNING:
            payload["error_type"] = "warning"
        elif scenario == FakeScenario.SCHEMA_INVALID:
            payload["status"] = "error"
            payload["error_type"] = "schema_invalid"
        elif scenario == FakeScenario.NON_PARSEABLE_OUTPUT:
            payload["status"] = "error"
            payload["error_type"] = "non_parseable_output"
        elif scenario == FakeScenario.PROTOCOL_VIOLATION:
            payload["status"] = "error"
            payload["error_type"] = "protocol_violation"
        elif scenario == FakeScenario.SOURCE_CONFUSION:
            payload["status"] = "error"
            payload["error_type"] = "source_confusion"
        elif scenario == FakeScenario.PUBLICATION_BLOCKING:
            payload["status"] = "blocked"
            payload["error_type"] = "publication_blocking"
        elif scenario == FakeScenario.RUN_002_REQUIRED:
            payload["status"] = "prudence"
            payload["error_type"] = "run_002_required"
        return payload


__all__ = ["FakeAdapterError", "FakeAgentAdapter", "FakeScenario"]
