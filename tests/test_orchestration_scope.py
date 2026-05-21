import pytest
from pydantic import ValidationError

from dico_impro.orchestration import ExplicitScope, ScopeEntry


def test_explicit_scope_is_accepted():
    scope = ExplicitScope.model_validate(
        {
            "batch_id": "BATCH_001",
            "entries": [
                {"id_entree_original": "026", "titre_original_exact": "Entry title"},
                {"id_entree_original": "027"},
            ],
        }
    )

    assert scope.batch_id == "BATCH_001"
    assert scope.entries[0] == ScopeEntry(
        id_entree_original="026", titre_original_exact="Entry title"
    )
    assert scope.entry_ids == ["026", "027"]


def test_scope_rejects_missing_batch_id():
    with pytest.raises(ValidationError):
        ExplicitScope.model_validate({"entries": [{"id_entree_original": "026"}]})


def test_scope_rejects_empty_scope():
    with pytest.raises(ValidationError):
        ExplicitScope.model_validate({"batch_id": "BATCH_001", "entries": []})
