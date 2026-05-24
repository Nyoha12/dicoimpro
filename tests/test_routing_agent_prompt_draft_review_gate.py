from __future__ import annotations

import re
import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
GATE_PATH = DOCS_DIR / "ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md"


def read_gate() -> str:
    assert GATE_PATH.exists(), f"RoutingAgent prompt draft review gate is missing: {GATE_PATH}"
    return GATE_PATH.read_text(encoding="utf-8")


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
        "RoutingAgent prompt draft review gate is missing required text: "
        f"{missing!r}"
    )


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


def test_review_gate_exists_and_declares_non_activation_status() -> None:
    gate = read_gate()

    assert_contains_all(
        gate,
        (
            "Status: Codex 029 review gate",
            "review gate",
            "documentation-only",
            "non-runtime",
            "non-consuming",
            "non-activation",
            "non-approval",
            "pre-mock",
            "pre-runtime",
            "docs/tests only",
            "does not activate the prompt",
            "does not approve the prompt for mock",
            "does not approve the prompt for runtime",
            "load or render the prompt",
            "consume the prompt from CLI, OpenAIAdapter, mock planning or runtime",
            "create `prompts.py`",
            "create final JSON contracts",
            "create runtime enums",
            "activate OpenAI",
            "launch RUN",
            "read or write the active journal",
            "apply JournalPatch",
            "export XLSX/CSV",
            "use the old PDF",
        ),
    )


def test_purpose_keeps_codex_029_documentary_only() -> None:
    gate = read_gate()
    purpose = extract_markdown_section(gate, "1. Purpose")

    assert_contains_all(
        purpose,
        (
            "documentary control for the disabled RoutingAgent prompt draft",
            "Codex 029 does not activate the prompt",
            "Codex 029 does not approve the prompt for mock",
            "Codex 029 does not approve the prompt for runtime",
            "Codex 029 does not load, render or consume the prompt",
            "Codex 029 only checks that the draft remains coherent with prior docs and safe as a disabled document",
        ),
    )


def test_review_sources_and_codex_sequence_are_explicit() -> None:
    gate = read_gate()
    sources = extract_markdown_section(gate, "2. Review sources")

    assert_contains_all(
        sources,
        (
            "docs/prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md",
            "ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md",
            "ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md",
            "AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md",
            "PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md",
            "PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md",
            "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md",
            "Codex 026 specified the RoutingAgent functional perimeter",
            "Codex 027 checked readiness for a disabled prompt draft",
            "Codex 028 created the disabled prompt draft",
            "Codex 029 reviews that draft as a disabled document only",
        ),
    )


def test_review_checklist_covers_sections_a_through_l() -> None:
    gate = read_gate()

    assert_contains_all(
        gate,
        (
            "### A. Lifecycle and activation status",
            "### B. Scope coherence",
            "### C. Role-boundary coherence",
            "### D. Input-boundary coherence",
            "### E. Output-boundary coherence",
            "### F. Forbidden-output coherence",
            "### G. Routing behavior coherence",
            "### H. RUN posture coherence",
            "### I. Relance/audit coherence",
            "### J. Guardrail wording coherence",
            "### K. Synthetic example coherence",
            "### L. Review verdict",
        ),
    )


def test_lifecycle_and_activation_status_stays_disabled_non_consumed() -> None:
    gate = read_gate()
    section = extract_markdown_section(gate, "A. Lifecycle and activation status")

    assert_contains_all(
        section,
        (
            "draft status is `draft_documented`",
            "`activation_status` is `disabled`",
            "draft is documentation-only",
            "draft is non-runtime",
            "draft is non-consumed",
            "draft is not approved for mock",
            "draft is not approved for runtime",
            "draft is not approved for CLI",
            "draft is not approved for real OpenAI",
            "draft is not approved for batch processing",
            "draft must not be loaded, rendered or consumed",
        ),
    )


def test_scope_coherence_keeps_routing_conservative() -> None:
    gate = read_gate()
    section = extract_markdown_section(gate, "B. Scope coherence")

    assert_contains_all(
        section,
        (
            "RoutingAgent is conservative routing/aiguillage",
            "RoutingAgent reads only supplied structured input",
            "RoutingAgent proposes conservative pre-RUN routing",
            "RoutingAgent surfaces uncertainty",
            "RoutingAgent may recommend perimeter control, relance or audit",
            "RoutingAgent avoids forced `fiche_pratique`",
            "RoutingAgent explains why RUN is not authorized when routing is unstable",
        ),
    )


def test_role_boundary_coherence_excludes_other_agent_roles() -> None:
    gate = read_gate()
    section = extract_markdown_section(gate, "C. Role-boundary coherence")

    assert_contains_all(
        section,
        (
            "source auditor",
            "classifier",
            "publisher",
            "validation agent",
            "RUN executor",
            "JournalPatch applier",
            "source search agent",
        ),
    )


def test_input_boundary_coherence_forbids_unsupplied_data_and_search() -> None:
    gate = read_gate()
    section = extract_markdown_section(gate, "D. Input-boundary coherence")

    assert_contains_all(
        section,
        (
            "browsing",
            "external search",
            "source discovery",
            "`data/local_files` access unless supplied by architecture",
            "implicit active journal access",
            "old PDF usage",
            "inference from unavailable project data",
            "archives treated as active sources",
            "real project data not supplied",
        ),
    )


