from dico_impro.models import ClassificationInput, Indices, SourceAuditInput
from dico_impro.validators import validate_classification


def test_s_a_without_decisive_source_is_downgraded_to_s_b():
    report = validate_classification(
        ClassificationInput(
            id_entree_original="999",
            indices=Indices(D="D-A", S="S-A", I="I-B", C="C-B1", E="E-B"),
            sources=[
                SourceAuditInput(
                    source_id="SRC-1",
                    role_source="contexte",
                    source_decisive="non",
                    verification_independante=True,
                )
            ],
        )
    )

    assert report.indices_apres_validation.S == "S-B"
    assert report.run_002_requis is True
    assert any(c.regle == "V-S-001" for c in report.corrections_automatiques)


def test_i_a_without_central_improvisation_proof_is_downgraded_to_i_b():
    report = validate_classification(
        ClassificationInput(
            id_entree_original="999",
            indices=Indices(D="D-A", S="S-B", I="I-A", C="C-B1", E="E-B"),
            preuve_improvisation_centrale_explicitement_documentee=False,
        )
    )

    assert report.indices_apres_validation.I == "I-B"
    assert any(c.regle == "V-I-001" for c in report.corrections_automatiques)


def test_c_a_without_stable_scope_is_downgraded_to_c_b1():
    report = validate_classification(
        ClassificationInput(
            id_entree_original="999",
            indices=Indices(D="D-A", S="S-B", I="I-B", C="C-A", E="E-B"),
            perimetre_stable=False,
        )
    )

    assert report.indices_apres_validation.C == "C-B1"
    assert any(c.regle == "V-C-001" for c in report.corrections_automatiques)


def test_d_b_blocks_publication():
    report = validate_classification(
        ClassificationInput(
            id_entree_original="999",
            indices=Indices(D="D-B", S="S-B", I="I-B", C="C-B1", E="E-B"),
        )
    )

    assert report.publication_bloquee is True
    assert report.audit_gravite == "rouge"
    assert report.validation_status == "non_publiable_en_l_etat"
