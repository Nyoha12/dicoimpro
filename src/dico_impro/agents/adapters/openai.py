from __future__ import annotations

from collections.abc import Mapping

from dico_impro.contracts import AgentContract, AgentResult, AgentTask, ValidationStatus


class OpenAIAdapterError(ValueError):
    """Base error for the disabled OpenAI adapter skeleton."""


class OpenAIAdapterDisabledError(OpenAIAdapterError):
    """Raised when the adapter is used without explicit opt-in."""


class OpenAIAdapterConfigurationError(OpenAIAdapterError):
    """Raised when the adapter is enabled without the required injected client."""


class OpenAIAdapterResponseError(OpenAIAdapterError):
    """Raised when the injected client returns a non-structured response."""


class OpenAIAdapter:
    """Disabled-by-default adapter skeleton for structured mock responses only."""

    adapter_type = "openai"

    def __init__(self, *, enabled: bool = False, client: object | None = None) -> None:
        self.enabled = enabled
        self._client = client

    def run_task(self, task: AgentTask, contract: AgentContract) -> AgentResult:
        if not self.enabled:
            raise OpenAIAdapterDisabledError(
                "OpenAIAdapter is disabled; pass enabled=True with an injected client to run."
            )
        if self._client is None:
            raise OpenAIAdapterConfigurationError(
                "OpenAIAdapter requires an injected client when enabled."
            )

        self._validate_inputs(task, contract)
        client_run_task = getattr(self._client, "run_task", None)
        if not callable(client_run_task):
            raise OpenAIAdapterConfigurationError(
                "OpenAIAdapter injected client must expose run_task(task=..., contract=...)."
            )

        response = client_run_task(task=task, contract=contract)
        return self._result_from_response(response, task, contract)

    def _validate_inputs(self, task: AgentTask, contract: AgentContract) -> None:
        if task.agent_name != contract.agent_name:
            raise OpenAIAdapterConfigurationError(
                "task.agent_name does not match contract.agent_name"
            )
        if task.expected_schema != contract.required_output_schema:
            raise OpenAIAdapterConfigurationError(
                "task.expected_schema does not match contract.required_output_schema"
            )

    def _result_from_response(
        self,
        response: object,
        task: AgentTask,
        contract: AgentContract,
    ) -> AgentResult:
        if not isinstance(response, Mapping):
            raise OpenAIAdapterResponseError("OpenAIAdapter client response must be a mapping.")

        payload = response.get("payload")
        if not isinstance(payload, Mapping):
            raise OpenAIAdapterResponseError(
                "OpenAIAdapter client response must include a structured payload mapping."
            )

        raw_model_trace_ref = response.get("raw_model_trace_ref")
        if not isinstance(raw_model_trace_ref, str) or not raw_model_trace_ref.strip():
            raise OpenAIAdapterResponseError(
                "OpenAIAdapter client response must include raw_model_trace_ref."
            )

        return AgentResult.model_validate(
            {
                "object_type": "AgentResult",
                "schema_version": task.schema_version,
                "created_by": "OpenAIAdapter",
                "result_id": _optional_string(
                    response,
                    "result_id",
                    default=f"OPENAI_RESULT_{task.task_id}",
                ),
                "task_id": task.task_id,
                "batch_id": task.batch_id,
                "agent_name": contract.agent_name,
                "schema_name": contract.required_output_schema,
                "payload": dict(payload),
                "warnings": _optional_string_list(response, "warnings"),
                "audit_notes": _optional_string_list(response, "audit_notes"),
                "raw_model_trace_ref": raw_model_trace_ref,
                "validation_status": _optional_validation_status(response),
            }
        )


def _optional_string(response: Mapping[str, object], field_name: str, *, default: str) -> str:
    value = response.get(field_name, default)
    if not isinstance(value, str) or not value.strip():
        raise OpenAIAdapterResponseError(f"OpenAIAdapter response field {field_name} must be text.")
    return value


def _optional_string_list(response: Mapping[str, object], field_name: str) -> list[str]:
    value = response.get(field_name, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise OpenAIAdapterResponseError(
            f"OpenAIAdapter response field {field_name} must be a list of text values."
        )
    return value


def _optional_validation_status(response: Mapping[str, object]) -> ValidationStatus:
    value = response.get("validation_status", ValidationStatus.SCHEMA_VALID)
    try:
        return ValidationStatus(value)
    except ValueError as exc:
        raise OpenAIAdapterResponseError(
            "OpenAIAdapter response field validation_status is unknown."
        ) from exc


__all__ = [
    "OpenAIAdapter",
    "OpenAIAdapterConfigurationError",
    "OpenAIAdapterDisabledError",
    "OpenAIAdapterError",
    "OpenAIAdapterResponseError",
]
