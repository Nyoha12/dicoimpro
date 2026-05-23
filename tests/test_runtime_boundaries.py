from __future__ import annotations

import ast
import builtins
import json
from pathlib import Path
import sys
from typing import Any

import pytest

from dico_impro.agents import prompt_contracts
from dico_impro.agents.adapters.openai import OpenAIAdapter
from dico_impro.contracts.common import SCHEMA_VERSION
from dico_impro.orchestration import ExplicitScope, plan_batch_with_mock_openai
import dico_impro.orchestration.mock_openai_plan as mock_openai_plan
from helpers.runtime_guards import (
    PROMPT_FIXTURE_DIR,
    REPO_ROOT,
    SRC_DIR,
    assert_no_forbidden_fragments,
    guard_cli_runtime_boundaries,
    guard_network_calls,
    guard_prompt_package_consumption,
    invoke_cli,
    load_json_exports,
    write_explicit_scope,
)

FORBIDDEN_DIRECT_MODULES = ("openai", "requests", "httpx", "urllib3", "socket")
FORBIDDEN_DOTTED_MODULES = ("urllib.request",)
CLI_SCOPE_BATCH_ID = "BATCH_BOUNDARY_CLI"
CLI_SCOPE_ENTRIES = (
    {
        "id_entree_original": "BOUNDARY_ENTRY_001",
        "titre_original_exact": "Temporary boundary scope entry one",
        "fake_scenario": "success_valid",
    },
    {
        "id_entree_original": "BOUNDARY_ENTRY_002",
        "titre_original_exact": "Temporary boundary scope entry two",
        "fake_scenario": "success_valid",
    },
)
FORBIDDEN_OUTPUT_FRAGMENTS = (
    "OpenAIAdapter",
    "PromptPackage",
    "prompt_body_ref",
    "SourceDiscoveryAgent",
    "JournalPatch",
    "data/local_files",
    "data/active_journal",
    "active_journal",
    ".xlsx",
    ".csv",
    "candidate",
)
FORBIDDEN_OPERATIONAL_FRAGMENTS = (
    "PromptPackage",
    "prompt_body_ref",
    "SourceDiscoveryAgent",
    "JournalPatch",
    "data/local_files",
    "data/active_journal",
    "active_journal",
    ".xlsx",
    ".csv",
    "candidate",
)
FORBIDDEN_PROMPT_PHRASES = (
    "developer message",
    "follow these instructions",
    "system prompt",
    "system:",
    "user prompt",
    "user:",
    "you are",
)


def runtime_source_paths() -> list[Path]:
    return sorted(SRC_DIR.rglob("*.py"))


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        if parent is None:
            return None
        return f"{parent}.{node.attr}"
    return None


def forbidden_label_for_dotted_name(name: str) -> str | None:
    for forbidden in FORBIDDEN_DOTTED_MODULES:
        if name == forbidden or name.startswith(f"{forbidden}."):
            return forbidden

    root = name.partition(".")[0]
    if root in FORBIDDEN_DIRECT_MODULES:
        return root
    return None


def import_issues_for_node(node: ast.AST, path: Path, lines: list[str]) -> list[str]:
    issues: list[str] = []
    relative = path.relative_to(REPO_ROOT)

    if isinstance(node, ast.Import):
        for alias in node.names:
            label = forbidden_label_for_dotted_name(alias.name)
            if label is None:
                continue
            issues.append(
                f"{relative}:{node.lineno} imports forbidden integration {label!r}: "
                f"{lines[node.lineno - 1].strip()}"
            )
    elif isinstance(node, ast.ImportFrom):
        module = node.module or ""
        imported_names = {alias.name for alias in node.names}

        label = forbidden_label_for_dotted_name(module)
        if label is None and module == "urllib" and "request" in imported_names:
            label = "urllib.request"
        if label is None:
            return issues

        issues.append(
            f"{relative}:{node.lineno} imports forbidden integration {label!r}: "
            f"{lines[node.lineno - 1].strip()}"
        )

    return issues


