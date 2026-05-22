from __future__ import annotations

import ast
import builtins
import inspect
from pathlib import Path

import pytest
from pydantic import ValidationError

from dico_impro.agents import (
    FORBIDDEN_INLINE_PROMPT_FIELDS,
    PromptPackage,
    REQUIRED_FORBIDDEN_CONTEXT_KEYS,
    REQUIRED_PROMPT_GUARDRAILS,
)
import dico_impro.agents.adapters.openai as openai_adapter_module
import dico_impro.agents.prompt_contracts as prompt_contracts_module


FORBIDDEN_IMPORT_ROOTS = {"openai", "requests", "httpx", "urllib", "socket"}


def valid_prompt_package_data() -> dict[str, object]:
    return {
        "package_id": "prompt-package.routing.v0.2.3-auto",
        "schema_version": "v0.2.3-auto",
        "agent_name": "RoutingAgent",
        "required_output_schema": "RoutingDecision",
        "input_schema": "EntryState",
        "output_schema": "RoutingDecision",
        "allowed_context_keys": ["entry_state", "batch_scope"],
        "forbidden_context_keys": [
            "active_journal",
            "candidate_selection",
            "data/local_files",
            "legacy_pdf",
        ],
        "required_guardrails": list(REQUIRED_PROMPT_GUARDRAILS),
        "prompt_body_ref": "prompt-package:RoutingAgent:v0.2.3-auto",
    }


def test_prompt_package_accepts_valid_disabled_metadata_package():
    package = PromptPackage.model_validate(valid_prompt_package_data())

    assert package.package_id == "prompt-package.routing.v0.2.3-auto"
    assert package.schema_version == "v0.2.3-auto"
    assert package.agent_name == "RoutingAgent"
    assert package.required_output_schema == "RoutingDecision"
    assert package.input_schema == "EntryState"
    assert package.output_schema == "RoutingDecision"
    assert package.allowed_context_keys == ("entry_state", "batch_scope")
    assert package.forbidden_context_keys == (
        "active_journal",
        "candidate_selection",
        "data/local_files",
        "legacy_pdf",
    )
    assert package.required_guardrails == REQUIRED_PROMPT_GUARDRAILS
    assert package.prompt_body_ref == "prompt-package:RoutingAgent:v0.2.3-auto"
    assert package.enabled is False


def test_prompt_package_enabled_defaults_to_false():
    package = PromptPackage.model_validate(valid_prompt_package_data())

    assert package.enabled is False


def test_prompt_package_rejects_enabled_true():
    data = valid_prompt_package_data()
    data["enabled"] = True

    with pytest.raises(ValidationError, match="disabled-only"):
        PromptPackage.model_validate(data)


@pytest.mark.parametrize("field_name", FORBIDDEN_INLINE_PROMPT_FIELDS)
def test_prompt_package_rejects_inline_prompt_fields(field_name: str):
    data = valid_prompt_package_data()
    data[field_name] = "forbidden-inline-value"

    with pytest.raises(ValidationError, match="inline prompt body fields"):
        PromptPackage.model_validate(data)


@pytest.mark.parametrize(
    "field_name",
    [
        "package_id",
        "agent_name",
        "required_output_schema",
        "input_schema",
        "output_schema",
        "prompt_body_ref",
    ],
)
def test_prompt_package_rejects_empty_required_fields(field_name: str):
    data = valid_prompt_package_data()
    data[field_name] = "   "

    with pytest.raises(ValidationError):
        PromptPackage.model_validate(data)


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("allowed_context_keys", ["entry_state", ""]),
        ("forbidden_context_keys", ["active_journal", "data/local_files", ""]),
        ("required_guardrails", list(REQUIRED_PROMPT_GUARDRAILS) + [""]),
        ("allowed_context_keys", "entry_state"),
        ("forbidden_context_keys", {"active_journal", "data/local_files"}),
        ("required_guardrails", "structured_output_only"),
    ],
)
def test_prompt_package_rejects_invalid_sequence_fields(field_name: str, value: object):
    data = valid_prompt_package_data()
    data[field_name] = value

    with pytest.raises(ValidationError):
        PromptPackage.model_validate(data)


def test_prompt_package_rejects_prompt_body_ref_that_is_not_reference_string():
    data = valid_prompt_package_data()
    data["prompt_body_ref"] = "not a reference string"

    with pytest.raises(ValidationError, match="reference string"):
        PromptPackage.model_validate(data)


def test_prompt_package_rejects_context_key_overlap():
    data = valid_prompt_package_data()
    data["forbidden_context_keys"] = [
        "active_journal",
        "batch_scope",
        "data/local_files",
    ]

    with pytest.raises(ValidationError, match="must not overlap"):
        PromptPackage.model_validate(data)


@pytest.mark.parametrize("guardrail", REQUIRED_PROMPT_GUARDRAILS)
def test_prompt_package_rejects_missing_required_guardrails(guardrail: str):
    data = valid_prompt_package_data()
    data["required_guardrails"] = [
        item for item in REQUIRED_PROMPT_GUARDRAILS if item != guardrail
    ]

    with pytest.raises(ValidationError, match="missing required values"):
        PromptPackage.model_validate(data)


@pytest.mark.parametrize("context_key", REQUIRED_FORBIDDEN_CONTEXT_KEYS)
def test_prompt_package_rejects_missing_required_forbidden_context_keys(context_key: str):
    data = valid_prompt_package_data()
    data["forbidden_context_keys"] = [
        item
        for item in valid_prompt_package_data()["forbidden_context_keys"]
        if item != context_key
    ]

    with pytest.raises(ValidationError, match="forbidden_context_keys missing"):
        PromptPackage.model_validate(data)


def test_prompt_package_does_not_read_files(monkeypatch: pytest.MonkeyPatch):
    def fail_file_access(*args: object, **kwargs: object) -> None:
        raise AssertionError("PromptPackage must not read files")

    monkeypatch.setattr(builtins, "open", fail_file_access)
    monkeypatch.setattr(Path, "open", fail_file_access)
    monkeypatch.setattr(Path, "read_text", fail_file_access)

    package = PromptPackage.model_validate(valid_prompt_package_data())

    assert package.enabled is False


def test_prompt_contract_source_has_no_network_or_openai_imports():
    source = inspect.getsource(prompt_contracts_module)

    for node in ast.walk(ast.parse(source)):
        imported_roots: list[str] = []
        if isinstance(node, ast.Import):
            imported_roots = [alias.name.partition(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_roots = [node.module.partition(".")[0]]

        assert FORBIDDEN_IMPORT_ROOTS.isdisjoint(imported_roots)


def test_openai_adapter_does_not_consume_prompt_package_yet():
    source = inspect.getsource(openai_adapter_module)

    assert "PromptPackage" not in source
    assert "prompt_contracts" not in source


def test_no_prompts_module_was_added():
    prompts_module = (
        Path(__file__).parents[1] / "src" / "dico_impro" / "agents" / "prompts.py"
    )

    assert not prompts_module.exists()
