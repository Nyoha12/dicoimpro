from __future__ import annotations

from typing import Protocol, runtime_checkable

from dico_impro.contracts import AgentContract, AgentResult, AgentTask


@runtime_checkable
class AgentAdapter(Protocol):
    def run_task(self, task: AgentTask, contract: AgentContract) -> AgentResult:
        """Run a bounded agent task and return a validated AgentResult."""


__all__ = ["AgentAdapter"]
