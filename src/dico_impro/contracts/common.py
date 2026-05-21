from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


SCHEMA_VERSION = "v0.2.3-auto"
SchemaVersion = Literal["v0.2.3-auto"]
NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class VersionedContract(StrictContractModel):
    schema_version: SchemaVersion
    created_by: NonEmptyStr


class BatchScopedContract(VersionedContract):
    batch_id: NonEmptyStr


class PrudenceLevel(StrEnum):
    FAIBLE = "faible"
    MOYEN = "moyen"
    ELEVE = "eleve"
    BLOQUANT = "bloquant"


class ValidationStatus(StrEnum):
    SCHEMA_VALID = "schema_valid"
    SCHEMA_INVALID = "schema_invalid"
    VALIDE_SANS_CORRECTION = "valide_sans_correction"
    VALIDE_AVEC_CORRECTIONS = "valide_avec_corrections"
    RUN_002_AUTO_REQUIS = "run_002_auto_requis"
    NON_PUBLIABLE_EN_L_ETAT = "non_publiable_en_l_etat"
    AUDIT_HUMAIN_REQUIS = "audit_humain_requis"


class PublicationStatus(StrEnum):
    PUBLIABLE = "publiable"
    PUBLIABLE_AVEC_NOTE = "publiable_avec_note"
    PUBLICATION_BLOQUEE = "publication_bloquee"
    NON_PUBLIABLE_COMME_FICHE_PRATIQUE = "non_publiable_comme_fiche_pratique"
    PUBLICATION_DIFFEREE = "publication_differee"


class GoldenSetCase(VersionedContract):
    object_type: Literal["GoldenSetCase"]
    case_id: NonEmptyStr
    id_entree_original: NonEmptyStr
    titre_original_exact: NonEmptyStr | None = None
    purpose: NonEmptyStr
    input_fixture_refs: list[NonEmptyStr] = Field(default_factory=list)
    expected_must: list[NonEmptyStr] = Field(default_factory=list)
    expected_must_not: list[NonEmptyStr] = Field(default_factory=list)
    expected_alerts: list[NonEmptyStr] = Field(default_factory=list)
    expected_publication_status: PublicationStatus | None = None
    notes: NonEmptyStr | None = None


__all__ = [
    "BatchScopedContract",
    "GoldenSetCase",
    "NonEmptyStr",
    "PrudenceLevel",
    "PublicationStatus",
    "SCHEMA_VERSION",
    "SchemaVersion",
    "StrictContractModel",
    "ValidationStatus",
    "VersionedContract",
]
