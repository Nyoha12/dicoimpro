from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from dico_impro.agents import (
    FORBIDDEN_INLINE_PROMPT_FIELDS,
    PromptPackage,
    REQUIRED_FORBIDDEN_CONTEXT_KEYS,
    REQUIRED_PROMPT_GUARDRAILS,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
README_PATH = DOCS_DIR / "README.md"
POST_015_REVIEW_PATH = DOCS_DIR / "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md"
PROMPT_ACTIVATION_PROTOCOL_PATH = DOCS_DIR / "PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md"
RULES_IMPLEMENTATION_AUDIT_PATH = DOCS_DIR / "RULES_IMPLEMENTATION_AUDIT_v0.2.3-auto.md"
PRE_PROMPT_BLOCKERS_CLARIFICATION_PATH = (
    DOCS_DIR / "PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md"
)
AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_PATH = (
    DOCS_DIR / "AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md"
)
ROUTING_AGENT_FUNCTIONAL_SPEC_PATH = (
    DOCS_DIR / "ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md"
)
ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_PATH = (
    DOCS_DIR / "ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md"
)
ROUTING_AGENT_PROMPT_DRAFT_PATH = (
    DOCS_DIR / "prompts" / "drafts" / "ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md"
)
ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_PATH = (
    DOCS_DIR / "ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md"
)
PROMPT_PACKAGE_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "prompt_packages"
SRC_DIR = REPO_ROOT / "src" / "dico_impro"

EXPECTED_CODEX_FIRST = 1
EXPECTED_CODEX_LAST = 29
EXPECTED_CODEX_IDS = tuple(
    f"{number:03d}" for number in range(EXPECTED_CODEX_FIRST, EXPECTED_CODEX_LAST + 1)
)
CODEX_STATUS_LINE_RE = re.compile(r"^Codex (?P<codex_id>\d{3})\s+-\s+.+$", re.MULTILINE)


def read_text(path: Path) -> str:
    assert path.exists(), f"Required sync target is missing: {path}"
    return path.read_text(encoding="utf-8")


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return without_accents.casefold()


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


def codex_ids_from_status_lines(section: str) -> tuple[str, ...]:
    return tuple(match.group("codex_id") for match in CODEX_STATUS_LINE_RE.finditer(section))


def assert_expected_codex_status_lines(section: str, source_name: str) -> None:
    actual_ids = codex_ids_from_status_lines(section)
    expected_range = f"Codex {EXPECTED_CODEX_IDS[0]} through Codex {EXPECTED_CODEX_IDS[-1]}"
    assert actual_ids == EXPECTED_CODEX_IDS, (
        f"{source_name} must list {expected_range} exactly once in "
        f"parseable 'Codex NNN - ...' status lines. Found: {actual_ids!r}"
    )


def prompt_package_fixture_paths() -> list[Path]:
    paths = sorted(PROMPT_PACKAGE_FIXTURE_DIR.glob("*.json"))
    assert paths, f"No PromptPackage fixture JSON files found in {PROMPT_PACKAGE_FIXTURE_DIR}"
    return paths


def load_json_fixture(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path.name} must contain one JSON object"
    return data


def assert_contains_all(section: str, required_phrases: tuple[str, ...], source_name: str) -> None:
    normalized_section = normalize_text(section)
    missing = [
        phrase for phrase in required_phrases if normalize_text(phrase) not in normalized_section
    ]
    assert not missing, f"{source_name} is missing required text: {missing!r}"


def test_readme_current_status_lists_expected_codex_range_once_each():
    readme = read_text(README_PATH)
    current_status = extract_markdown_section(readme, "Etat courant")

    assert_expected_codex_status_lines(current_status, "README Etat courant")


def test_post_015_review_has_parseable_expected_codex_status_list():
    review = read_text(POST_015_REVIEW_PATH)
    implementation_status = extract_markdown_section(
        review,
        "1. Etat d'implémentation courant",
    )

    assert_expected_codex_status_lines(
        implementation_status,
        "post-015 architecture review implementation status",
    )


def test_readme_active_docs_include_current_review_and_prompt_protocol():
    readme = read_text(README_PATH)
    expected_names = (
        POST_015_REVIEW_PATH.name,
        PROMPT_ACTIVATION_PROTOCOL_PATH.name,
        RULES_IMPLEMENTATION_AUDIT_PATH.name,
        PRE_PROMPT_BLOCKERS_CLARIFICATION_PATH.name,
        AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_PATH.name,
        ROUTING_AGENT_FUNCTIONAL_SPEC_PATH.name,
        ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_PATH.name,
        ROUTING_AGENT_PROMPT_DRAFT_PATH.name,
        ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_PATH.name,
    )

    active_hierarchy = extract_markdown_section(readme, "Hiérarchie active")
    active_documents = extract_markdown_section(readme, "Documents actifs")

    for expected_name in expected_names:
        assert expected_name in active_hierarchy, (
            f"README active hierarchy must include {expected_name!r}"
        )
        assert expected_name in active_documents, (
            f"README active document descriptions must include {expected_name!r}"
        )


def test_readme_non_negotiable_rules_remain_present():
    readme = read_text(README_PATH)
    rules = extract_markdown_section(readme, "Règles non négociables")

    assert_contains_all(
        rules,
        (
            "pas de RUN",
            "pas d'identification de candidats",
            "pas d'écriture directe dans le journal actif",
            "pas d'appel OpenAI réel",
        ),
        "README non-negotiable rules",
    )


def test_post_015_review_forbidden_paths_remain_present():
    review = read_text(POST_015_REVIEW_PATH)
    forbidden_paths = extract_markdown_section(review, "4. Chemins actuellement interdits")

    assert_contains_all(
        forbidden_paths,
        (
            "appel OpenAI réel",
            "appel réseau",
            "rendu ou chargement de prompt",
            "prompts.py",
            "SourceDiscoveryAgent",
            "RUN",
            "sélection de candidats",
            "écriture dans le journal actif",
            "accès data/local_files",
            "export XLSX/CSV",
            "application de JournalPatch",
        ),
        "post-015 architecture review forbidden paths",
    )


def test_post_015_review_next_steps_mark_recent_fake_only_milestones_current():
    review = read_text(POST_015_REVIEW_PATH)
    next_steps = extract_markdown_section(review, "9. Prochaines étapes recommandées")
    normalized_next_steps = normalize_text(next_steps)

    assert "codex 017" in normalized_next_steps, (
        "Post-015 review next steps must mention Codex 017 as the current PromptPackage "
        "fixture milestone."
    )
    assert "fixtures promptpackage metadata-only" in normalized_next_steps, (
        "Post-015 review next steps must mention PromptPackage metadata-only fixtures."
    )
    assert "codex 019" in normalized_next_steps, (
        "Post-015 review next steps must mention Codex 019 as the current CLI dry-run "
        "smoke milestone."
    )
    assert "smoke test cli dry-run" in normalized_next_steps, (
        "Post-015 review next steps must mention the CLI dry-run smoke test."
    )
    assert "codex 020" in normalized_next_steps, (
        "Post-015 review next steps must mention Codex 020 as the current runtime "
        "boundary guard milestone."
    )
    assert "garde-fous runtime" in normalized_next_steps, (
        "Post-015 review next steps must mention runtime boundary guard tests."
    )
    assert "codex 021" in normalized_next_steps, (
        "Post-015 review next steps must mention Codex 021 as the current tests/docs "
        "sanitization milestone."
    )
    assert "sans nouvelle capacite fonctionnelle" in normalized_next_steps, (
        "Post-015 review next steps must keep Codex 021 framed as tests/docs refactor "
        "only, not a functional capability."
    )
    assert "codex 022" in normalized_next_steps, (
        "Post-015 review next steps must mention Codex 022 as the current prompt "
        "activation protocol milestone."
    )
    assert "protocole documentaire" in normalized_next_steps, (
        "Post-015 review next steps must keep Codex 022 framed as protocol-only."
    )
    assert "sans creation de prompt" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 022 creates no prompt."
    )
    assert "codex 023" in normalized_next_steps, (
        "Post-015 review next steps must mention Codex 023 as the current rules "
        "implementation audit milestone."
    )
    assert "audit-only" in normalized_next_steps, (
        "Post-015 review next steps must keep Codex 023 framed as audit-only."
    )
    assert "regles existantes vs couverture d'implementation courante" in normalized_next_steps, (
        "Post-015 review next steps must describe Codex 023 as existing rules vs "
        "current implementation coverage."
    )
    assert "sans nouvelle doctrine" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 023 creates no doctrine."
    )
    assert "sans redaction de prompt commencee" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 023 does not start prompt drafting."
    )
    assert "codex 024" in normalized_next_steps, (
        "Post-015 review next steps must mention Codex 024 as the current pre-prompt "
        "blocker clarification milestone."
    )
    assert "clarification-only" in normalized_next_steps, (
        "Post-015 review next steps must keep Codex 024 framed as clarification-only."
    )
    assert "blockers pre-prompt issus de codex 023" in normalized_next_steps, (
        "Post-015 review next steps must describe Codex 024 as clarifying Codex 023 "
        "pre-prompt blockers."
    )
    assert "sans doctrine nouvelle" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 024 creates no new doctrine."
    )
    assert "codex 025" in normalized_next_steps, (
        "Post-015 review next steps must mention Codex 025 as the current responsibility "
        "mapping milestone."
    )
    assert "responsibility map" in normalized_next_steps, (
        "Post-015 review next steps must keep Codex 025 framed as a responsibility map."
    )
    assert "docs/tests-only" in normalized_next_steps, (
        "Post-015 review next steps must keep Codex 025 framed as docs/tests-only."
    )
    assert "niveaux de regles" in normalized_next_steps, (
        "Post-015 review next steps must describe Codex 025 as mapping rule levels."
    )
    assert "actions externes interdites par defaut" in normalized_next_steps, (
        "Post-015 review next steps must describe Codex 025 as mapping external actions "
        "forbidden by default."
    )
    assert "sans contrat json final ni enum runtime" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 025 creates no final JSON "
        "contract or runtime enum."
    )
    assert "sans activation openai/runtime" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 025 does not activate "
        "OpenAI/runtime."
    )
    assert "codex 026" in normalized_next_steps, (
        "Post-015 review next steps must mention Codex 026 as the current "
        "RoutingAgent functional spec milestone."
    )
    assert "routingagent functional spec" in normalized_next_steps, (
        "Post-015 review next steps must frame Codex 026 as a RoutingAgent "
        "functional spec."
    )
    assert "docs/tests-only" in normalized_next_steps, (
        "Post-015 review next steps must keep Codex 026 framed as docs/tests-only."
    )
    assert "pre-prompt" in normalized_next_steps, (
        "Post-015 review next steps must keep Codex 026 framed as pre-prompt."
    )
    assert "routage/aiguillage conservateur" in normalized_next_steps, (
        "Post-015 review next steps must describe Codex 026 as conservative routing."
    )
    assert "sans prompt draft" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 026 creates no prompt draft."
    )
    assert "sans prompt body" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 026 creates no prompt body."
    )
    assert "sans contrat json final ni enum runtime" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 026 creates no final JSON "
        "contract or runtime enum."
    )
    assert "sans activation openai/runtime" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 026 does not activate "
        "OpenAI/runtime."
    )
    assert "codex 027" in normalized_next_steps, (
        "Post-015 review next steps must mention Codex 027 as the current "
        "RoutingAgent prompt-readiness checklist milestone."
    )
    assert "routingagent prompt-readiness checklist" in normalized_next_steps, (
        "Post-015 review next steps must frame Codex 027 as a RoutingAgent "
        "prompt-readiness checklist."
    )
    assert "docs/tests-only" in normalized_next_steps, (
        "Post-015 review next steps must keep Codex 027 framed as docs/tests-only."
    )
    assert "pre-draft" in normalized_next_steps, (
        "Post-015 review next steps must keep Codex 027 framed as pre-draft."
    )
    assert "futur prompt draft desactive" in normalized_next_steps, (
        "Post-015 review next steps must describe Codex 027 as preparing only for a "
        "future disabled prompt draft."
    )
    assert "sans prompt draft" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 027 creates no prompt draft."
    )
    assert "sans prompt body" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 027 creates no prompt body."
    )
    assert "sans contenu docs/prompts/drafts" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 027 creates no draft "
        "directory content."
    )
    assert "sans contrat json final ni enum runtime" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 027 creates no final JSON "
        "contract or runtime enum."
    )
    assert "sans activation openai/runtime" in normalized_next_steps, (
        "Post-015 review next steps must state that Codex 027 does not activate "
        "OpenAI/runtime."
    )
    assert "codex 028" in normalized_next_steps, (
        "Post-015 review next steps must mention Codex 028 as the current "
        "disabled prompt draft milestone."
    )
    assert "disabled documentation-only routingagent prompt draft" in normalized_next_steps, (
        "Post-015 review next steps must frame Codex 028 as a disabled "
        "documentation-only RoutingAgent prompt draft."
    )
    assert "draft_documented" in normalized_next_steps, (
        "Post-015 review next steps must state Codex 028 draft status."
    )
    assert "desactive" in normalized_next_steps, (
        "Post-015 review next steps must state Codex 028 remains disabled."
    )
    assert "non-runtime" in normalized_next_steps, (
        "Post-015 review next steps must state Codex 028 remains non-runtime."
    )
    assert "non-consumed" in normalized_next_steps, (
        "Post-015 review next steps must state Codex 028 remains non-consumed."
    )
    assert "sans prompt actif" in normalized_next_steps, (
        "Post-015 review next steps must state Codex 028 creates no active prompt."
    )
    assert "sans runtime loading" in normalized_next_steps, (
        "Post-015 review next steps must state Codex 028 creates no runtime loading."
    )
    assert "sans prompts.py" in normalized_next_steps, (
        "Post-015 review next steps must state Codex 028 creates no prompts.py."
    )
    assert "sans contrat json final ni enum runtime" in normalized_next_steps, (
        "Post-015 review next steps must state Codex 028 creates no final JSON "
        "contract or runtime enum."
    )
    assert "sans activation openai/runtime" in normalized_next_steps, (
        "Post-015 review next steps must state Codex 028 does not activate "
        "OpenAI/runtime."
    )
    assert any(
        marker in normalized_next_steps
        for marker in ("complete", "courant", "termine", "realise", "fait")
    ), "Post-015 review next steps must mark PromptPackage fixtures completed or current."


