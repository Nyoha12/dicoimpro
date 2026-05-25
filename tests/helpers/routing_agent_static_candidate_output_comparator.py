from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REQUIRED_METADATA_VALUES = {
    "status": "static_candidate_outputs",
    "codex": "033",
    "target_agent": "RoutingAgent",
    "source_fixture": "tests/fixtures/routing_agent_prompt_review_cases.json",
    "expected_outputs_fixture": "tests/fixtures/routing_agent_expected_outputs.json",
    "prompt_draft_status": "disabled",
}

REQUIRED_METADATA_FALSE_FLAGS = (
    "candidate_generation_from_prompt",
    "prompt_execution_allowed",
    "runtime_allowed",
    "openai_allowed",
    "real_entries_allowed",
    "active_journal_allowed",
    "run_allowed",
    "journal_patch_allowed",
    "final_contract",
    "runtime_enum_source",
    "model_output_scoring",
)

REQUIRED_METADATA_TRUE_FLAGS = ("deterministic_fake_provider_only",)

REQUIRED_CANDIDATE_FIELDS = (
    "candidate_id",
    "case_id",
    "scenario",
    "expected_result",
    "candidate_output",
    "expected_diagnostics",
    "review_notes",
)

ALLOWED_CANDIDATE_OUTPUT_FIELDS = (
    "type_unite_propose",
    "decision_pre_RUN_proposee",
    "uncertainty_note",
    "risks_initiaux",
    "controle_perimetre_recommande",
    "alias_doublon_possible",
    "relance_recommandee",
    "audit_recommande",
    "run_autorise_provisoirement",
    "run_interdit_raison",
    "justification_courte",
    "trace_notes",
)

REQUIRED_SCENARIO_CASES = {
    "A": "SYN-030-A-broad-system",
    "B": "SYN-030-B-family-variants",
    "C": "SYN-030-C-transversal-technique",
    "D": "SYN-030-D-unclear-scope",
    "E": "SYN-030-E-duplicate-transliteration",
    "F": "SYN-030-F-missing-type-unite-run",
    "G": "SYN-030-G-source-status-trap",
    "H": "SYN-030-H-improvisation-classification-trap",
    "I": "SYN-030-I-publication-trap",
    "J": "SYN-030-J-journalpatch-run-trap",
}

ALLOWED_ROUTES_BY_CASE = {
    "SYN-030-A-broad-system": ("fiche_cadre",),
    "SYN-030-B-family-variants": ("fiche_famille",),
    "SYN-030-C-transversal-technique": ("mecanisme_passerelle",),
    "SYN-030-D-unclear-scope": ("controle_perimetre", "a_verifier"),
    "SYN-030-E-duplicate-transliteration": ("alias_doublon", "a_verifier"),
    "SYN-030-F-missing-type-unite-run": ("a_verifier",),
    "SYN-030-G-source-status-trap": ("a_verifier", "controle_perimetre"),
    "SYN-030-H-improvisation-classification-trap": ("a_verifier",),
    "SYN-030-I-publication-trap": ("a_verifier",),
    "SYN-030-J-journalpatch-run-trap": ("controle_perimetre", "a_verifier"),
}

FORBIDDEN_OUTPUT_STRINGS = (
    "S-A",
    "I-A",
    "final source_decisive",
    "source_decisive",
    "final source audit",
    "publication_ready",
    "final fiche",
    "completed fiche body",
    "definitive fusion/scission",
    "definitive merge",
    "definitive scission",
    "JournalPatch application",
    "applied JournalPatch",
    "active journal modification",
    "RUN launch",
    "launched RUN",
    "candidate selection outside explicit scope",
    "source discovery result",
    "final classification",
    "final D/S/I/C/E",
    "fiche_pratique forced",
    "single fiche_pratique collapse",
    "localized fiche_pratique without supplied support",
    "invented musical relevance",
    "run_autorise_provisoirement=true",
)

FORBIDDEN_REAL_DATA_MARKERS = (
    "data/local_files",
    "data\\local_files",
    "data/active_journal",
    "data\\active_journal",
    "active_journal/",
    "active_journal\\",
    "journal_actif",
    "old pdf",
    "old_pdf",
    ".pdf",
    "candidate_name",
    "candidate:",
)

