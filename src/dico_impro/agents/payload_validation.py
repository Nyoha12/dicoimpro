from __future__ import annotations

from dataclasses import dataclass

from dico_impro.contracts import AgentResult


@dataclass(frozen=True)
class PayloadValidationResult:
    ok: bool
    reasons: tuple[str, ...] = ()


def validate_agent_result_payload(result: AgentResult) -> PayloadValidationResult:
    payload = result.payload
    reasons: list[str] = []

    object_type = payload.get("object_type")
    if object_type is None:
        reasons.append("payload missing object_type")
    elif object_type != result.schema_name:
        reasons.append("payload object_type does not match result.schema_name")

    schema_version = payload.get("schema_version")
    if schema_version is None:
        reasons.append("payload missing schema_version")
    elif schema_version != result.schema_version:
        reasons.append("payload schema_version does not match result.schema_version")

    return PayloadValidationResult(ok=not reasons, reasons=tuple(reasons))


__all__ = ["PayloadValidationResult", "validate_agent_result_payload"]
