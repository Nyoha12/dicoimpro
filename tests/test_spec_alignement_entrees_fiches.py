from __future__ import annotations

import re
import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "docs" / "SPEC_ALIGNEMENT_ENTREES_FICHES_v0.2.3-auto.md"
README_PATH = REPO_ROOT / "docs" / "README.md"
POST_015_REVIEW_PATH = (
    REPO_ROOT / "docs" / "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md"
)


def read_text(path: Path) -> str:
    assert path.exists(), f"Required document is missing: {path}"
    return path.read_text(encoding="utf-8")


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return without_accents.casefold()


def assert_contains_all(document: str, required_phrases: tuple[str, ...]) -> None:
    normalized_document = normalize_text(document)
    missing = [
        phrase for phrase in required_phrases if normalize_text(phrase) not in normalized_document
    ]
    assert not missing, f"Document is missing required text: {missing!r}"


def table_notions(document: str) -> set[str]:
    rows = re.findall(r"^\|\s*([^|\n]+?)\s*\|.*$", document, flags=re.MULTILINE)
    notions: set[str] = set()
    for row in rows:
        cell = row.strip().strip("`")
        if cell and cell not in {"Notion", "---"}:
            notions.add(cell)
    return notions


def test_spec_exists():
    assert SPEC_PATH.exists()


def test_spec_states_docs_tests_only_and_forbidden_runtime_scope():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "docs/tests-only alignment specification",
            "documentation/tests only",
            "does not modify `src/`",
            "does not modify `scripts/`",
            "does not implement the fiche lifecycle",
            "does not introduce `id_fiche`",
            "does not create a `Fiche` model",
            "does not change runtime behavior",
        ),
    )


def test_spec_states_no_run_journal_patch_or_data_processing():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "process data",
            "launch RUN",
            "write the active journal",
            "apply JournalPatch",
            "active journal read/write",
            "JournalPatch application",
        ),
    )


def test_spec_aligns_type_unite_run_and_future_type_fiche():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "`type_unite_RUN` is the existing pre-RUN framing",
            "Future `type_fiche` must be mapped to `type_unite_RUN` before any field, enum",
            "Codex 044 adds no `type_fiche` field or enum",
        ),
    )


def test_spec_states_no_categorization_now():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "introduce categorization",
            "Categorization is out of scope until the base is realized",
            "NO-GO for fiche lifecycle implementation",
        ),
    )


def test_spec_contains_mandatory_vocabulary_alignment_table():
    spec = read_text(SPEC_PATH)
    required_header = (
        "| Notion | Existing repo term | Current level | Doctrine retained | "
        "Integration stage | Code now? |"
    )
    assert required_header in spec

    expected_notions = {
        "entree originale",
        "id_entree_original",
        "future fiche",
        "fiche_id",
        "type_unite_RUN",
        "future type_fiche",
        "a_revoir",
        "objectif_reprise",
        "alias",
        "variante",
        "non_fiche_rattachee",
        "controle_perimetre",
        "mecanisme_passerelle",
        "fiche_cadre",
        "fiche_famille",
        "DeltaRecord",
        "JournalPatch",
        "categorization",
    }
    assert expected_notions.issubset(table_notions(spec))


def test_docs_sync_references_are_updated():
    readme = read_text(README_PATH)
    review = read_text(POST_015_REVIEW_PATH)
    spec_name = SPEC_PATH.name

    assert spec_name in readme
    assert spec_name in review
    assert "Codex 044" in readme
    assert "Codex 044" in review
