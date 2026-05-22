from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Mapping

from dico_impro.contracts import AgentContract, AgentResult, AgentTask


@dataclass(frozen=True)
class AgentTraceMetadata:
    task_id: str
    result_id: str
    agent_name: str
    agent_version: str | None
    adapter_type: str
    input_hash: str
    output_hash: str
    contract_version: str
    duration_ms: int
    retry_count: int
    raw_trace_ref: str | None


def canonical_payload_hash(payload: Any) -> str:
    normalized = _to_json_compatible(payload)
    encoded = json.dumps(
        normalized,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_agent_trace_metadata(
    task: AgentTask,
    result: AgentResult,
    contract: AgentContract,
    *,
    adapter_type: str,
    duration_ms: int = 0,
    retry_count: int = 0,
) -> AgentTraceMetadata:
    if task.task_id != result.task_id:
        raise ValueError("task/result task_id mismatch")
    if task.agent_name != result.agent_name:
        raise ValueError("task/result agent_name mismatch")
    if duration_ms < 0:
        raise ValueError("duration_ms cannot be negative")
    if retry_count < 0:
        raise ValueError("retry_count cannot be negative")

    input_hash = canonical_payload_hash(
        {
            "task_id": task.task_id,
            "batch_id": task.batch_id,
            "agent_name": task.agent_name,
            "task_type": task.task_type,
            "expected_schema": task.expected_schema,
            "input_payload": task.input_payload,
        }
    )
    output_hash = canonical_payload_hash(
        {
            "result_id": result.result_id,
            "task_id": result.task_id,
            "agent_name": result.agent_name,
            "schema_name": result.schema_name,
            "payload": result.payload,
            "warnings": result.warnings,
            "audit_notes": result.audit_notes,
            "validation_status": result.validation_status,
        }
    )

    return AgentTraceMetadata(
        task_id=task.task_id,
        result_id=result.result_id,
        agent_name=result.agent_name,
        agent_version=contract.agent_version,
        adapter_type=adapter_type,
        input_hash=input_hash,
        output_hash=output_hash,
        contract_version=contract.schema_version,
        duration_ms=duration_ms,
        retry_count=retry_count,
        raw_trace_ref=result.raw_model_trace_ref,
    )


def _to_json_compatible(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _to_json_compatible(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        return {str(key): _to_json_compatible(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_json_compatible(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [_to_json_compatible(item) for item in sorted(value, key=repr)]
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"Object of type {type(value).__name__} is not JSON compatible")


__all__ = [
    "AgentTraceMetadata",
    "build_agent_trace_metadata",
    "canonical_payload_hash",
]
