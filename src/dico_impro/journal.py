from __future__ import annotations

from dico_impro.models import JournalPatch


class JournalPatchError(ValueError):
    """Raised when a JournalPatch violates v0.2.3-auto guardrails."""


def validate_journal_patch(patch: JournalPatch) -> JournalPatch:
    """Validate a proposed journal patch without writing to the active journal."""

    expected_count = len(patch.entries)
    if patch.controle_patch.nb_entries != expected_count:
        raise JournalPatchError(
            f"nb_entries={patch.controle_patch.nb_entries} does not match entries={expected_count}"
        )

    if patch.controle_patch.contains_direct_journal_write:
        raise JournalPatchError("JournalPatch cannot contain direct journal writes")

    ids = [entry.id_entree_original for entry in patch.entries]
    if len(ids) != len(set(ids)):
        raise JournalPatchError("JournalPatch contains duplicate id_entree_original values")

    for entry in patch.entries:
        if not entry.id_entree_original.strip():
            raise JournalPatchError("JournalPatch entry missing id_entree_original")
        if not entry.titre_original_exact.strip():
            raise JournalPatchError(
                f"JournalPatch entry {entry.id_entree_original} missing titre_original_exact"
            )

    return patch


__all__ = ["JournalPatchError", "validate_journal_patch"]
