from __future__ import annotations

from copy import deepcopy

from dico_impro.models import (
    ClassificationInput,
    CorrectionAutomatique,
    Indices,
    Run002Cible,
    ValidationReport,
)


PUBLICATION_BLOCKING_C = {"C-B2", "C-C", "C-D", "C-X"}


def _add_correction(
    corrections: list[CorrectionAutomatique],
    *,
    champ: str,
    avant: str | None,
    apres: str | None,
    raison: str,
    regle: str,
) -> None:
    corrections.append(
        CorrectionAutomatique(champ=champ, avant=avant, apres=apres, raison=raison, regle=regle)
    )


def validate_classification(item: ClassificationInput) -> ValidationReport:
    """Apply deterministic v0.2.3-auto guardrails to D/S/I/C/E classification.

    This function does not launch a RUN and does not write a journal patch.
    It only applies automatic corrections and flags RUN_002/audit/publication status.
    """

    before = deepcopy(item.indices)
    after = deepcopy(item.indices)
    corrections: list[CorrectionAutomatique] = []
    run_002_targets: list[Run002Cible] = []
    audit_queue_requis = False
    publication_bloquee = False
    audit_gravite: str | None = None

    decisive_sources = [s for s in item.sources if s.source_decisive == "oui"]
    independent_check = any(s.verification_independante for s in item.sources)

    if after.S == "S-A" and not decisive_sources:
        _add_correction(
            corrections,
            champ="S",
            avant=after.S,
            apres="S-B",
            raison="S-A interdit sans source décisive.",
            regle="V-S-001",
        )
        after.S = "S-B"
        run_002_targets.append(
            Run002Cible(
                champ="S",
                faiblesse="source décisive absente",
                question_ciblee="Chercher une source décisive ou maintenir S-B.",
            )
        )

    if after.S == "S-A" and not independent_check and not item.exception_S_A_justifiee:
        _add_correction(
            corrections,
            champ="S",
            avant=after.S,
            apres="S-B",
            raison="S-A interdit sans vérification indépendante ou complémentaire.",
            regle="V-S-002",
        )
        after.S = "S-B"
        run_002_targets.append(
            Run002Cible(
                champ="S",
                faiblesse="vérification indépendante absente",
                question_ciblee="Chercher une source indépendante ou justifier explicitement l’exception.",
            )
        )

    if after.I == "I-A" and not item.preuve_improvisation_centrale_explicitement_documentee:
        _add_correction(
            corrections,
            champ="I",
            avant=after.I,
            apres="I-B",
            raison="I-A interdit sans preuve explicite d’improvisation centrale.",
            regle="V-I-001",
        )
        after.I = "I-B"
        run_002_targets.append(
            Run002Cible(
                champ="I",
                faiblesse="preuve d’improvisation centrale insuffisante",
                question_ciblee="Vérifier si l’improvisation est centrale pour l’objet classé.",
            )
        )

    if after.C == "C-A" and not item.perimetre_stable:
        _add_correction(
            corrections,
            champ="C",
            avant=after.C,
            apres="C-B1",
            raison="C-A interdit si le périmètre n’est pas stabilisé.",
            regle="V-C-001",
        )
        after.C = "C-B1"
        run_002_targets.append(
            Run002Cible(
                champ="C",
                faiblesse="périmètre insuffisamment stabilisé",
                question_ciblee="Contrôler le périmètre avant classement fort.",
            )
        )

    if after.D is not None and after.D != "D-A":
        publication_bloquee = True
        audit_queue_requis = True
        audit_gravite = "rouge"

    if after.C in PUBLICATION_BLOCKING_C:
        publication_bloquee = True
        audit_queue_requis = True
        audit_gravite = "rouge"

    if corrections and audit_gravite is None:
        audit_queue_requis = True
        audit_gravite = "orange"

    run_002_requis = bool(run_002_targets)
    if publication_bloquee:
        validation_status = "non_publiable_en_l_etat"
    elif run_002_requis:
        validation_status = "run_002_auto_requis"
    elif corrections:
        validation_status = "validé_avec_corrections"
    else:
        validation_status = "validé_sans_correction"

    return ValidationReport(
        id_entree_original=item.id_entree_original,
        validation_status=validation_status,
        indices_avant_validation=before,
        indices_apres_validation=after,
        corrections_automatiques=corrections,
        run_002_requis=run_002_requis,
        run_002_cible=run_002_targets,
        audit_queue_requis=audit_queue_requis,
        audit_gravite=audit_gravite,
        publication_bloquee=publication_bloquee,
        justification_courte="Validation automatique v0.2.3-auto appliquée.",
    )


__all__ = ["validate_classification", "PUBLICATION_BLOCKING_C"]
