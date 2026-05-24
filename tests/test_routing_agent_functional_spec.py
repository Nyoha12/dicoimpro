from __future__ import annotations

import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "docs" / "ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md"
PROMPT_DRAFT_DIR = REPO_ROOT / "docs" / "prompts" / "drafts"
EXPECTED_DISABLED_DRAFT = (
    PROMPT_DRAFT_DIR / "ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md"
)
PROMPTS_MODULE = REPO_ROOT / "src" / "dico_impro" / "agents" / "prompts.py"


def read_spec() -> str:
    assert SPEC_PATH.exists(), f"RoutingAgent functional spec is missing: {SPEC_PATH}"
    return SPEC_PATH.read_text(encoding="utf-8")


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return " ".join(without_accents.casefold().split())


def assert_contains_all(document: str, required_phrases: tuple[str, ...]) -> None:
    normalized_document = normalize_text(document)
    missing = [
        phrase for phrase in required_phrases if normalize_text(phrase) not in normalized_document
    ]
    assert not missing, f"RoutingAgent functional spec is missing required text: {missing!r}"


def test_spec_exists_and_is_pre_prompt_non_runtime_non_contract() -> None:
    spec = read_spec()

    assert_contains_all(
        spec,
        (
            "Codex 026 pre-prompt functional specification",
            "documentation/tests only",
            "non-runtime",
            "non-prompt",
            "non-contract",
            "non-final enum",
            "pre-implementation",
            "does not create a real prompt",
            "does not create a prompt draft",
            "does not create prompt bodies",
            "does not create `docs/prompts/drafts` content",
            "does not create `prompts.py`",
            "does not create final JSON contracts",
            "does not create runtime enums",
            "No real prompt exists yet",
            "No runtime prompt loading or OpenAI activation exists",
        ),
    )


def test_routing_agent_purpose_is_conservative_aiguillage() -> None:
    spec = read_spec()

    assert_contains_all(
        spec,
        (
            "`RoutingAgent` is a conservative routing/aiguillage agent",
            "what kind of unit this entry probably is",
            "whether standard documentary processing is possible",
            "whether perimeter control is needed",
            "possible alias/doublon",
            "`fiche_pratique`, `fiche_cadre`, `fiche_famille`",
            "`mecanisme_passerelle`, `controle_perimetre` or `a_verifier`",
            "uncertainty, relance or audit",
            "not a source auditor",
            "not a classifier",
            "not a publisher",
            "not a JournalPatch applier",
            "not a RUN executor",
            "not a validation agent",
        ),
    )


def test_allowed_conceptual_inputs_are_limited_to_supplied_structured_input() -> None:
    spec = read_spec()

    assert_contains_all(
        spec,
        (
            "entry id",
            "entry label",
            "minimal existing metadata supplied by explicit scope",
            "authorized steering context if provided by architecture",
            "known already-treated status if supplied by architecture",
            "allowed `type_unite` vocabulary",
            "allowed `decision_pre_RUN` vocabulary",
            "project guardrails",
            "no active journal write access",
            "must not fetch external sources",
            "must not browse",
            "must not inspect `data/local_files`",
            "must not infer from unavailable project data",
            "operates only on supplied structured input",
        ),
    )


def test_allowed_conceptual_outputs_are_non_contractual() -> None:
    spec = read_spec()

    assert_contains_all(
        spec,
        (
            "`type_unite_propose`",
            "`decision_pre_RUN_proposee`",
            "confidence / uncertainty note",
            "`risks_initiaux`",
            "`controle_perimetre_recommande`",
            "`alias_doublon_possible`",
            "`relance_recommandee`",
            "`audit_recommande`",
            "`run_autorise_provisoirement`",
            "`run_interdit_raison`",
            "`justification_courte`",
            "`trace_notes`",
            "recommended conceptual fields, not final contracts or runtime enums",
        ),
    )


def test_forbidden_outputs_are_explicitly_blocked() -> None:
    spec = read_spec()

    assert_contains_all(
        spec,
        (
            "S-A",
            "I-A",
            "final D/S/I/C/E status",
            "final `source_decisive`",
            "final source audit",
            "`publication_ready`",
            "final fiche",
            "definitive fusion/scission",
            "applied journal patch",
            "launched RUN",
            "active journal modification",
            "source publication status",
            "final classification",
            "old PDF source use",
            "candidate selection outside explicit scope",
            "JournalPatch was applied",
            "RUN was launched",
            "final source_decisive status",
        ),
    )


