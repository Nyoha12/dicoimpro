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


class StatutTraitement(StrEnum):
    JAMAIS_TRAITE = "jamais_traite"
    CONTROLE_TRIAGE_FAIT = "controle_triage_fait"
    RUN_001_FAIT = "RUN_001_fait"
    RUN_002_FAIT = "RUN_002_fait"
    STABLE = "stable"
    ACCEPTE_AVEC_PRUDENCE = "accepté_avec_prudence"
    FICHE_CADRE = "fiche_cadre"
    A_REVOIR = "à_revoir"
    TRAITE_NON_PUBLIABLE = "traité_non_publiable"
    A_REJOUER = "a_rejouer"


class DecisionFinaleProvisoire(StrEnum):
    STABLE = "stable"
    STABLE_COMME_FICHE_CADRE = "stable_comme_fiche_cadre"
    ACCEPTE_AVEC_PRUDENCE = "accepté_avec_prudence"
    RESTER_FICHE_FAMILLE = "rester_fiche_famille"
    CONTROLE_PERIMETRE_AVANT_RUN = "controle_perimetre_avant_RUN"
    MECANISME_PASSERELLE = "mecanisme_passerelle"
    VERIFIER_ALIAS_DOUBLON = "verifier_alias_doublon"
    A_SCINDER_PLUS_TARD = "a_scinder_plus_tard"
    A_REVOIR_APRES_RUN_002 = "à_revoir_après_RUN_002"
    BLOQUE_PAR_INCOHERENCE_PROTOCOLE = "bloqué_par_incohérence_protocolaire"
    NON_RETRAITER_COMME_NOUVEAU = "non_retraiter_comme_nouveau"


class PublicationStatus(StrEnum):
    PUBLIABLE = "publiable"
    PUBLIABLE_AVEC_NOTE = "publiable_avec_note"
    PUBLICATION_BLOQUEE = "publication_bloquée"
    NON_PUBLIABLE_COMME_FICHE_PRATIQUE = "non_publiable_comme_fiche_pratique"
    PUBLICATION_DIFFEREE = "publication_differee"


class AuditStatus(StrEnum):
    AUDIT_ROUGE = "audit_rouge"
    AUDIT_ORANGE = "audit_orange"
    AUDIT_JAUNE = "audit_jaune"
    AUDIT_INFO = "audit_info"
    AUCUN_AUDIT_REQUIS = "aucun_audit_requis"


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


class DeltaRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_type: Literal["DeltaRecord"] = "DeltaRecord"
    delta_id: str
    id_entree_original: str
    champ_modifie: str
    valeur_avant: str | None
    valeur_apres: str | None
    raison_delta: str
    impact_decision: str
    source_ou_regle_declencheuse: str | None = None


class FinalProvisionalDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_type: Literal["FinalProvisionalDecision"] = "FinalProvisionalDecision"
    id_entree_original: str
    titre_original_exact: str
    statut_traitement: StatutTraitement
    decision_finale_provisoire: DecisionFinaleProvisoire
    type_unite_RUN: TypeUniteRun
    indices_finaux: Indices
    publication_status: PublicationStatus
    audit_status: AuditStatus = AuditStatus.AUCUN_AUDIT_REQUIS
    note_prudence: str | None = None
    deltas_associes: list[str] = Field(default_factory=list)
    alertes_associees: list[str] = Field(default_factory=list)


class JournalPatchEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_entree_original: str
    titre_original_exact: str
    operation: Literal["append", "update"]
    statut_traitement: StatutTraitement
    dernier_controle: str | None = None
    dernier_RUN: str | None = None
    decision_finale_provisoire: DecisionFinaleProvisoire
    type_unite_RUN: TypeUniteRun
    lien_archive_RUN: str | None = None
    remarque: str | None = None
    a_ne_pas_retraiter_nouveau: bool = True


class JournalPatchControl(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nb_entries: int
    contains_direct_journal_write: bool = False
    requires_human_review_before_publication: bool = False
    schema_valid: bool = True


class JournalPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_type: Literal["JournalPatch"] = "JournalPatch"
    patch_id: str
    active_journal_cible: str
    mode: Literal["append_or_update_controlled"] = "append_or_update_controlled"
    entries: list[JournalPatchEntry]
    controle_patch: JournalPatchControl
