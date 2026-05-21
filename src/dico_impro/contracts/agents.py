from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from dico_impro.contracts.common import BatchScopedContract, NonEmptyStr, ValidationStatus, VersionedContract


class AgentContract(VersionedContract):
    object_type: Literal["AgentContract"]
    agent_name: NonEmptyStr
    agent_version: NonEmptyStr
    mission: NonEmptyStr
    allowed_inputs: list[NonEmptyStr] = Field(default_factory=list)
    required_output_schema: NonEmptyStr
    forbidden_actions: list[NonEmptyStr] = Field(min_length=1)
    quality_gates: list[NonEmptyStr] = Field(default_factory=list)
    handoff_targets: list[NonEmptyStr] = Field(default_factory=list)


class AgentTask(BatchScopedContract):
    object_type: Literal["AgentTask"]
    task_id: NonEmptyStr
    id_entree_original: NonEmptyStr | None = None
    titre_original_exact: NonEmptyStr | None = None
    task_type: NonEmptyStr
    agent_name: NonEmptyStr
    input_payload: dict[str, Any]
    allowed_files: list[NonEmptyStr] = Field(default_factory=list)
    forbidden_files: list[NonEmptyStr] = Field(default_factory=list)
    expected_schema: NonEmptyStr


class AgentResult(BatchScopedContract):
    object_type: Literal["AgentResult"]
    result_id: NonEmptyStr
    task_id: NonEmptyStr
    agent_name: NonEmptyStr
    schema_name: NonEmptyStr
    payload: dict[str, Any]
    warnings: list[NonEmptyStr] = Field(default_factory=list)
    audit_notes: list[NonEmptyStr] = Field(default_factory=list)
    raw_model_trace_ref: NonEmptyStr | None = None
    validation_status: ValidationStatus


__all__ = ["AgentContract", "AgentResult", "AgentTask"]
