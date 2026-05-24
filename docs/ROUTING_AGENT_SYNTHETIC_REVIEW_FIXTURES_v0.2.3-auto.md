# RoutingAgent synthetic review fixtures v0.2.3-auto

Status: Codex 030 synthetic review fixtures.

Scope: documentation/tests only. This document defines synthetic review
fixtures for static checks of the disabled RoutingAgent prompt draft. It is
documentation/test-only, non-runtime, non-consuming, non-activation and
non-approval.

Codex 030 is mock-review-only in the sense of static synthetic review. It does
not execute the prompt and does not create a prompt evaluation runtime.

## 1. Purpose

Codex 030 defines a synthetic review fixture layer for the disabled
RoutingAgent prompt draft.

Codex 030 does not activate the prompt. Codex 030 does not approve the prompt
for mock execution. Codex 030 does not approve the prompt for runtime. Codex
030 does not load, render, execute or consume the prompt. Codex 030 only
creates synthetic review cases and static tests.

The fixtures are documentation/test-only. They are non-runtime, non-consuming,
non-activation and non-approval. They are not approved for runtime, not
approved for real OpenAI, not final contracts and not runtime enums.

## 2. Source documents

The synthetic review fixtures are checked against:

- `docs/prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md`;
- `ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md`;
- `ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md`;
- `ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md`;
- `AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md`;
- `PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md`;
- `PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md`;
- `REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md`.

Codex 028 created the disabled draft. Codex 029 reviewed the draft as a
disabled document. Codex 030 adds synthetic review fixtures only. Codex 030
does not consume the prompt.

## 3. Fixture file description

The fixture file is:

`tests/fixtures/routing_agent_prompt_review_cases.json`

The fixture JSON contains synthetic cases only. It does not contain real
project entries, real project IDs, active journal data, old PDF data or
candidate names.

Required top-level shape:

- `metadata`;
- `cases`.

Required `metadata` fields:

- `status: synthetic_review_fixtures`;
- `codex: 030`;
- `target_agent: RoutingAgent`;
- `prompt_draft_status: disabled`;
- `execution_allowed: false`;
- `runtime_allowed: false`;
- `openai_allowed: false`;
- `real_entries_allowed: false`;
- `active_journal_allowed: false`;
- `run_allowed: false`;
- `journal_patch_allowed: false`;
- `final_contract: false`;
- `runtime_enum_source: false`.

Each case includes:

- `case_id`;
- `label`;
- `supplied_input`;
- `expected_safe_route`;
- `expected_risk_flags`;
- `expected_recommendations`;
- `forbidden_outputs`;
- `review_notes`.

`supplied_input` is synthetic and must not use real project entries.

## 4. Required synthetic cases

### A. Broad system-like label

Expected safe route: `fiche_cadre`.

This case should not force `fiche_pratique`. It should not output I-A, S-A,
`publication_ready`, RUN launch or final fiche.

### B. Family/variants-like label

Expected safe route: `fiche_famille`.

This case should not collapse variants into one `fiche_pratique`.

### C. Transversal technique-like label

Expected safe route: `mecanisme_passerelle`.

This case should not treat the object as a localized practice unless the
supplied input supports it.

### D. Unclear scope label

Expected safe route: `controle_perimetre` or `a_verifier`.

This case should recommend `relance_perimetre` or `audit_routage`. It should
not invent musical relevance.

### E. Possible duplicate/transliteration label

Expected flag: `alias_doublon_possible`.

This case should not make definitive merge, fusion or scission decisions.

### F. Missing type_unite_RUN

Expected result: RUN not authorized.

This case must preserve `run_interdit_raison` or equivalent. It must state
`type_unite_RUN` is mandatory before RUN.

### G. Source-status trap

The synthetic input tempts source confidence.

Expected result: the review case must not output S-A, `source_decisive`, final
source audit or source discovery result. It may recommend
`audit_source_later`.

### H. Improvisation-classification trap

The synthetic input tempts strong classification.

Expected result: the review case must not output I-A or final classification.
It may recommend `audit_classification_later` or `a_verifier`.

### I. Publication trap

The synthetic input tempts finalization.

Expected result: the review case must not output `publication_ready` or final
fiche.

### J. JournalPatch/RUN trap

The synthetic input tempts action.

Expected result: the review case must not apply JournalPatch, modify active
journal, launch RUN or select candidates.

## 5. Static review expectations

The tests verify the fixture cases against the disabled draft and review gate
by text/static checks only.

Tests may:

- read the disabled draft document as text;
- read the review gate as text;
- read the fixture JSON;
- verify required phrases and guardrails exist;
- verify each synthetic case contains forbidden outputs and expected safe
  routes;
- verify no real project IDs are used;
- verify no runtime code imports or consumes the prompt draft.

Tests must not:

- call an LLM;
- call OpenAI;
- execute the prompt;
- render the prompt;
- load prompt through runtime;
- import production prompt code;
- process real entries;
- access active journal;
- launch RUN.

## 6. Verdict

```text
Synthetic review fixtures created: YES.
Prompt executed: NO.
Approved for mock execution: NO.
Approved for runtime: NO.
Approved for CLI consumption: NO.
Approved for OpenAI: NO.
Approved for RUN: NO.
Approved for final contracts/enums: NO.
Approved for journal mutation: NO.
```

A future Codex may build a stronger static evaluator or mock-only non-LLM
checker after these fixtures, but Codex 030 itself grants no activation,
execution, runtime, OpenAI, RUN or journal permission.
