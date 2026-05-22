from __future__ import annotations

import inspect
import json
import re
from pathlib import Path
from typing import Any

from dico_impro.agents import (
    FORBIDDEN_INLINE_PROMPT_FIELDS,
    PromptPackage,
    REQUIRED_FORBIDDEN_CONTEXT_KEYS,
    REQUIRED_PROMPT_GUARDRAILS,
)
import dico_impro.agents.adapters.openai as openai_adapter_module
import dico_impro.orchestration.mock_openai_plan as mock_openai_plan_module


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "prompt_packages"
PROMPT_BODY_REF_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/@#-]*")
EXPECTED_FIXTURES = {
    "classification_agent_metadata.json": {
        "package_id": "prompt-package.classification-agent.v0.2.3-auto",
        "agent_name": "ClassificationAgent",
        "input_schema": "EntryState",
        "output_schema": "ClassificationResult",
        "required_output_schema": "ClassificationResult",
    },
    "routing_agent_metadata.json": {
        "package_id": "prompt-package.routing-agent.v0.2.3-auto",
        "agent_name": "RoutingAgent",
        "input_schema": "EntryState",
        "output_schema": "RoutingDecision",
        "required_output_schema": "RoutingDecision",
    },
    "source_audit_agent_metadata.json": {
        "package_id": "prompt-package.source-audit-agent.v0.2.3-auto",
        "agent_name": "SourceAuditAgent",
        "input_schema": "EntryState",
        "output_schema": "SourceAuditReport",
        "required_output_schema": "SourceAuditReport",
    },
}
FORBIDDEN_PROMPT_PHRASES = (
    "developer message",
    "follow these instructions",
    "system prompt",
    "system:",
    "user prompt",
    "user:",
    "you are",
)


def load_prompt_package_fixtures() -> list[tuple[Path, dict[str, Any]]]:
    paths = sorted(FIXTURE_DIR.glob("*.json"))

    assert {path.name for path in paths} == set(EXPECTED_FIXTURES)
    return [
        (path, json.loads(path.read_text(encoding="utf-8")))
        for path in paths
    ]


def iter_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for key, item in value.items():
            strings.append(str(key))
            strings.extend(iter_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(iter_strings(item))
        return strings
    return []


def iter_keys(value: object) -> list[str]:
    if not isinstance(value, dict):
        return []

    keys: list[str] = []
    for key, item in value.items():
        keys.append(str(key))
        keys.extend(iter_keys(item))
    return keys


def test_all_prompt_package_fixtures_validate_as_prompt_packages():
    for path, data in load_prompt_package_fixtures():
        package = PromptPackage.model_validate(data)

        assert package.package_id == EXPECTED_FIXTURES[path.name]["package_id"]
        assert package.agent_name == EXPECTED_FIXTURES[path.name]["agent_name"]
        assert package.input_schema == EXPECTED_FIXTURES[path.name]["input_schema"]
        assert package.output_schema == EXPECTED_FIXTURES[path.name]["output_schema"]
        assert (
            package.required_output_schema
            == EXPECTED_FIXTURES[path.name]["required_output_schema"]
        )


def test_all_prompt_package_fixtures_are_disabled():
    for _path, data in load_prompt_package_fixtures():
        package = PromptPackage.model_validate(data)

        assert data.get("enabled", False) is False
        assert package.enabled is False


def test_prompt_package_fixtures_are_metadata_only_without_inline_prompt_fields():
    for _path, data in load_prompt_package_fixtures():
        assert set(iter_keys(data)).isdisjoint(FORBIDDEN_INLINE_PROMPT_FIELDS)


def test_prompt_package_fixtures_do_not_contain_prompt_like_long_text_bodies():
    for path, data in load_prompt_package_fixtures():
        for value in iter_strings(data):
            lowered_value = value.lower()

            assert "\n" not in value, f"{path.name} contains multiline text"
            assert len(value) <= 80, f"{path.name} contains long text: {value!r}"
            assert not any(
                phrase in lowered_value for phrase in FORBIDDEN_PROMPT_PHRASES
            ), f"{path.name} contains prompt-like text: {value!r}"


def test_prompt_package_fixtures_include_all_required_guardrails():
    required_guardrails = set(REQUIRED_PROMPT_GUARDRAILS)

    for _path, data in load_prompt_package_fixtures():
        assert required_guardrails.issubset(set(data["required_guardrails"]))


def test_prompt_package_fixtures_include_required_forbidden_context_keys():
    required_forbidden_keys = set(REQUIRED_FORBIDDEN_CONTEXT_KEYS)

    for _path, data in load_prompt_package_fixtures():
        assert required_forbidden_keys.issubset(set(data["forbidden_context_keys"]))
        assert "active_journal" in data["forbidden_context_keys"]
        assert "data/local_files" in data["forbidden_context_keys"]


def test_prompt_package_fixtures_allowed_and_forbidden_context_keys_do_not_overlap():
    for _path, data in load_prompt_package_fixtures():
        allowed = set(data["allowed_context_keys"])
        forbidden = set(data["forbidden_context_keys"])

        assert allowed.isdisjoint(forbidden)


def test_prompt_package_fixture_prompt_body_refs_are_compact_references():
    for _path, data in load_prompt_package_fixtures():
        prompt_body_ref = data["prompt_body_ref"]

        assert isinstance(prompt_body_ref, str)
        assert PROMPT_BODY_REF_PATTERN.fullmatch(prompt_body_ref) is not None
        assert not any(character.isspace() for character in prompt_body_ref)
        assert ":" in prompt_body_ref
        assert len(prompt_body_ref) <= 48


def test_openai_adapter_still_does_not_consume_prompt_package():
    source = inspect.getsource(openai_adapter_module)

    assert "PromptPackage" not in source
    assert "prompt_contracts" not in source
    assert "prompt_body_ref" not in source


def test_mock_openai_planning_still_does_not_consume_prompt_package():
    source = inspect.getsource(mock_openai_plan_module)
    lowered_source = source.lower()

    assert "promptpackage" not in lowered_source
    assert "prompt_contracts" not in lowered_source
    assert "prompt_body_ref" not in lowered_source


def test_no_prompts_module_exists():
    prompts_module = (
        Path(__file__).parents[1] / "src" / "dico_impro" / "agents" / "prompts.py"
    )

    assert not prompts_module.exists()
