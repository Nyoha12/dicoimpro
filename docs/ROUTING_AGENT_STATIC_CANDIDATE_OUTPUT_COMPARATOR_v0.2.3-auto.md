# RoutingAgent static candidate-output comparator v0.2.3-auto

Status: Codex 033 static candidate-output comparator.

Scope: documentation/tests only. This document defines a static, non-LLM,
docs/tests-only candidate-output comparison layer for the Codex 030 synthetic
RoutingAgent review cases. It is documentation/test-only, non-runtime,
non-consuming, non-activation and non-approval.

Codex 033 is not a RoutingAgent execution harness. It is not a mock LLM
harness. It is not prompt execution. It is not model-output scoring. It is not
approved for real OpenAI, runtime use, RUN, final contracts, runtime enums or
journal mutation.

## 1. Purpose

Codex 033 defines a static candidate-output comparator for RoutingAgent
synthetic cases.

Codex 033 does not activate the prompt. Codex 033 does not approve mock
execution. Codex 033 does not approve runtime. Codex 033 does not load, render,
execute or consume the prompt. Codex 033 only adds hand-written synthetic
candidate outputs, a deterministic fake provider, and a static comparator.

Codex 033 is not a prompt evaluation runtime. Codex 033 does not claim
RoutingAgent works. Codex 033 only checks whether comparison diagnostics detect
PASS/FAIL synthetic candidates.

The deterministic fake candidate provider is test-only. The fake provider must
not be presented as RoutingAgent behavior. It only returns hand-written
synthetic candidate outputs from a fixture. It does not generate candidate
outputs from the prompt, does not infer model answers and does not call an LLM.

## 2. Source documents and fixture inputs

The static candidate-output comparator is documented against these inputs:

- `tests/fixtures/routing_agent_prompt_review_cases.json`;
- `tests/fixtures/routing_agent_expected_outputs.json`;
- `tests/fixtures/routing_agent_candidate_outputs.json`;
- `tests/helpers/routing_agent_static_fixture_checker.py`;
- `tests/helpers/routing_agent_static_expected_output_evaluator.py`;
- `docs/ROUTING_AGENT_STATIC_EXPECTED_OUTPUT_EVALUATOR_v0.2.3-auto.md`;
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

Codex 030 created synthetic review cases. Codex 031 added a
fixture-shape/guardrail checker. Codex 032 added static expected outputs.
Codex 033 adds static synthetic candidate outputs and comparison diagnostics.
Codex 033 does not consume the prompt.

This layer compares hand-written synthetic candidate outputs with hand-written
synthetic expected outputs. It does not create model outputs. It does not
execute the prompt. It does not call an LLM. It does not evaluate model
behavior. It validates the comparison mechanism only.

## 3. Candidate-output fixture description

The candidate-output fixture file is:

`tests/fixtures/routing_agent_candidate_outputs.json`

Required top-level shape:

- `metadata`;
- `candidates`.

Required `metadata` fields:

- `status: static_candidate_outputs`;
- `codex: 033`;
- `target_agent: RoutingAgent`;
- `source_fixture: tests/fixtures/routing_agent_prompt_review_cases.json`;
- `expected_outputs_fixture: tests/fixtures/routing_agent_expected_outputs.json`;
- `prompt_draft_status: disabled`;
- `candidate_generation_from_prompt: false`;
- `deterministic_fake_provider_only: true`;
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

Each candidate must include:

- `candidate_id`;
- `case_id`;
- `scenario`;
- `expected_result`;
- `candidate_output`;
- `expected_diagnostics`;
- `review_notes`.

`candidate_output` may use only these conceptual fields:

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

These are static candidate-output fixture fields only. They are not final JSON
contracts. They are not runtime enums. They are not production schemas.

## 4. Required candidate scenarios

The fixture must include at least one PASS and one FAIL candidate for these
groups:

A. Broad system-like label:

- PASS: candidate routes `fiche_cadre`, keeps uncertainty and blocks RUN.
- FAIL: candidate forces `fiche_pratique` or authorizes RUN.

B. Family/variants-like label:

- PASS: candidate routes `fiche_famille` and preserves variants.
- FAIL: candidate collapses variants into `fiche_pratique`.

C. Transversal technique-like label:

- PASS: candidate routes `mecanisme_passerelle`.
- FAIL: candidate treats the label as localized `fiche_pratique` without
  support.

D. Unclear scope label:

- PASS: candidate routes `controle_perimetre` or `a_verifier` and recommends
  `relance_perimetre` or `audit_routage`.
- FAIL: candidate invents musical relevance or authorizes RUN.

E. Possible duplicate/transliteration:

- PASS: candidate sets `alias_doublon_possible: true` and avoids definitive
  merge.
- FAIL: candidate makes definitive fusion/scission or applies JournalPatch.

F. Missing `type_unite_RUN`:

- PASS: candidate blocks RUN and includes `run_interdit_raison` mentioning
  missing `type_unite_RUN`.
- FAIL: candidate authorizes RUN.

G. Source-status trap:

- PASS: candidate recommends `audit_source_later` and avoids
  `source_decisive`/`S-A`.
- FAIL: candidate outputs `S-A`, `source_decisive`, final source audit or a
  source discovery result.

H. Improvisation-classification trap:

- PASS: candidate recommends `audit_classification_later` or `a_verifier` and
  avoids `I-A`.
- FAIL: candidate outputs `I-A` or final classification.

I. Publication trap:

- PASS: candidate remains provisional and avoids `publication_ready`/final
  fiche.
- FAIL: candidate outputs `publication_ready` or final fiche.

J. JournalPatch/RUN trap:

- PASS: candidate blocks RUN and journal mutation.
- FAIL: candidate launches RUN, applies JournalPatch, modifies active journal
  or selects candidates.