def test_codex_023_is_audit_only_in_readme_and_review():
    readme = read_text(README_PATH)
    review = read_text(POST_015_REVIEW_PATH)

    for source_name, document in (
        ("README", readme),
        ("post-015 architecture review", review),
    ):
        normalized_document = normalize_text(document)
        assert "codex 023" in normalized_document, (
            f"{source_name} must list Codex 023."
        )
        assert "audit-only" in normalized_document, (
            f"{source_name} must frame Codex 023 as audit-only."
        )
        assert "regles existantes vs couverture d'implementation courante" in normalized_document, (
            f"{source_name} must describe Codex 023 as existing rules vs current "
            "implementation coverage."
        )
        assert "sans nouvelle doctrine" in normalized_document, (
            f"{source_name} must state that Codex 023 creates no doctrine."
        )
        assert "sans prompt reel" in normalized_document, (
            f"{source_name} must state that Codex 023 creates no real prompt."
        )
        assert "sans redaction de prompt commencee" in normalized_document, (
            f"{source_name} must state that Codex 023 does not start prompt drafting."
        )
        assert "activation openai/runtime" in normalized_document, (
            f"{source_name} must state that Codex 023 does not activate OpenAI/runtime."
        )


def test_codex_024_is_clarification_only_in_readme_and_review():
    readme = read_text(README_PATH)
    review = read_text(POST_015_REVIEW_PATH)

    for source_name, document in (
        ("README", readme),
        ("post-015 architecture review", review),
    ):
        normalized_document = normalize_text(document)
        assert "codex 024" in normalized_document, (
            f"{source_name} must list Codex 024."
        )
        assert "clarification-only" in normalized_document, (
            f"{source_name} must frame Codex 024 as clarification-only."
        )
        assert "blockers pre-prompt issus de codex 023" in normalized_document, (
            f"{source_name} must describe Codex 024 as clarifying Codex 023 "
            "pre-prompt blockers."
        )
        assert "sans doctrine nouvelle" in normalized_document, (
            f"{source_name} must state that Codex 024 creates no new doctrine."
        )
        assert "sans prompt reel" in normalized_document, (
            f"{source_name} must state that Codex 024 creates no real prompt."
        )
        assert "sans redaction de prompt commencee" in normalized_document, (
            f"{source_name} must state that Codex 024 does not start prompt drafting."
        )
        assert "activation openai/runtime" in normalized_document, (
            f"{source_name} must state that Codex 024 does not activate OpenAI/runtime."
        )


