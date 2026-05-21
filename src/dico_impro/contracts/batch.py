from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field, NonNegativeInt, model_validator

from dico_impro.contracts.common import BatchScopedContract, NonEmptyStr


class BatchStatus(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    COMPLETED_CLEAN = "completed_clean"
    FAILED_RECOVERABLE = "failed_recoverable"
    FAILED_BLOCKING = "failed_blocking"
    CANCELLED = "cancelled"


class BatchState(BatchScopedContract):
    object_type: Literal["BatchState"] = "BatchState"
    created_at: NonEmptyStr
    status: BatchStatus
    steps_completed: list[NonEmptyStr] = Field(default_factory=list)
    entries_scope: list[NonEmptyStr] = Field(default_factory=list)
    artifacts: list[NonEmptyStr] = Field(default_factory=list)
    errors_recoverable: list[NonEmptyStr] = Field(default_factory=list)
    errors_blocking: list[NonEmptyStr] = Field(default_factory=list)
    replay_command: NonEmptyStr | None = None


class BatchReport(BatchScopedContract):
    object_type: Literal["BatchReport"] = "BatchReport"
    protocol_version: NonEmptyStr
    automation_layer: NonEmptyStr
    entries_total: NonNegativeInt
    entries_processed: NonNegativeInt
    entries_skipped: NonNegativeInt
    entries_blocked: NonNegativeInt
    run_002_requested: NonNegativeInt
    publication_blocked: NonNegativeInt
    audit_queue_count: NonNegativeInt
    journal_patch_id: NonEmptyStr | None = None
    artifacts: list[NonEmptyStr] = Field(default_factory=list)
    summary_human: NonEmptyStr
    warnings: list[NonEmptyStr] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_entry_counts(self) -> BatchReport:
        accounted_entries = self.entries_processed + self.entries_skipped + self.entries_blocked
        if accounted_entries > self.entries_total:
            raise ValueError("processed, skipped and blocked entries cannot exceed entries_total")
        return self


__all__ = ["BatchReport", "BatchState", "BatchStatus"]
