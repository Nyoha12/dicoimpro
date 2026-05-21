from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any


class PipelineStep(StrEnum):
    LOAD_MANIFEST = "LOAD_MANIFEST"
    LOAD_PROJECT_STATE = "LOAD_PROJECT_STATE"
    BUILD_AGENT_TASKS = "BUILD_AGENT_TASKS"
    RUN_ROUTING_AGENT = "RUN_ROUTING_AGENT"
    RUN_SOURCE_AUDIT_AGENT = "RUN_SOURCE_AUDIT_AGENT"
    RUN_CLASSIFICATION_AGENT = "RUN_CLASSIFICATION_AGENT"
    APPLY_DETERMINISTIC_VALIDATION = "APPLY_DETERMINISTIC_VALIDATION"
    BUILD_FINAL_DECISION = "BUILD_FINAL_DECISION"
    BUILD_DELTA_RECORDS = "BUILD_DELTA_RECORDS"
    BUILD_JOURNAL_PATCH = "BUILD_JOURNAL_PATCH"
    WRITE_OUTPUT_ARTIFACTS = "WRITE_OUTPUT_ARTIFACTS"


@dataclass(frozen=True)
class PipelineConfig:
    batch_id: str
    manifest_path: Path = Path("data_manifest.yaml")
    output_root: Path = Path("data/outputs")
    dry_run: bool = True
    allow_direct_journal_write: bool = False
    use_legacy_pdf_by_default: bool = False


@dataclass
class PipelineState:
    config: PipelineConfig
    completed_steps: list[PipelineStep] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)

    def mark_done(self, step: PipelineStep) -> None:
        self.completed_steps.append(step)


def build_default_steps() -> list[PipelineStep]:
    return [
        PipelineStep.LOAD_MANIFEST,
        PipelineStep.LOAD_PROJECT_STATE,
        PipelineStep.BUILD_AGENT_TASKS,
        PipelineStep.RUN_ROUTING_AGENT,
        PipelineStep.RUN_SOURCE_AUDIT_AGENT,
        PipelineStep.RUN_CLASSIFICATION_AGENT,
        PipelineStep.APPLY_DETERMINISTIC_VALIDATION,
        PipelineStep.BUILD_FINAL_DECISION,
        PipelineStep.BUILD_DELTA_RECORDS,
        PipelineStep.BUILD_JOURNAL_PATCH,
        PipelineStep.WRITE_OUTPUT_ARTIFACTS,
    ]


def assert_pipeline_guards(config: PipelineConfig) -> None:
    if config.allow_direct_journal_write:
        raise ValueError("Direct journal writes are forbidden in v0.2.3-auto")
    if config.use_legacy_pdf_by_default:
        raise ValueError("Legacy PDF cannot be used by default")


__all__ = [
    "PipelineConfig",
    "PipelineState",
    "PipelineStep",
    "assert_pipeline_guards",
    "build_default_steps",
]
