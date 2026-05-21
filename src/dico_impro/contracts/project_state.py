from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field

from dico_impro.contracts.common import BatchScopedContract, NonEmptyStr


class AuditGravite(StrEnum):
    INFO = "info"
    JAUNE = "jaune"
    ORANGE = "orange"
    ROUGE = "rouge"


class EntryState(BatchScopedContract):
    object_type: Literal["EntryState"]
    id_entree_original: NonEmptyStr
    titre_original_exact: NonEmptyStr
    source_base_ref: NonEmptyStr | None = None
    triage_ref: NonEmptyStr | None = None
    journal_ref: NonEmptyStr | None = None
    statut_journal_connu: NonEmptyStr | None = None
    dernier_RUN_connu: NonEmptyStr | None = None
    a_ne_pas_retraiter_nouveau: bool
    est_archive_non_active: bool
    notes_etat: list[NonEmptyStr] = Field(default_factory=list)
    alertes_initiales: list[NonEmptyStr] = Field(default_factory=list)


class AuditQueueRecord(BatchScopedContract):
    object_type: Literal["AuditQueueRecord"]
    id_entree_original: NonEmptyStr
    titre_original_exact: NonEmptyStr | None = None
    audit_id: NonEmptyStr
    audit_gravite: AuditGravite
    audit_reason: list[NonEmptyStr] = Field(min_length=1)
    blocking_for_publication: bool
    blocking_for_processing: bool
    recommended_action: NonEmptyStr
    linked_objects: list[NonEmptyStr] = Field(default_factory=list)


__all__ = ["AuditGravite", "AuditQueueRecord", "EntryState"]
