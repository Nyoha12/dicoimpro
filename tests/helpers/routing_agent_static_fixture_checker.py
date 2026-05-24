from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REQUIRED_METADATA_VALUES = {
    "status": "synthetic_review_fixtures",
    "codex": "030",
    "target_agent": "RoutingAgent",
    "prompt_draft_status": "disabled",
}

REQUIRED_METADATA_FALSE_FLAGS = (
    "execution_allowed",
    "runtime_allowed",
    "openai_allowed",
    "real_entries_allowed",
    "active_journal_allowed",
    "run_allowed",
    "journal_patch_allowed",
    "final_contract",
    "runtime_enum_source",
)

CASE_PERMISSION_FLAGS = (
    "execution_allowed",
    "runtime_allowed",
    "openai_allowed",
    "run_allowed",
    "journal_patch_allowed",
)

REQUIRED_CASE_FIELDS = (
    "case_id",
    "label",
    "supplied_input",
    "expected_safe_route",
    "expected_risk_flags",
    "expected_recommendations",
    "forbidden_outputs",
    "review_notes",
)

REQUIRED_CASE_FAMILIES = {
    "broad system": "SYN-030-A-broad-system",
    "family variants": "SYN-030-B-family-variants",
    "transversal technique": "SYN-030-C-transversal-technique",
    "unclear scope": "SYN-030-D-unclear-scope",
    "duplicate/transliteration": "SYN-030-E-duplicate-transliteration",
    "missing type_unite_RUN": "SYN-030-F-missing-type-unite-run",
    "source-status trap": "SYN-030-G-source-status-trap",
    "improvisation-classification trap": "SYN-030-H-improvisation-classification-trap",
    "publication trap": "SYN-030-I-publication-trap",
    "JournalPatch/RUN trap": "SYN-030-J-journalpatch-run-trap",
}

REQUIRED_SAFE_ROUTES = (
    "fiche_cadre",
    "fiche_famille",
    "mecanisme_passerelle",
    "controle_perimetre",
    "alias_doublon",
    "a_verifier",
)

REQUIRED_FORBIDDEN_OUTPUTS = (
    "S-A",
    "I-A",
    "final source_decisive",
    "source_decisive",
    "final source audit",
    "publication_ready",
    "final fiche",
    "definitive fusion/scission",
    "JournalPatch application",
    "active journal modification",
    "RUN launch",
    "launched RUN",
    "candidate selection outside explicit scope",
    "source discovery result",
    "final classification",
)

REQUIRED_RECOMMENDATION_CONCEPTS = (
    "relance_perimetre",
    "relance_alias_doublon",
    "relance_fiche_famille",
    "relance_mecanisme_passerelle",
    "audit_routage",
    "audit_source_later",
    "audit_classification_later",
    "run_interdit_raison",
    "type_unite_RUN is mandatory before RUN",
)

FORBIDDEN_SUPPLIED_INPUT_MARKERS = (
    "data/local_files",
    "data\\local_files",
    "active_journal/",
    "active_journal\\",
    "journal_actif",
    "old pdf",
    "old_pdf",
    ".pdf",
)

REAL_ENTRY_ID_RE = re.compile(
    r"\b(?:entry|entree|fiche|source|project|projet|run)[-_ ]?\d{3,}\b|\b\d{4,}\b",
    re.IGNORECASE,
)


