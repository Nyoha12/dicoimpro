# RoutingAgent prompt-readiness checklist v0.2.3-auto

Status: Codex 027 prompt-readiness checklist.

Scope: documentation/tests only. This document is pre-draft, non-runtime,
non-prompt, non-contract, non-final enum and pre-implementation. It verifies
readiness conditions before a future disabled `RoutingAgent` prompt draft. It
does not create a real prompt, does not create a prompt draft, does not create
prompt bodies, does not create `docs/prompts/drafts` content, does not create
`prompts.py`, does not create final JSON contracts, does not create runtime
enums, does not implement agents, does not activate OpenAI, does not perform
network calls and does not change runtime behavior.

No real prompt exists yet. No prompt draft exists yet. No runtime prompt
loading or OpenAI activation exists. This checklist authorizes no RUN, no
candidate selection, no real entry processing, no active journal read/write, no
JournalPatch application, no XLSX/CSV export and no old PDF usage.

## 1. Purpose

This checklist is the last documentary gate before a future disabled
`RoutingAgent` prompt draft. It verifies that the documentary perimeter,
guardrails, source references and negative guarantees are coherent enough for a
later Codex to prepare a disabled draft safely.

Codex 027 does not create the prompt. Codex 027 does not create a prompt draft.
Codex 027 does not start prompt drafting. Codex 027 does not authorize runtime
loading. Codex 027 only checks that the future Codex 028 prompt draft can be
prepared safely if all conditions are satisfied.

## 2. Readiness sources

Readiness is checked against the current documentation chain:

- `PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md` defines the future prompt
  lifecycle, disabled-by-default posture, storage policy and runtime activation
  prohibition. It is the governing prompt activation protocol.
- `RULES_IMPLEMENTATION_AUDIT_v0.2.3-auto.md` audits existing documented rules
  against current implementation coverage and names gaps without creating new
  doctrine.
- `PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md` clarifies pre-prompt
  blockers from the rule audit so prompt work does not collapse ambiguity into
  premature decisions.
- `AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md` maps responsibilities
  between rule levels, agents, SDK architecture and external actions forbidden
  by default.
- `ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md` defines the future
  `RoutingAgent` functional perimeter, conceptual inputs, conceptual outputs,
  forbidden outputs, routing categories, RUN posture, relance/audit posture and
  architecture feedback compatibility.
- `REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md` records the current
  architecture status, authorized fake/mock paths, forbidden paths and remaining
  OpenAI/prompt/source/RUN guardrails.

Codex 023 audited rule coverage. Codex 024 clarified pre-prompt blockers.
Codex 025 mapped agents / architecture / external actions. Codex 026 specified
the RoutingAgent functional perimeter. Codex 027 checks whether a disabled
prompt draft is safe to prepare next.

## 3. Checklist categories

### A. Prompt lifecycle readiness

- [ ] The prompt activation protocol exists:
  `PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md`.
- [ ] Real prompts are not active by default.
- [ ] A future prompt draft must be disabled.
- [ ] A future prompt draft must not be consumed by CLI, `OpenAIAdapter`, mock
  planning or runtime.
- [ ] A future prompt draft must remain documentation-only unless a later
  activation mission approves otherwise.

### B. RoutingAgent scope readiness

- [ ] `RoutingAgent` is conservative routing/aiguillage.
- [ ] `RoutingAgent` is not source auditor, classifier, publisher,
  JournalPatch applier, RUN executor or validation agent.
- [ ] Allowed conceptual inputs are limited to supplied structured input.
- [ ] No browsing, no external source fetching, no `data/local_files`
  inspection and no implicit active journal access are allowed.
- [ ] Allowed conceptual outputs are known.
- [ ] Forbidden outputs are known.

### C. Forbidden-output readiness

A future `RoutingAgent` prompt must not output:

- S-A;
- I-A;
- final D/S/I/C/E;
- final `source_decisive`;
- final source audit;
- `publication_ready`;
- final fiche;
- definitive fusion/scission;
- applied JournalPatch;
- JournalPatch application;
- launched RUN;
- RUN launch;
- active journal modification;
- source publication status;
- candidate selection outside explicit scope;
- old PDF source use.

### D. Routing category readiness