def source_usage_issues_for_node(node: ast.AST, path: Path, lines: list[str]) -> list[str]:
    if isinstance(node, ast.Import | ast.ImportFrom):
        return []

    name = dotted_name(node)
    if name is None:
        return []

    label = forbidden_label_for_dotted_name(name)
    if label is None:
        return []

    relative = path.relative_to(REPO_ROOT)
    return [
        f"{relative}:{node.lineno} uses forbidden integration {label!r}: "
        f"{lines[node.lineno - 1].strip()}"
    ]


def valid_mock_openai_payload() -> dict[str, object]:
    return {
        "object_type": "RoutingDecision",
        "schema_version": SCHEMA_VERSION,
        "scenario": "success_valid",
        "status": "ok",
    }


class BoundaryMockOpenAIClient:
    def __init__(self) -> None:
        self.calls: list[tuple[object, object]] = []

    def run_task(self, *, task: object, contract: object) -> dict[str, object]:
        self.calls.append((task, contract))
        task_id = getattr(task, "task_id")
        return {
            "result_id": f"BOUNDARY_MOCK_RESULT_{task_id}",
            "payload": valid_mock_openai_payload(),
            "warnings": [],
            "audit_notes": [],
            "raw_model_trace_ref": f"mock_openai_trace:{task_id}:boundary",
            "validation_status": "schema_valid",
        }


def make_explicit_scope() -> ExplicitScope:
    return ExplicitScope.model_validate(
        {
            "batch_id": "BATCH_BOUNDARY_MOCK",
            "entries": [
                {
                    "id_entree_original": "BOUNDARY_MOCK_ENTRY_001",
                    "titre_original_exact": "Temporary mock boundary entry",
                }
            ],
        }
    )


def operational_result_payload(result: object) -> dict[str, object]:
    return {
        "batch_state": getattr(result, "batch_state"),
        "batch_report": getattr(result, "batch_report"),
        "agent_results": getattr(result, "agent_results"),
        "quality_gate_results": getattr(result, "quality_gate_results"),
        "evaluation_records": getattr(result, "evaluation_records"),
    }


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


def test_runtime_source_has_no_direct_forbidden_network_imports_or_usages() -> None:
    issues: list[str] = []

    for path in runtime_source_paths():
        source = read_source(path)
        lines = source.splitlines()
        tree = ast.parse(source, filename=str(path))

        for node in ast.walk(tree):
            issues.extend(import_issues_for_node(node, path, lines))
            issues.extend(source_usage_issues_for_node(node, path, lines))

    assert not issues, (
        "Runtime source must stay free of direct OpenAI/network integrations "
        "(openai, requests, httpx, urllib.request, urllib3, socket).\n"
        + "\n".join(issues)
    )


def test_cli_dry_run_runtime_boundary_is_fake_only_and_tmp_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    scope_path = tmp_path / "scope.json"
    output_dir = tmp_path / "exports"
    write_explicit_scope(scope_path, batch_id=CLI_SCOPE_BATCH_ID, entries=CLI_SCOPE_ENTRIES)
    guard_cli_runtime_boundaries(tmp_path, monkeypatch, context="CLI dry-run boundary")

    exit_code, stdout, stderr = invoke_cli(
        [
            "plan-batch",
            "--dry-run",
            "--scope",
            str(scope_path),
            "--output-dir",
            str(output_dir),
        ],
        capsys,
    )

    assert exit_code == 0, f"CLI dry-run must succeed. stdout={stdout!r} stderr={stderr!r}"
    assert stderr == "", f"CLI dry-run boundary must not write stderr: {stderr!r}"

    summary = json.loads(stdout)
    assert summary["ok"] is True
    assert summary["batch_id"] == CLI_SCOPE_BATCH_ID
    assert summary["output_dir"] == str(output_dir)

    output_paths = sorted(output_dir.iterdir())
    output_names = {path.name for path in output_paths}
    assert output_names == set(summary["created_files"])
    assert output_names, "CLI dry-run must create JSON audit outputs"
    assert all(path.suffix == ".json" for path in output_paths), (
        f"CLI dry-run must only create JSON files. Found: {sorted(output_names)!r}"
    )

    parsed_outputs = load_json_exports(output_dir)
    assert "FakeAgentAdapter" in json.dumps(parsed_outputs, ensure_ascii=False)
    assert "fake_trace:" in json.dumps(parsed_outputs, ensure_ascii=False)

    batch_state = parsed_outputs["batch_state.json"]
    batch_report = parsed_outputs["batch_report.json"]
    assert batch_state["artifacts"] == []
    assert batch_state["replay_command"] is None
    assert batch_report["artifacts"] == []
    assert batch_report["journal_patch_id"] is None
    assert batch_report["run_002_requested"] == 0
    assert batch_report["entries_processed"] == len(CLI_SCOPE_ENTRIES)

    assert_no_forbidden_fragments(
        {"summary": summary, "outputs": parsed_outputs},
        FORBIDDEN_OUTPUT_FRAGMENTS,
        "CLI dry-run JSON outputs",
    )


