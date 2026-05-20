from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field


class ManifestFile(BaseModel):
    model_config = ConfigDict(extra="allow")

    file_name: str
    local_path: str
    status: str
    role: str
    layer: str | None = None
    may_be_used_as_documentary_source: bool = False
    may_be_written_directly_by_pipeline: bool = False


class DataManifest(BaseModel):
    model_config = ConfigDict(extra="allow")

    project: str
    protocol_version: str
    automation_layer: str
    local_files_root: str = "data/local_files/"
    files: list[ManifestFile] = Field(default_factory=list)

    def by_file_name(self) -> dict[str, ManifestFile]:
        return {item.file_name: item for item in self.files}

    def documentary_files(self) -> list[ManifestFile]:
        return [item for item in self.files if item.may_be_used_as_documentary_source]

    def writable_files(self) -> list[ManifestFile]:
        return [item for item in self.files if item.may_be_written_directly_by_pipeline]


def load_manifest(path: str | Path = "data_manifest.yaml") -> DataManifest:
    manifest_path = Path(path)
    with manifest_path.open("r", encoding="utf-8") as handle:
        raw: dict[str, Any] = yaml.safe_load(handle)
    return DataManifest.model_validate(raw)


def planned_local_paths(manifest: DataManifest) -> list[Path]:
    return [Path(item.local_path) for item in manifest.files]


__all__ = ["DataManifest", "ManifestFile", "load_manifest", "planned_local_paths"]
