from __future__ import annotations

import re

from pydantic import ConfigDict, field_validator, model_validator

from dico_impro.contracts.common import NonEmptyStr, SchemaVersion, StrictContractModel


REQUIRED_PROMPT_GUARDRAILS: tuple[str, ...] = (
    "no_real_openai_call_by_default",
    "no_network_by_default",
    "structured_output_only",
    "payload_validation_required",
    "quality_gate_required",
    "trace_metadata_required",
    "no_candidate_selection",
    "no_active_journal_write",
    "no_data_local_files",
)
REQUIRED_FORBIDDEN_CONTEXT_KEYS: tuple[str, ...] = (
    "active_journal",
    "data/local_files",
)
FORBIDDEN_INLINE_PROMPT_FIELDS: tuple[str, ...] = (
    "prompt",
    "prompt_text",
    "system_prompt",
    "user_prompt",
    "instructions",
)

_PROMPT_BODY_REF_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/@#-]*")


class PromptPackage(StrictContractModel):
    """Strict disabled metadata contract for future prompt packages."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    package_id: NonEmptyStr
    schema_version: SchemaVersion
    agent_name: NonEmptyStr
    required_output_schema: NonEmptyStr
    input_schema: NonEmptyStr
    output_schema: NonEmptyStr
    allowed_context_keys: tuple[NonEmptyStr, ...]
    forbidden_context_keys: tuple[NonEmptyStr, ...]
    required_guardrails: tuple[NonEmptyStr, ...]
    prompt_body_ref: NonEmptyStr
    enabled: bool = False

    @field_validator(
        "allowed_context_keys",
        "forbidden_context_keys",
        "required_guardrails",
        mode="before",
    )
    @classmethod
    def sequence_fields_must_be_text_sequences(cls, value: object) -> object:
        if not isinstance(value, (list, tuple)):
            raise ValueError("field must be a list or tuple of text")
        if not all(isinstance(item, str) for item in value):
            raise ValueError("field must be a list or tuple of text")
        return value

    @field_validator("prompt_body_ref")
    @classmethod
    def prompt_body_ref_must_be_reference(cls, value: str) -> str:
        if any(character.isspace() for character in value):
            raise ValueError("prompt_body_ref must be a compact reference string")
        if _PROMPT_BODY_REF_PATTERN.fullmatch(value) is None:
            raise ValueError("prompt_body_ref must be a reference string only")
        return value

    @field_validator("enabled", mode="before")
    @classmethod
    def enabled_must_remain_disabled(cls, value: object) -> object:
        if value is not False:
            raise ValueError("PromptPackage is disabled-only in this phase")
        return value

    @model_validator(mode="before")
    @classmethod
    def reject_inline_prompt_fields(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data

        present_forbidden_fields = sorted(
            set(data).intersection(FORBIDDEN_INLINE_PROMPT_FIELDS)
        )
        if present_forbidden_fields:
            raise ValueError(
                "inline prompt body fields are forbidden: "
                + ", ".join(present_forbidden_fields)
            )
        return data

    @model_validator(mode="after")
    def validate_guardrails_and_context_keys(self) -> PromptPackage:
        allowed = set(self.allowed_context_keys)
        forbidden = set(self.forbidden_context_keys)
        if allowed.intersection(forbidden):
            raise ValueError("allowed_context_keys and forbidden_context_keys must not overlap")

        missing_guardrails = set(REQUIRED_PROMPT_GUARDRAILS).difference(self.required_guardrails)
        if missing_guardrails:
            raise ValueError(
                "required_guardrails missing required values: "
                + ", ".join(sorted(missing_guardrails))
            )

        missing_forbidden_context_keys = set(REQUIRED_FORBIDDEN_CONTEXT_KEYS).difference(forbidden)
        if missing_forbidden_context_keys:
            raise ValueError(
                "forbidden_context_keys missing required values: "
                + ", ".join(sorted(missing_forbidden_context_keys))
            )

        return self


__all__ = [
    "FORBIDDEN_INLINE_PROMPT_FIELDS",
    "PromptPackage",
    "REQUIRED_FORBIDDEN_CONTEXT_KEYS",
    "REQUIRED_PROMPT_GUARDRAILS",
]
