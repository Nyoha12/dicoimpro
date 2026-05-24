from __future__ import annotations

import re
import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
DRAFT_DIR = DOCS_DIR / "prompts" / "drafts"
DRAFT_PATH = DRAFT_DIR / "ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md"
SRC_DIR = REPO_ROOT / "src" / "dico_impro"
PROMPTS_MODULE = SRC_DIR / "agents" / "prompts.py"
RUNTIME_BOUNDARY_PATHS = (
    SRC_DIR / "cli.py",
    SRC_DIR / "agents" / "adapters" / "openai.py",
    SRC_DIR / "orchestration" / "mock_openai_plan.py",
)


def read_text(path: Path) -> str:
    assert path.exists(), f"Required file is missing: {path}"
    return path.read_text(encoding="utf-8")


def read_draft() -> str:
    return read_text(DRAFT_PATH)


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
    assert not missing, f"RoutingAgent prompt draft is missing required text: {missing!r}"


def extract_markdown_section(document: str, heading_text: str) -> str:
    headings = list(re.finditer(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$", document, re.MULTILINE))
    expected_heading = normalize_text(heading_text)

    for index, heading in enumerate(headings):
        if normalize_text(heading.group("title")) != expected_heading:
            continue

        level = len(heading.group("marks"))
        end = len(document)
        for next_heading in headings[index + 1 :]:
            if len(next_heading.group("marks")) <= level:
                end = next_heading.start()
                break
        return document[heading.end() : end]

    available = [heading.group("title") for heading in headings]
    raise AssertionError(
        f"Missing markdown section {heading_text!r}. Available headings: {available!r}"
    )


def test_disabled_draft_file_exists_under_docs_prompts_drafts() -> None:
    assert DRAFT_DIR.exists(), f"Prompt draft directory is missing: {DRAFT_DIR}"
    assert DRAFT_PATH.exists(), f"Disabled RoutingAgent prompt draft is missing: {DRAFT_PATH}"

    draft_files = sorted(path for path in DRAFT_DIR.rglob("*") if path.is_file())
    assert draft_files == [DRAFT_PATH], (
        "docs/prompts/drafts must contain only the disabled Codex 028 draft. "
        f"Found: {draft_files!r}"
    )
    assert DRAFT_PATH.suffix == ".md"


def test_draft_status_is_disabled_documentation_only_non_runtime_non_consumed() -> None:
    draft = read_draft()

    assert_contains_all(
        draft,
        (
            "title: RoutingAgent prompt draft v0.2.3-auto",
            "status: draft_documented",
            "activation_status: disabled",
            "lifecycle_status: not approved for mock or runtime",
            "target_agent: RoutingAgent",
            "draft_documented",
            "disabled",
            "documentation-only",
            "non-runtime",
            "non-consumed",
            "not approved for mock",
            "not approved for real OpenAI",
            "not approved for CLI",
            "not approved for batch processing",
            "not approved for mock, runtime, CLI or real OpenAI",
            "not a final contract",
            "not a final enum source",
            "not loaded, rendered or consumed by any runtime",
        ),
    )


def test_draft_references_required_source_documents() -> None:
    draft = read_draft()

    assert_contains_all(
        draft,
        (
            "PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md",
            "ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md",
            "ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md",
            "AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md",
            "PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md",
        ),
    )


def test_draft_defines_conservative_routing_agent_purpose_and_exclusions() -> None:
    draft = read_draft()

    assert_contains_all(
        draft,
        (
            "`RoutingAgent` is a conservative routing/aiguillage agent",
            "read only supplied structured input",
            "propose conservative pre-RUN routing",
            "identify probable unit type",
            "surface uncertainty",
            "recommend perimeter control, relance or audit when needed",
            "avoid forced `fiche_pratique`",
            "explain why RUN is not authorized when routing is unstable",
            "not a source auditor",
            "not a classifier",
            "not a publisher",
            "not a validation agent",
            "not a RUN executor",
            "not a JournalPatch applier",
            "not a source search agent",
        ),
    )


def test_allowed_input_frame_is_limited_to_supplied_structured_input() -> None:
    draft = read_draft()

    assert_contains_all(
        draft,
        (
            "rely only on supplied structured input",
            "entry id",
            "entry label",
            "explicit-scope metadata if supplied",
            "authorized steering context if supplied",
            "already-treated status if supplied",
            "allowed `type_unite` vocabulary if supplied",
            "allowed `decision_pre_RUN` vocabulary if supplied",
            "project guardrails",
            "no browsing",
            "no external search",
            "no source discovery",
            "no use of `data/local_files` unless architecture supplies authorized input",
            "no implicit active journal access",
            "no old PDF usage",
            "no inference from unavailable project data",
        ),
    )


def test_allowed_conceptual_output_frame_is_non_contractual() -> None:
    draft = read_draft()

    assert_contains_all(
        draft,
        (
            "review-only conceptual output shape",
            "not a final JSON contract",
            "not runtime enum creation",
            "`type_unite_propose`",
            "`decision_pre_RUN_proposee`",
            "`uncertainty_note`",
            "`risks_initiaux`",
            "`controle_perimetre_recommande`",
            "`alias_doublon_possible`",
            "`relance_recommandee`",
            "`audit_recommande`",
            "`run_autorise_provisoirement`",
            "`run_interdit_raison`",
            "`justification_courte`",
            "`trace_notes`",
            "keep output concise",
            "justify routing briefly",
            "mark uncertainty explicitly",
            "do not fill missing information by plausibility",
            "prefer `a_verifier` or `controle_perimetre` when safe routing is impossible",
        ),
    )


def test_forbidden_outputs_are_explicitly_listed() -> None:
    draft = read_draft()

    assert_contains_all(
        draft,
        (
            "S-A",
            "I-A",
            "final D/S/I/C/E",
            "final source_decisive",
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
            "source discovery result",
            "final classification",
        ),
    )


def test_routing_categories_are_complete_and_conservative() -> None:
    draft = read_draft()

    assert_contains_all(
        draft,
        (
            "Conservative routing is preferred over forced `fiche_pratique`",
            "### `fiche_pratique`",
            "unitary, identifiable",
            "not obviously broader, family-like, transversal or perimeter-unstable",
            "### `fiche_cadre`",
            "broad systems, frameworks, traditions, repertoires, modal systems",
            "### `fiche_famille`",
            "related but distinct practices, variants or sub-objects",
            "### `mecanisme_passerelle`",
            "transversal mechanisms, techniques, roles or concepts",
            "### `controle_perimetre`",
            "uncertain scope, non-musical ambiguity, unclear improvisation relevance",
            "### `alias_doublon`",
            "duplicate, transliteration, variant naming, alias or relation suspicion",
            "Never make a definitive merge",
            "### `a_verifier`",
            "insufficient information or unclear routing",
        ),
    )


def test_run_posture_is_non_executing_and_preserves_block_reason() -> None:
    draft = read_draft()

    assert_contains_all(
        draft,
        (
            "RUN possible does not mean fiche ready",
            "`type_unite_RUN` is mandatory before RUN",
            "`RoutingAgent` does not launch RUN",
            "`RoutingAgent` does not decide RUN_002",
            "`RoutingAgent` may recommend no RUN or RUN not authorized",
            "`run_interdit_raison` or equivalent concept must be preserved",
        ),
    )


def test_relance_audit_concepts_are_recommendations_only_and_non_contractual() -> None:
    draft = read_draft()

    assert_contains_all(
        draft,
        (
            "may recommend relance or audit only",
            "`relance_perimetre`",
            "`relance_alias_doublon`",
            "`relance_categorisation`",
            "`relance_fiche_cadre_vs_pratique`",
            "`relance_fiche_famille`",
            "`relance_mecanisme_passerelle`",
            "`audit_routage`",
            "`audit_classification_later`",
            "`audit_source_later`",
            "conceptual, non-contractual and not active enums",
        ),
    )


def test_guardrail_wording_is_explicit() -> None:
    draft = read_draft()

    assert_contains_all(
        draft,
        (
            "Do not invent sources.",
            "Do not invent facts.",
            "Do not infer from missing project data.",
            "Do not convert uncertainty into validation.",
            "Do not classify strongly.",
            "Do not publish.",
            "Do not modify journal.",
            "Do not launch RUN.",
            "Do not treat old PDF as a source.",
            "Do not treat archives as active sources.",
            "Do not select candidates outside explicit scope.",
        ),
    )


def test_examples_are_synthetic_and_cover_positive_negative_cases() -> None:
    draft = read_draft()
    examples = extract_markdown_section(draft, "11. Synthetic Examples")

    assert_contains_all(
        examples,
        (
            "synthetic and non-project-specific",
            "do not use real project entries",
            "do not use active journal data",
            "do not use old PDF data",
            "do not select candidates",
            "Broad system-like label",
            "`type_unite_propose=\"fiche_cadre\"`",
            "Group/variants-like label",
            "`type_unite_propose=\"fiche_famille\"`",
            "Transversal technique-like label",
            "`type_unite_propose=\"mecanisme_passerelle\"`",
            "Unclear scope label",
            "`type_unite_propose=\"controle_perimetre\"`",
            "`type_unite_propose=\"a_verifier\"`",
            "Possible duplicate/transliteration",
            "`alias_doublon_possible=true`",
            "Do not output I-A",
            "Do not output S-A",
            "Do not output `publication_ready`",
            "Do not apply JournalPatch",
            "Do not launch RUN",
            "Do not create final fiche",
        ),
    )

    synthetic_entry_ids = re.findall(r'entry_id="([^"]+)"', examples)
    assert synthetic_entry_ids, "Synthetic examples must include explicit synthetic entry ids."
    assert all(entry_id.startswith("SYN-") for entry_id in synthetic_entry_ids)


def test_relationship_to_previous_docs_and_activation_no_go_is_explicit() -> None:
    draft = read_draft()

    assert_contains_all(
        draft,
        (
            "Codex 023 rule audit",
            "Codex 024 pre-prompt blockers clarification",
            "Codex 025 responsibility map",
            "Codex 026 RoutingAgent functional spec",
            "Codex 027 prompt-readiness checklist",
            "Prompt activation protocol",
            "Codex 028 creates a disabled draft only",
            "does not supersede the activation protocol",
            "must not be loaded or consumed until a later explicit activation mission",
            "Runtime activation remains NO",
            "Real OpenAI remains NO",
            "Real RUN remains NO",
            "Final contracts/enums remain NO",
        ),
    )


def test_draft_directory_is_documentation_only_and_runtime_does_not_reference_it() -> None:
    assert not PROMPTS_MODULE.exists(), f"prompts.py must not exist: {PROMPTS_MODULE}"

    forbidden_terms = (
        DRAFT_PATH.name,
        "ROUTING_AGENT_PROMPT_DRAFT",
        "docs/prompts/drafts",
        "prompts/drafts",
    )

    for path in sorted(SRC_DIR.rglob("*.py")):
        source = read_text(path)
        relative = path.relative_to(REPO_ROOT)
        for term in forbidden_terms:
            assert term not in source, f"{relative} must not reference disabled prompt draft {term!r}"


def test_cli_openai_adapter_and_mock_planning_do_not_load_or_import_draft() -> None:
    forbidden_terms = (
        DRAFT_PATH.name,
        "ROUTING_AGENT_PROMPT_DRAFT",
        "docs/prompts/drafts",
        "prompts/drafts",
        "PromptPackage",
        "prompt_body_ref",
    )

    for path in RUNTIME_BOUNDARY_PATHS:
        source = read_text(path)
        relative = path.relative_to(REPO_ROOT)
        for term in forbidden_terms:
            assert term not in source, f"{relative} must not import, load or consume {term!r}"
