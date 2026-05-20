import pytest

from dico_impro.journal import JournalPatchError, validate_journal_patch
from dico_impro.models import (
    DecisionFinaleProvisoire,
    Indices,
    JournalPatch,
    JournalPatchControl,
    JournalPatchEntry,
    StatutTraitement,
    TypeUniteRun,
)


def _entry(id_entree_original: str = "999") -> JournalPatchEntry:
    return JournalPatchEntry(
        id_entree_original=id_entree_original,
        titre_original_exact="Entrée test",
        operation="update",
        statut_traitement=StatutTraitement.RUN_002_FAIT,
        decision_finale_provisoire=DecisionFinaleProvisoire.ACCEPTE_AVEC_PRUDENCE,
        type_unite_RUN=TypeUniteRun.FICHE_CADRE,
        lien_archive_RUN="BATCH_TEST.master.json",
        a_ne_pas_retraiter_nouveau=True,
    )


def test_valid_journal_patch_passes_without_writing():
    patch = JournalPatch(
        patch_id="PATCH-TEST",
        active_journal_cible="JOURNAL.xlsx",
        entries=[_entry()],
        controle_patch=JournalPatchControl(nb_entries=1, contains_direct_journal_write=False),
    )

    assert validate_journal_patch(patch) == patch


def test_journal_patch_rejects_direct_write_flag():
    patch = JournalPatch(
        patch_id="PATCH-TEST",
        active_journal_cible="JOURNAL.xlsx",
        entries=[_entry()],
        controle_patch=JournalPatchControl(nb_entries=1, contains_direct_journal_write=True),
    )

    with pytest.raises(JournalPatchError):
        validate_journal_patch(patch)


def test_journal_patch_rejects_count_mismatch():
    patch = JournalPatch(
        patch_id="PATCH-TEST",
        active_journal_cible="JOURNAL.xlsx",
        entries=[_entry()],
        controle_patch=JournalPatchControl(nb_entries=2),
    )

    with pytest.raises(JournalPatchError):
        validate_journal_patch(patch)


def test_journal_patch_rejects_duplicate_ids():
    patch = JournalPatch(
        patch_id="PATCH-TEST",
        active_journal_cible="JOURNAL.xlsx",
        entries=[_entry("999"), _entry("999")],
        controle_patch=JournalPatchControl(nb_entries=2),
    )

    with pytest.raises(JournalPatchError):
        validate_journal_patch(patch)


def test_delta_record_model_available():
    from dico_impro.models import DeltaRecord

    delta = DeltaRecord(
        delta_id="DELTA-999-001",
        id_entree_original="999",
        champ_modifie="S",
        valeur_avant="S-A",
        valeur_apres="S-B",
        raison_delta="S-A non justifié par source décisive.",
        impact_decision="accepté avec prudence",
        source_ou_regle_declencheuse="V-S-001",
    )

    assert delta.object_type == "DeltaRecord"
    assert delta.champ_modifie == "S"
