from __future__ import annotations

from pydantic import Field

from dico_impro.contracts.common import NonEmptyStr, StrictContractModel


class ScopeEntry(StrictContractModel):
    id_entree_original: NonEmptyStr
    titre_original_exact: NonEmptyStr | None = None
    fake_scenario: NonEmptyStr | None = None


class ExplicitScope(StrictContractModel):
    """Entry scope supplied by the caller.

    The orchestration dry-run intentionally has no discovery or fallback path:
    callers must provide every entry identifier they want exercised.
    """

    batch_id: NonEmptyStr
    entries: list[ScopeEntry] = Field(min_length=1)

    @property
    def entry_ids(self) -> list[str]:
        return [entry.id_entree_original for entry in self.entries]

    @classmethod
    def from_entry_ids(cls, *, batch_id: str, entry_ids: list[str]) -> ExplicitScope:
        return cls.model_validate(
            {
                "batch_id": batch_id,
                "entries": [{"id_entree_original": entry_id} for entry_id in entry_ids],
            }
        )


__all__ = ["ExplicitScope", "ScopeEntry"]
