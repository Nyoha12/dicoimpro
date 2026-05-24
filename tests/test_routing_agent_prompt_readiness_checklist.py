from __future__ import annotations

import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKLIST_PATH = (
    REPO_ROOT / "docs" / "ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md"
)
PROMPT_DRAFT_DIR = REPO_ROOT / "docs" / "prompts" / "drafts"
EXPECTED_DISABLED_DRAFT = (
    PROMPT_DRAFT_DIR / "ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md"
)
PROMPTS_MODULE = REPO_ROOT / "src" / "dico_impro" / "agents" / "prompts.py"


def read_checklist() -> str:
    assert CHECKLIST_PATH.exists(), f"RoutingAgent checklist is missing: {CHECKLIST_PATH}"
    return CHECKLIST_PATH.read_text(encoding="utf-8")


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
    assert not missing, (
        "RoutingAgent prompt-readiness checklist is missing required text: "
        f"{missing!r}"
    )


def test_checklist_exists_and_is_pre_draft_non_runtime_non_prompt_non_contract() -> None:
    checklist = read_checklist()

    assert_contains_all(
        checklist,
        (
            "prompt-readiness checklist",
            "pre-draft",
            "non-runtime",
            "non-prompt",
            "non-contract",
            "non-final enum",
            "pre-implementation",
            "documentation/tests only",
            "does not create a real prompt",
            "does not create a prompt draft",
            "does not create prompt bodies",
            "does not create `docs/prompts/drafts` content",
            "does not create `prompts.py`",
            "does not create final JSON contracts",
            "does not create runtime enums",
            "No real prompt exists yet",
            "No prompt draft exists yet",
            "No runtime prompt loading or OpenAI activation exists",
        ),
    )


def test_codex_027_does_not_create_or_start_prompt_draft() -> None:
    checklist = read_checklist()

    assert_contains_all(
        checklist,
        (
            "Codex 027 does not create the prompt",
            "Codex 027 does not create a prompt draft",
            "Codex 027 does not start prompt drafting",
            "Codex 027 does not authorize runtime loading",
            "Codex 027 only checks that the future Codex 028 prompt draft can be prepared safely",
        ),
    )


def test_readiness_sources_reference_required_documents_and_codex_history() -> None:
    checklist = read_checklist()

    assert_contains_all(
        checklist,
        (
            "PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md",
            "RULES_IMPLEMENTATION_AUDIT_v0.2.3-auto.md",
            "PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md",
            "AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md",
            "ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md",
            "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md",
            "Codex 023 audited rule coverage",
            "Codex 024 clarified pre-prompt blockers",
            "Codex 025 mapped agents / architecture / external actions",
            "Codex 026 specified the RoutingAgent functional perimeter",
            "Codex 027 checks whether a disabled prompt draft is safe to prepare next",
        ),
    )


def test_checklist_covers_categories_a_through_i() -> None:
    checklist = read_checklist()

    assert_contains_all(
        checklist,
        (
            "### A. Prompt lifecycle readiness",
            "### B. RoutingAgent scope readiness",
            "### C. Forbidden-output readiness",
            "### D. Routing category readiness",
            "### E. RUN posture readiness",
            "### F. Relance / audit readiness",
            "### G. Architecture feedback readiness",
            "### H. Example readiness",
            "### I. Remaining non-readiness / future work",
        ),
    )


def test_prompt_lifecycle_and_scope_readiness_are_documented() -> None:
    checklist = read_checklist()

    assert_contains_all(
        checklist,
        (
            "The prompt activation protocol exists",
            "Real prompts are not active by default",
            "A future prompt draft must be disabled",
            "must not be consumed by CLI, `OpenAIAdapter`, mock planning or runtime",
            "must remain documentation-only",
            "`RoutingAgent` is conservative routing/aiguillage",
            "not source auditor, classifier, publisher, JournalPatch applier, RUN executor or validation agent",
            "Allowed conceptual inputs are limited to supplied structured input",
            "No browsing, no external source fetching, no `data/local_files` inspection",
            "no implicit active journal access",
            "Allowed conceptual outputs are known",
            "Forbidden outputs are known",
        ),
    )


def test_forbidden_outputs_are_listed() -> None:
    checklist = read_checklist()

    assert_contains_all(
        checklist,
        (
            "S-A",
            "I-A",
            "final D/S/I/C/E",
            "final `source_decisive`",
            "final source audit",
            "`publication_ready`",
            "final fiche",
            "definitive fusion/scission",
            "applied JournalPatch",
            "JournalPatch application",
            "launched RUN",
            "RUN launch",
            "active journal modification",
            "source publication status",
            "candidate selection outside explicit scope",
            "old PDF source use",
        ),
    )