def test_routing_categories_and_conservative_behavior_are_covered() -> None:
    spec = read_spec()

    assert_contains_all(
        spec,
        (
            "must prefer conservative routing over forced `fiche_pratique`",
            "### `fiche_pratique`",
            "unitary, identifiable",
            "not obviously a broader frame, family, mechanism or perimeter issue",
            "### `fiche_cadre`",
            "broad systems, frameworks, traditions, repertoires, modal systems",
            "### `fiche_famille`",
            "groups of related but distinct practices, variants or sub-objects",
            "### `mecanisme_passerelle`",
            "transversal processes, mechanisms, techniques or concepts",
            "### `controle_perimetre`",
            "uncertain scope, non-musical ambiguity",
            "### `alias_doublon`",
            "possible duplicate, transliteration, variant naming, alias",
            "### `a_verifier`",
            "insufficient information or unclear routing",
        ),
    )


def test_run_posture_is_pre_run_and_non_executing() -> None:
    spec = read_spec()

    assert_contains_all(
        spec,
        (
            "RUN possible does not mean fiche ready",
            "`type_unite_RUN` is mandatory before RUN",
            "recommend no RUN or a RUN-not-authorized decision",
            "may recommend no RUN or RUN not authorized",
            "does not launch RUN",
            "does not decide RUN_002",
            "audit or relance before RUN",
        ),
    )


def test_relance_and_audit_recommendations_are_conceptual_only() -> None:
    spec = read_spec()

    assert_contains_all(
        spec,
        (
            "`relance_perimetre`",
            "`relance_alias_doublon`",
            "`relance_categorisation`",
            "`relance_fiche_cadre_vs_pratique`",
            "`relance_fiche_famille`",
            "`relance_mecanisme_passerelle`",
            "`audit_routage`",
            "`audit_classification_later`",
            "`audit_source_later`",
            "not final contracts or runtime enums",
            "recommends relance/audit; it does not perform them",
        ),
    )


def test_architecture_feedback_compatibility_is_documented() -> None:
    spec = read_spec()

    assert_contains_all(
        spec,
        (
            "`AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md`",
            "return structured feedback to `RoutingAgent`",
            "invalid field",
            "forbidden output",
            "unsupported category",
            "overstrong claim",
            "attempt to output `publication_ready`",
            "attempt to output S-A/I-A",
            "attempt to authorize RUN without required `type_unite`",
            "attempt to create final classification",
            "identify failed rule and allowed repair path",
            "must not tell the agent to force evidence",
            "\"make the test pass\"",
        ),
    )


def test_positive_and_negative_synthetic_examples_are_present() -> None:
    spec = read_spec()

    assert_contains_all(
        spec,
        (
            "synthetic, non-project-specific and illustrative only",
            "do not process real project entries",
            "do not use current active journal data",
            "do not use old PDF data",
            "do not select candidates",
            "Broad modal/tradition-like label",
            "`fiche_cadre` probable",
            "Group/family-like label",
            "`fiche_famille` possible",
            "Transversal technique-like label",
            "`mecanisme_passerelle` possible",
            "Unclear non-musical or scope-uncertain label",
            "`controle_perimetre` / `a_verifier`",
            "Possible duplicate/transliteration",
            "`alias_doublon_possible`",
            "must not emit I-A",
            "must not emit S-A",
            "must not say `publication_ready`",
            "must not apply JournalPatch",
            "must not launch RUN",
            "must not create a final fiche",
        ),
    )


def test_relationship_to_previous_docs_and_codex_history_is_documented() -> None:
    spec = read_spec()

    assert_contains_all(
        spec,
        (
            "AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md",
            "PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md",
            "PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md",
            "RULES_IMPLEMENTATION_AUDIT_v0.2.3-auto.md",
            "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md",
            "Codex 025 mapped responsibilities",
            "Codex 026 specifies the future `RoutingAgent` functional perimeter",
            "Codex 026 does not start prompt drafting",
            "Codex 026 does not supersede the prompt activation protocol",
            "future Codex may create a disabled prompt draft only after this spec is reviewed",
        ),
    )


def test_current_prompt_artifacts_are_limited_to_disabled_codex_028_draft() -> None:
    draft_paths = sorted(PROMPT_DRAFT_DIR.glob("*.md")) if PROMPT_DRAFT_DIR.exists() else []

    assert draft_paths == [EXPECTED_DISABLED_DRAFT], (
        "Current prompt drafts must be limited to the disabled Codex 028 "
        f"documentation-only draft. Found: {draft_paths!r}"
    )
    assert not PROMPTS_MODULE.exists(), f"prompts.py must not exist: {PROMPTS_MODULE}"
