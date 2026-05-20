from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from dico_impro.manifest import load_manifest
from dico_impro.models import ClassificationInput, Indices, SourceAuditInput
from dico_impro.validators import validate_classification


def _print_json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def cmd_check_manifest(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest)
    root = Path(args.root)
    missing: list[str] = []
    present: list[str] = []

    for item in manifest.files:
        path = root / item.local_path
        if path.exists():
            present.append(item.file_name)
        else:
            missing.append(item.file_name)

    result = {
        "project": manifest.project,
        "protocol_version": manifest.protocol_version,
        "automation_layer": manifest.automation_layer,
        "present": present,
        "missing": missing,
        "ok": not missing,
    }
    _print_json(result)
    return 0 if not missing else 1


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

    validate_sample = subparsers.add_parser(
        "validate-sample",
        help="Exécute un exemple de validation automatique sans lire ni écrire de fichier projet.",
    )
    validate_sample.set_defaults(func=cmd_validate_sample)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
