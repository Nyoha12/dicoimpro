import builtins
from pathlib import Path

from dico_impro.agents import FakeAgentAdapter
from dico_impro.contracts import BatchReport, BatchState, BatchStatus
from dico_impro.orchestration import DryRunResult, ExplicitScope, run_dry_run


def make_scope() -> ExplicitScope:
    return ExplicitScope.model_validate(
        {
            "batch_id": "BATCH_001",
            "entries": [
                {"id_entree_original": "026", "titre_original_exact": "First"},
                {"id_entree_original": "031", "titre_original_exact": "Second"},
            ],
        }
    )


def test_dry_run_returns_batch_state_and_report():
    result = run_dry_run(make_scope(), created_at="2026-05-21T00:00:00Z")

    assert isinstance(result, DryRunResult)
    assert isinstance(result.batch_state, BatchState)
    assert isinstance(result.batch_report, BatchReport)
    assert result.batch_state.status == BatchStatus.COMPLETED_CLEAN
    assert result.batch_report.entries_total == 2


def test_dry_run_respects_explicit_scope_exactly():
    result = run_dry_run(make_scope(), created_at="2026-05-21T00:00:00Z")

    assert result.batch_state.entries_scope == ["026", "031"]
    assert [task.id_entree_original for task in result.tasks] == ["026", "031"]
    assert result.batch_report.entries_processed == 2
    assert result.batch_report.entries_skipped == 0
    assert result.batch_report.entries_blocked == 0


def test_dry_run_uses_fake_agent_adapter():
    result = run_dry_run(
        make_scope(),
        adapter=FakeAgentAdapter(),
        created_at="2026-05-21T00:00:00Z",
    )

    assert [agent_result.created_by for agent_result in result.agent_results] == [
        "FakeAgentAdapter",
        "FakeAgentAdapter",
    ]
    assert [agent_result.payload["scenario"] for agent_result in result.agent_results] == [
        "success_valid",
        "success_valid",
    ]


def test_dry_run_writes_no_file_output(monkeypatch):
    def fail_open(*args: object, **kwargs: object) -> None:
        raise AssertionError("dry-run orchestration must not open files")

    def fail_write_text(*args: object, **kwargs: object) -> None:
        raise AssertionError("dry-run orchestration must not write files")

    monkeypatch.setattr(builtins, "open", fail_open)
    monkeypatch.setattr(Path, "open", fail_open)
    monkeypatch.setattr(Path, "write_text", fail_write_text)

    result = run_dry_run(make_scope(), created_at="2026-05-21T00:00:00Z")

    assert result.batch_state.artifacts == []
    assert result.batch_report.artifacts == []
    assert result.batch_report.journal_patch_id is None
