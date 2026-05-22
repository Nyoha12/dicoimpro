from __future__ import annotations

import ast
import builtins
import importlib
import inspect
import sys

import pytest

from dico_impro.agents import (
    AgentAdapter,
    AgentNotFoundError,
    OpenAIAdapter,
    OpenAIAdapterConfigurationError,
    OpenAIAdapterDisabledError,
    OpenAIAdapterResponseError,
    QualityGateClassification,
    evaluate_agent_result,
    validate_agent_result_payload,
)
import dico_impro.agents.adapters.openai as openai_adapter_module
from dico_impro.contracts import AgentContract, AgentResult, AgentTask
from dico_impro.orchestration import ExplicitScope, build_default_registry, run_dry_run
from dico_impro.orchestration.task_builder import DEFAULT_DRY_RUN_AGENT_NAME


FORBIDDEN_IMPORT_ROOTS = {"openai", "requests", "httpx", "urllib", "socket"}


def make_contract() -> AgentContract:
    return AgentContract.model_validate(
        {
            "object_type": "AgentContract",
            "schema_version": "v0.2.3-auto",
            "created_by": "tests",
            "agent_name": "RoutingAgent",
            "agent_version": "v0.2.3-auto",
            "mission": "Produce a bounded structured mock object.",
            "allowed_inputs": ["EntryState"],
            "required_output_schema": "RoutingDecision",
            "forbidden_actions": ["write_active_journal", "launch_RUN", "openai_call"],
            "quality_gates": ["schema_validation"],
            "handoff_targets": [],
        }
    )


def make_task() -> AgentTask:
    return AgentTask.model_validate(
        {
            "object_type": "AgentTask",
            "schema_version": "v0.2.3-auto",
            "created_by": "tests",
            "task_id": "TASK_BATCH_001_026_ROUTING",
            "batch_id": "BATCH_001",
            "id_entree_original": "026",
            "titre_original_exact": "Entry title",
            "task_type": "routing",
            "agent_name": "RoutingAgent",
            "input_payload": {"mock_scenario": "success_valid"},
            "allowed_files": [],
            "forbidden_files": ["legacy_pdf", "active_journal", "data/local_files"],
            "expected_schema": "RoutingDecision",
        }
    )


def make_scope() -> ExplicitScope:
    return ExplicitScope.model_validate(
        {
            "batch_id": "BATCH_OPENAI_REJECTED",
            "entries": [{"id_entree_original": "026", "titre_original_exact": "First"}],
        }
    )


class DeterministicMockClient:
    def __init__(self, *, payload: dict[str, object] | None = None) -> None:
        self.calls: list[tuple[AgentTask, AgentContract]] = []
        self.payload = payload or {
            "object_type": "RoutingDecision",
            "schema_version": "v0.2.3-auto",
            "scenario": "success_valid",
            "status": "ok",
        }

    def run_task(self, *, task: AgentTask, contract: AgentContract) -> dict[str, object]:
        self.calls.append((task, contract))
        return {
            "result_id": f"MOCK_RESULT_{task.task_id}",
            "payload": self.payload,
            "warnings": [],
            "audit_notes": [],
            "raw_model_trace_ref": f"mock_trace:{task.task_id}:deterministic",
            "validation_status": "schema_valid",
        }


class FailingClient:
    def __init__(self) -> None:
        self.calls = 0

    def run_task(self, *, task: AgentTask, contract: AgentContract) -> dict[str, object]:
        self.calls += 1
        raise AssertionError("disabled OpenAIAdapter must not call the injected client")


def test_openai_adapter_matches_agent_adapter_protocol():
    assert isinstance(OpenAIAdapter(), AgentAdapter)
    assert OpenAIAdapter.adapter_type == "openai"


