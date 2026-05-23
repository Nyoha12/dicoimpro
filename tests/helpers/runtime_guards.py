from __future__ import annotations

import builtins
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from enum import Enum
import json
from pathlib import Path
import socket
from typing import Any

from pydantic import BaseModel

from dico_impro import cli
from dico_impro.agents import prompt_contracts
from dico_impro.agents.adapters.openai import OpenAIAdapter
import dico_impro.orchestration.mock_openai_plan as mock_openai_plan


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src" / "dico_impro"
PROMPT_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "prompt_packages"

DEFAULT_CLI_FORBIDDEN_ROOTS = (
    REPO_ROOT / "data" / "local_files",
    REPO_ROOT / "data" / "active_journal",
    PROMPT_FIXTURE_DIR,
)
DEFAULT_CLI_FORBIDDEN_FILES = (SRC_DIR / "agents" / "prompts.py",)


def write_explicit_scope(
    path: Path,
    *,
    batch_id: str,
    entries: Sequence[Mapping[str, object]],
) -> None:
    path.write_text(
        json.dumps({"batch_id": batch_id, "entries": [dict(entry) for entry in entries]}),
        encoding="utf-8",
    )


def invoke_cli(argv: list[str], capsys: Any) -> tuple[int, str, str]:
    try:
        exit_code = cli.main(argv)
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def load_json_exports(output_dir: Path) -> dict[str, Any]:
    return {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(output_dir.iterdir())
    }


def assert_no_forbidden_fragments(
    payload: object,
    forbidden_fragments: tuple[str, ...],
    context: str,
) -> None:
    serialized = json.dumps(to_json_compatible(payload), ensure_ascii=False, sort_keys=True)
    normalized = serialized.casefold()
    present = [
        fragment
        for fragment in forbidden_fragments
        if fragment.casefold() in normalized
    ]
    assert not present, f"{context} must not contain forbidden fragments: {present!r}"


