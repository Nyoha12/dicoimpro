from __future__ import annotations

import re
import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "docs" / "SPEC_VOCABULAIRE_ENTREES_RUN_REPRISE_v0.2.3-auto.md"
README_PATH = REPO_ROOT / "docs" / "README.md"
POST_015_REVIEW_PATH = (
    REPO_ROOT / "docs" / "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md"
)
DOCS_SYNC_TEST_PATH = REPO_ROOT / "tests" / "test_docs_sync.py"


def read_text(path: Path) -> str:
    assert path.exists(), f"Required document is missing: {path}"
    return path.read_text(encoding="utf-8")


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    without_markup = without_accents.replace("`", "")
    return " ".join(without_markup.casefold().split())


def assert_contains_all(document: str, required_phrases: tuple[str, ...]) -> None:
    normalized_document = normalize_text(document)
    missing = [
        phrase
        for phrase in required_phrases
        if normalize_text(phrase) not in normalized_document
    ]
    assert not missing, f"Document is missing required text: {missing!r}"


def vocabulary_map_terms(document: str) -> set[str]:
    terms: set[str] = set()
    for row in re.findall(r"^\|\s*([^|\n]+?)\s*\|.*$", document, flags=re.MULTILINE):
        cell = row.strip().strip("`")
        if cell and cell not in {"Vocabulary", "---"}:
            terms.add(cell)
    return terms


def test_spec_exists():
    assert SPEC_PATH.exists()


def test_spec_states_codex_045_docs_tests_only_and_non_runtime_scope():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "Codex 045",
            "docs/tests-only",
            "documentation/tests only",
            "vocabulary alignment, not runtime implementation",
            "no src",
            "no scripts",
            "no data",
            "no schemas",
            "no runtime contracts",
        ),
    )


def test_spec_forbids_fiche_identity_and_runtime_type_fiche():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "There is no id_fiche",
            "There is no fiche_id runtime field",
            "There is no type_fiche runtime field or enum",
            "no Fiche model",
            "no type_fiche runtime field or enum",
        ),
    )


def test_spec_defines_type_unite_run_boundary():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "type_unite_RUN is pre-RUN framing",
            "type_unite_RUN is not a final fiche type",
            "It must not be replaced by type_fiche",
            "Future type_fiche must be mapped to type_unite_RUN",
            "No type_fiche is added now",
        ),
    )


def test_spec_states_run_possible_is_not_fiche_ready_or_categorization():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "RUN possible != fiche ready",
            "RUN possible does not mean fiche_pratique ready",
            "RUN possible does not mean fiche lifecycle complete",
            "RUN possible does not mean categorization",
            "type_unite_RUN is required before a RUN posture",
            "Codex 045 launches no RUN",
        ),
    )


def test_spec_forbids_run_journal_write_and_journalpatch_application():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "no RUN",
            "no journal write",
            "no JournalPatch application",
            "JournalPatch is proposal boundary, not automatic application",
            "Codex 045 does not apply JournalPatch",
        ),
    )


def test_spec_states_review_reprise_and_scope_control_boundaries():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "a_verifier is uncertainty/review posture",
            "a_revoir exists as review/reprise vocabulary",
            "not yet a full runtime state machine",
            "Future a_revoir should be oriented",
            "does not add a new enum now",
            "raison_a_revoir and objectif_reprise are future alignment concepts",
            "They remain docs-only in Codex 045",
            "They are not runtime fields yet",
            "must not trigger automatic RUN",
            "controle_perimetre is scope-control",
            "not final exclusion and not a category",
        ),
    )


def test_spec_states_alias_variant_non_fiche_and_rattachement_boundaries():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "Alias/doublon already exists as protocol vocabulary or alert",
            "variante must not be collapsed into alias_doublon by default",
            "non_fiche_rattachee is future doctrine, not current runtime state",
            "No merge, delete, fusion, scission or fiche creation is authorized",
            "No relation graph is added",
        ),
    )


def test_spec_states_mechanism_cadre_and_family_boundaries():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "mecanisme_passerelle must not be erased or renamed abruptly",
            "Mechanism as descriptor/relation by default is future doctrine",
            "autonomous mechanism fiche is exceptional and future-only",
            "fiche_cadre is a documentary structuring frame, not a category",
            "fiche_famille is useful documentary grouping, not vague uncertainty",
            "makes no runtime changes",
        ),
    )


def test_spec_states_delta_record_and_journal_patch_boundaries():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "DeltaRecord is precedent for future changelog",
            "not current fiche changelog",
            "not a full fiche changelog",
            "JournalPatch is proposal boundary, not automatic application",
            "does not implement changelog",
        ),
    )


def test_spec_states_ascii_accent_policy_without_runtime_normalization():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "Vocabulary may appear with accents in human docs and ASCII in runtime contracts",
            "must not normalize code values",
            "Future normalization requires a separate mapping/spec",
            "does not modify enums or runtime values now",
        ),
    )


def test_spec_states_categorization_is_out_of_scope():
    spec = read_text(SPEC_PATH)

    assert_contains_all(
        spec,
        (
            "no categorization",
            "Categorization belongs much later after base realization",
            "NO-GO for runtime implementation",
        ),
    )


def test_spec_contains_mandatory_vocabulary_map_terms():
    spec = read_text(SPEC_PATH)
    expected_header = (
        "| Vocabulary | Current role | Current evidence level | Future interpretation | "
        "Code now? |"
    )
    assert expected_header in spec

    expected_terms = {
        "id_entree_original",
        "titre_original_exact",
        "type_unite_RUN",
        "fiche_pratique",
        "fiche_cadre",
        "fiche_famille",
        "mecanisme_passerelle",
        "alias_doublon",
        "controle_perimetre",
        "a_verifier",
        "a_revoir",
        "run_autorise",
        "run_interdit_raison",
        "DeltaRecord",
        "JournalPatch",
        "type_fiche",
        "fiche_id",
        "categorization",
    }
    assert expected_terms.issubset(vocabulary_map_terms(spec))


def test_readme_and_post_015_review_reference_codex_045_spec():
    readme = read_text(README_PATH)
    review = read_text(POST_015_REVIEW_PATH)
    spec_name = SPEC_PATH.name

    for source_name, document in (("README", readme), ("post-015 review", review)):
        assert spec_name in document, f"{source_name} must reference {spec_name}"
        assert "Codex 045" in document, f"{source_name} must reference Codex 045"


def test_docs_sync_expects_codex_045_when_tracking_expected_codex_range():
    source = read_text(DOCS_SYNC_TEST_PATH)

    assert "EXPECTED_CODEX_LAST = 45" in source
    assert "ENTRY_RUN_REPRISE_VOCABULARY_SPEC_PATH" in source
    assert "SPEC_VOCABULAIRE_ENTREES_RUN_REPRISE_v0.2.3-auto.md" in source
