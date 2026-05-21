import pytest

from dico_impro.orchestrator import PipelineConfig, PipelineStep, assert_pipeline_guards, build_default_steps


def test_default_pipeline_steps_define_system_architecture_order():
    steps = build_default_steps()

    assert steps[0] == PipelineStep.LOAD_MANIFEST
    assert PipelineStep.BUILD_AGENT_TASKS in steps
    assert PipelineStep.BUILD_JOURNAL_PATCH in steps
    assert steps[-1] == PipelineStep.WRITE_OUTPUT_ARTIFACTS


def test_pipeline_blocks_direct_journal_write():
    config = PipelineConfig(batch_id="BATCH-TEST", allow_direct_journal_write=True)

    with pytest.raises(ValueError):
        assert_pipeline_guards(config)


def test_pipeline_blocks_legacy_pdf_by_default():
    config = PipelineConfig(batch_id="BATCH-TEST", use_legacy_pdf_by_default=True)

    with pytest.raises(ValueError):
        assert_pipeline_guards(config)
