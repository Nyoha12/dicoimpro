from __future__ import annotations

import tomllib
import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DICOIMPRO_DIR = REPO_ROOT / ".dicoimpro"
DOCS_DIR = REPO_ROOT / "docs"
SCRIPTS_DIR = REPO_ROOT / "scripts"
SRC_DIR = REPO_ROOT / "src" / "dico_impro"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

FINAL_AUDIT_PATH = DOCS_DIR / "COACH_LOOP_FINAL_AUDIT_FREEZE_v0.2.3-auto.md"
README_PATH = DOCS_DIR / "README.md"
POST_015_REVIEW_PATH = DOCS_DIR / "REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md"
COACH_GUIDANCE_PATH = DICOIMPRO_DIR / "COACH_GUIDANCE.md"
DOCS_SYNC_TEST_PATH = REPO_ROOT / "tests" / "test_docs_sync.py"


def read_text(path: Path) -> str:
    assert path.exists(), f"Required file is missing: {path}"
    return path.read_text(encoding="utf-8")


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return " ".join(without_accents.casefold().split())


def test_final_audit_doc_exists_and_mentions_codex_035_through_042():
    assert FINAL_AUDIT_PATH.exists()
    document = normalize_text(read_text(FINAL_AUDIT_PATH))
    for codex_id in range(35, 43):
        assert f"codex {codex_id:03d}" in document


def test_final_audit_doc_states_baseline_and_freeze_status():
    document = normalize_text(read_text(FINAL_AUDIT_PATH))
    required_phrases = (
        "current main before codex 043 is 609 tests passing",
        "codex 043 adds no runtime feature",
        "coach-loop block is ready for controlled local usage after merge if tests pass",
        "generated .dicoimpro/runs artifacts are local/ignored",
    )
    for phrase in required_phrases:
        assert phrase in document, f"Final audit doc is missing: {phrase}"


def test_final_audit_doc_states_core_boundaries():
    document = normalize_text(read_text(FINAL_AUDIT_PATH))
    required_phrases = (
        "api requires --execute-api",
        "codex execution remains manual handoff",
        "merge is never default",
        "auto-merge requires --execute-merge plus merge_mode auto_after_verify plus verify gate success",
        "unknown risk means stop_human",
        "no run/journal/journalpatch/real data",
        "no src runtime behavior",
        "no old pdf usage",
        "no publication",
        "no source discovery",
        "candidate selection",
        "dictionary entry processing",
    )
    for phrase in required_phrases:
        assert phrase in document, f"Final audit doc is missing: {phrase}"


def test_final_audit_doc_contains_final_usage_checklist_commands():
    document = read_text(FINAL_AUDIT_PATH)
    required_commands = (
        "python scripts/coach_loop.py doctor",
        "python scripts/coach_loop.py start --run-id <run_id> --stage pre_cadrage",
        "python scripts/coach_loop.py validate-run --run-id <run_id>",
        "python scripts/coach_loop.py explain-next --run-id <run_id>",
        'python scripts/coach_loop.py start --run-id <run_id> --stage pre_cadrage --execute-api --user-instruction "..."',
        "python scripts/coach_loop.py resume-codex --run-id <run_id> --return-path <path>",
        "python scripts/coach_loop.py verify-pr --run-id <run_id> --merge-mode manual",
        "python scripts/coach_loop.py verify-pr --run-id <run_id> --merge-mode auto_after_verify --execute-merge",
    )
    for command in required_commands:
        assert command in document

    normalized = normalize_text(document)
    assert "the last command is optional and dangerous unless the verify gate is green" in normalized
    assert "must not be used casually" in normalized
    assert "only when the user explicitly wants guarded auto-merge" in normalized


def test_remaining_work_is_optional_not_blocker():
    document = normalize_text(read_text(FINAL_AUDIT_PATH))
    required_phrases = (
        "remaining work is optional, not blocker",
        "real controlled end-to-end test on a harmless docs pr",
        "ergonomics improvements if usage shows friction",
        "richer cost accounting",
        "ci integration if desired",
        "later production integration only after separate decision",
        "not blockers",
    )
    for phrase in required_phrases:
        assert phrase in document, f"Final audit doc is missing: {phrase}"


def test_guidance_readme_and_post_015_reference_codex_043_freeze():
    guidance = normalize_text(read_text(COACH_GUIDANCE_PATH))
    readme = normalize_text(read_text(README_PATH))
    review = normalize_text(read_text(POST_015_REVIEW_PATH))

    assert "coach-loop freeze status" in guidance
    assert "frozen after codex 043 if tests pass" in guidance
    assert "no new autonomy" in guidance
    assert "api, codex, pr verification, and merge boundaries remain unchanged" in guidance
    assert "future production integration requires a separate explicit decision" in guidance
    assert "no run/journal/journalpatch/real data/src runtime behavior change" in guidance

    assert "coach_loop_final_audit_freeze_v0.2.3-auto.md" in readme
    assert "codex 043" in readme
    assert "final audit and freeze" in readme

    assert "codex 043" in review
    assert "609 tests passing" in review
    assert "no runtime feature" in review
    assert "no script change" in review
    assert "production integration reste hors scope" in review


def test_docs_sync_expects_codex_043_and_final_audit_doc():
    source = read_text(DOCS_SYNC_TEST_PATH)
    assert "EXPECTED_CODEX_LAST = 43" in source
    assert "COACH_LOOP_FINAL_AUDIT_FREEZE_PATH" in source
    assert "COACH_LOOP_FINAL_AUDIT_FREEZE_v0.2.3-auto.md" in source


def test_scripts_do_not_reference_codex_043_or_final_audit_doc():
    forbidden_terms = (
        "Codex 043",
        "COACH_LOOP_FINAL_AUDIT_FREEZE",
        "coach loop final audit freeze",
    )
    for path in SCRIPTS_DIR.glob("*.py"):
        source = read_text(path)
        for term in forbidden_terms:
            assert term not in source, f"{path} must not be changed for Codex 043 freeze: {term}"


def test_no_src_references_coach_loop_or_final_audit():
    forbidden_terms = (
        "coach_loop.py",
        "COACH_LOOP_FINAL_AUDIT_FREEZE",
        "coach loop final audit freeze",
    )
    for path in SRC_DIR.rglob("*.py"):
        source = read_text(path)
        for term in forbidden_terms:
            assert term not in source, f"{path} must not reference coach-loop freeze: {term}"


def test_no_openai_or_codex_dependency_and_no_github_workflow_added():
    pyproject = tomllib.loads(read_text(PYPROJECT_PATH))
    dependency_groups = [
        pyproject.get("project", {}).get("dependencies", []),
        *pyproject.get("project", {}).get("optional-dependencies", {}).values(),
    ]
    dependencies = [
        dependency.casefold()
        for group in dependency_groups
        for dependency in group
    ]

    assert not any("openai" in dependency for dependency in dependencies)
    assert not any("codex" in dependency for dependency in dependencies)
    assert not (REPO_ROOT / ".github" / "workflows").exists()
