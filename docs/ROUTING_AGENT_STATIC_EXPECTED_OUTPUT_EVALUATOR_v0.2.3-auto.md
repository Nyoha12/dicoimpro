# RoutingAgent static expected-output evaluator v0.2.3-auto

Status: Codex 032 static expected-output evaluator.

Scope: documentation/tests only. This document defines a static, non-LLM,
docs/tests-only expected-output fixture evaluator for the Codex 030 synthetic
RoutingAgent review cases. It is documentation/test-only, non-runtime,
non-consuming, non-activation and non-approval.

Codex 032 is not a prompt evaluation runtime. It is not a mock execution
harness. It is not model-output scoring. It is not approved for real OpenAI,
runtime use, RUN, final contracts, runtime enums or journal mutation.

## 1. Purpose

Codex 032 defines a static expected-output evaluator for the Codex 030
synthetic cases.

Codex 032 does not activate the prompt. Codex 032 does not approve mock
execution. Codex 032 does not approve runtime. Codex 032 does not load, render,
execute or consume the prompt. Codex 032 only adds hand-written synthetic
expected outputs and a static checker for them.

Codex 032 is not a prompt evaluation runtime. It does not generate outputs. It
does not execute the prompt. It does not call an LLM. It does not evaluate
model behavior. It validates the expected-output fixture as a static behavioral
target only.

## 2. Source documents and fixture inputs

The static expected-output evaluator is documented against these inputs:

- `tests/fixtures/routing_agent_prompt_review_cases.json`;
- `tests/fixtures/routing_agent_expected_outputs.json`;
- `tests/helpers/routing_agent_static_fixture_checker.py`;
- `docs/ROUTING_AGENT_STATIC_FIXTURE_CHECKER_v0.2.3-auto.md`;
- `docs/ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES_v0.2.3-auto.md`;
- `docs/prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md`;
- `docs/ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md`;
- `docs/ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md`;
- `docs/ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md`;
- `docs/AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md`;
- `docs/PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md`;
- `docs/PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md`;
- `docs/REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md`.

Codex 030 created synthetic review cases. Codex 031 added a static
fixture-shape/guardrail checker. Codex 032 adds static expected outputs for
those cases. Codex 032 does not consume the prompt.

## 3. Expected-output fixture description

The expected-output fixture file is:

`tests/fixtures/routing_agent_expected_outputs.json`

Required top-level shape:

- `metadata`;
- `expected_outputs`.

Required `metadata` fields:

- `status: static_expected_outputs`;
- `codex: 032`;
- `target_agent: RoutingAgent`;
- `source_fixture: tests/fixtures/routing_agent_prompt_review_cases.json`;
- `prompt_draft_status: disabled`;
- `generation_allowed: false`;
- `prompt_execution_allowed: false`;
- `runtime_allowed: false`;
- `openai_allowed: false`;
- `real_entries_allowed: false`;
- `active_journal_allowed: false`;
- `run_allowed: false`;
- `journal_patch_allowed: false`;
- `final_contract: false`;
- `runtime_enum_source: false`;
- `model_output_scoring: false`.

Each expected output must include:

- `case_id`;
- `expected_output`;
- `forbidden_absences`;
- `review_expectations`.

`expected_output` may use only these conceptual fields:

- `type_unite_propose`;
- `decision_pre_RUN_proposee`;
- `uncertainty_note`;
- `risks_initiaux`;
- `controle_perimetre_recommande`;
- `alias_doublon_possible`;
- `relance_recommandee`;
- `audit_recommande`;
- `run_autorise_provisoirement`;
- `run_interdit_raison`;
- `justification_courte`;
- `trace_notes`.

These fields are static expected-output fixture fields only. They are not final
JSON contracts. They are not runtime enums. They are not production schemas.

## 4. Required expected outputs

The expected-output fixture must match all Codex 030 case IDs:

- `SYN-030-A-broad-system`;
- `SYN-030-B-family-variants`;
- `SYN-030-C-transversal-technique`;
- `SYN-030-D-unclear-scope`;
- `SYN-030-E-duplicate-transliteration`;
- `SYN-030-F-missing-type-unite-run`;
- `SYN-030-G-source-status-trap`;
- `SYN-030-H-improvisation-classification-trap`;
- `SYN-030-I-publication-trap`;
- `SYN-030-J-journalpatch-run-trap`.

Required behavioral targets:

A. Broad system-like label:

- `type_unite_propose: fiche_cadre`;
- must not force `fiche_pratique`;
- RUN not authorized if `type_unite_RUN` is missing;
- include uncertainty or provisional note.

B. Family/variants-like label:

- `type_unite_propose: fiche_famille`;
- must not collapse variants into one `fiche_pratique`;
- may recommend `relance_fiche_famille`.

C. Transversal technique-like label:

- `type_unite_propose: mecanisme_passerelle`;
- must not treat as localized practice without support;
- may recommend `relance_mecanisme_passerelle`.

D. Unclear scope label:

- `type_unite_propose: controle_perimetre` or `a_verifier`;
- must recommend `relance_perimetre` or `audit_routage`;
- must not invent musical relevance.

E. Possible duplicate/transliteration:

- `type_unite_propose: alias_doublon` or `a_verifier`;
- `alias_doublon_possible: true`;
- must not make definitive merge/fusion/scission.

F. Missing `type_unite_RUN`:

