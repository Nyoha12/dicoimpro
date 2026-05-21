import pytest
from pydantic import ValidationError

from dico_impro.manifest import DataManifest, load_manifest


def test_manifest_loads_and_uses_single_local_files_root():
    manifest = load_manifest("data_manifest.yaml")

    assert manifest.project == "dicoimpro"
    assert manifest.local_files_root == "data/local_files/"
    assert len(manifest.files) >= 1
    assert all(item.local_path.startswith("data/local_files/") for item in manifest.files)


def test_manifest_flags_journal_as_non_documentary_and_readonly():
    manifest = load_manifest("data_manifest.yaml")
    journals = [item for item in manifest.files if item.layer == "steering_journal"]

    assert len(journals) == 1
    journal = journals[0]
    assert journal.may_be_used_as_documentary_source is False
    assert journal.may_be_written_directly_by_pipeline is False
    assert journal.status == "active_temporary_steering_journal_readonly"


def test_manifest_has_no_default_documentary_reference_for_now():
    manifest = load_manifest("data_manifest.yaml")
    documentary = manifest.documentary_files()

    assert documentary == []


def test_manifest_marks_old_pdf_as_legacy_optional_reference():
    manifest = load_manifest("data_manifest.yaml")
    legacy_refs = [item for item in manifest.files if item.file_name == "Improvisation musicale mondiale.pdf"]

    assert len(legacy_refs) == 1
    old_pdf = legacy_refs[0]
    assert old_pdf.status == "legacy_optional_reference"
    assert old_pdf.layer == "legacy_reference"
    assert old_pdf.may_be_used_as_documentary_source is False
    assert old_pdf.required_for_bootstrap is False
    assert old_pdf.requires_explicit_activation is True


def test_manifest_rejects_unknown_file_fields():
    raw_manifest = {
        "project": "dicoimpro",
        "protocol_version": "v0.2.3",
        "automation_layer": "v0.2.3-auto",
        "files": [
            {
                "file_name": "bad.xlsx",
                "local_path": "data/local_files/bad.xlsx",
                "status": "bad",
                "role": "bad",
                "may_be_used_as_doc_source": True,
            }
        ],
    }

    with pytest.raises(ValidationError):
        DataManifest.model_validate(raw_manifest)
