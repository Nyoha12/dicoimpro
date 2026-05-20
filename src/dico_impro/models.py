from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TypeUniteRun(StrEnum):
    FICHE_PRATIQUE = "fiche_pratique"
    FICHE_CADRE = "fiche_cadre"
    FICHE_FAMILLE = "fiche_famille"
    MECANISME_PASSERELLE = "mecanisme_passerelle"
    CONTROLE_PERIMETRE = "controle_perimetre"
    ALIAS_DOUBLON = "alias_doublon"


class DecisionPreRun(StrEnum):
    PRET_RUN_001_FICHE_PRATIQUE = "pret_RUN_001_fiche_pratique"
    PRET_RUN_001_FICHE_CADRE = "pret_RUN_001_fiche_cadre"
    MECANISME_PASSERELLE = "mecanisme_passerelle"
    CONTROLE_PERIMETRE_AVANT_RUN = "controle_perimetre_avant_RUN"
    RESTER_FICHE_FAMILLE = "rester_fiche_famille"
    VERIFIER_ALIAS_DOUBLON = "verifier_alias_doublon"


class StatutUniteClassable(StrEnum):
    CLASSABLE_COMME_FICHE_UNIQUE = "classable_comme_fiche_unique"
    FICHE_FAMILLE_A_DEPLIER = "fiche_famille_a_deplier"
    AGREGAT_A_SCINDER = "agregat_a_scinder"
    MECANISME_PASSERELLE = "mecanisme_passerelle"
    DOUBLON_OU_ALIAS = "doublon_ou_alias"
    A_VERIFIER = "a_verifier"


class Indices(BaseModel):
    model_config = ConfigDict(extra="forbid")

    D: str | None = None
    S: str | None = None
    I: str | None = None
    C: str | None = None
    E: str | None = None


class RoutingDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_type: Literal["RoutingDecision"] = "RoutingDecision"
    id_entree_original: str
    titre_original_exact: str
    statut_unite_classable: StatutUniteClassable
    type_unite_RUN: TypeUniteRun
    decision_pre_RUN: DecisionPreRun
    run_autorise: bool
    run_interdit_raison: list[str] = Field(default_factory=list)
    question_documentaire_prioritaire: str | None = None
    risque_perte_donnees: str | None = None
    alerte_doublon: bool = False
    alerte_scission: bool = False
    alerte_passerelle: bool = False
    conservation_parent_requise: bool = True
    sous_pistes_a_conserver: list[str] = Field(default_factory=list)
    justification_courte: str | None = None


class CorrectionAutomatique(BaseModel):
    model_config = ConfigDict(extra="forbid")

    champ: str
    avant: str | None
    apres: str | None
    raison: str
    regle: str


class Run002Cible(BaseModel):
    model_config = ConfigDict(extra="forbid")

    champ: str
    faiblesse: str
    question_ciblee: str


class ValidationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_type: Literal["ValidationReport"] = "ValidationReport"
    id_entree_original: str
    validation_status: str
    indices_avant_validation: Indices
    indices_apres_validation: Indices
    corrections_automatiques: list[CorrectionAutomatique] = Field(default_factory=list)
    run_002_requis: bool = False
    run_002_cible: list[Run002Cible] = Field(default_factory=list)
    audit_queue_requis: bool = False
    audit_gravite: str | None = None
    publication_bloquee: bool = False
    justification_courte: str | None = None


class SourceAuditInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str
    role_source: str
    source_decisive: Literal["oui", "non", "partiel"]
    verification_independante: bool = False
    est_plateforme_acces: bool = False


class ClassificationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_entree_original: str
    indices: Indices
    sources: list[SourceAuditInput] = Field(default_factory=list)
    preuve_improvisation_centrale_explicitement_documentee: bool = False
    perimetre_stable: bool = False
    exception_S_A_justifiee: bool = False
