# RoutingAgent static fixture checker v0.2.3-auto

Status: Codex 031 static non-LLM fixture checker.

Scope: documentation/tests only. This document defines a test-only static
non-LLM checker layer for the synthetic review fixtures of the disabled
RoutingAgent prompt draft. It is documentation/test-only, test-only,
non-runtime, non-consuming, non-activation and non-approval.

Codex 031 is not a prompt evaluation runtime. It is not a mock execution
harness. It is not approved for real OpenAI, runtime use, RUN, final contracts,
runtime enums or journal mutation.

## 1. Purpose

Codex 031 defines a static non-LLM checker layer for the synthetic review
fixtures created in Codex 030.

Codex 031 does not activate the prompt. Codex 031 does not approve mock
execution. Codex 031 does not approve runtime. Codex 031 does not load, render,
execute or consume the prompt. Codex 031 only adds test-only static checks over
synthetic fixture JSON and related documentation.

Codex 031 is not a prompt evaluation runtime. It does not infer expected model
answers, score generated output, call an LLM, call OpenAI or approve any
prompt-consuming path.

## 2. Source documents and fixture inputs

The static checker is documented against these fixture and documentation
inputs:

- `tests/fixtures/routing_agent_prompt_review_cases.json`;
- `docs/ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES_v0.2.3-auto.md`;
- `docs/prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md`;
- `docs/ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md`;
- `ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md`;
- `ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md`;
- `AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md`;
- `PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md`;
- `PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md`;
- `REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md`.

Codex 028 created the disabled prompt draft. Codex 029 added the
disabled-draft review gate. Codex 030 created synthetic static review fixtures.
Codex 031 adds a static checker for those fixtures only. Codex 031 does not
consume the prompt.

## 3. Checker location and scope

Helper path:

`tests/helpers/routing_agent_static_fixture_checker.py`

Tests path:

`tests/test_routing_agent_static_fixture_checker.py`

The helper is test-only. It must not be imported from `src/`. It must not
create runtime APIs. It must not define final JSON contracts. It must not
define runtime enums. It must not be used by CLI, `OpenAIAdapter`, mock
planning, runtime or production code.

The helper may read fixture JSON and documentation text from tests. It must not
execute, render, load or consume the prompt. It must not call an LLM or OpenAI.
It must not import or modify production code.

## 4. Static checker responsibilities

The checker validates the fixture JSON mechanically.

It may verify:

- top-level `metadata` exists;
- top-level `cases` exists;
- `metadata` contains required fields;
- negative permission flags are false;
- `codex` is `030`;
- `status` is `synthetic_review_fixtures`;
- `target_agent` is `RoutingAgent`;
- `prompt_draft_status` is `disabled`;
- cases are non-empty;
- each case contains required fields:
  - `case_id`;
  - `label`;
  - `supplied_input`;
  - `expected_safe_route`;
  - `expected_risk_flags`;
  - `expected_recommendations`;
  - `forbidden_outputs`;
  - `review_notes`;
- `case_id` starts with `SYN-030-`;
- `supplied_input.entry_id` starts with `SYN-030-`;
- `supplied_input.entry_label` exists;
- `supplied_input` does not contain real project IDs or real entry-like
  numeric IDs;
- `supplied_input` does not contain active journal data/path references;
- `supplied_input` does not contain old PDF references;
- no case claims `execution_allowed`, `runtime_allowed`, `openai_allowed`,
  `run_allowed` or `journal_patch_allowed`;
- required case families are covered:
  - broad system;
  - family variants;
  - transversal technique;
  - unclear scope;
  - duplicate/transliteration;
  - missing `type_unite_RUN`;
  - source-status trap;
  - improvisation-classification trap;
  - publication trap;
  - JournalPatch/RUN trap;
- required safe routes are covered:
  - `fiche_cadre`;
  - `fiche_famille`;
  - `mecanisme_passerelle`;
  - `controle_perimetre`;
  - `alias_doublon`;
  - `a_verifier`;
- required forbidden outputs are covered:
  - `S-A`;
  - `I-A`;
  - final `source_decisive`;
  - `source_decisive`;
  - final source audit;
  - `publication_ready`;
  - final fiche;
  - definitive fusion/scission;
  - JournalPatch application;
  - active journal modification;
  - RUN launch;
  - launched RUN;
  - candidate selection outside explicit scope;
  - source discovery result;
  - final classification;
- required recommendation concepts are covered:
  - `relance_perimetre`;
  - `relance_alias_doublon`;
  - `relance_fiche_famille`;
  - `relance_mecanisme_passerelle`;
  - `audit_routage`;
  - `audit_source_later`;
  - `audit_classification_later`;
  - `run_interdit_raison`;
  - `type_unite_RUN is mandatory before RUN`.

## 5. Checker non-responsibilities

The checker must not:

- infer expected model answers;
- score generated output;
- execute the prompt;
- render a prompt package;
- load prompt text into runtime;
- call OpenAI or any LLM;
- call network;
- validate real entries;
- read active journal;
- launch RUN;
- apply JournalPatch;
- select candidates;
- decide final classification;
- decide S-A or I-A;
- create final contract/schema/enums;
- mutate any project data.

Codex 031 is a fixture-shape and guardrail checker only. It is not a prompt
evaluator runtime. It is not a mock execution harness. It is not final
contracts. It is not runtime enums.

## 6. Helper implementation guidance

Implement `tests/helpers/routing_agent_static_fixture_checker.py` as test-only
utility code.

It may expose simple functions such as:

- `load_fixture(path: Path) -> dict`;
- `validate_fixture_metadata(data: dict) -> list[str]`;
- `validate_fixture_cases(data: dict) -> list[str]`;
- `validate_fixture_coverage(data: dict) -> list[str]`;
- `validate_no_forbidden_real_data_markers(data: dict) -> list[str]`;
- `validate_static_fixture(data: dict) -> list[str]`.

These functions should return a list of human-readable errors. An empty list
means the static fixture is valid for test purposes.

Do not use pydantic. Do not create production contracts. Do not import from
`src/dico_impro`. Use only Python standard library.

## 7. Static test requirements

The tests verify:

- the checker helper exists under `tests/helpers`;
- the checker helper imports no `src/dico_impro` production modules;
- the checker helper uses no network libraries;
- the checker helper uses no OpenAI imports;
- the checker helper does not read or write the active journal;
- `validate_static_fixture` returns no errors for the existing fixture;
- metadata checks fail on missing metadata;
- metadata checks fail when negative flags are true;
- case checks fail on missing required fields;
- case checks fail on non-synthetic `case_id` or `entry_id`;
- coverage checks fail when a required case family is missing;
- coverage checks fail when required forbidden outputs are missing;
- coverage checks fail when required recommendations are missing;
- the disabled prompt draft still says disabled, non-runtime and non-consumed;
- the review gate still says non-activation and non-approval;
- no `src/` code references the fixture JSON, checker helper or prompt draft;
- no CLI, `OpenAIAdapter` or mock planning code imports or loads the fixture
  JSON, checker helper or prompt draft.

## 8. Verdict

```text
Static fixture checker created: YES.
Prompt executed: NO.
Prompt loaded/rendered: NO.
Approved for mock execution: NO.
Approved for runtime: NO.
Approved for CLI consumption: NO.
Approved for OpenAI: NO.
Approved for RUN: NO.
Approved for final contracts/enums: NO.
Approved for journal mutation: NO.
```

A future Codex may build a stronger static evaluator after this checker, but
Codex 031 itself grants no activation, prompt execution, runtime, OpenAI, RUN
or journal permission.