def test_mock_openai_planning_boundary_uses_only_injected_mock_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delitem(sys.modules, "openai", raising=False)
    client = BoundaryMockOpenAIClient()
    adapter_init_calls: list[tuple[bool, object | None]] = []
    adapter_run_calls: list[tuple[object, object]] = []

    class SpyOpenAIAdapter(OpenAIAdapter):
        def __init__(self, *, enabled: bool = False, client: object | None = None) -> None:
            adapter_init_calls.append((enabled, client))
            super().__init__(enabled=enabled, client=client)

        def run_task(self, task: object, contract: object) -> object:
            assert self.enabled is True
            assert self._client is client
            adapter_run_calls.append((task, contract))
            return super().run_task(task, contract)  # type: ignore[arg-type]

    original_builtin_open = builtins.open
    original_path_open = Path.open
    original_path_read_text = Path.read_text
    original_path_write_text = Path.write_text
    real_import = builtins.__import__

    def fail_file_access(*args: object, **kwargs: object) -> None:
        raise AssertionError("mock OpenAI planning boundary must not access files")

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.partition(".")[0] in {"openai", "requests", "httpx", "urllib3"}:
            raise AssertionError(f"mock OpenAI planning imported forbidden module: {name}")
        if name == "urllib.request":
            raise AssertionError("mock OpenAI planning imported urllib.request")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(mock_openai_plan, "OpenAIAdapter", SpyOpenAIAdapter)
    monkeypatch.setattr(builtins, "open", fail_file_access)
    monkeypatch.setattr(Path, "open", fail_file_access)
    monkeypatch.setattr(Path, "read_text", fail_file_access)
    monkeypatch.setattr(Path, "write_text", fail_file_access)
    guard_network_calls(monkeypatch, context="mock OpenAI planning boundary")
    monkeypatch.setattr(builtins, "__import__", guarded_import)
    guard_prompt_package_consumption(monkeypatch, context="mock OpenAI planning boundary")

    result = plan_batch_with_mock_openai(
        make_explicit_scope(),
        client,
        created_at="2026-05-23T00:00:00Z",
    )

    assert adapter_init_calls == [(True, client)]
    assert len(adapter_run_calls) == 1
    assert len(client.calls) == 1
    assert client.calls == adapter_run_calls
    assert "openai" not in sys.modules
    assert builtins.open is not original_builtin_open
    assert Path.open is not original_path_open
    assert Path.read_text is not original_path_read_text
    assert Path.write_text is not original_path_write_text

    assert result.batch_report.entries_total == 1
    assert result.batch_report.entries_processed == 1
    assert result.batch_report.entries_blocked == 0
    assert result.batch_report.run_002_requested == 0
    assert result.batch_report.journal_patch_id is None
    assert result.batch_report.artifacts == []
    assert result.batch_state.artifacts == []
    assert result.batch_state.replay_command is None

    agent_result = result.agent_results[0]
    assert agent_result.created_by == "OpenAIAdapter"
    assert agent_result.raw_model_trace_ref == (
        f"mock_openai_trace:{result.tasks[0].task_id}:boundary"
    )
    assert result.evaluation_records[0].trace_metadata.adapter_type == "openai"
    assert result.evaluation_records[0].trace_metadata.raw_trace_ref == (
        agent_result.raw_model_trace_ref
    )

    task = result.tasks[0]
    assert task.allowed_files == []
    assert set(task.input_payload) == {
        "explicit_scope_index",
        "scope_entry",
        "fake_scenario",
    }
    assert "candidate" not in json.dumps(task.input_payload, ensure_ascii=False).casefold()

    assert_no_forbidden_fragments(
        operational_result_payload(result),
        FORBIDDEN_OPERATIONAL_FRAGMENTS,
        "mock OpenAI operational payload",
    )


