from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = REPO_ROOT / "docs" / "AUDIT_METIER_POST_COACH_LOOP_v0.2.3-auto.md"


MANDATORY_HEADINGS = (
    "# Audit métier post-coach-loop v0.2.3-auto",
    "## 1. Purpose",
    "## 2. Baseline after Codex 043",
    "## 3. Scope and prohibitions",
    "## 4. Files inspected",
    "## 5. Sources and files inventory",
    "## 6. Sources/files verdict",
    "## 7. Journal inventory",
    "## 8. Journal verdict",
    "## 9. Schema inventory",
    "## 10. Categorization inventory",
    "## 11. Categorization verdict",
    "## 12. Reclassification / recategorization inventory",
    "## 13. Reclassification / recategorization verdict",
    "## 14. Existing guardrails",
    "## 15. Gaps and risks",
    "## 16. Decision matrix for Codex 045",
    "## 17. Recommended next implementation sequence",
    "## 18. Codex 045 candidate scope",
    "## 19. Final guarantees",
)

MANDATORY_VERDICTS = (
    "Sources/files verdict",
    "Journal verdict",
    "Categorization verdict",
    "Reclassification / recategorization verdict",
)

ALLOWED_RECLASSIFICATION_VERDICTS = (
    "implémentée",
    "partiellement_documentée",
    "absente",
    "incertaine_faute_d_élément",
)


def read_audit() -> str:
    assert AUDIT_PATH.exists(), f"Missing audit document: {AUDIT_PATH}"
    return AUDIT_PATH.read_text(encoding="utf-8")


def test_audit_document_exists_and_contains_all_mandatory_headings():
    audit = read_audit()

    missing = [heading for heading in MANDATORY_HEADINGS if heading not in audit]
    assert not missing, f"Audit document is missing headings: {missing!r}"


def test_audit_document_contains_four_mandatory_verdict_sections():
    audit = read_audit()

    for verdict in MANDATORY_VERDICTS:
        assert verdict in audit, f"Audit document must contain {verdict!r}"


def test_reclassification_verdict_uses_one_allowed_value():
    audit = read_audit()
    verdict_lines = re.findall(r"^verdict:\s*(.+?)\s*$", audit, flags=re.MULTILINE)

    assert len(verdict_lines) == 1, (
        "Audit document must contain exactly one explicit reclassification verdict line."
    )
    assert verdict_lines[0] in ALLOWED_RECLASSIFICATION_VERDICTS


def test_audit_document_contains_final_guarantees_and_prohibitions():
    audit = read_audit()
    required_phrases = (
        "## 19. Final guarantees",
        "no RUN",
        "no journal write",
        "no JournalPatch",
        "no real data processing",
        "no real data processed",
        "no export",
        "no export produced",
        "no src/scripts modification",
        "no src/** modified",
        "no scripts/** modified",
        "no XLSX/CSV modification",
        "no XLSX/CSV modified",
    )

    missing = [phrase for phrase in required_phrases if phrase not in audit]
    assert not missing, f"Audit document is missing prohibitions: {missing!r}"


def test_audit_document_is_decision_cartography_for_codex_045():
    audit = read_audit()
    required_phrases = (
        "Codex 044",
        "audit-only",
        "cartographie decision-oriented pour Codex 045",
        "main a 620 tests passing",
        "coach-loop",
        "n'est pas le moteur metier dicoimpro complet",
        "no categorization implemented",
        "no reclassification implemented",
    )

    missing = [phrase for phrase in required_phrases if phrase not in audit]
    assert not missing, f"Audit document is missing decision framing: {missing!r}"