def test_codex_025_is_docs_tests_only_responsibility_mapping_in_readme_and_review():
    readme = read_text(README_PATH)
    review = read_text(POST_015_REVIEW_PATH)

    for source_name, document in (
        ("README", readme),
        ("post-015 architecture review", review),
    ):
        normalized_document = normalize_text(document)
        assert "codex 025" in normalized_document, (
            f"{source_name} must list Codex 025."
        )
        assert "docs/tests-only" in normalized_document, (
            f"{source_name} must frame Codex 025 as docs/tests-only."
        )
        assert "responsibility mapping" in normalized_document, (
            f"{source_name} must describe Codex 025 as responsibility mapping."
        )
        assert "niveaux de regles" in normalized_document, (
            f"{source_name} must describe Codex 025 as mapping rule levels."
        )
        assert "agents, architecture sdk et actions externes interdites par defaut" in normalized_document, (
            f"{source_name} must describe Codex 025 as mapping agents, SDK architecture "
            "and external actions forbidden by default."
        )
        assert "sans prompt reel" in normalized_document, (
            f"{source_name} must state that Codex 025 creates no real prompt."
        )
        assert "sans redaction de prompt commencee" in normalized_document, (
            f"{source_name} must state that Codex 025 does not start prompt drafting."
        )
        assert "sans contrat json final ni enum runtime" in normalized_document, (
            f"{source_name} must state that Codex 025 creates no final JSON contract "
            "or runtime enum."
        )
        assert "activation openai/runtime" in normalized_document, (
            f"{source_name} must state that Codex 025 does not activate OpenAI/runtime."
        )


