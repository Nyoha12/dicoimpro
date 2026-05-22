from __future__ import annotations

import pytest
from pydantic import ValidationError

from dico_impro.agents import OpenAIClientResponse
from dico_impro.contracts import ValidationStatus


def valid_openai_client_response_data() -> dict[str, object]:
    return {
        "payload": {
            "object_type": "RoutingDecision",
            "schema_version": "v0.2.3-auto",
            "status": "ok",
        },
        "raw_model_trace_ref": "mock_trace:TASK_001",
        "result_id": "MOCK_RESULT_TASK_001",
        "warnings": ["bounded mock warning"],
        "audit_notes": ("bounded mock audit",),
        "validation_status": "schema_valid",
    }


def test_openai_client_response_accepts_valid_structured_response():
    response = OpenAIClientResponse.model_validate(valid_openai_client_response_data())

    assert response.payload["status"] == "ok"
    assert response.raw_model_trace_ref == "mock_trace:TASK_001"
    assert response.result_id == "MOCK_RESULT_TASK_001"
    assert response.warnings == ("bounded mock warning",)
    assert response.audit_notes == ("bounded mock audit",)
    assert response.validation_status == ValidationStatus.SCHEMA_VALID


def test_openai_client_response_defaults_optional_structured_fields():
    response = OpenAIClientResponse.model_validate(
        {
            "payload": {"object_type": "RoutingDecision", "schema_version": "v0.2.3-auto"},
            "raw_model_trace_ref": "mock_trace:TASK_001",
        }
    )

    assert response.result_id is None
    assert response.warnings == ()
    assert response.audit_notes == ()
    assert response.validation_status == ValidationStatus.SCHEMA_VALID


def test_openai_client_response_rejects_non_mapping_payload():
    data = valid_openai_client_response_data()
    data["payload"] = ["not", "a", "mapping"]

    with pytest.raises(ValidationError):
        OpenAIClientResponse.model_validate(data)


def test_openai_client_response_rejects_empty_raw_model_trace_ref():
    data = valid_openai_client_response_data()
    data["raw_model_trace_ref"] = "   "

    with pytest.raises(ValidationError):
        OpenAIClientResponse.model_validate(data)


@pytest.mark.parametrize("warnings", ["warning", [123], ("ok", 123)])
def test_openai_client_response_rejects_warnings_not_sequence_of_strings(
    warnings: object,
):
    data = valid_openai_client_response_data()
    data["warnings"] = warnings

    with pytest.raises(ValidationError):
        OpenAIClientResponse.model_validate(data)


@pytest.mark.parametrize("audit_notes", ["note", [123], ("ok", 123)])
def test_openai_client_response_rejects_audit_notes_not_sequence_of_strings(
    audit_notes: object,
):
    data = valid_openai_client_response_data()
    data["audit_notes"] = audit_notes

    with pytest.raises(ValidationError):
        OpenAIClientResponse.model_validate(data)


def test_openai_client_response_rejects_unknown_validation_status():
    data = valid_openai_client_response_data()
    data["validation_status"] = "unknown_status"

    with pytest.raises(ValidationError):
        OpenAIClientResponse.model_validate(data)


def test_openai_client_response_has_no_future_real_api_or_prompt_fields():
    forbidden_fields = {
        "text",
        "response_text",
        "prompt",
        "prompt_text",
        "model",
        "model_name",
        "token_usage",
        "api_metadata",
    }

    assert forbidden_fields.isdisjoint(OpenAIClientResponse.model_fields)

    data = valid_openai_client_response_data()
    data["text"] = "free-form fallback must not be accepted"

    with pytest.raises(ValidationError):
        OpenAIClientResponse.model_validate(data)
