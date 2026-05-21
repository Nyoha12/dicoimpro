from dico_impro.agents import AgentRegistry
from dico_impro.contracts import AgentTask
from dico_impro.orchestration import (
    DRY_RUN_FORBIDDEN_FILES,
    ExplicitScope,
    build_agent_tasks,
    build_dry_run_agent_contract,
)


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


def make_registry() -> AgentRegistry:
    registry = AgentRegistry()
    registry.register(build_dry_run_agent_contract(), adapter_type="fake")
    return registry


def test_task_builder_builds_agent_tasks_with_object_type_and_schema_version():
    tasks = build_agent_tasks(make_scope(), make_registry())

    assert all(isinstance(task, AgentTask) for task in tasks)
    assert [task.object_type for task in tasks] == ["AgentTask", "AgentTask"]
    assert [task.schema_version for task in tasks] == ["v0.2.3-auto", "v0.2.3-auto"]
    assert [task.expected_schema for task in tasks] == ["RoutingDecision", "RoutingDecision"]


def test_task_builder_respects_explicit_scope_exactly():
    tasks = build_agent_tasks(make_scope(), make_registry())

    assert [task.id_entree_original for task in tasks] == ["026", "031"]
    assert [task.titre_original_exact for task in tasks] == ["First", "Second"]
    assert [task.input_payload["scope_entry"]["id_entree_original"] for task in tasks] == [
        "026",
        "031",
    ]
    assert all(task.allowed_files == [] for task in tasks)
    assert all(task.forbidden_files == DRY_RUN_FORBIDDEN_FILES for task in tasks)