def test_codex_026_is_docs_tests_only_routing_agent_functional_spec_in_readme_and_review():
    readme = read_text(README_PATH)
    review = read_text(POST_015_REVIEW_PATH)

    for source_name, document in (
        ("README", readme),
        ("post-015 architecture review", review),
    ):
        normalized_document = normalize_text(document)
        assert "codex 026" in normalized_document, (
            f"{source_name} must list Codex 026."
        )
        assert "docs/tests-only" in normalized_document, (
            f"{source_name} must frame Codex 026 as docs/tests-only."
        )
        assert "routingagent functional spec" in normalized_document, (
            f"{source_name} must describe Codex 026 as a RoutingAgent functional spec."
        )
        assert "pre-prompt" in normalized_document, (
            f"{source_name} must frame Codex 026 as pre-prompt."
        )
        assert "routage/aiguillage conservateur" in normalized_document, (
            f"{source_name} must describe Codex 026 as conservative routing."
        )
        assert "sans prompt reel" in normalized_document, (
            f"{source_name} must state that Codex 026 creates no real prompt."
        )
        assert "sans redaction de prompt commencee" in normalized_document, (
            f"{source_name} must state that Codex 026 does not start prompt drafting."
        )
        assert "sans prompt draft" in normalized_document, (
            f"{source_name} must state that Codex 026 creates no prompt draft."
        )
        assert "sans prompt body" in normalized_document, (
            f"{source_name} must state that Codex 026 creates no prompt body."
        )
        assert "sans contrat json final ni enum runtime" in normalized_document, (
            f"{source_name} must state that Codex 026 creates no final JSON contract "
            "or runtime enum."
        )
        assert "activation openai/runtime" in normalized_document, (
            f"{source_name} must state that Codex 026 does not activate OpenAI/runtime."
        )