- [ ] A future prompt can safely distinguish `fiche_pratique`.
- [ ] A future prompt can safely distinguish `fiche_cadre`.
- [ ] A future prompt can safely distinguish `fiche_famille`.
- [ ] A future prompt can safely distinguish `mecanisme_passerelle`.
- [ ] A future prompt can safely distinguish `controle_perimetre`.
- [ ] A future prompt can safely distinguish `alias_doublon`.
- [ ] A future prompt can safely distinguish `a_verifier`.
- [ ] Conservative routing is preferred over forced `fiche_pratique`.
- [ ] Possible alias/doublon never means definitive merge.
- [ ] `controle_perimetre` is preferred over premature
  `hors_perimetre` final category.
- [ ] Broad systems should route to `fiche_cadre` rather than
  `fiche_pratique` when appropriate.
- [ ] Related variants should route to `fiche_famille` rather than forced
  single practice when appropriate.
- [ ] Transversal mechanisms should route to `mecanisme_passerelle` rather than
  forced localized practice when appropriate.

### E. RUN posture readiness

- [ ] RUN possible does not mean fiche ready.
- [ ] `type_unite_RUN` is mandatory before RUN.
- [ ] `RoutingAgent` does not launch RUN.
- [ ] `RoutingAgent` does not decide RUN_002.
- [ ] `RoutingAgent` may recommend no RUN or RUN not authorized.
- [ ] A future prompt must preserve `run_interdit_raison` or equivalent concept
  without creating final contracts.

### F. Relance / audit readiness

- [ ] `RoutingAgent` may recommend relance/audit but not perform it.
- [ ] Allowed recommendation concepts are documented:
  `relance_perimetre`, `relance_alias_doublon`, `relance_categorisation`,
  `relance_fiche_cadre_vs_pratique`, `relance_fiche_famille`,
  `relance_mecanisme_passerelle`, `audit_routage`,
  `audit_classification_later`, `audit_source_later`.
- [ ] Recommendation names remain conceptual and non-contractual.

### G. Architecture feedback readiness

- [ ] Future architecture can reject invalid fields.
- [ ] Future architecture can reject forbidden outputs.
- [ ] Future architecture can reject unsupported categories.
- [ ] Future architecture can reject overstrong claims.
- [ ] Future architecture can reject `publication_ready`.
- [ ] Future architecture can reject S-A/I-A.
- [ ] Future architecture can reject RUN authorization without
  `type_unite_RUN`.
- [ ] Future architecture can reject final classification.
- [ ] Feedback must identify failed rule and allowed repair path.
- [ ] Feedback must not tell the prompt/agent to force evidence or "make the
  test pass".

### H. Example readiness

- [ ] Positive synthetic examples exist in
  `ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md`.
- [ ] Negative synthetic examples exist in
  `ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md`.
- [ ] Examples are synthetic and non-project-specific.
- [ ] Examples do not process real entries, active journal, old PDF or
  candidates.

### I. Remaining non-readiness / future work

After Codex 027, the following items are still NOT ready:

- no runtime prompt loading;
- no active prompt;
- no prompt contract;
- no final JSON schema;
- no runtime enum;
- no real RoutingAgent execution;
- no source search;
- no SourceAuditAgent prompt;
- no ClassificationAgent prompt;
- no publication flow;
- no JournalPatch application;
- no real OpenAI.

## 4. Readiness verdict

```text
Ready for future disabled RoutingAgent prompt draft: YES, if this checklist passes.
Ready for runtime prompt activation: NO.
Ready for real OpenAI: NO.
Ready for real RUN: NO.
Ready for source audit/classification prompts: NO.
Ready for final JSON contracts/enums: NO.
Ready for active journal mutation: NO.
```

A future Codex 028 may create a disabled prompt draft only if it remains
documentation-only, disabled, non-runtime, non-consumed and aligned with this
checklist.

## 5. Current negative guarantees

Codex 027 remains docs/tests only:

```text
- no production code changes;
- no behavior change;
- no runtime prompt loading;
- no prompt body;
- no prompt draft;
- no docs/prompts/drafts content;
- no prompts.py;
- no final JSON contracts or enum creation;
- no real agents;
- no real OpenAI/API/network;
- no RUN;
- no candidate selection;
- no real entry processing;
- no active journal read/write;
- no JournalPatch application;
- no XLSX/CSV export;
- no old PDF usage.
```