def test_prompt_package_fixture_boundary_is_disabled_metadata_only() -> None:
    fixture_paths = sorted(PROMPT_FIXTURE_DIR.glob("*.json"))
    assert fixture_paths, f"PromptPackage fixture directory is empty: {PROMPT_FIXTURE_DIR}"

    forbidden_inline_fields = set(prompt_contracts.FORBIDDEN_INLINE_PROMPT_FIELDS)
    required_guardrails = set(prompt_contracts.REQUIRED_PROMPT_GUARDRAILS)
    required_forbidden_context_keys = set(prompt_contracts.REQUIRED_FORBIDDEN_CONTEXT_KEYS)

    for path in fixture_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        package = prompt_contracts.PromptPackage.model_validate(data)

        assert data.get("enabled") is False, f"{path.name} must keep enabled=false"
        assert package.enabled is False, f"{path.name} must validate as disabled"
        assert forbidden_inline_fields.isdisjoint(iter_keys(data)), (
            f"{path.name} must remain metadata-only; forbidden inline prompt fields "
            f"present: {sorted(forbidden_inline_fields.intersection(iter_keys(data)))!r}"
        )
        assert required_guardrails.issubset(set(data["required_guardrails"]))
        assert required_forbidden_context_keys.issubset(set(data["forbidden_context_keys"]))

        for value in iter_strings(data):
            lowered_value = value.casefold()
            assert "\n" not in value, f"{path.name} contains multiline prompt-like text"
            assert len(value) <= 80, f"{path.name} contains long prompt-like text: {value!r}"
            assert not any(phrase in lowered_value for phrase in FORBIDDEN_PROMPT_PHRASES), (
                f"{path.name} contains prompt-like text: {value!r}"
            )


def test_prompt_package_runtime_boundary_is_contract_only_and_no_prompts_module() -> None:
    prompts_module = SRC_DIR / "agents" / "prompts.py"
    assert not prompts_module.exists(), f"prompts.py must not exist: {prompts_module}"

    allowed_prompt_package_sources = {
        Path("src/dico_impro/agents/prompt_contracts.py"),
        Path("src/dico_impro/agents/__init__.py"),
    }
    issues: list[str] = []

    for path in runtime_source_paths():
        relative = path.relative_to(REPO_ROOT)
        if relative in allowed_prompt_package_sources:
            continue

        source = read_source(path)
        lines = source.splitlines()
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imported_names = {alias.name for alias in node.names}
                if "PromptPackage" in imported_names:
                    issues.append(
                        f"{relative}:{node.lineno} imports PromptPackage: "
                        f"{lines[node.lineno - 1].strip()}"
                    )
            elif isinstance(node, ast.Name) and node.id == "PromptPackage":
                issues.append(
                    f"{relative}:{node.lineno} uses PromptPackage outside prompt_contracts: "
                    f"{lines[node.lineno - 1].strip()}"
                )

        lowered_source = source.casefold()
        assert "prompt_body_ref" not in lowered_source, (
            f"{relative} must not consume PromptPackage prompt_body_ref metadata"
        )

    assert not issues, (
        "Runtime modules must not consume PromptPackage outside prompt_contracts; "
        "agents/__init__.py is allowed only as the existing public API re-export.\n"
        + "\n".join(issues)
    )