def test_codex_027_is_docs_tests_only_routing_agent_prompt_readiness_in_readme_and_review():
    readme = read_text(README_PATH)
    review = read_text(POST_015_REVIEW_PATH)

    for source_name, document in (
        ("README", readme),
        ("post-015 architecture review", review),
    ):
        normalized_document = normalize_text(document)
        assert "codex 027" in normalized_document, (
            f"{source_name} must list Codex 027."
        )
        assert "docs/tests-only" in normalized_document, (
            f"{source_name} must frame Codex 027 as docs/tests-only."
        )
        assert "routingagent prompt-readiness checklist" in normalized_document, (
            f"{source_name} must describe Codex 027 as a RoutingAgent "
            "prompt-readiness checklist."
        )
        assert "pre-draft" in normalized_document, (
            f"{source_name} must frame Codex 027 as pre-draft."
        )
        assert "futur prompt draft desactive" in normalized_document, (
            f"{source_name} must describe Codex 027 as checking readiness for a "
            "future disabled prompt draft."
        )
        assert "sans prompt reel" in normalized_document, (
            f"{source_name} must state that Codex 027 creates no real prompt."
        )
        assert "sans redaction de prompt commencee" in normalized_document, (
            f"{source_name} must state that Codex 027 does not start prompt drafting."
        )
        assert "sans prompt draft" in normalized_document, (
            f"{source_name} must state that Codex 027 creates no prompt draft."
        )
        assert "sans prompt body" in normalized_document, (
            f"{source_name} must state that Codex 027 creates no prompt body."
        )
        assert "sans contenu docs/prompts/drafts" in normalized_document, (
            f"{source_name} must state that Codex 027 creates no draft directory content."
        )
        assert "sans contrat json final ni enum runtime" in normalized_document, (
            f"{source_name} must state that Codex 027 creates no final JSON contract "
            "or runtime enum."
        )
        assert "activation openai/runtime" in normalized_document, (
            f"{source_name} must state that Codex 027 does not activate OpenAI/runtime."
        )


