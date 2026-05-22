from __future__ import annotations

from pydantic import ValidationError

from dico_impro.agents.adapters.openai_contracts import OpenAIClientResponse
from dico_impro.contracts import AgentContract, AgentResult, AgentTask


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
        try:
            client_response = OpenAIClientResponse.model_validate(response)
        except ValidationError as exc:
            raise OpenAIAdapterResponseError(
                "OpenAIAdapter client response does not match OpenAIClientResponse."
            ) from exc

        return AgentResult.model_validate(
            {
                "object_type": "AgentResult",
                "schema_version": task.schema_version,
                "created_by": "OpenAIAdapter",
                "result_id": client_response.result_id or f"OPENAI_RESULT_{task.task_id}",
                "task_id": task.task_id,
                "batch_id": task.batch_id,
                "agent_name": contract.agent_name,
                "schema_name": contract.required_output_schema,
                "payload": dict(client_response.payload),
                "warnings": list(client_response.warnings),
                "audit_notes": list(client_response.audit_notes),
                "raw_model_trace_ref": client_response.raw_model_trace_ref,
                "validation_status": client_response.validation_status,
            }
        )


__all__ = [
    "OpenAIClientResponse",
    "OpenAIAdapter",
    "OpenAIAdapterConfigurationError",
    "OpenAIAdapterDisabledError",
    "OpenAIAdapterError",
    "OpenAIAdapterResponseError",
]
