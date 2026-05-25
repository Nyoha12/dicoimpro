# RoutingAgent disabled prompt draft access boundary v0.2.3-auto

Status: Codex 034 disabled prompt draft access boundary.

Scope: documentation/tests only. This document defines a docs/tests-only
disabled prompt draft access boundary for reading the disabled RoutingAgent
prompt draft as plain markdown text in tests. It is documentation/test-only,
plain markdown inspection only, non-runtime, non-consuming, non-rendering,
non-execution, non-activation, non-approval and non-LLM.

Codex 034 is not a prompt evaluator runtime. It is not a mock execution
harness. It is not model-output scoring. It is not approved for mock execution,
runtime use, CLI consumption, OpenAI, RUN, final contracts, runtime enums or
journal mutation.

## 1. Purpose

Codex 034 defines a disabled prompt draft access boundary.

Codex 034 does not activate the prompt. Codex 034 does not approve mock
execution. Codex 034 does not approve runtime. Codex 034 does not render,
execute or consume the prompt. Codex 034 only permits test-only markdown
inspection of the disabled prompt draft.

Codex 034 does not claim RoutingAgent works. Codex 034 does not evaluate model
behavior. Codex 034 exists to prevent accidental transition from documentation
to executable prompt usage.

## 2. Source documents and prior layers

The disabled prompt draft access boundary is documented against these inputs:

- `docs/prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md`;
- `docs/ROUTING_AGENT_STATIC_CANDIDATE_OUTPUT_COMPARATOR_v0.2.3-auto.md`;
- `docs/ROUTING_AGENT_STATIC_EXPECTED_OUTPUT_EVALUATOR_v0.2.3-auto.md`;
- `docs/ROUTING_AGENT_STATIC_FIXTURE_CHECKER_v0.2.3-auto.md`;
- `docs/ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES_v0.2.3-auto.md`;
- `docs/ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md`;
- `docs/ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md`;
- `docs/ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md`;
- `docs/AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md`;
- `docs/PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md`;
- `docs/PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md`;
- `docs/REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md`;
- `tests/fixtures/routing_agent_prompt_review_cases.json`;
- `tests/fixtures/routing_agent_expected_outputs.json`;
- `tests/fixtures/routing_agent_candidate_outputs.json`;
- `tests/helpers/routing_agent_static_fixture_checker.py`;
- `tests/helpers/routing_agent_static_expected_output_evaluator.py`;
- `tests/helpers/routing_agent_static_candidate_output_comparator.py`.

Codex 028 created a disabled documentation-only prompt draft. Codex 029 added
a review gate. Codex 030 added synthetic review fixtures. Codex 031 added
static fixture checking. Codex 032 added expected outputs. Codex 033 added
candidate outputs and comparator diagnostics. Codex 034 now defines the safe
test-only access boundary for the disabled draft itself. Codex 034 does not
consume the prompt.

## 3. Access boundary definition

Reading the markdown file as documentation is allowed in tests; consuming the
markdown as an executable prompt is forbidden.

Allowed access:

- read the draft markdown file in tests;
- inspect textual markers;
- verify lifecycle/status vocabulary;
- verify explicit denial flags or phrases;
- verify required sections exist;
- verify no forbidden runtime references are introduced;
- verify no production code references the draft.

Forbidden access:

- rendering the prompt;
- building prompt messages;
- creating chat/completion payloads;
- using the text as task instructions for an agent;
- passing it to an adapter;
- passing it to a fake generator;
- passing it to CLI;
- passing it to OpenAI;
- using it to generate candidate outputs;
- scoring model output against it;
- converting it into a runtime PromptPackage;
- treating it as approved for mock or runtime use.

## 4. Boundary checker responsibilities

Implement
`tests/helpers/routing_agent_disabled_prompt_draft_boundary_checker.py` as
test-only utility code.

It may:

- read the disabled prompt draft markdown as text;
- validate required status markers;
- validate required denial markers;
- validate required non-runtime/non-consuming/non-activation language;
- validate that the draft does not declare itself approved;
- validate that no source file under `src/` references the prompt draft path,
  prompt review cases, expected outputs, candidate outputs, fixture checkers
  or draft access checker;
- validate that no `src/` file contains runtime prompt-loading names such as
  `render_prompt`, `load_prompt`, `execute_prompt`, `consume_prompt`,
  `prompt_loader`, `prompt_registry` or `ROUTING_AGENT_PROMPT_DRAFT`;
