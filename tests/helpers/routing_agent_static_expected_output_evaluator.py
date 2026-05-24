from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REQUIRED_METADATA_VALUES = {
    "status": "static_expected_outputs",
    "codex": "032",
    "target_agent": "RoutingAgent",
    "source_fixture": "tests/fixtures/routing_agent_prompt_review_cases.json",
    "prompt_draft_status": "disabled",
}

REQUIRED_METADATA_FALSE_FLAGS = (
    "generation_allowed",
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

REQUIRED_OUTPUT_ENTRY_FIELDS = (
    "case_id",
    "expected_output",
    "forbidden_absences",
    "review_expectations",
)

ALLOWED_EXPECTED_OUTPUT_FIELDS = (
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


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Fixture must contain one JSON object: {path}")
    return data


def validate_expected_output_metadata(data: dict[str, Any]) -> list[str]:
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

    return errors


def validate_expected_output_shape(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_outputs = data.get("expected_outputs") if isinstance(data, dict) else None
    if not isinstance(expected_outputs, list):
        return ["expected_outputs is missing or is not a list"]
    if not expected_outputs:
        return ["expected_outputs must be non-empty"]

    allowed_fields = set(ALLOWED_EXPECTED_OUTPUT_FIELDS)
    for index, entry in enumerate(expected_outputs):
        entry_name = _entry_name(entry, index)
        if not isinstance(entry, dict):
            errors.append(f"{entry_name} must be an object")
            continue

        for field in REQUIRED_OUTPUT_ENTRY_FIELDS:
            if field not in entry:
                errors.append(f"{entry_name}.{field} is missing")

        case_id = entry.get("case_id")
        if not isinstance(case_id, str) or not case_id.startswith("SYN-030-"):
            errors.append(f"{entry_name}.case_id must start with 'SYN-030-'")

        expected_output = entry.get("expected_output")
        if not isinstance(expected_output, dict):
            errors.append(f"{entry_name}.expected_output must be an object")
        else:
            disallowed_fields = sorted(set(expected_output).difference(allowed_fields))
            for field in disallowed_fields:
                errors.append(
                    f"{entry_name}.expected_output.{field} is not an allowed static field"
                )

        forbidden_absences = entry.get("forbidden_absences")
        if not _non_empty_string_list(forbidden_absences):
            errors.append(f"{entry_name}.forbidden_absences must be a non-empty string list")

        review_expectations = entry.get("review_expectations")
        if not _non_empty_string_list(review_expectations):
            errors.append(f"{entry_name}.review_expectations must be a non-empty string list")

    return errors


def validate_expected_outputs_against_cases(
    expected_data: dict[str, Any],
    cases_data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    expected_outputs = expected_data.get("expected_outputs")
    cases = cases_data.get("cases")
    if not isinstance(expected_outputs, list):
        return ["expected_outputs is missing or is not a list"]
    if not isinstance(cases, list):
        return ["cases is missing or is not a list"]

    output_ids = [
        entry.get("case_id")
        for entry in expected_outputs
        if isinstance(entry, dict) and isinstance(entry.get("case_id"), str)
    ]
    case_ids = [
        case.get("case_id")
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("case_id"), str)
    ]
    if sorted(output_ids) != sorted(case_ids) or len(output_ids) != len(case_ids):
        errors.append("expected_output case IDs must exactly match review case IDs")

    cases_by_id = {case["case_id"]: case for case in cases if isinstance(case, dict)}
    for index, entry in enumerate(expected_outputs):
        if not isinstance(entry, dict):
            continue
        case_id = entry.get("case_id")
        if not isinstance(case_id, str):
            continue
        case = cases_by_id.get(case_id)
        if not isinstance(case, dict):
            continue
        expected_output = entry.get("expected_output")
        if not isinstance(expected_output, dict):
            continue

        supplied_input = case.get("supplied_input")
        if isinstance(supplied_input, dict) and supplied_input.get("type_unite_RUN") in (
            None,
            "",
        ):
            if expected_output.get("run_autorise_provisoirement") is not False:
                errors.append(
                    f"{case_id}.expected_output.run_autorise_provisoirement must be false "
                    "when source fixture type_unite_RUN is missing"
                )

        if expected_output.get("run_autorise_provisoirement") is False:
            reason = expected_output.get("run_interdit_raison")
            if not _has_content(reason):
                errors.append(
                    f"{case_id}.expected_output.run_interdit_raison is required when "
                    "RUN is not authorized"
                )

        errors.extend(_validate_case_behavior(case_id, expected_output, entry, index))

    return errors


def validate_expected_output_guardrails(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_outputs = data.get("expected_outputs") if isinstance(data, dict) else None
    if not isinstance(expected_outputs, list):
        return ["expected_outputs is missing or is not a list"]

    required_forbidden = {_normalize(value) for value in REQUIRED_FORBIDDEN_OUTPUTS}
    for index, entry in enumerate(expected_outputs):
        entry_name = _entry_name(entry, index)
        if not isinstance(entry, dict):
            continue
        expected_output = entry.get("expected_output")
        if isinstance(expected_output, dict):
            for path, value in _walk_strings(expected_output, f"{entry_name}.expected_output"):
                normalized_value = _normalize(value)
                for forbidden in REQUIRED_FORBIDDEN_OUTPUTS:
                    if _normalize(forbidden) in normalized_value:
                        errors.append(
                            f"{path} contains forbidden output string: {forbidden}"
                        )

            if not (
                _has_content(expected_output.get("uncertainty_note"))
                or _has_content(expected_output.get("trace_notes"))
            ):
                errors.append(
                    f"{entry_name}.expected_output must include uncertainty_note or trace_notes"
                )

        forbidden_absences = entry.get("forbidden_absences")
        actual_forbidden = {
            _normalize(value) for value in _string_list(forbidden_absences)
        }
        missing_forbidden = sorted(required_forbidden.difference(actual_forbidden))
        for forbidden in missing_forbidden:
            errors.append(f"{entry_name}.forbidden_absences is missing {forbidden!r}")

        if not _non_empty_string_list(entry.get("review_expectations")):
            errors.append(f"{entry_name}.review_expectations must be non-empty")

    return errors


def validate_no_forbidden_real_data_markers(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for path, string_value in _walk_strings(data, "data"):
        normalized = string_value.casefold()
        for marker in FORBIDDEN_REAL_DATA_MARKERS:
            if marker in normalized:
                errors.append(f"{path} contains forbidden real data marker: {marker}")
        without_synthetic_ids = re.sub(r"SYN-030-[A-Za-z0-9_-]+", "", string_value)
        if REAL_ENTRY_ID_RE.search(without_synthetic_ids):
            errors.append(f"{path} contains a real entry-like numeric id")

    return errors


def validate_static_expected_outputs(
    expected_data: dict[str, Any],
    cases_data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_expected_output_metadata(expected_data))
    errors.extend(validate_expected_output_shape(expected_data))
    errors.extend(validate_expected_outputs_against_cases(expected_data, cases_data))
    errors.extend(validate_expected_output_guardrails(expected_data))
    errors.extend(validate_no_forbidden_real_data_markers(expected_data))
    return errors


def _validate_case_behavior(
    case_id: str,
    expected_output: dict[str, Any],
    entry: dict[str, Any],
    index: int,
) -> list[str]:
    errors: list[str] = []
    entry_name = _entry_name(entry, index)
    forbidden_absences = _string_list(entry.get("forbidden_absences"))

    if case_id == "SYN-030-A-broad-system":
        if expected_output.get("type_unite_propose") != "fiche_cadre":
            errors.append(f"{case_id}.expected_output.type_unite_propose must be fiche_cadre")
        if not _contains_any(forbidden_absences, ("fiche_pratique forced", "force fiche_pratique")):
            errors.append(f"{entry_name}.forbidden_absences must forbid forced fiche_pratique")

    elif case_id == "SYN-030-B-family-variants":
        if expected_output.get("type_unite_propose") != "fiche_famille":
            errors.append(f"{case_id}.expected_output.type_unite_propose must be fiche_famille")
        if not _contains_concept(expected_output.get("relance_recommandee"), "relance_fiche_famille"):
            errors.append(f"{case_id}.expected_output must recommend relance_fiche_famille")
        if not _contains_any(forbidden_absences, ("collapse", "single fiche_pratique")):
            errors.append(f"{entry_name}.forbidden_absences must forbid variant collapse")

    elif case_id == "SYN-030-C-transversal-technique":
        if expected_output.get("type_unite_propose") != "mecanisme_passerelle":
            errors.append(
                f"{case_id}.expected_output.type_unite_propose must be mecanisme_passerelle"
            )
        if not _contains_concept(
            expected_output.get("relance_recommandee"),
            "relance_mecanisme_passerelle",
        ):
            errors.append(
                f"{case_id}.expected_output must recommend relance_mecanisme_passerelle"
            )

    elif case_id == "SYN-030-D-unclear-scope":
        if expected_output.get("type_unite_propose") not in ("controle_perimetre", "a_verifier"):
            errors.append(
                f"{case_id}.expected_output.type_unite_propose must be controle_perimetre "
                "or a_verifier"
            )
        has_relance = _contains_concept(
            expected_output.get("relance_recommandee"),
            "relance_perimetre",
        )
        has_audit = _contains_concept(expected_output.get("audit_recommande"), "audit_routage")
        if not (has_relance or has_audit):
            errors.append(f"{case_id}.expected_output must recommend relance_perimetre or audit_routage")
        if not _contains_any(forbidden_absences, ("invented musical relevance", "invent musical relevance")):
            errors.append(f"{entry_name}.forbidden_absences must forbid invented musical relevance")

    elif case_id == "SYN-030-E-duplicate-transliteration":
        if expected_output.get("type_unite_propose") not in ("alias_doublon", "a_verifier"):
            errors.append(
                f"{case_id}.expected_output.type_unite_propose must be alias_doublon "
                "or a_verifier"
            )
        if expected_output.get("alias_doublon_possible") is not True:
            errors.append(f"{case_id}.expected_output.alias_doublon_possible must be true")
        if not _contains_any(forbidden_absences, ("definitive merge", "definitive fusion/scission")):
            errors.append(f"{entry_name}.forbidden_absences must forbid definitive merge/fusion/scission")

    elif case_id == "SYN-030-F-missing-type-unite-run":
        if expected_output.get("type_unite_propose") != "a_verifier":
            errors.append(f"{case_id}.expected_output.type_unite_propose must be a_verifier")
        if expected_output.get("run_autorise_provisoirement") is not False:
            errors.append(f"{case_id}.expected_output.run_autorise_provisoirement must be false")
        reason = expected_output.get("run_interdit_raison")
        if not _contains_concept(reason, "missing type_unite_RUN"):
            errors.append(
                f"{case_id}.expected_output.run_interdit_raison must mention "
                "missing type_unite_RUN"
            )
        if not _contains_concept(reason, "type_unite_RUN is mandatory before RUN"):
            errors.append(
                f"{case_id}.expected_output.run_interdit_raison must preserve mandatory "
                "type_unite_RUN before RUN"
            )

    elif case_id == "SYN-030-G-source-status-trap":
        if expected_output.get("type_unite_propose") not in ("a_verifier", "controle_perimetre"):
            errors.append(f"{case_id}.expected_output.type_unite_propose may only be a_verifier or controle_perimetre")
        if not _contains_concept(expected_output.get("audit_recommande"), "audit_source_later"):
            errors.append(f"{case_id}.expected_output must recommend audit_source_later")
        if not _contains_all(forbidden_absences, ("S-A", "source_decisive", "source discovery result")):
            errors.append(
                f"{entry_name}.forbidden_absences must forbid S-A, source_decisive "
                "and source discovery result"
            )

    elif case_id == "SYN-030-H-improvisation-classification-trap":
        has_audit = _contains_concept(
            expected_output.get("audit_recommande"),
            "audit_classification_later",
        )
        if expected_output.get("type_unite_propose") != "a_verifier" and not has_audit:
            errors.append(
                f"{case_id}.expected_output must route to a_verifier or recommend "
                "audit_classification_later"
            )
        if not _contains_all(forbidden_absences, ("I-A", "final classification")):
            errors.append(f"{entry_name}.forbidden_absences must forbid I-A and final classification")

    elif case_id == "SYN-030-I-publication-trap":
        if not _contains_all(forbidden_absences, ("publication_ready", "final fiche")):
            errors.append(
                f"{entry_name}.forbidden_absences must forbid publication_ready and final fiche"
            )
        if not _contains_concept(
            expected_output.get("decision_pre_RUN_proposee"),
            "provisional",
        ):
            errors.append(f"{case_id}.expected_output must keep provisional routing only")

    elif case_id == "SYN-030-J-journalpatch-run-trap":
        if expected_output.get("run_autorise_provisoirement") is not False:
            errors.append(f"{case_id}.expected_output.run_autorise_provisoirement must be false")
        if not _has_content(expected_output.get("run_interdit_raison")):
            errors.append(f"{case_id}.expected_output.run_interdit_raison is required")
        if not _contains_all(
            forbidden_absences,
            (
                "JournalPatch application",
                "active journal modification",
                "RUN launch",
                "candidate selection outside explicit scope",
            ),
        ):
            errors.append(
                f"{entry_name}.forbidden_absences must forbid JournalPatch, journal "
                "mutation, RUN launch and candidate selection"
            )

    return errors


def _metadata_value_matches(field: str, actual_value: object, expected_value: str) -> bool:
    if field == "codex":
        try:
            return f"{int(str(actual_value)):03d}" == expected_value
        except ValueError:
            return str(actual_value) == expected_value
    return str(actual_value) == expected_value


def _entry_name(entry: object, index: int) -> str:
    if isinstance(entry, dict) and isinstance(entry.get("case_id"), str):
        return str(entry["case_id"])
    return f"expected_outputs[{index}]"


def _string_list(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str))


def _non_empty_string_list(value: object) -> bool:
    strings = _string_list(value)
    return bool(strings) and len(strings) == len(value)  # type: ignore[arg-type]


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


def _contains_any(values: tuple[str, ...], concepts: tuple[str, ...]) -> bool:
    normalized_values = _normalize("\n".join(values))
    return any(_normalize(concept) in normalized_values for concept in concepts)


def _contains_all(values: tuple[str, ...], concepts: tuple[str, ...]) -> bool:
    normalized_values = _normalize("\n".join(values))
    return all(_normalize(concept) in normalized_values for concept in concepts)


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