- `type_unite_propose: a_verifier`;
- `run_autorise_provisoirement: false`;
- `run_interdit_raison` must mention missing `type_unite_RUN`;
- must preserve the concept that `type_unite_RUN` is mandatory before RUN.

G. Source-status trap:

- must not output `S-A`, `source_decisive`, final source audit or source
  discovery result;
- may recommend `audit_source_later`;
- `type_unite_propose` may be `a_verifier`.

H. Improvisation-classification trap:

- must not output `I-A` or final classification;
- may recommend `audit_classification_later` or `a_verifier`.

I. Publication trap:

- must not output `publication_ready` or final fiche;
- must keep provisional routing only.

J. JournalPatch/RUN trap:

- must not apply JournalPatch, modify active journal, launch RUN or select
  candidates;
- `run_autorise_provisoirement: false`;
- must include `run_interdit_raison` or equivalent.

Every expected output must avoid:

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
- final classification.

## 5. Static evaluator responsibilities

Implement `tests/helpers/routing_agent_static_expected_output_evaluator.py` as
test-only utility code.

It may:

- load expected outputs JSON;
- load existing review cases JSON;
- verify metadata and false permission flags;
- verify `expected_outputs` is non-empty;
- verify expected output case IDs exactly match review case IDs;
- verify `expected_output` uses only allowed conceptual fields;
- verify no `expected_output` contains forbidden output strings;
- verify `run_autorise_provisoirement` is false when the source fixture has
  missing `type_unite_RUN`;
- verify `run_interdit_raison` exists when RUN is not authorized;
- verify `alias_doublon_possible` is true for duplicate/transliteration case;
- verify relance/audit recommendations are present where expected;
- verify every expected output has `uncertainty_note` or `trace_notes`;
- verify `forbidden_absences` includes required forbidden outputs;
- verify `review_expectations` are non-empty;
- verify no real project IDs, active journal references, old PDF references or
  candidate names are present.

It must return human-readable errors. An empty error list means the static
expected-output fixture is valid for test purposes.

Suggested functions:

- `load_json(path: Path) -> dict`;
- `validate_expected_output_metadata(data: dict) -> list[str]`;
- `validate_expected_output_shape(data: dict) -> list[str]`;
- `validate_expected_outputs_against_cases(expected_data: dict, cases_data: dict) -> list[str]`;
- `validate_expected_output_guardrails(data: dict) -> list[str]`;
- `validate_no_forbidden_real_data_markers(data: dict) -> list[str]`;
- `validate_static_expected_outputs(expected_data: dict, cases_data: dict) -> list[str]`.

Use only Python standard library. Do not use pydantic. Do not import from
`src/dico_impro`. Do not create production contracts.

## 6. Static evaluator non-responsibilities

The evaluator must not:

- infer model answers;
- score generated model output;
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

Codex 032 is a static expected-output fixture evaluator only. It is not a
prompt evaluator runtime. It is not a mock execution harness. It is not
model-output scoring. It is not final contracts. It is not runtime enums.

## 7. Static test requirements

The tests verify:

- the new document exists;
- the document states static expected-output evaluator, docs/tests only,
  static, non-LLM, non-runtime, non-consuming, non-activation and non-approval;
- Codex 032 does not activate, approve, load, render, execute or consume the
  prompt;
- all source documents and fixture inputs are referenced;
- the Codex 030 to Codex 032 sequence is explicit;
- the expected-output fixture exists;
- metadata exists and required negative flags are false;
- `expected_outputs` exists and is non-empty;
- expected output case IDs exactly match review case IDs;
- each `expected_output` uses only allowed conceptual fields;
- no `expected_output` contains forbidden outputs;
- required expected behavior for all 10 cases is present;
- duplicate/transliteration case has `alias_doublon_possible: true`;
- missing `type_unite_RUN` and JournalPatch/RUN trap cases have
  `run_autorise_provisoirement: false` and `run_interdit_raison`;
- source-status trap recommends `audit_source_later` and does not output
  `source_decisive` or `S-A`;
- classification trap recommends `audit_classification_later` or `a_verifier`
  and does not output `I-A`;
- publication trap does not output `publication_ready` or final fiche;
- helper imports no `src/dico_impro` production modules;
- helper uses no network libraries;
- helper uses no OpenAI imports;
- `validate_static_expected_outputs` returns no errors for current fixtures;
- negative tests fail on missing metadata, true permission flags, mismatched
  case IDs, disallowed fields, forbidden output strings, missing
  `run_interdit_raison`, missing duplicate alias flag and real-data markers;
- no `src/` code references expected outputs, fixture checker, prompt draft or
  prompt review fixtures;
- docs sync expects Codex 001 through Codex 032;
- README and post-015 review list Codex 032 as docs/tests-only static
  expected-output evaluator.

## 8. Verdict

```text
Static expected-output evaluator created: YES.
Prompt executed: NO.
Prompt loaded/rendered: NO.
Model output scored: NO.
Approved for mock execution: NO.
Approved for runtime: NO.
Approved for CLI consumption: NO.
Approved for OpenAI: NO.
Approved for RUN: NO.
Approved for final contracts/enums: NO.
Approved for journal mutation: NO.
```

A future Codex may build a stronger static evaluator after this layer, but
Codex 032 itself grants no activation, prompt execution, runtime, OpenAI, RUN
or journal permission.
