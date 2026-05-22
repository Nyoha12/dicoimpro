from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from pydantic import ValidationError

from dico_impro.exports import export_dry_run_result_json
from dico_impro.journal_reader import check_post005_guards, load_journal_records
from dico_impro.manifest import DataManifest, load_manifest
from dico_impro.models import ClassificationInput, Indices, SourceAuditInput
from dico_impro.orchestration import ExplicitScope, run_dry_run
from dico_impro.validators import validate_classification


def _print_json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def _print_error(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str), file=sys.stderr)


def _find_journal_file(manifest: DataManifest) -> Path:
    candidates = [item for item in manifest.files if item.layer == "steering_journal"]
    if len(candidates) != 1:
        raise ValueError(f"Expected exactly one steering_journal file, found {len(candidates)}")
    return Path(candidates[0].local_path)


def cmd_check_manifest(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest)
    root = Path(args.root)
    missing_required: list[str] = []
    missing_optional: list[str] = []
    present: list[str] = []

    for item in manifest.files:
        path = root / item.local_path
        if path.exists():
            present.append(item.file_name)
        elif item.required_for_bootstrap:
            missing_required.append(item.file_name)
        else:
            missing_optional.append(item.file_name)

    result = {
        "project": manifest.project,
        "protocol_version": manifest.protocol_version,
        "automation_layer": manifest.automation_layer,
        "present": present,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "ok": not missing_required,
    }
    _print_json(result)
    return 0 if not missing_required else 1


def cmd_check_journal_post005(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest)
    root = Path(args.root)
    journal_path = root / _find_journal_file(manifest)

    if not journal_path.exists():
        _print_json(
            {
                "ok": False,
                "error": "journal_file_missing",
                "journal_path": str(journal_path),
            }
        )
        return 1

    records = load_journal_records(journal_path)
    report = check_post005_guards(records)
    _print_json(
        {
            "ok": report.ok,
            "journal_path": str(journal_path),
            "id_026_guard_ok": report.id_026_guard_ok,
            "id_030_guard_ok": report.id_030_guard_ok,
            "id_032_guard_ok": report.id_032_guard_ok,
        }
    )
    return 0 if report.ok else 1


def cmd_validate_sample(_: argparse.Namespace) -> int:
    sample = ClassificationInput(
        id_entree_original="SAMPLE",
        indices=Indices(D="D-A", S="S-A", I="I-A", C="C-A", E="E-B"),
        sources=[
            SourceAuditInput(
                source_id="SRC-SAMPLE-1",
                role_source="contexte",
                source_decisive="non",
                verification_independante=False,
            )
        ],
        preuve_improvisation_centrale_explicitement_documentee=False,
        perimetre_stable=False,
    )
    report = validate_classification(sample)
    _print_json(report.model_dump(mode="json"))
    return 0


def cmd_plan_batch(args: argparse.Namespace) -> int:
    scope_path = Path(args.scope)
    output_dir = Path(args.output_dir)

    if not scope_path.is_file():
        _print_error(
            {
                "ok": False,
                "error": "scope_file_missing",
                "scope": str(scope_path),
            }
        )
        return 1

    if output_dir.exists() and not output_dir.is_dir():
        _print_error(
            {
                "ok": False,
                "error": "output_path_not_directory",
                "output_dir": str(output_dir),
            }
        )
        return 1

    try:
        scope_payload = json.loads(scope_path.read_text(encoding="utf-8"))
        scope = ExplicitScope.model_validate(scope_payload)
        result = run_dry_run(scope)
        export_report = export_dry_run_result_json(result, output_dir)
    except (OSError, json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        _print_error(
            {
                "ok": False,
                "error": "dry_run_failed",
                "detail": str(exc),
            }
        )
        return 1

    batch_report = result.batch_report
    _print_json(
        {
            "ok": True,
            "batch_id": batch_report.batch_id,
            "output_dir": str(export_report.output_dir),
            "created_files": sorted(
                path.name for path in export_report.created_files.values()
            ),
            "entries_total": batch_report.entries_total,
            "entries_processed": batch_report.entries_processed,
            "entries_skipped": batch_report.entries_skipped,
            "entries_blocked": batch_report.entries_blocked,
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dico-impro")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_manifest = subparsers.add_parser(
        "check-manifest",
        help="Vérifie que les fichiers listés dans data_manifest.yaml existent localement.",
    )
    check_manifest.add_argument("--manifest", default="data_manifest.yaml")
    check_manifest.add_argument("--root", default=".")
    check_manifest.set_defaults(func=cmd_check_manifest)

    check_journal = subparsers.add_parser(
        "check-journal-post005",
        help="Vérifie les garde-fous post-005 du journal de pilotage, sans le modifier.",
    )
    check_journal.add_argument("--manifest", default="data_manifest.yaml")
    check_journal.add_argument("--root", default=".")
    check_journal.set_defaults(func=cmd_check_journal_post005)

    validate_sample = subparsers.add_parser(
        "validate-sample",
        help="Exécute un exemple de validation automatique sans lire ni écrire de fichier projet.",
    )
    validate_sample.set_defaults(func=cmd_validate_sample)

    plan_batch = subparsers.add_parser(
        "plan-batch",
        help="Prepare a local dry-run batch from an explicit JSON scope.",
    )
    plan_batch.add_argument("--dry-run", action="store_true", required=True)
    plan_batch.add_argument("--scope", required=True)
    plan_batch.add_argument("--output-dir", required=True)
    plan_batch.set_defaults(func=cmd_plan_batch)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
