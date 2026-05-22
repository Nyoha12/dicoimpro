from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime
from enum import Enum
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from dico_impro.orchestration import DryRunResult


BASE_EXPORT_FILES = {
    "batch_report": "batch_report.json",
    "batch_state": "batch_state.json",
    "agent_results": "agent_results.json",
    "quality_gates": "quality_gates.json",
    "evaluation_records": "evaluation_records.json",
}
OPTIONAL_EXPORT_FILES = {
    "journal_patch": "journal_patch.json",
    "audit_queue": "audit_queue.json",
}
MASTER_FILE_NAME = "master.json"


@dataclass(frozen=True)
class JsonExportReport:
    output_dir: Path
    created_files: dict[str, Path]


def export_dry_run_result_json(
    result: DryRunResult,
    output_dir: str | Path,
) -> JsonExportReport:
    if not isinstance(result, DryRunResult):
        raise TypeError("export_dry_run_result_json requires an existing DryRunResult")

    destination = Path(output_dir)
    if destination.exists() and not destination.is_dir():
        raise NotADirectoryError(f"export output path is not a directory: {destination}")
    destination.mkdir(parents=True, exist_ok=True)

    payloads: dict[str, Any] = {
        "batch_report": _to_json_compatible(result.batch_report),
        "batch_state": _to_json_compatible(result.batch_state),
        "agent_results": _to_json_compatible(result.agent_results),
        "quality_gates": _to_json_compatible(result.quality_gate_results),
        "evaluation_records": _to_json_compatible(result.evaluation_records),
    }
    for logical_name in OPTIONAL_EXPORT_FILES:
        optional_payload = getattr(result, logical_name, None)
        if optional_payload is not None:
            payloads[logical_name] = _to_json_compatible(optional_payload)

    created_files: dict[str, Path] = {}
    for logical_name, file_name in _selected_file_names(payloads).items():
        path = destination / file_name
        _write_json(path, payloads[logical_name])
        created_files[logical_name] = path

    master_path = destination / MASTER_FILE_NAME
    _write_json(master_path, _build_master_payload(result, created_files))

    return JsonExportReport(
        output_dir=destination,
        created_files={"master": master_path, **created_files},
    )


def _selected_file_names(payloads: Mapping[str, Any]) -> dict[str, str]:
    selected = dict(BASE_EXPORT_FILES)
    for logical_name, file_name in OPTIONAL_EXPORT_FILES.items():
        if logical_name in payloads:
            selected[logical_name] = file_name
    return selected


def _build_master_payload(result: DryRunResult, created_files: Mapping[str, Path]) -> dict[str, Any]:
    return {
        "object_type": "DryRunJsonExport",
        "source_object_type": "DryRunResult",
        "batch_id": result.batch_report.batch_id,
        "files": {logical_name: path.name for logical_name, path in created_files.items()},
        "counts": {
            "tasks": len(result.tasks),
            "agent_results": len(result.agent_results),
            "quality_gates": len(result.quality_gate_results),
            "evaluation_records": len(result.evaluation_records),
        },
    }


def _write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def _to_json_compatible(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return _to_json_compatible(value.model_dump(mode="json"))
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
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


__all__ = ["JsonExportReport", "export_dry_run_result_json"]
