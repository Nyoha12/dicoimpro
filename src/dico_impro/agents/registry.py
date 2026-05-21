from __future__ import annotations

from dataclasses import dataclass
from typing import Collection

from dico_impro.contracts import AgentContract, AgentTask


KNOWN_OUTPUT_SCHEMAS = frozenset(
    {
        "AgentResult",
        "AuditQueueRecord",
        "BatchReport",
        "BatchState",
        "ClassificationResult",
        "ConservationRecord",
        "DeltaRecord",
        "EntryState",
        "FinalProvisionalDecision",
        "GoldenSetCase",
        "JournalPatch",
        "RoutingDecision",
        "Run002Request",
        "SourceAuditReport",
        "SourceRecord",
        "ValidationReport",
    }
)


class AgentRegistryError(ValueError):
    """Base error for local agent registry violations."""


class AgentNotFoundError(AgentRegistryError):
    """Raised when an agent name is not registered."""


class AgentDisabledError(AgentRegistryError):
    """Raised when a registered agent is disabled."""


class AgentContractMismatchError(AgentRegistryError):
    """Raised when a task or registry entry contradicts an agent contract."""


@dataclass(frozen=True)
class RegisteredAgent:
    contract: AgentContract
    enabled: bool = True
    adapter_type: str = "fake"
    expected_schema: str | None = None
    max_retries: int = 0

    @property
    def resolved_expected_schema(self) -> str:
        return self.expected_schema or self.contract.required_output_schema


class AgentRegistry:
    """Local registry for already-validated agent contracts.

    The registry records which bounded agents are available. It does not execute
    tasks, choose a workflow, read files, or select entries.
    """

    def __init__(self, *, known_output_schemas: Collection[str] | None = None) -> None:
        self._known_output_schemas = set(known_output_schemas or KNOWN_OUTPUT_SCHEMAS)
        self._agents: dict[str, RegisteredAgent] = {}

    def register(
        self,
        contract: AgentContract,
        *,
        enabled: bool = True,
        adapter_type: str = "fake",
        expected_schema: str | None = None,
        max_retries: int = 0,
    ) -> RegisteredAgent:
        if not isinstance(contract, AgentContract):
            raise TypeError("AgentRegistry only registers validated AgentContract objects")
        if max_retries < 0:
            raise AgentRegistryError("max_retries cannot be negative")

        resolved_schema = expected_schema or contract.required_output_schema
        if resolved_schema != contract.required_output_schema:
            raise AgentContractMismatchError(
                "registered expected_schema must match contract.required_output_schema"
            )
        if resolved_schema not in self._known_output_schemas:
            raise AgentContractMismatchError(f"unknown output schema: {resolved_schema}")

        registered = RegisteredAgent(
            contract=contract,
            enabled=enabled,
            adapter_type=adapter_type,
            expected_schema=resolved_schema,
            max_retries=max_retries,
        )
        self._agents[contract.agent_name] = registered
        return registered

    def get(self, agent_name: str) -> RegisteredAgent:
        try:
            registered = self._agents[agent_name]
        except KeyError as exc:
            raise AgentNotFoundError(f"agent is not registered: {agent_name}") from exc

        if not registered.enabled:
            raise AgentDisabledError(f"agent is disabled: {agent_name}")
        return registered

    def get_contract(self, agent_name: str) -> AgentContract:
        return self.get(agent_name).contract

    def validate_task(self, task: AgentTask) -> AgentContract:
        registered = self.get(task.agent_name)
        contract = registered.contract
        if task.agent_name != contract.agent_name:
            raise AgentContractMismatchError("task.agent_name does not match contract.agent_name")
        if task.expected_schema != registered.resolved_expected_schema:
            raise AgentContractMismatchError(
                "task.expected_schema does not match registered expected_schema"
            )
        return contract


__all__ = [
    "AgentContractMismatchError",
    "AgentDisabledError",
    "AgentNotFoundError",
    "AgentRegistry",
    "AgentRegistryError",
    "KNOWN_OUTPUT_SCHEMAS",
    "RegisteredAgent",
]