def test_importing_openai_adapter_does_not_import_openai_package(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.delitem(sys.modules, "openai", raising=False)
    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.partition(".")[0] == "openai":
            raise AssertionError("OpenAIAdapter must not import the openai package")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    module = importlib.import_module("dico_impro.agents.adapters.openai")

    assert module.OpenAIAdapter.adapter_type == "openai"
    assert "openai" not in sys.modules


def test_openai_adapter_source_has_no_network_library_imports():
    source = inspect.getsource(openai_adapter_module)

    for node in ast.walk(ast.parse(source)):
        imported_roots: list[str] = []
        if isinstance(node, ast.Import):
            imported_roots = [alias.name.partition(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_roots = [node.module.partition(".")[0]]

        assert FORBIDDEN_IMPORT_ROOTS.isdisjoint(imported_roots)


def test_disabled_openai_adapter_raises_before_client_use():
    client = FailingClient()
    adapter = OpenAIAdapter(client=client)

    with pytest.raises(OpenAIAdapterDisabledError, match="disabled"):
        adapter.run_task(make_task(), make_contract())

    assert client.calls == 0


def test_enabled_openai_adapter_without_client_raises_configuration_error():
    adapter = OpenAIAdapter(enabled=True)

    with pytest.raises(OpenAIAdapterConfigurationError, match="injected client"):
        adapter.run_task(make_task(), make_contract())


def test_enabled_openai_adapter_with_mock_client_returns_valid_agent_result():
    client = DeterministicMockClient()
    adapter = OpenAIAdapter(enabled=True, client=client)

    result = adapter.run_task(make_task(), make_contract())

    assert isinstance(result, AgentResult)
    assert result.created_by == "OpenAIAdapter"
    assert result.result_id == "MOCK_RESULT_TASK_BATCH_001_026_ROUTING"
    assert result.raw_model_trace_ref == "mock_trace:TASK_BATCH_001_026_ROUTING:deterministic"
    assert result.payload == {
        "object_type": "RoutingDecision",
        "schema_version": "v0.2.3-auto",
        "scenario": "success_valid",
        "status": "ok",
    }
    assert len(client.calls) == 1
    assert client.calls[0] == (make_task(), make_contract())

    validation = validate_agent_result_payload(result)
    assert validation.ok is True
    assert validation.reasons == ()


def test_openai_adapter_uses_openai_client_response_normalization():
    class TupleResponseClient:
        def __init__(self) -> None:
            self.calls = 0

        def run_task(self, *, task: AgentTask, contract: AgentContract) -> dict[str, object]:
            self.calls += 1
            return {
                "payload": {
                    "object_type": "RoutingDecision",
                    "schema_version": "v0.2.3-auto",
                    "scenario": "success_valid",
                    "status": "ok",
                },
                "warnings": ("tuple warning",),
                "audit_notes": ("tuple audit note",),
                "raw_model_trace_ref": f"mock_trace:{task.task_id}:tuple",
                "validation_status": "schema_valid",
            }

    client = TupleResponseClient()
    result = OpenAIAdapter(enabled=True, client=client).run_task(make_task(), make_contract())

    assert result.result_id == "OPENAI_RESULT_TASK_BATCH_001_026_ROUTING"
    assert result.warnings == ["tuple warning"]
    assert result.audit_notes == ["tuple audit note"]
    assert result.validation_status.value == "schema_valid"
    assert client.calls == 1


def test_openai_adapter_rejects_free_form_text_only_response():
    class TextOnlyClient:
        def __init__(self) -> None:
            self.calls = 0

        def run_task(self, *, task: AgentTask, contract: AgentContract) -> dict[str, object]:
            self.calls += 1
            return {"text": "unstructured model output"}

    client = TextOnlyClient()

    with pytest.raises(OpenAIAdapterResponseError, match="OpenAIClientResponse"):
        OpenAIAdapter(enabled=True, client=client).run_task(make_task(), make_contract())

    assert client.calls == 1


def test_openai_adapter_run_task_uses_no_forbidden_imports(monkeypatch: pytest.MonkeyPatch):
    client = DeterministicMockClient()
    adapter = OpenAIAdapter(enabled=True, client=client)
    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.partition(".")[0] in FORBIDDEN_IMPORT_ROOTS:
            raise AssertionError(f"forbidden import during OpenAIAdapter run_task: {name}")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    result = adapter.run_task(make_task(), make_contract())

    assert result.payload["status"] == "ok"
    assert len(client.calls) == 1


def test_openai_adapter_invalid_mock_payload_becomes_blocking_quality_gate():
    client = DeterministicMockClient(
        payload={
            "schema_version": "v0.2.3-auto",
            "scenario": "missing_object_type",
            "status": "ok",
        }
    )
    result = OpenAIAdapter(enabled=True, client=client).run_task(make_task(), make_contract())

    validation = validate_agent_result_payload(result)
    evaluation = evaluate_agent_result(result)

    assert validation.ok is False
    assert validation.reasons == ("payload missing object_type",)
    assert evaluation.classification == QualityGateClassification.BLOCKING
    assert evaluation.reasons == ("payload missing object_type",)


def test_default_dry_run_registry_remains_fake_only():
    registry = build_default_registry()

    registered = registry.get(DEFAULT_DRY_RUN_AGENT_NAME)
    assert registered.adapter_type == "fake"

    with pytest.raises(AgentNotFoundError):
        registry.get("OpenAIAdapter")


def test_run_dry_run_rejects_openai_adapter_before_client_call():
    client = DeterministicMockClient()

    with pytest.raises(TypeError, match="FakeAgentAdapter"):
        run_dry_run(make_scope(), adapter=OpenAIAdapter(enabled=True, client=client))

    assert client.calls == []