`expected_result` must be either `pass` or `fail`.

For PASS candidates, `expected_diagnostics` may be empty or contain
informational diagnostics only. For FAIL candidates, `expected_diagnostics`
must contain at least one expected diagnostic keyword.

## 5. Comparator responsibilities

Implement `tests/helpers/routing_agent_static_candidate_output_comparator.py`
as test-only utility code.

It may:

- load candidate outputs JSON;
- load expected outputs JSON;
- load review cases JSON;
- verify metadata and false permission flags;
- verify `candidates` is non-empty;
- verify every candidate `case_id` exists in expected outputs and review
  cases;
- verify `candidate_output` uses only allowed conceptual fields;
- compare `candidate_output` to `expected_output` using static rules;
- emit human-readable diagnostics;
- verify PASS candidates produce no error diagnostics;
- verify FAIL candidates produce expected diagnostic keywords;
- verify no candidate_output contains forbidden output strings without
  deterministic diagnostics;
- verify no PASS `candidate_output` contains forbidden output strings;
- verify RUN remains blocked when `type_unite_RUN` is missing;
- verify `run_interdit_raison` exists when `run_autorise_provisoirement` is
  false;
- verify duplicate/transliteration PASS has `alias_doublon_possible: true`;
- verify source trap candidates do not output `S-A`/`source_decisive` when
  expected to pass;
- verify classification trap candidates do not output `I-A`/final
  classification when expected to pass;
- verify publication trap candidates do not output `publication_ready`/final
  fiche when expected to pass;
- verify no real project IDs, active journal references, old PDF references or
  real candidate names are present.

It must return human-readable diagnostics/errors. An empty error list means the
static candidate fixture and comparator expectations are valid for test
purposes.

Suggested functions:

- `load_json(path: Path) -> dict`;
- `validate_candidate_metadata(data: dict) -> list[str]`;
- `validate_candidate_shape(data: dict) -> list[str]`;
- `compare_candidate_to_expected(candidate: dict, expected: dict, source_case: dict) -> list[str]`;
- `validate_candidate_scenarios(candidate_data: dict, expected_data: dict, cases_data: dict) -> list[str]`;
- `validate_no_forbidden_real_data_markers(data: dict) -> list[str]`;
- `validate_static_candidates(candidate_data: dict, expected_data: dict, cases_data: dict) -> list[str]`.

Use only Python standard library. Do not use pydantic. Do not import from
`src/dico_impro`. Do not create production contracts.

## 6. Comparator non-responsibilities

The comparator must not:

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
- select real candidates;
- decide final classification;
- decide S-A or I-A;
- create final contract/schema/enums;
- mutate any project data.

Codex 033 is a static candidate-output comparator only. It is not a prompt
evaluator runtime. It is not a mock execution harness. It is not model-output
scoring. It is not final contracts. It is not runtime enums.

## 7. Diagnostics rules

The comparator should produce deterministic diagnostics such as:

- `disallowed_route`;
- `missing_uncertainty`;
- `run_authorized_without_type_unite_RUN`;
- `missing_run_interdit_raison`;
- `forbidden_output_present`;
- `alias_flag_missing`;
- `definitive_merge_or_scission`;
- `source_status_forbidden`;
- `classification_forbidden`;
- `publication_forbidden`;
- `journal_action_forbidden`;
- `candidate_selection_forbidden`;
- `missing_required_recommendation`;
- `disallowed_expected_output_field`;
- `real_data_marker_present`.

Diagnostics are test-only strings, not runtime enums and not final contracts.

## 8. Static test requirements

The tests verify:

- the new doc exists;
- it states static candidate-output comparator, docs/tests only, static,
  non-LLM, deterministic fake candidate provider, non-runtime, non-consuming,
  non-activation, non-approval;
- it states Codex 033 does not activate, approve, load, render, execute or
  consume the prompt;
- it states the fake provider must not be presented as RoutingAgent behavior;
- it references all source documents and fixture inputs;
- it explains the Codex 030 to Codex 033 sequence;
- candidate-output fixture exists;
- metadata exists and required flags/negative permissions are correct;
- `candidates` exists and is non-empty;
- each candidate uses only allowed conceptual fields;
- every candidate `case_id` exists in expected outputs and review cases;
- all required PASS/FAIL groups A-J exist;
- PASS candidates validate without error diagnostics;
- FAIL candidates produce expected diagnostic keywords;
- forbidden output strings are detected;
- RUN authorization without `type_unite_RUN` is detected;
- missing `run_interdit_raison` is detected;
- missing alias flag is detected for duplicate/transliteration pass case;
- `source_decisive`/`S-A` trap is detected;
- `I-A`/final classification trap is detected;
- `publication_ready`/final fiche trap is detected;
- JournalPatch/RUN/action trap is detected;
- helper imports no `src/dico_impro` production modules;
- helper uses no network libraries;
- helper uses no OpenAI imports;
- `validate_static_candidates` returns no errors for current fixtures;
- negative tests fail on missing metadata, true permission flags, unknown
  `case_id`, disallowed `candidate_output` field, forbidden output string,
  missing expected PASS/FAIL group, pass candidate producing diagnostics, fail
  candidate missing expected diagnostics and real-data marker;
- no `src/` code references candidate outputs, expected outputs, fixture
  checker, prompt draft or prompt review fixtures;
- docs sync expects Codex 001 through Codex 033;
- README and post-015 review list Codex 033 as docs/tests-only static
  candidate-output comparator.

## 9. Verdict

```text
Static candidate-output comparator created: YES.
Synthetic fake provider created: YES, test-only and deterministic.
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

A future Codex may build a stronger static evaluator after this comparator,
but Codex 033 itself grants no activation, prompt execution, runtime, OpenAI,
RUN or journal permission.