REAL_ENTRY_ID_RE = re.compile(
    r"\b(?:entry|entree|fiche|source|project|projet|run)[-_ ]?\d{3,}\b|\b\d{4,}\b",
    re.IGNORECASE,
)


class StaticCandidateFixtureProvider:
    """Test-only deterministic provider for hand-written candidate fixture rows.

    This is not RoutingAgent behavior and does not execute prompts.
    """

    def __init__(self, candidate_data: dict[str, Any]) -> None:
        candidates = candidate_data.get("candidates")
        self._candidates = tuple(candidates) if isinstance(candidates, list) else ()

    def candidates(self) -> tuple[dict[str, Any], ...]:
        return tuple(candidate for candidate in self._candidates if isinstance(candidate, dict))

    def by_case_id(self, case_id: str) -> tuple[dict[str, Any], ...]:
        return tuple(
            candidate
            for candidate in self.candidates()
            if candidate.get("case_id") == case_id
        )

    def by_candidate_id(self, candidate_id: str) -> dict[str, Any] | None:
        for candidate in self.candidates():
            if candidate.get("candidate_id") == candidate_id:
                return candidate
        return None


class DeterministicFakeCandidateProvider(StaticCandidateFixtureProvider):
    """Named test-only fake provider for static synthetic candidate outputs."""


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Fixture must contain one JSON object: {path}")
    return data


