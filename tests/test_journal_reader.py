from pathlib import Path

from openpyxl import Workbook

from dico_impro.journal_reader import (
    check_post005_guards,
    index_records_by_id,
    load_journal_records,
    normalize_id,
)


def test_normalize_id_pads_numeric_values():
    assert normalize_id(26) == "026"
    assert normalize_id("30") == "030"
    assert normalize_id("32") == "032"


def test_load_journal_records_finds_header_row(tmp_path: Path):
    path = tmp_path / "journal.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "JOURNAL"
    sheet.append(["Mode emploi", None])
    sheet.append(["id_entree_original", "titre_original_exact", "statut_traitement"])
    sheet.append([26, "Raga hindoustani", "RUN_002_fait"])
    workbook.save(path)

    records = load_journal_records(path)

    assert len(records) == 1
    assert records[0]["titre_original_exact"] == "Raga hindoustani"
    assert records[0]["_row_index"] == 3
    assert index_records_by_id(records)["026"]["statut_traitement"] == "RUN_002_fait"


def test_load_journal_records_tracks_real_row_index(tmp_path: Path):
    path = tmp_path / "journal.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "JOURNAL"
    sheet.append(["Mode emploi", None])
    sheet.append(["id_entree_original", "titre_original_exact", "statut_traitement"])
    sheet.append([26, "Raga hindoustani", "RUN_002_fait"])
    sheet.append([30, "Maqam", "RUN_002_fait"])
    workbook.save(path)

    records = load_journal_records(path)

    assert [record["_row_index"] for record in records] == [3, 4]


def test_post005_guards_accept_expected_state():
    records = [
        {"id_entree_original": "026", "statut_traitement": "RUN_002_fait"},
        {"id_entree_original": "030", "statut_traitement": "RUN_002_fait"},
        {"id_entree_original": "032", "statut_traitement": "reserve_P2_non_traite"},
    ]

    report = check_post005_guards(records)

    assert report.ok is True


def test_post005_guards_fail_if_032_marked_run_done():
    records = [
        {"id_entree_original": "026", "statut_traitement": "RUN_002_fait"},
        {"id_entree_original": "030", "statut_traitement": "RUN_002_fait"},
        {"id_entree_original": "032", "statut_traitement": "RUN_002_fait"},
    ]

    report = check_post005_guards(records)

    assert report.ok is False
    assert report.id_032_guard_ok is False