def test_routing_category_readiness_prefers_conservative_routing() -> None:
    checklist = read_checklist()

    assert_contains_all(
        checklist,
        (
            "`fiche_pratique`",
            "`fiche_cadre`",
            "`fiche_famille`",
            "`mecanisme_passerelle`",
            "`controle_perimetre`",
            "`alias_doublon`",
            "`a_verifier`",
            "Conservative routing is preferred over forced `fiche_pratique`",
            "Possible alias/doublon never means definitive merge",
            "`controle_perimetre` is preferred over premature `hors_perimetre` final category",
            "Broad systems should route to `fiche_cadre` rather than `fiche_pratique`",
            "Related variants should route to `fiche_famille` rather than forced single practice",
            "Transversal mechanisms should route to `mecanisme_passerelle`",
        ),
    )


def test_run_posture_readiness_is_non_executing() -> None:
    checklist = read_checklist()

    assert_contains_all(
        checklist,
        (
            "RUN possible does not mean fiche ready",
            "`type_unite_RUN` is mandatory before RUN",
            "`RoutingAgent` does not launch RUN",
            "`RoutingAgent` does not decide RUN_002",
            "`RoutingAgent` may recommend no RUN or RUN not authorized",
            "must preserve `run_interdit_raison` or equivalent concept",
            "without creating final contracts",
        ),
    )


def test_relance_audit_recommendations_are_conceptual_and_non_contractual() -> None:
    checklist = read_checklist()

    assert_contains_all(
        checklist,
        (
            "`RoutingAgent` may recommend relance/audit but not perform it",
            "`relance_perimetre`",
            "`relance_alias_doublon`",
            "`relance_categorisation`",
            "`relance_fiche_cadre_vs_pratique`",
            "`relance_fiche_famille`",
            "`relance_mecanisme_passerelle`",
            "`audit_routage`",
            "`audit_classification_later`",
            "`audit_source_later`",
            "Recommendation names remain conceptual and non-contractual",
        ),
    )


def test_architecture_feedback_and_examples_are_ready() -> None:
    checklist = read_checklist()

    assert_contains_all(
        checklist,
        (
            "Future architecture can reject invalid fields",
            "Future architecture can reject forbidden outputs",
            "Future architecture can reject unsupported categories",
            "Future architecture can reject overstrong claims",
            "Future architecture can reject `publication_ready`",
            "Future architecture can reject S-A/I-A",
            "Future architecture can reject RUN authorization without `type_unite_RUN`",
            "Future architecture can reject final classification",
            "Feedback must identify failed rule and allowed repair path",
            "must not tell the prompt/agent to force evidence",
            "\"make the test pass\"",
            "Positive synthetic examples exist",
            "Negative synthetic examples exist",
            "Examples are synthetic and non-project-specific",
            "Examples do not process real entries, active journal, old PDF or candidates",
        ),
    )


def test_remaining_non_readiness_and_verdict_are_explicit() -> None:
    checklist = read_checklist()

    assert_contains_all(
        checklist,
        (
            "no runtime prompt loading",
            "no active prompt",
            "no prompt contract",
            "no final JSON schema",
            "no runtime enum",
            "no real RoutingAgent execution",
            "no source search",
            "no SourceAuditAgent prompt",
            "no ClassificationAgent prompt",
            "no publication flow",
            "no JournalPatch application",
            "no real OpenAI",
            "Ready for future disabled RoutingAgent prompt draft: YES, if this checklist passes",
            "Ready for runtime prompt activation: NO",
            "Ready for real OpenAI: NO",
            "Ready for real RUN: NO",
            "Ready for source audit/classification prompts: NO",
            "Ready for final JSON contracts/enums: NO",
            "Ready for active journal mutation: NO",
            "A future Codex 028 may create a disabled prompt draft only if it remains documentation-only, disabled, non-runtime, non-consumed and aligned with this checklist",
        ),
    )


def test_current_prompt_artifacts_are_limited_to_disabled_codex_028_draft() -> None:
    draft_paths = sorted(path for path in PROMPT_DRAFT_DIR.rglob("*") if path.is_file()) if PROMPT_DRAFT_DIR.exists() else []

    assert draft_paths == [EXPECTED_DISABLED_DRAFT], (
        "Current prompt drafts must be limited to the disabled Codex 028 "
        f"documentation-only draft. Found: {draft_paths!r}"
    )
    assert not PROMPTS_MODULE.exists(), f"prompts.py must not exist: {PROMPTS_MODULE}"