- validate that tests/helper code imports only the Python standard library;
- return human-readable errors.

Suggested functions:

- `read_text(path: Path) -> str`;
- `validate_draft_access_metadata(text: str) -> list[str]`;
- `validate_disabled_status_markers(text: str) -> list[str]`;
- `validate_denial_markers(text: str) -> list[str]`;
- `validate_no_approval_markers(text: str) -> list[str]`;
- `validate_no_src_prompt_references(repo_root: Path) -> list[str]`;
- `validate_helper_import_boundaries(helper_path: Path) -> list[str]`;
- `validate_disabled_prompt_draft_access_boundary(repo_root: Path) -> list[str]`.

Use only Python standard library. Do not use pydantic. Do not import from
`src/dico_impro`. Do not create production contracts. Do not create a reusable
runtime prompt loader.

## 5. Required marker checks

The checker requires the disabled prompt draft or its surrounding docs to
include markers equivalent to:

- `draft_documented`;
- disabled;
- documentation-only;
- non-runtime;
- non-consumed;
- non-activation;
- non-approval;
- not approved for mock execution;
- not approved for runtime;
- not approved for OpenAI;
- not approved for RUN;
- not final contracts;
- not runtime enums.

The checker fails if the draft text suggests positive approval language such
as:

- active prompt;
- approved prompt;
- approved for mock execution;
- approved for runtime;
- approved for CLI consumption;
- approved for OpenAI;
- approved for RUN;
- production prompt;
- runtime prompt.

Negative phrases are good markers. The checker must not fail merely because
the document contains negative phrases such as `not approved for runtime`.
It fails only on positive approval language.

## 6. Static test requirements

The tests verify:

- the new doc exists;
- it states disabled prompt draft access boundary;
- it states docs/tests only;
- it states plain markdown inspection only;
- it states non-runtime, non-consuming, non-rendering, non-execution,
  non-activation, non-approval and non-LLM;
- it states the key distinction: reading as documentation is allowed;
  consuming as executable prompt is forbidden;
- it references all prior source documents and fixtures;
- it explains the Codex 028 to Codex 034 sequence;
- the boundary checker exists;
- the boundary checker uses only standard-library imports;
- the boundary checker imports no `src/dico_impro` modules;
- the boundary checker imports no OpenAI/network packages;
- the disabled prompt draft exists;
- the disabled prompt draft contains required disabled/status markers;
- the disabled prompt draft contains required denial markers;
- the disabled prompt draft does not contain positive approval markers;
- no `src/` file references the disabled prompt draft path;
- no `src/` file references `routing_agent_prompt_review_cases.json`;
- no `src/` file references `routing_agent_expected_outputs.json`;
- no `src/` file references `routing_agent_candidate_outputs.json`;
- no `src/` file references the static checker/evaluator/comparator helpers;
- no `src/` file contains runtime prompt-loading names such as
  `render_prompt`, `load_prompt`, `execute_prompt`, `consume_prompt`,
  `prompt_loader`, `prompt_registry` or `ROUTING_AGENT_PROMPT_DRAFT`;
- `validate_disabled_prompt_draft_access_boundary` returns no errors for the
  current repository;
- negative tests fail on missing disabled marker, missing non-runtime marker,
  positive approved-for-runtime language, positive approved-for-mock language,
  positive approved-for-OpenAI language, `src/` reference to the prompt draft,
  `src/` reference to candidate outputs, runtime prompt-loading function names
  in `src/`, helper import from `src/dico_impro`, and helper import from
  `openai` or `requests`;
- docs sync expects Codex 001 through Codex 034;
- README and post-015 review list Codex 034 as docs/tests-only disabled prompt
  draft access boundary.

## 7. Verdict

```text
Disabled prompt draft access boundary created: YES.
Plain markdown inspection in tests allowed: YES.
Prompt consumed as executable prompt: NO.
Prompt rendered: NO.
Prompt executed: NO.
Model output scored: NO.
Approved for mock execution: NO.
Approved for runtime: NO.
Approved for CLI consumption: NO.
Approved for OpenAI: NO.
Approved for RUN: NO.
Approved for final contracts/enums: NO.
Approved for journal mutation: NO.
```

A future Codex may define a stronger prompt-use harness only after this
boundary remains green, but Codex 034 itself grants no activation, prompt
execution, runtime, OpenAI, RUN or journal permission.