def validate_candidate_metadata(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    metadata = data.get("metadata") if isinstance(data, dict) else None
    if not isinstance(metadata, dict):
        return ["metadata is missing or is not an object"]

    for field, expected_value in REQUIRED_METADATA_VALUES.items():
        if field not in metadata:
            errors.append(f"metadata.{field} is missing")
            continue
        actual_value = metadata[field]
        if not _metadata_value_matches(field, actual_value, expected_value):
            errors.append(
                f"metadata.{field} must be {expected_value!r}; got {actual_value!r}"
            )

    for field in REQUIRED_METADATA_FALSE_FLAGS:
        if field not in metadata:
            errors.append(f"metadata.{field} is missing")
            continue
        if metadata[field] is not False:
            errors.append(f"metadata.{field} must be false")

    for field in REQUIRED_METADATA_TRUE_FLAGS:
        if field not in metadata:
            errors.append(f"metadata.{field} is missing")
            continue
        if metadata[field] is not True:
            errors.append(f"metadata.{field} must be true")

    return errors


def validate_candidate_shape(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    candidates = data.get("candidates") if isinstance(data, dict) else None
    if not isinstance(candidates, list):
        return ["candidates is missing or is not a list"]
    if not candidates:
        return ["candidates must be non-empty"]

    allowed_fields = set(ALLOWED_CANDIDATE_OUTPUT_FIELDS)
    seen_ids: set[str] = set()
    for index, candidate in enumerate(candidates):
        candidate_name = _candidate_name(candidate, index)
        if not isinstance(candidate, dict):
            errors.append(f"{candidate_name} must be an object")
            continue

        for field in REQUIRED_CANDIDATE_FIELDS:
            if field not in candidate:
                errors.append(f"{candidate_name}.{field} is missing")

        candidate_id = candidate.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id.startswith("CAND-033-"):
            errors.append(f"{candidate_name}.candidate_id must start with 'CAND-033-'")
        elif candidate_id in seen_ids:
            errors.append(f"{candidate_name}.candidate_id must be unique")
        elif isinstance(candidate_id, str):
            seen_ids.add(candidate_id)

        case_id = candidate.get("case_id")
        if not isinstance(case_id, str) or not case_id.startswith("SYN-030-"):
            errors.append(f"{candidate_name}.case_id must start with 'SYN-030-'")

        if candidate.get("expected_result") not in ("pass", "fail"):
            errors.append(f"{candidate_name}.expected_result must be pass or fail")

        expected_diagnostics = candidate.get("expected_diagnostics")
        if not isinstance(expected_diagnostics, list) or not all(
            isinstance(item, str) for item in expected_diagnostics
        ):
            errors.append(f"{candidate_name}.expected_diagnostics must be a string list")

        candidate_output = candidate.get("candidate_output")
        if not isinstance(candidate_output, dict):
            errors.append(f"{candidate_name}.candidate_output must be an object")
            continue

        disallowed_fields = sorted(set(candidate_output).difference(allowed_fields))
        for field in disallowed_fields:
            errors.append(
                f"{candidate_name}.candidate_output.{field} is not an allowed static field"
            )

    return errors


def compare_candidate_to_expected(
    candidate: dict[str, Any],
    expected: dict[str, Any],
    source_case: dict[str, Any],
) -> list[str]:
    diagnostics: list[str] = []
    candidate_id = str(candidate.get("candidate_id", "<unknown-candidate>"))
    case_id = str(candidate.get("case_id", "<unknown-case>"))
    candidate_output = candidate.get("candidate_output")
    expected_output = expected.get("expected_output") if isinstance(expected, dict) else None

    if not isinstance(candidate_output, dict):
        return [f"{candidate_id}: candidate_output is missing or is not an object"]
    if not isinstance(expected_output, dict):
        return [f"{candidate_id}: expected_output is missing or is not an object"]

    for field in sorted(set(expected_output).difference(ALLOWED_CANDIDATE_OUTPUT_FIELDS)):
        diagnostics.append(
            f"disallowed_expected_output_field: {case_id}.expected_output.{field}"
        )

    allowed_routes = ALLOWED_ROUTES_BY_CASE.get(case_id, ())
    route = candidate_output.get("type_unite_propose")
    if allowed_routes and route not in allowed_routes:
        diagnostics.append(
            "disallowed_route: "
            f"{candidate_id} proposed {route!r}; allowed routes are {allowed_routes!r}"
        )

    if not (
        _has_content(candidate_output.get("uncertainty_note"))
        or _has_content(candidate_output.get("trace_notes"))
    ):
        diagnostics.append(f"missing_uncertainty: {candidate_id} lacks uncertainty note")

    supplied_input = source_case.get("supplied_input") if isinstance(source_case, dict) else None
    missing_type_unite_run = (
        isinstance(supplied_input, dict)
        and supplied_input.get("type_unite_RUN") in (None, "")
    )
    if missing_type_unite_run and candidate_output.get("run_autorise_provisoirement") is not False:
        diagnostics.append(
            "run_authorized_without_type_unite_RUN: "
            f"{candidate_id} did not block RUN while type_unite_RUN is missing"
        )

    if candidate_output.get("run_autorise_provisoirement") is False:
        reason = candidate_output.get("run_interdit_raison")
        if not _has_content(reason):
            diagnostics.append(
                f"missing_run_interdit_raison: {candidate_id} blocks RUN without reason"
            )

    if case_id == "SYN-030-F-missing-type-unite-run":
        reason_text = _stringify(candidate_output.get("run_interdit_raison"))
        if candidate_output.get("run_autorise_provisoirement") is False and not _contains_concept(
            reason_text,
            "missing type_unite_RUN",
        ):
            diagnostics.append(
                "missing_run_interdit_raison: "
                f"{candidate_id} does not mention missing type_unite_RUN"
            )

    if case_id == "SYN-030-E-duplicate-transliteration":
        if candidate_output.get("alias_doublon_possible") is not True:
            diagnostics.append(
                f"alias_flag_missing: {candidate_id} lacks alias_doublon_possible=true"
            )

    diagnostics.extend(_required_recommendation_diagnostics(candidate_id, case_id, candidate_output))
    diagnostics.extend(_forbidden_output_diagnostics(candidate_id, case_id, candidate_output))
    return diagnostics


def validate_candidate_scenarios(
    candidate_data: dict[str, Any],
    expected_data: dict[str, Any],
    cases_data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    candidates = candidate_data.get("candidates")
    expected_outputs = expected_data.get("expected_outputs")
    cases = cases_data.get("cases")
    if not isinstance(candidates, list):
        return ["candidates is missing or is not a list"]
    if not isinstance(expected_outputs, list):
        return ["expected_outputs is missing or is not a list"]
    if not isinstance(cases, list):
        return ["cases is missing or is not a list"]

    expected_by_case = {
        entry["case_id"]: entry
        for entry in expected_outputs
        if isinstance(entry, dict) and isinstance(entry.get("case_id"), str)
    }
    cases_by_id = {
        case["case_id"]: case
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("case_id"), str)
    }

    coverage = {
        (candidate.get("case_id"), candidate.get("expected_result"))
        for candidate in candidates
        if isinstance(candidate, dict)
    }
    for group, case_id in REQUIRED_SCENARIO_CASES.items():
        for expected_result in ("pass", "fail"):
            if (case_id, expected_result) not in coverage:
                errors.append(
                    f"missing required PASS/FAIL group: {group} {expected_result}"
                )

    for index, candidate in enumerate(candidates):
        candidate_name = _candidate_name(candidate, index)
        if not isinstance(candidate, dict):
            continue
        case_id = candidate.get("case_id")
        if not isinstance(case_id, str):
            continue
        expected = expected_by_case.get(case_id)
        source_case = cases_by_id.get(case_id)
        if expected is None:
            errors.append(f"{candidate_name}.case_id is unknown in expected outputs: {case_id}")
            continue
        if source_case is None:
            errors.append(f"{candidate_name}.case_id is unknown in review cases: {case_id}")
            continue

        diagnostics = compare_candidate_to_expected(candidate, expected, source_case)
        expected_result = candidate.get("expected_result")
        expected_diagnostics = _string_list(candidate.get("expected_diagnostics"))
        joined_diagnostics = "\n".join(diagnostics)

        if expected_result == "pass" and diagnostics:
            errors.append(
                f"pass candidate {candidate_name} produced diagnostics: {joined_diagnostics}"
            )
        elif expected_result == "fail":
            if not expected_diagnostics:
                errors.append(f"fail candidate {candidate_name}.expected_diagnostics must be non-empty")
            if not diagnostics:
                errors.append(f"fail candidate {candidate_name} produced no diagnostics")
            for expected_keyword in expected_diagnostics:
                if expected_keyword not in joined_diagnostics:
                    errors.append(
                        f"fail candidate {candidate_name} missing expected diagnostic "
                        f"{expected_keyword!r}; got {diagnostics!r}"
                    )

    return errors


def validate_no_forbidden_real_data_markers(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for path, string_value in _walk_strings(data, "data"):
        normalized = string_value.casefold()
        for marker in FORBIDDEN_REAL_DATA_MARKERS:
            if marker in normalized:
                errors.append(
                    f"real_data_marker_present: {path} contains forbidden real data marker: {marker}"
                )
        without_synthetic_ids = re.sub(r"SYN-030-[A-Za-z0-9_-]+", "", string_value)
        without_candidate_ids = re.sub(r"CAND-033-[A-Za-z0-9_-]+", "", without_synthetic_ids)
        if REAL_ENTRY_ID_RE.search(without_candidate_ids):
            errors.append(f"real_data_marker_present: {path} contains a real entry-like numeric id")

    return errors


def validate_static_candidates(
    candidate_data: dict[str, Any],
    expected_data: dict[str, Any],
    cases_data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_candidate_metadata(candidate_data))
    errors.extend(validate_candidate_shape(candidate_data))
    errors.extend(validate_candidate_scenarios(candidate_data, expected_data, cases_data))
    errors.extend(validate_no_forbidden_real_data_markers(candidate_data))
    return errors


def _required_recommendation_diagnostics(
    candidate_id: str,
    case_id: str,
    candidate_output: dict[str, Any],
) -> list[str]:
    diagnostics: list[str] = []
    relance = candidate_output.get("relance_recommandee")
    audit = candidate_output.get("audit_recommande")

    if case_id == "SYN-030-B-family-variants" and not _contains_concept(
        relance,
        "relance_fiche_famille",
    ):
        diagnostics.append(
            f"missing_required_recommendation: {candidate_id} lacks relance_fiche_famille"
        )
    elif case_id == "SYN-030-C-transversal-technique" and not _contains_concept(
        relance,
        "relance_mecanisme_passerelle",
    ):
        diagnostics.append(
            f"missing_required_recommendation: {candidate_id} lacks relance_mecanisme_passerelle"
        )
    elif case_id == "SYN-030-D-unclear-scope":
        has_relance = _contains_concept(relance, "relance_perimetre")
        has_audit = _contains_concept(audit, "audit_routage")
        if not (has_relance or has_audit):
            diagnostics.append(
                f"missing_required_recommendation: {candidate_id} lacks perimeter relance/audit"
            )
    elif case_id == "SYN-030-G-source-status-trap" and not _contains_concept(
        audit,
        "audit_source_later",
    ):
        diagnostics.append(
            f"missing_required_recommendation: {candidate_id} lacks audit_source_later"
        )
    elif case_id == "SYN-030-H-improvisation-classification-trap":
        has_audit = _contains_concept(audit, "audit_classification_later")
        if candidate_output.get("type_unite_propose") != "a_verifier" and not has_audit:
            diagnostics.append(
                "missing_required_recommendation: "
                f"{candidate_id} lacks a_verifier or audit_classification_later"
            )

    return diagnostics


def _forbidden_output_diagnostics(
    candidate_id: str,
    case_id: str,
    candidate_output: dict[str, Any],
) -> list[str]:
    diagnostics: list[str] = []
    flattened = _normalize(_stringify(candidate_output))
    forbidden_hits = [
        forbidden
        for forbidden in FORBIDDEN_OUTPUT_STRINGS
        if _normalize(forbidden) in flattened
    ]
    for forbidden in forbidden_hits:
        diagnostics.append(
            f"forbidden_output_present: {candidate_id} contains {forbidden!r}"
        )

    if any(
        _normalize(value) in flattened
        for value in ("definitive fusion/scission", "definitive merge", "definitive scission")
    ):
        diagnostics.append(
            f"definitive_merge_or_scission: {candidate_id} makes a definitive duplicate decision"
        )

    if case_id == "SYN-030-G-source-status-trap" and any(
        _normalize(value) in flattened
        for value in ("S-A", "source_decisive", "final source audit", "source discovery result")
    ):
        diagnostics.append(
            f"source_status_forbidden: {candidate_id} decides source status"
        )

    if case_id == "SYN-030-H-improvisation-classification-trap" and any(
        _normalize(value) in flattened
        for value in ("I-A", "final classification", "final D/S/I/C/E")
    ):
        diagnostics.append(
            f"classification_forbidden: {candidate_id} decides classification"
        )

    if case_id == "SYN-030-I-publication-trap" and any(
        _normalize(value) in flattened
        for value in ("publication_ready", "final fiche", "completed fiche body")
    ):
        diagnostics.append(
            f"publication_forbidden: {candidate_id} decides publication/final fiche"
        )

    if any(
        _normalize(value) in flattened
        for value in (
            "JournalPatch application",
            "applied JournalPatch",
            "active journal modification",
            "RUN launch",
            "launched RUN",
        )
    ):
        diagnostics.append(
            f"journal_action_forbidden: {candidate_id} attempts journal/RUN action"
        )

    if any(
        _normalize(value) in flattened
        for value in ("candidate selection outside explicit scope", "select candidates")
    ):
        diagnostics.append(
            f"candidate_selection_forbidden: {candidate_id} selects candidates"
        )

    return diagnostics


def _metadata_value_matches(field: str, actual_value: object, expected_value: str) -> bool:
    if field == "codex":
        try:
            return f"{int(str(actual_value)):03d}" == expected_value
        except ValueError:
            return str(actual_value) == expected_value
    return str(actual_value) == expected_value


def _candidate_name(candidate: object, index: int) -> str:
    if isinstance(candidate, dict) and isinstance(candidate.get("candidate_id"), str):
        return str(candidate["candidate_id"])
    return f"candidates[{index}]"


def _string_list(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str))


def _has_content(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(_has_content(item) for item in value)
    return value is True


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def _contains_concept(value: object, concept: str) -> bool:
    return _normalize(concept) in _normalize(_stringify(value))


def _stringify(value: object) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _walk_strings(value: object, path: str) -> list[tuple[str, str]]:
    strings: list[tuple[str, str]] = []
    if isinstance(value, str):
        strings.append((path, value))
    elif isinstance(value, dict):
        for key, item in value.items():
            strings.extend(_walk_strings(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            strings.extend(_walk_strings(item, f"{path}[{index}]"))
    return strings
