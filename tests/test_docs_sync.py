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
PROMPT_PACKAGE_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "prompt_packages"
SRC_DIR = REPO_ROOT / "src" / "dico_impro"

EXPECTED_CODEX_FIRST = 1
EXPECTED_CODEX_LAST = 20
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


def test_readme_active_docs_include_post_015_review():
    readme = read_text(README_PATH)
    expected_name = POST_015_REVIEW_PATH.name

    active_hierarchy = extract_markdown_section(readme, "Hiérarchie active")
    active_documents = extract_markdown_section(readme, "Documents actifs")

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
    assert any(
        marker in normalized_next_steps
        for marker in ("complete", "courant", "termine", "realise", "fait")
    ), "Post-015 review next steps must mark PromptPackage fixtures completed or current."


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
