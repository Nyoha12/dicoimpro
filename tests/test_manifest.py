from dico_impro.manifest import load_manifest


def test_manifest_loads_and_uses_single_local_files_root():
    manifest = load_manifest("data_manifest.yaml")

    assert manifest.project == "dicoimpro"
    assert manifest.local_files_root == "data/local_files/"
    assert len(manifest.files) >= 1
    assert all(item.local_path.startswith("data/local_files/") for item in manifest.files)


def test_manifest_flags_journal_as_non_documentary_and_readonly():
    manifest = load_manifest("data_manifest.yaml")
    files = manifest.by_file_name()
    journal = files["JOURNAL_PILOTAGE_ACTIF_TEMP_v0.2.3_POST005_RUN002_026030_NON_SOURCE_DOC.xlsx"]

    assert journal.may_be_used_as_documentary_source is False
    assert journal.may_be_written_directly_by_pipeline is False
    assert journal.layer == "steering_journal"


def test_manifest_has_only_pdf_as_documentary_reference_for_now():
    manifest = load_manifest("data_manifest.yaml")
    documentary = manifest.documentary_files()

    assert [item.file_name for item in documentary] == ["Improvisation musicale mondiale.pdf"]
