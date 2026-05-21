from __future__ import annotations

from dico_impro.agents import AgentRegistry
from dico_impro.agents.adapters import FakeScenario
from dico_impro.contracts import AgentContract, AgentTask
from dico_impro.contracts.common import SCHEMA_VERSION
from dico_impro.orchestration.scope import ExplicitScope


DEFAULT_DRY_RUN_AGENT_NAME = "DryRunAgent"
DEFAULT_DRY_RUN_OUTPUT_SCHEMA = "RoutingDecision"

DRY_RUN_FORBIDDEN_ACTIONS = [
    "launch_RUN",
    "identify_candidates",
    "read_real_project_data",
    "read_data_local_files",
    "read_active_journal",
    "use_old_pdf",
    "write_outputs",
    "openai_call",
    "network_call",
]

DRY_RUN_FORBIDDEN_FILES = [
    "data/local_files",
    "data/active_journal",
    "data/outputs",
    "legacy_pdf",
    "old_pdf",
]


def build_dry_run_agent_contract(
    *,
    agent_name: str = DEFAULT_DRY_RUN_AGENT_NAME,
    output_schema: str = DEFAULT_DRY_RUN_OUTPUT_SCHEMA,
) -> AgentContract:
    return AgentContract.model_validate(
        {
            "object_type": "AgentContract",
            "schema_version": SCHEMA_VERSION,
            "created_by": "dico_impro.orchestration",
            "agent_name": agent_name,
            "agent_version": SCHEMA_VERSION,
            "mission": "Run deterministic in-memory tasks for an explicit dry-run scope.",
            "allowed_inputs": ["ExplicitScopeEntry"],
            "required_output_schema": output_schema,
            "forbidden_actions": DRY_RUN_FORBIDDEN_ACTIONS,
            "quality_gates": ["schema_validation", "quality_gate_evaluation"],
            "handoff_targets": [],
        }
    )


def build_agent_tasks(
    scope: ExplicitScope,
    registry: AgentRegistry,
    *,
    agent_name: str = DEFAULT_DRY_RUN_AGENT_NAME,
) -> tuple[AgentTask, ...]:
    registered = registry.get(agent_name)
    tasks: list[AgentTask] = []

    for index, entry in enumerate(scope.entries, start=1):
        input_payload: dict[str, object] = {
            "explicit_scope_index": index,
            "scope_entry": entry.model_dump(exclude_none=True),
            "fake_scenario": entry.fake_scenario or FakeScenario.SUCCESS_VALID.value,
        }
        task = AgentTask.model_validate(
            {
                "object_type": "AgentTask",
                "schema_version": SCHEMA_VERSION,
                "created_by": "dico_impro.orchestration.task_builder",
                "task_id": f"TASK_{scope.batch_id}_{index:03d}_DRY_RUN",
                "batch_id": scope.batch_id,
                "id_entree_original": entry.id_entree_original,
                "titre_original_exact": entry.titre_original_exact,
                "task_type": "dry_run_explicit_scope",
                "agent_name": registered.contract.agent_name,
                "input_payload": input_payload,
                "allowed_files": [],
                "forbidden_files": DRY_RUN_FORBIDDEN_FILES,
                "expected_schema": registered.resolved_expected_schema,
            }
        )
        registry.validate_task(task)
        tasks.append(task)

    return tuple(tasks)


__all__ = [
    "DEFAULT_DRY_RUN_AGENT_NAME",
    "DEFAULT_DRY_RUN_OUTPUT_SCHEMA",
    "DRY_RUN_FORBIDDEN_ACTIONS",
    "DRY_RUN_FORBIDDEN_FILES",
    "build_agent_tasks",
    "build_dry_run_agent_contract",
]
