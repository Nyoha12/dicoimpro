from __future__ import annotations

import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = REPO_ROOT / "docs" / "AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md"
PROMPT_DRAFT_DIR = REPO_ROOT / "docs" / "prompts" / "drafts"
PROMPTS_MODULE = REPO_ROOT / "src" / "dico_impro" / "agents" / "prompts.py"


def read_map() -> str:
    assert MAP_PATH.exists(), f"Responsibility map document is missing: {MAP_PATH}"
    return MAP_PATH.read_text(encoding="utf-8")


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
    assert not missing, f"Responsibility map is missing required text: {missing!r}"


def test_responsibility_map_exists_and_is_non_runtime_non_prompt_non_contract() -> None:
    responsibility_map = read_map()

    assert_contains_all(
        responsibility_map,
        (
            "Codex 025 responsibility map only",
            "documentation/tests only",
            "non-runtime",
            "non-prompt",
            "non-contract",
            "pre-implementation",
            "does not create a real prompt",
            "does not create prompt drafts",
            "does not create prompt bodies",
            "does not create final JSON contracts",
            "does not create runtime enums",
            "No real prompt exists yet",
            "No runtime prompt loading or OpenAI activation exists",
            "no real agent activation",
            "no real OpenAI/network path",
            "no RUN",
            "no candidate selection",
            "no active journal read/write",
            "no JournalPatch application",
            "no official public export",
        ),
    )


def test_rule_levels_are_distinguished() -> None:
    responsibility_map = read_map()

    assert_contains_all(
        responsibility_map,
        (
            "A. Database finality / quality goals",
            "cautious and traceable database",
            "preserve fragile leads without validating them too early",
            "do not transform hypotheses into facts",
            "do not force all entries into `fiche_pratique`",
            "avoid cultural reduction and overclassification",
            "separate existence, source, improvisation, classification and prudence",
            "B. Categorization / quality-labeling rules",
            "`fiche_pratique`",
            "`fiche_cadre`",
            "`fiche_famille`",
            "`mecanisme_passerelle`",
            "`controle_perimetre`",
            "`alias_doublon`",
            "`sous_piste_candidate`",
            "`a_verifier`",
            "D/S/I/C/E quality axes",
            "D/S/I/C/E are quality/risk labels, not final decisions by themselves",
            "C. Agentic process rules",
            "A difficult case does not mean human review by default",
            "`validation_agentique_simple`",
            "`validation_agentique_renforcee`",
            "`audit_contradictoire_interne`",
            "`blocage_structure`",
            "`autorisation_action_externe`",
            "D. Per-agent rules",
            "A future agent receives only the rules required for its role",
            "E. SDK architecture rules",
            "SDK architecture executes, validates format, blocks forbidden transitions",
            "F. External actions forbidden by default",
        ),
    )


def test_agents_architecture_and_external_actions_are_separated() -> None:
    responsibility_map = read_map()

    assert_contains_all(
        responsibility_map,
        (
            "Agentic reasoning responsibility",
            "SDK/architecture responsibility",
            "External action or forbidden-by-default responsibility",
            "| Batch |",
            "| Routing |",
            "| Source search |",
            "| Source audit |",
            "| Classification |",
            "| Prudence / ethics |",
            "| Contradiction |",
            "| Validation |",
            "| DELTA |",
            "| Journal patch |",
            "| Archiving / exports |",
            "`BatchSupervisor` must be split into `BatchOrchestrator` architecture",
            "`SourceSearchAgent` must be split into `SearchPlannerAgent`",
            "`ValidationAgent` must be split into `ContractValidator`/`QualityGate`",
            "`DeltaAgent` must be split into `DiffEngine` architecture",
            "`JournalPatchAgent` proposes only",
            "`ArchivageAgent` is not a primary agent by default",
        ),
    )


def test_agentic_roles_sdk_components_and_external_actions_are_named() -> None:
    responsibility_map = read_map()

    assert_contains_all(
        responsibility_map,
        (
            "RoutingAgent",
            "SourceAuditAgent",
            "ClassificationAgent",
            "PrudenceEthicsAgent",
            "ContradictionAgent",
            "ValidationReviewAgent",
            "DeltaInterpretationAgent",
            "JournalPatchAgent",
            "BatchOrchestrator",
            "SearchToolRunner",
            "ContractValidator",
            "QualityGate",
            "DiffEngine",
            "TraceLogger",
            "Exporter",
            "JournalPatchValidator",
            "JournalPatchApplier",
            "publication officielle",
            "modification source active",
            "active journal application",
            "real OpenAI/API activation",
            "protocol change",
            "official public export",
        ),
    )