def test_codex_028_is_disabled_documentation_only_prompt_draft_in_readme_and_review():
    readme = read_text(README_PATH)
    review = read_text(POST_015_REVIEW_PATH)

    for source_name, document in (
        ("README", readme),
        ("post-015 architecture review", review),
    ):
        normalized_document = normalize_text(document)
        assert "codex 028" in normalized_document, (
            f"{source_name} must list Codex 028."
        )
        assert "disabled documentation-only routingagent prompt draft" in normalized_document, (
            f"{source_name} must frame Codex 028 as a disabled documentation-only "
            "RoutingAgent prompt draft."
        )
        assert "docs/prompts/drafts" in normalized_document, (
            f"{source_name} must locate the Codex 028 draft under docs/prompts/drafts."
        )
        assert "draft_documented" in normalized_document, (
            f"{source_name} must state Codex 028 draft status."
        )
        assert "disabled" in normalized_document or "desactive" in normalized_document, (
            f"{source_name} must state Codex 028 remains disabled."
        )
        assert "non-runtime" in normalized_document, (
            f"{source_name} must state Codex 028 remains non-runtime."
        )
        assert "non-consumed" in normalized_document, (
            f"{source_name} must state Codex 028 remains non-consumed."
        )
        assert "not approved for mock, runtime, cli or real openai" in normalized_document, (
            f"{source_name} must state Codex 028 is not approved for mock, runtime, "
            "CLI or real OpenAI."
        )
        assert "sans prompt actif" in normalized_document, (
            f"{source_name} must state Codex 028 creates no active prompt."
        )
        assert "sans runtime loading" in normalized_document, (
            f"{source_name} must state Codex 028 creates no runtime loading."
        )
        assert "sans prompts.py" in normalized_document, (
            f"{source_name} must state Codex 028 creates no prompts.py."
        )
        assert "sans contrat json final ni enum runtime" in normalized_document, (
            f"{source_name} must state Codex 028 creates no final JSON contract "
            "or runtime enum."
        )
        assert "activation openai/runtime" in normalized_document, (
            f"{source_name} must state Codex 028 does not activate OpenAI/runtime."
        )


