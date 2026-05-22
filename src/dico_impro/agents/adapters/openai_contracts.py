from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import ConfigDict, Field, field_validator

from dico_impro.contracts import ValidationStatus
from dico_impro.contracts.common import NonEmptyStr, StrictContractModel


class OpenAIClientResponse(StrictContractModel):
    """Strict local contract for injected mock OpenAI client responses."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    payload: Mapping[str, Any]
    raw_model_trace_ref: NonEmptyStr
    result_id: NonEmptyStr | None = None
    warnings: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    audit_notes: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    validation_status: ValidationStatus = ValidationStatus.SCHEMA_VALID

    @field_validator("payload", mode="before")
    @classmethod
    def payload_must_be_mapping(cls, value: object) -> object:
        if not isinstance(value, Mapping):
            raise ValueError("payload must be a mapping")
        return value

    @field_validator("warnings", "audit_notes", mode="before")
    @classmethod
    def notes_must_be_sequence_of_text(cls, value: object) -> object:
        if not isinstance(value, (list, tuple)):
            raise ValueError("field must be a list or tuple of text")
        if not all(isinstance(item, str) for item in value):
            raise ValueError("field must be a list or tuple of text")
        return value


__all__ = ["OpenAIClientResponse"]
