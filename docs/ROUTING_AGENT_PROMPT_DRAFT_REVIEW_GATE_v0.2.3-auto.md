# RoutingAgent prompt draft review gate v0.2.3-auto

Status: Codex 029 review gate.

Scope: documentation/tests only. This document is a review gate,
documentation-only, non-runtime, non-consuming, non-activation, non-approval,
pre-mock and pre-runtime. It reviews the disabled Codex 028 RoutingAgent prompt
draft as a document before any later mock or runtime consideration.

This gate does not activate the prompt, approve the prompt for mock, approve
the prompt for runtime, load or render the prompt, consume the prompt from CLI,
OpenAIAdapter, mock planning or runtime, create `prompts.py`, create final JSON
contracts, create runtime enums, implement agents, activate OpenAI, perform
network calls, process real entries, launch RUN, select candidates, read or
write the active journal, apply JournalPatch, export XLSX/CSV or use the old
PDF.

## 1. Purpose

This review gate is a documentary control for the disabled RoutingAgent prompt
draft created in Codex 028. It checks whether the draft remains coherent with
the prior documentation chain and safe as a disabled document.

Codex 029 does not activate the prompt. Codex 029 does not approve the prompt
for mock. Codex 029 does not approve the prompt for runtime. Codex 029 does not
load, render or consume the prompt. Codex 029 only checks that the draft
remains coherent with prior docs and safe as a disabled document.

## 2. Review sources

The review is checked against:

- `docs/prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md`;
- `ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md`;
- `ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md`;
- `AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md`;
- `PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md`;
- `PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md`;
- `REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md`.

Codex 026 specified the RoutingAgent functional perimeter. Codex 027 checked
readiness for a disabled prompt draft. Codex 028 created the disabled prompt
draft. Codex 029 reviews that draft as a disabled document only.

## 3. Review checklist

### A. Lifecycle and activation status

This gate must verify:

- draft status is `draft_documented`;
- `activation_status` is `disabled`;
- draft is documentation-only;
- draft is non-runtime;
- draft is non-consumed;
- draft is not approved for mock;
- draft is not approved for runtime;
- draft is not approved for CLI;
- draft is not approved for real OpenAI;
- draft is not approved for batch processing;
- draft must not be loaded, rendered or consumed.

### B. Scope coherence

This gate must verify:

- RoutingAgent is conservative routing/aiguillage;
- RoutingAgent reads only supplied structured input;
- RoutingAgent proposes conservative pre-RUN routing;
- RoutingAgent surfaces uncertainty;
- RoutingAgent may recommend perimeter control, relance or audit;
- RoutingAgent avoids forced `fiche_pratique`;
- RoutingAgent explains why RUN is not authorized when routing is unstable.

### C. Role-boundary coherence

This gate must verify RoutingAgent is not:

- source auditor;
- classifier;
- publisher;
- validation agent;
- RUN executor;
- JournalPatch applier;
- source search agent.

### D. Input-boundary coherence

This gate must verify the draft forbids:

- browsing;
- external search;
- source discovery;
- `data/local_files` access unless supplied by architecture;
- implicit active journal access;
- old PDF usage;
- inference from unavailable project data;
- archives treated as active sources;
- real project data not supplied.

### E. Output-boundary coherence

This gate must verify the draft output frame remains conceptual and review-only:

- not a final JSON contract;
- not runtime enum creation;
- allowed conceptual output fields remain provisional;
- output should be concise;
- uncertainty must be explicit;
- missing information must not be filled by plausibility.

### F. Forbidden-output coherence

This gate must verify the draft forbids:

- S-A;
- I-A;
- final D/S/I/C/E;
- final `source_decisive`;
- final source_decisive;
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
- old PDF source use;
- source discovery result;
- final classification.

### G. Routing behavior coherence

This gate must verify the draft covers:

- `fiche_pratique`;
- `fiche_cadre`;
- `fiche_famille`;
- `mecanisme_passerelle`;
- `controle_perimetre`;
- `alias_doublon`;
- `a_verifier`.

This gate must also verify:

- conservative routing is preferred over forced `fiche_pratique`;
- `alias_doublon` never means definitive merge;
- broad systems may route to `fiche_cadre`;
- related variants may route to `fiche_famille`;
- transversal mechanisms may route to `mecanisme_passerelle`;
- unstable scope may route to `controle_perimetre` or `a_verifier`.

### H. RUN posture coherence

This gate must verify:

- RUN possible does not mean fiche ready;
- `type_unite_RUN` is mandatory before RUN;
- RoutingAgent does not launch RUN;
- RoutingAgent does not decide RUN_002;
- RoutingAgent may recommend no RUN or RUN not authorized;
- `run_interdit_raison` or equivalent is preserved conceptually.

### I. Relance/audit coherence

This gate must verify:

- relance/audit are recommendations only;
- RoutingAgent does not execute relance, audit, RUN, publication, source search
  or journal mutation;
- recommendation names are conceptual, non-contractual and not active enums;
- recommendation list includes:
  `relance_perimetre`, `relance_alias_doublon`, `relance_categorisation`,
  `relance_fiche_cadre_vs_pratique`, `relance_fiche_famille`,
  `relance_mecanisme_passerelle`, `audit_routage`,
  `audit_classification_later`, `audit_source_later`.

### J. Guardrail wording coherence

This gate must verify the draft contains guardrails:

- Do not invent sources.
- Do not invent facts.
- Do not infer from missing project data.
- Do not convert uncertainty into validation.
- Do not classify strongly.
- Do not publish.
- Do not modify journal.
- Do not launch RUN.
- Do not treat old PDF as a source.
- Do not treat archives as active sources.
- Do not select candidates outside explicit scope.

### K. Synthetic example coherence

This gate must verify:

- examples are synthetic and non-project-specific;
- examples do not use real project entries;
- examples do not use active journal data;
- examples do not use old PDF data;
- examples do not select candidates;
- positive examples cover broad system, group/variants, transversal technique,
  unclear scope and possible duplicate/transliteration;
- negative examples cover I-A, S-A, `publication_ready`, JournalPatch
  application, RUN launch and final fiche.

### L. Review verdict

This gate must verify the verdict remains:

- Coherent as disabled draft: YES, if all review checks pass.
- Approved for mock: NO.
- Approved for runtime: NO.
- Approved for CLI consumption: NO.
- Approved for real OpenAI: NO.
- Approved for RUN: NO.
- Approved for final contracts/enums: NO.
- Approved for journal mutation: NO.

A future Codex may prepare a mock-only review fixture or evaluation harness only
after this gate, but this document itself grants no activation or consumption
permission.

## 4. Review verdict

```text
Coherent as disabled draft: YES, if all review checks pass.
Approved for mock: NO.
Approved for runtime: NO.
Approved for CLI consumption: NO.
Approved for real OpenAI: NO.
Approved for RUN: NO.
Approved for final contracts/enums: NO.
Approved for journal mutation: NO.
```

This verdict is documentary only. The only YES is coherence as a disabled
draft, conditioned on every review check passing. All mock, runtime, CLI,
OpenAI, RUN, final contract/enum and journal mutation approvals remain NO.

## 5. Current negative guarantees

Codex 029 remains docs/tests only:

```text
- no production code changes;
- no behavior change;
- no prompt activation;
- no mock approval;
- no runtime approval;
- no CLI consumption;
- no prompt loading/rendering;
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