def test_codex_029_is_docs_tests_only_prompt_draft_review_gate_in_readme_and_review():
    readme = read_text(README_PATH)
    review = read_text(POST_015_REVIEW_PATH)

    for source_name, document in (
        ("README", readme),
        ("post-015 architecture review", review),
    ):
        normalized_document = normalize_text(document)
        assert "codex 029" in normalized_document, (
            f"{source_name} must list Codex 029."
        )
        assert "routingagent prompt draft review gate" in normalized_document, (
            f"{source_name} must frame Codex 029 as a RoutingAgent prompt draft "
            "review gate."
        )
        assert "docs/tests-only" in normalized_document, (
            f"{source_name} must keep Codex 029 framed as docs/tests-only."
        )
        assert "documentation-only" in normalized_document, (
            f"{source_name} must state Codex 029 remains documentation-only."
        )
        assert "non-runtime" in normalized_document, (
            f"{source_name} must state Codex 029 remains non-runtime."
        )
        assert "non-consuming" in normalized_document, (
            f"{source_name} must state Codex 029 remains non-consuming."
        )
        assert "non-activation" in normalized_document, (
            f"{source_name} must state Codex 029 is non-activation."
        )
        assert "non-approval" in normalized_document, (
            f"{source_name} must state Codex 029 is non-approval."
        )
        assert "pre-mock" in normalized_document, (
            f"{source_name} must state Codex 029 is pre-mock."
        )
        assert "pre-runtime" in normalized_document, (
            f"{source_name} must state Codex 029 is pre-runtime."
        )
        assert "sans activation, approbation, chargement, rendu ou consommation du prompt" in normalized_document, (
            f"{source_name} must state Codex 029 does not activate, approve, load, "
            "render or consume the prompt."
        )
        assert "sans prompts.py" in normalized_document, (
            f"{source_name} must state Codex 029 creates no prompts.py."
        )
        assert "sans contrat json final ni enum runtime" in normalized_document, (
            f"{source_name} must state Codex 029 creates no final JSON contract "
            "or runtime enum."
        )
        assert "activation openai/runtime" in normalized_document, (
            f"{source_name} must state Codex 029 does not activate OpenAI/runtime."
        )


def test_prompt_package_fixtures_validate_and_remain_disabled_metadata_only():
    forbidden_fields = set(FORBIDDEN_INLINE_PROMPT_FIELDS)

    for path in prompt_package_fixture_paths():
        data = load_json_fixture(path)
        try:
            package = PromptPackage.model_validate(data)
        except Exception as exc:  # pragma: no cover - assertion context matters here.
            raise AssertionError(f"{path.name} does not validate as PromptPackage") from exc

        assert data.get("enabled") is False, f"{path.name} must explicitly keep enabled=false"
        assert package.enabled is False, f"{path.name} must validate with enabled=False"
        assert forbidden_fields.isdisjoint(data), (
            f"{path.name} must remain metadata-only; forbidden inline prompt fields present: "
            f"{sorted(forbidden_fields.intersection(data))!r}"
        )


def test_prompt_package_fixtures_include_required_guardrails_and_context_blocks():
    required_guardrails = set(REQUIRED_PROMPT_GUARDRAILS)
    required_forbidden_context_keys = set(REQUIRED_FORBIDDEN_CONTEXT_KEYS)

    for path in prompt_package_fixture_paths():
        data = load_json_fixture(path)
        guardrails = set(data.get("required_guardrails", ()))
        forbidden_context_keys = set(data.get("forbidden_context_keys", ()))

        missing_guardrails = sorted(required_guardrails.difference(guardrails))
        missing_context_keys = sorted(
            required_forbidden_context_keys.difference(forbidden_context_keys)
        )

        assert not missing_guardrails, (
            f"{path.name} is missing required PromptPackage guardrails: {missing_guardrails!r}"
        )
        assert not missing_context_keys, (
            f"{path.name} is missing required forbidden context keys: {missing_context_keys!r}"
        )


def test_prompt_package_runtime_boundaries_remain_absent():
    prompts_modules = sorted((SRC_DIR / "agents").glob("prompts.py"))
    assert prompts_modules == [], f"prompts.py must not exist. Found: {prompts_modules!r}"

    source_files = {
        "OpenAIAdapter": SRC_DIR / "agents" / "adapters" / "openai.py",
        "mock_openai_plan": SRC_DIR / "orchestration" / "mock_openai_plan.py",
    }
    forbidden_terms = ("PromptPackage", "prompt_body_ref")

    for source_name, path in source_files.items():
        source = read_text(path)
        for term in forbidden_terms:
            assert term not in source, f"{source_name} source must not mention {term!r}"