def test_external_actions_are_forbidden_by_default() -> None:
    responsibility_map = read_map()

    assert_contains_all(
        responsibility_map,
        (
            "External actions are side effects or public/project-level changes",
            "forbidden by default",
            "publishing",
            "applying a JournalPatch",
            "modifying the active journal",
            "reading or modifying active sources",
            "deleting an original entry",
            "changing protocol",
            "activating real OpenAI",
            "launching unapproved cost/API",
            "official public export",
        ),
    )


def test_routing_agent_allowed_and_forbidden_outputs_are_defined() -> None:
    responsibility_map = read_map()

    assert_contains_all(
        responsibility_map,
        (
            "`RoutingAgent` is a conservative routing/aiguillage agent",
            "`RoutingAgent` may output",
            "`type_unite_propose`",
            "`decision_pre_RUN_proposee`",
            "initial risks",
            "uncertainties",
            "recommended `controle_perimetre`",
            "`alias_doublon_possible`",
            "recommended relance",
            "recommended audit",
            "reason why RUN is not authorized",
            "`RoutingAgent` must not output",
            "S-A",
            "I-A",
            "final `source_decisive`",
            "`publication_ready`",
            "final fiche",
            "definitive fusion/scission",
            "applied journal patch",
            "launched RUN",
            "real source audit",
            "public publication status",
        ),
    )


def test_architecture_to_agent_feedback_loop_is_documented() -> None:
    responsibility_map = read_map()

    assert_contains_all(
        responsibility_map,
        (
            "Feedback loops from architecture to agents",
            "architecture-to-agent feedback loop",
            "Technical/contract failure",
            "invalid JSON",
            "missing required field",
            "invalid enum",
            "forbidden field",
            "out-of-scope output",
            "failed control",
            "allowed values if relevant",
            "repair mode",
            "fix only invalid fields and not add new conclusions",
            "Methodological failure or weak output",
            "I-A proposed without central improvisation proof",
            "platform used as original source",
            "`fiche_pratique` forced where `fiche_cadre`/`fiche_famille` seems likely",
            "prudence missing",
            "contradiction ignored",
            "same agent repair",
            "specialized agent",
            "`SourceAuditAgent`",
            "`ClassificationAgent`",
            "`ContradictionAgent`",
            "`ValidationReviewAgent`",
            "structured blocking",
            "must not tell an agent to \"make the test pass\" by forcing evidence",
            "identify the failed rule and the allowed next step",
        ),
    )


def test_recommended_vocabulary_is_non_contractual_and_not_active_enums() -> None:
    responsibility_map = read_map()

    assert_contains_all(
        responsibility_map,
        (
            "Recommended vocabulary, non-contractual",
            "recommended pre-contract vocabulary",
            "not active enums",
            "not final JSON enum names",
            "not implemented runtime values",
            "not a contract",
            "fait_atteste",
            "fait_atteste_limite",
            "mention_attestee",
            "hypothese_conservee",
            "indice_non_probant",
            "insuffisant",
            "ready_for_routing",
            "ready_for_search",
            "ready_for_RUN",
            "ready_for_RUN_002",
            "ready_for_validation_agentique",
            "ready_for_journal_patch",
            "publication_ready",
            "blocked_source",
            "blocked_perimetre",
            "blocked_type_unite",
            "blocked_contradiction",
            "blocked_ethics",
            "blocked_technical",
            "blocked_scope",
            "blocked_publication",
            "blocked_journal_application",
            "needs_source_audit",
            "needs_classification_audit",
            "needs_improvisation_audit",
            "needs_perimeter_audit",
            "needs_ethics_audit",
            "needs_publication_audit",
            "needs_technical_audit",
            "needs_journal_audit",
            "must not be treated as implemented runtime values",
        ),
    )


def test_relationship_to_previous_docs_and_codex_history_is_documented() -> None:
    responsibility_map = read_map()

    assert_contains_all(
        responsibility_map,
        (
            "RULES_IMPLEMENTATION_AUDIT_v0.2.3-auto.md",
            "PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md",
            "PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md",
            "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md",
            "Codex 023 audited rule coverage",
            "Codex 024 clarified pre-prompt blockers",
            "Codex 025 maps responsibilities and rule levels before any prompt drafting",
            "does not supersede `PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md`",
            "does not start prompt drafting",
        ),
    )


def test_responsibility_map_did_not_add_prompt_artifacts() -> None:
    draft_paths = sorted(PROMPT_DRAFT_DIR.glob("*.md")) if PROMPT_DRAFT_DIR.exists() else []

    assert draft_paths == [], f"Codex 025 must not add prompt drafts: {draft_paths!r}"
    assert not PROMPTS_MODULE.exists(), f"prompts.py must not exist: {PROMPTS_MODULE}"