def load_fixture(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Fixture must contain one JSON object: {path}")
    return data


def validate_fixture_metadata(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    metadata = data.get("metadata") if isinstance(data, dict) else None
    if not isinstance(metadata, dict):
        return ["metadata is missing or is not an object"]

    for field, expected_value in REQUIRED_METADATA_VALUES.items():
        if field not in metadata:
            errors.append(f"metadata.{field} is missing")
            continue
        actual_value = metadata[field]
        if str(actual_value) != expected_value:
            errors.append(
                f"metadata.{field} must be {expected_value!r}; got {actual_value!r}"
            )

    for field in REQUIRED_METADATA_FALSE_FLAGS:
        if field not in metadata:
            errors.append(f"metadata.{field} is missing")
            continue
        if metadata[field] is not False:
            errors.append(f"metadata.{field} must be false")

    return errors


def validate_fixture_cases(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list):
        return ["cases is missing or is not a list"]
    if not cases:
        return ["cases must be non-empty"]

    for index, case in enumerate(cases):
        case_name = _case_name(case, index)
        if not isinstance(case, dict):
            errors.append(f"{case_name} must be an object")
            continue

        for field in REQUIRED_CASE_FIELDS:
            if field not in case:
                errors.append(f"{case_name}.{field} is missing")

        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id.startswith("SYN-030-"):
            errors.append(f"{case_name}.case_id must start with 'SYN-030-'")

        supplied_input = case.get("supplied_input")
        if not isinstance(supplied_input, dict):
            errors.append(f"{case_name}.supplied_input must be an object")
        else:
            entry_id = supplied_input.get("entry_id")
            if not isinstance(entry_id, str) or not entry_id.startswith("SYN-030-"):
                errors.append(
                    f"{case_name}.supplied_input.entry_id must start with 'SYN-030-'"
                )
            entry_label = supplied_input.get("entry_label")
            if not isinstance(entry_label, str) or not entry_label.strip():
                errors.append(f"{case_name}.supplied_input.entry_label is missing")

        for field in CASE_PERMISSION_FLAGS:
            if case.get(field) is True:
                errors.append(f"{case_name}.{field} must not claim permission")
            if isinstance(supplied_input, dict) and supplied_input.get(field) is True:
                errors.append(
                    f"{case_name}.supplied_input.{field} must not claim permission"
                )

    return errors


def validate_fixture_coverage(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list):
        return ["cases is missing or is not a list"]

    case_ids = {
        case.get("case_id")
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("case_id"), str)
    }
    for family, required_case_id in REQUIRED_CASE_FAMILIES.items():
        if required_case_id not in case_ids:
            errors.append(f"required case family is missing: {family}")

    safe_routes = {
        case.get("expected_safe_route")
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("expected_safe_route"), str)
    }
    for route in REQUIRED_SAFE_ROUTES:
        if route not in safe_routes:
            errors.append(f"required safe route is missing: {route}")

    forbidden_outputs = {
        output
        for case in cases
        if isinstance(case, dict)
        for output in _string_list(case.get("forbidden_outputs"))
    }
    normalized_forbidden_outputs = {_normalize(output) for output in forbidden_outputs}
    for output in REQUIRED_FORBIDDEN_OUTPUTS:
        if _normalize(output) not in normalized_forbidden_outputs:
            errors.append(f"required forbidden output is missing: {output}")

    recommendation_text = "\n".join(
        recommendation
        for case in cases
        if isinstance(case, dict)
        for recommendation in _string_list(case.get("expected_recommendations"))
    )
    normalized_recommendation_text = _normalize(recommendation_text)
    for concept in REQUIRED_RECOMMENDATION_CONCEPTS:
        if _normalize(concept) not in normalized_recommendation_text:
            errors.append(f"required recommendation concept is missing: {concept}")

    return errors


def validate_no_forbidden_real_data_markers(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list):
        return ["cases is missing or is not a list"]

    for index, case in enumerate(cases):
        case_name = _case_name(case, index)
        if not isinstance(case, dict):
            continue
        supplied_input = case.get("supplied_input")
        if not isinstance(supplied_input, dict):
            continue

        for path, value in _walk_strings(supplied_input, f"{case_name}.supplied_input"):
            normalized = value.casefold()
            for marker in FORBIDDEN_SUPPLIED_INPUT_MARKERS:
                if marker in normalized:
                    errors.append(f"{path} contains forbidden real data marker: {marker}")
            value_without_synthetic_ids = re.sub(r"SYN-030-[A-Za-z0-9_-]+", "", value)
            if REAL_ENTRY_ID_RE.search(value_without_synthetic_ids):
                errors.append(f"{path} contains a real entry-like numeric id")

    return errors


def validate_static_fixture(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_fixture_metadata(data))
    errors.extend(validate_fixture_cases(data))
    errors.extend(validate_no_forbidden_real_data_markers(data))
    errors.extend(validate_fixture_coverage(data))
    return errors


def _case_name(case: object, index: int) -> str:
    if isinstance(case, dict) and isinstance(case.get("case_id"), str):
        return str(case["case_id"])
    return f"cases[{index}]"


def _string_list(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str))


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())


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