def test_output_boundary_coherence_stays_conceptual_and_review_only() -> None:
    gate = read_gate()
    section = extract_markdown_section(gate, "E. Output-boundary coherence")

    assert_contains_all(
        section,
        (
            "conceptual and review-only",
            "not a final JSON contract",
            "not runtime enum creation",
            "allowed conceptual output fields remain provisional",
            "output should be concise",
            "uncertainty must be explicit",
            "missing information must not be filled by plausibility",
        ),
    )


def test_forbidden_output_coherence_blocks_final_and_runtime_effects() -> None:
    gate = read_gate()
    section = extract_markdown_section(gate, "F. Forbidden-output coherence")

    assert_contains_all(
        section,
        (
            "S-A",
            "I-A",
            "final D/S/I/C/E",
            "final `source_decisive`",
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


def test_routing_behavior_coherence_covers_all_categories() -> None:
    gate = read_gate()
    section = extract_markdown_section(gate, "G. Routing behavior coherence")

    assert_contains_all(
        section,
        (
            "`fiche_pratique`",
            "`fiche_cadre`",
            "`fiche_famille`",
            "`mecanisme_passerelle`",
            "`controle_perimetre`",
            "`alias_doublon`",
            "`a_verifier`",
            "conservative routing is preferred over forced `fiche_pratique`",
            "`alias_doublon` never means definitive merge",
            "broad systems may route to `fiche_cadre`",
            "related variants may route to `fiche_famille`",
            "transversal mechanisms may route to `mecanisme_passerelle`",
            "unstable scope may route to `controle_perimetre` or `a_verifier`",
        ),
    )


def test_run_posture_coherence_is_non_executing() -> None:
    gate = read_gate()
    section = extract_markdown_section(gate, "H. RUN posture coherence")

    assert_contains_all(
        section,
        (
            "RUN possible does not mean fiche ready",
            "`type_unite_RUN` is mandatory before RUN",
            "RoutingAgent does not launch RUN",
            "RoutingAgent does not decide RUN_002",
            "RoutingAgent may recommend no RUN or RUN not authorized",
            "`run_interdit_raison` or equivalent is preserved conceptually",
        ),
    )


def test_relance_audit_coherence_keeps_recommendations_non_contractual() -> None:
    gate = read_gate()
    section = extract_markdown_section(gate, "I. Relance/audit coherence")

    assert_contains_all(
        section,
        (
            "relance/audit are recommendations only",
            "RoutingAgent does not execute relance, audit, RUN, publication, source search or journal mutation",
            "recommendation names are conceptual, non-contractual and not active enums",
            "`relance_perimetre`",
            "`relance_alias_doublon`",
            "`relance_categorisation`",
            "`relance_fiche_cadre_vs_pratique`",
            "`relance_fiche_famille`",
            "`relance_mecanisme_passerelle`",
            "`audit_routage`",
            "`audit_classification_later`",
            "`audit_source_later`",
        ),
    )


def test_guardrail_wording_coherence_is_explicit() -> None:
    gate = read_gate()
    section = extract_markdown_section(gate, "J. Guardrail wording coherence")

    assert_contains_all(
        section,
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


def test_synthetic_example_coherence_blocks_real_project_data() -> None:
    gate = read_gate()
    section = extract_markdown_section(gate, "K. Synthetic example coherence")

    assert_contains_all(
        section,
        (
            "examples are synthetic and non-project-specific",
            "examples do not use real project entries",
            "examples do not use active journal data",
            "examples do not use old PDF data",
            "examples do not select candidates",
            "positive examples cover broad system, group/variants, transversal technique, unclear scope and possible duplicate/transliteration",
            "negative examples cover I-A, S-A, `publication_ready`, JournalPatch application, RUN launch and final fiche",
        ),
    )


def test_review_verdict_has_yes_only_for_disabled_draft_coherence() -> None:
    gate = read_gate()
    verdict = extract_markdown_section(gate, "4. Review verdict")

    assert_contains_all(
        verdict,
        (
            "Coherent as disabled draft: YES, if all review checks pass.",
            "Approved for mock: NO.",
            "Approved for runtime: NO.",
            "Approved for CLI consumption: NO.",
            "Approved for real OpenAI: NO.",
            "Approved for RUN: NO.",
            "Approved for final contracts/enums: NO.",
            "Approved for journal mutation: NO.",
            "The only YES is coherence as a disabled draft",
            "All mock, runtime, CLI, OpenAI, RUN, final contract/enum and journal mutation approvals remain NO",
        ),
    )
    assert re.findall(r": YES\b", verdict) == [": YES"]


def test_future_mock_fixture_sentence_grants_no_activation_or_consumption() -> None:
    gate = read_gate()
    section = extract_markdown_section(gate, "L. Review verdict")

    assert_contains_all(
        section,
        (
            "A future Codex may prepare a mock-only review fixture or evaluation harness only after this gate",
            "this document itself grants no activation or consumption permission",
        ),
    )