def to_json_compatible(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return to_json_compatible(value.model_dump(mode="json"))
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: to_json_compatible(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, dict):
        return {str(key): to_json_compatible(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_compatible(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [to_json_compatible(item) for item in sorted(value, key=repr)]
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"Object of type {type(value).__name__} is not JSON compatible")


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def guard_filesystem_to_tmp_path(
    tmp_path: Path,
    monkeypatch: Any,
    *,
    context: str,
    forbidden_roots: Iterable[Path] = DEFAULT_CLI_FORBIDDEN_ROOTS,
    forbidden_files: Iterable[Path] = DEFAULT_CLI_FORBIDDEN_FILES,
    guard_glob: bool = True,
) -> None:
    tmp_root = tmp_path.absolute()
    forbidden_roots_tuple = tuple(root.absolute() for root in forbidden_roots)
    forbidden_files_tuple = tuple(path.absolute() for path in forbidden_files)

    def normalize_path(pathish: object) -> Path | None:
        if not isinstance(pathish, (str, Path)):
            return None
        path = Path(pathish)
        if not path.is_absolute():
            path = REPO_ROOT / path
        return path.absolute()

    def assert_allowed_path(pathish: object) -> None:
        path = normalize_path(pathish)
        if path is None:
            return
        for forbidden_root in forbidden_roots_tuple:
            if is_relative_to(path, forbidden_root):
                raise AssertionError(f"{context} touched forbidden path: {path}")
        if any(path == forbidden_file for forbidden_file in forbidden_files_tuple):
            raise AssertionError(f"{context} touched forbidden file: {path}")
        assert is_relative_to(path, tmp_root), (
            f"{context} must only read/write pytest tmp_path files. Touched: {path}"
        )

    original_builtin_open = builtins.open
    original_path_open = Path.open
    original_path_exists = Path.exists
    original_path_is_dir = Path.is_dir
    original_path_is_file = Path.is_file
    original_path_mkdir = Path.mkdir
    original_path_iterdir = Path.iterdir
    original_path_glob = Path.glob
    original_path_rglob = Path.rglob

    def guarded_builtin_open(file: object, *args: object, **kwargs: object) -> Any:
        assert_allowed_path(file)
        return original_builtin_open(file, *args, **kwargs)

    def guarded_path_open(self: Path, *args: object, **kwargs: object) -> Any:
        assert_allowed_path(self)
        return original_path_open(self, *args, **kwargs)

    def guarded_path_exists(self: Path) -> bool:
        assert_allowed_path(self)
        return original_path_exists(self)

    def guarded_path_is_dir(self: Path) -> bool:
        assert_allowed_path(self)
        return original_path_is_dir(self)

    def guarded_path_is_file(self: Path) -> bool:
        assert_allowed_path(self)
        return original_path_is_file(self)

    def guarded_path_mkdir(self: Path, *args: object, **kwargs: object) -> None:
        assert_allowed_path(self)
        return original_path_mkdir(self, *args, **kwargs)

    def guarded_path_iterdir(self: Path) -> Any:
        assert_allowed_path(self)
        return original_path_iterdir(self)

    def guarded_path_glob(self: Path, pattern: str) -> Any:
        assert_allowed_path(self)
        return original_path_glob(self, pattern)

    def guarded_path_rglob(self: Path, pattern: str) -> Any:
        assert_allowed_path(self)
        return original_path_rglob(self, pattern)

    monkeypatch.setattr(builtins, "open", guarded_builtin_open)
    monkeypatch.setattr(Path, "open", guarded_path_open)
    monkeypatch.setattr(Path, "exists", guarded_path_exists)
    monkeypatch.setattr(Path, "is_dir", guarded_path_is_dir)
    monkeypatch.setattr(Path, "is_file", guarded_path_is_file)
    monkeypatch.setattr(Path, "mkdir", guarded_path_mkdir)
    monkeypatch.setattr(Path, "iterdir", guarded_path_iterdir)
    if guard_glob:
        monkeypatch.setattr(Path, "glob", guarded_path_glob)
        monkeypatch.setattr(Path, "rglob", guarded_path_rglob)


def guard_network_calls(monkeypatch: Any, *, context: str) -> None:
    def fail_network_call(*args: object, **kwargs: object) -> None:
        raise AssertionError(f"{context} must not access the network")

    monkeypatch.setattr(socket, "socket", fail_network_call)
    monkeypatch.setattr(socket, "create_connection", fail_network_call)


def guard_openai_adapter_use(
    monkeypatch: Any,
    *,
    context: str,
    patch_mock_plan_symbol: bool = False,
) -> None:
    def fail_openai_adapter_use(*args: object, **kwargs: object) -> None:
        raise AssertionError(f"{context} must not use OpenAIAdapter")

    monkeypatch.setattr(OpenAIAdapter, "__init__", fail_openai_adapter_use)
    monkeypatch.setattr(OpenAIAdapter, "run_task", fail_openai_adapter_use)
    if patch_mock_plan_symbol:
        monkeypatch.setattr(mock_openai_plan, "OpenAIAdapter", OpenAIAdapter)


def guard_prompt_package_consumption(monkeypatch: Any, *, context: str) -> None:
    def fail_prompt_package_consumption(*args: object, **kwargs: object) -> None:
        raise AssertionError(f"{context} must not consume PromptPackage metadata")

    monkeypatch.setattr(
        prompt_contracts.PromptPackage,
        "model_validate",
        classmethod(fail_prompt_package_consumption),
    )
    monkeypatch.setattr(
        prompt_contracts.PromptPackage,
        "__init__",
        fail_prompt_package_consumption,
    )


def guard_cli_runtime_boundaries(
    tmp_path: Path,
    monkeypatch: Any,
    *,
    context: str,
) -> None:
    guard_filesystem_to_tmp_path(tmp_path, monkeypatch, context=context)
    guard_network_calls(monkeypatch, context=context)
    guard_openai_adapter_use(
        monkeypatch,
        context=context,
        patch_mock_plan_symbol=True,
    )
    guard_prompt_package_consumption(monkeypatch, context=context)
