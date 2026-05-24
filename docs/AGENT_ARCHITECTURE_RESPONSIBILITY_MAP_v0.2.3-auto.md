# Agent architecture responsibility map v0.2.3-auto

Status: Codex 025 responsibility map only.

Scope: documentation/tests only. This document is non-runtime, non-prompt,
non-contract and pre-implementation. It maps responsibility levels before any
prompt drafting. It does not create a real prompt, does not create prompt
drafts, does not create prompt bodies, does not render or load prompts, does
not create final JSON contracts, does not create runtime enums, does not
implement agents, does not activate OpenAI, does not perform network calls and
does not change runtime behavior.

No real prompt exists yet. No runtime prompt loading or OpenAI activation
exists. There is no real agent activation, no real OpenAI/network path, no RUN,
no candidate selection, no active journal read/write, no active journal write,
no JournalPatch application and no official public export authorized by this
document.

## 1. Rule levels

This map separates six rule levels that must not be collapsed into one prompt,
one enum set or one runtime component.

### A. Database finality / quality goals

Database finality rules define the quality target of the project database. They
are higher-level goals, not single-agent output fields.

Examples:

- maintain a cautious and traceable database;
- preserve fragile leads without validating them too early;
- do not transform hypotheses into facts;
- do not force all entries into `fiche_pratique`;
- avoid cultural reduction and overclassification;
- separate existence, source, improvisation, classification and prudence.

These goals guide later routing, source audit, classification, prudence and
validation, but they do not by themselves authorize publication, RUN execution,
JournalPatch application or source modification.

### B. Categorization / quality-labeling rules

Categorization and quality-labeling rules name the working categories, risk
labels and review signals used to discuss a unit before any final decision.

Required vocabulary at this level includes:

- `fiche_pratique`;
- `fiche_cadre`;
- `fiche_famille`;
- `mecanisme_passerelle`;
- `controle_perimetre`;
- `alias_doublon`;
- `sous_piste_candidate`;
- `a_verifier`;
- D/S/I/C/E quality axes.

D/S/I/C/E are quality/risk labels, not final decisions by themselves. A label
can trigger relance, audit, prudence, validation or blocking depending on the
entry context, the source context, the classification context and the current
architecture gate. A strong label never bypasses source evidence, perimeter
control, prudence review or validation.

### C. Agentic process rules

Agentic process rules describe how a difficult case is handled by agentic
method, without converting difficulty into automatic human review.

A difficult case does not mean human review by default. A difficult case may
trigger conditional relance, specialized audit, strengthened agentic
validation, internal contradictory audit or structured blocking.

Recommended methodological vocabulary at this level:

- `validation_agentique_simple`;
- `validation_agentique_renforcee`;
- `audit_contradictoire_interne`;
- `blocage_structure`;
- `autorisation_action_externe`.

These names are recommended methodological vocabulary only. They are not final
runtime enums, not final JSON contract values and not implemented state
transitions.

### D. Per-agent rules

A future agent receives only the rules required for its role. A prompt must not
contain the whole doctrine unless that breadth is explicitly required and
reviewed.

Per-agent outputs are limited by architecture contracts and guardrails. A
RoutingAgent may propose conservative routing; a SourceAuditAgent may assess
source roles; a ClassificationAgent may reason about category and quality axes;
a PrudenceEthicsAgent may identify reduction, overclassification or ethics
risks. None of these agents owns workflow, final publication, active journal
mutation, protocol changes or real OpenAI activation.

### E. SDK architecture rules

SDK architecture executes, validates format, blocks forbidden transitions,
traces, retries with structured feedback and prevents unauthorized external
actions. It owns deterministic workflow mechanics such as orchestration,
contract validation, quality gates, tracing, diffing and export boundaries.

SDK architecture must not perform musicological interpretation in place of
agents. It may identify a failed control and route the work to the same agent,
a specialized agent, validation, audit or structured blocking, but it must not
invent evidence, force conclusions or reinterpret source meaning as if it were
an agentic review.

### F. External actions forbidden by default

External actions are side effects or public/project-level changes. They are
forbidden by default unless a future explicit mission authorizes them with
separate contracts, tests and review.

Forbidden-by-default actions include:

- publishing;
- applying a JournalPatch;
- modifying the active journal;
- reading or modifying active sources;
- deleting an original entry;
- changing protocol;
- activating real OpenAI;
- launching unapproved cost/API;
- launching any real OpenAI/API/network path;
- official public export.

## 2. Agents vs architecture vs external actions

The split below separates agentic reasoning responsibility, SDK/architecture
responsibility and external actions that remain disabled by default.

| Area | Agentic reasoning responsibility | SDK/architecture responsibility | External action or forbidden-by-default responsibility |
|---|---|---|---|
| Batch | `BatchReviewAgent` may optionally provide qualitative review of a batch plan after deterministic scope exists. It does not orchestrate runtime. | `BatchOrchestrator` owns batching mechanics, explicit scope, task ordering, retries and stopping conditions. `TraceLogger` records audit traces. | Real OpenAI/API activation, candidate selection and RUN remain disabled by default. |
| Routing | `RoutingAgent` proposes conservative aiguillage, risks, uncertainties, relance/audit recommendations and why RUN is not authorized. | `ContractValidator` validates format. `QualityGate` blocks forbidden transitions and out-of-scope routing claims. `TraceLogger` records decisions. | RUN launch, candidate selection, definitive fusion/scission and publication status remain forbidden. |
| Source search | `SearchPlannerAgent` or agentic planning may propose what kind of source search would be needed. It does not execute network access by itself. | `SearchToolRunner` is architecture/tooling and may execute only explicitly approved search actions in a future authorized path. `TraceLogger` records tool use. | Real network/API search, active source modification and unapproved cost/API are disabled by default. |
| Source audit | `SourceAuditAgent` evaluates source role, source limits, platform/original-source confusion and whether evidence supports strong source claims. | `ContractValidator` and `QualityGate` reject invalid source-audit payloads, forbidden fields and unsupported strong claims. | Modifying active sources, treating a platform as an original source and public source publication are forbidden by default. |
| Classification | `ClassificationAgent` reasons about `fiche_pratique`, `fiche_cadre`, `fiche_famille`, `mecanisme_passerelle`, `alias_doublon`, `controle_perimetre` and D/S/I/C/E labels. | `ContractValidator` validates shape. `QualityGate` blocks S-A, I-A, C-A or publication-like claims when required evidence is missing. | Final fiche creation, publication readiness and RUN execution are forbidden by default. |
| Prudence / ethics | `PrudenceEthicsAgent` identifies cultural reduction, overclassification, fragile hypotheses, prudence needs and ethics risks. | `QualityGate` can block publication-like transitions. `TraceLogger` preserves warnings and audit notes. | Publishing, official public export and deleting fragile original entries are forbidden by default. |
| Contradiction | `ContradictionAgent` performs internal contradictory audit and names unresolved conflicts or missing evidence. | `QualityGate` converts unresolved contradictions into audit, repair or structured blocking routes. `TraceLogger` preserves contradiction records. | Protocol change, forced validation and publication despite unresolved contradiction are forbidden by default. |
| Validation | `ValidationReviewAgent` performs qualitative validation review and may recommend simple validation, strengthened validation, audit or blocking. | `ContractValidator` performs deterministic format validation. `QualityGate` enforces gates and allowed transitions. | Final publication decision, active journal application and real agent activation remain forbidden by default. |
| DELTA | `DeltaInterpretationAgent` interprets meaningful changes between passes when deterministic deltas exist. | `DiffEngine` computes deterministic structural differences. `TraceLogger` records delta evidence. | Active journal modification, JournalPatch application and publication of a delta are forbidden by default. |
| Journal patch | `JournalPatchAgent` proposes a separate JournalPatch object only. It does not apply it. | `JournalPatchValidator` validates proposed patch structure and forbidden transitions. `ContractValidator` enforces shape. | `JournalPatchApplier`, active journal application and active journal write are disabled by default. |
| Archiving / exports | `ArchiveReviewAgent` may optionally provide qualitative review. `ArchivageAgent` is not a primary agent by default. | `TraceLogger` and `Exporter` are architecture. They own traces and technical exports under approved paths. | Official public export, XLSX/CSV export creation and publication officielle are disabled by default. |

Important distinctions:

- `BatchSupervisor` must be split into `BatchOrchestrator` architecture and
  optional `BatchReviewAgent` qualitative review.
- `SourceSearchAgent` must be split into `SearchPlannerAgent` or agentic
  planning and `SearchToolRunner` architecture/tooling.
- `ValidationAgent` must be split into `ContractValidator`/`QualityGate`
  architecture and `ValidationReviewAgent` reasoning.
- `DeltaAgent` must be split into `DiffEngine` architecture and
  `DeltaInterpretationAgent` reasoning.
- `JournalPatchAgent` proposes only; `JournalPatchApplier` is an external
  action disabled by default.
- `ArchivageAgent` is not a primary agent by default; `TraceLogger` and
  `Exporter` are architecture, while `ArchiveReviewAgent` may be optional for
  qualitative review.

Agentic reasoning roles named by this map:

```text
RoutingAgent
SourceAuditAgent
ClassificationAgent
PrudenceEthicsAgent
ContradictionAgent
ValidationReviewAgent
DeltaInterpretationAgent
JournalPatchAgent
BatchReviewAgent
SearchPlannerAgent
ArchiveReviewAgent
```

SDK architecture components named by this map:

```text
BatchOrchestrator
SearchToolRunner
ContractValidator
QualityGate
DiffEngine
TraceLogger
Exporter
JournalPatchValidator
```

External actions disabled by default:

```text
JournalPatchApplier
publication officielle
modification source active
active journal application
real OpenAI/API activation
protocol change
official public export
```

## 3. RoutingAgent responsibilities

`RoutingAgent` is a conservative routing/aiguillage agent. Its purpose is to
propose a limited pre-RUN orientation and to surface uncertainty early. It is
not a source auditor, classifier, validator, publisher or journal writer.

`RoutingAgent` may output:

- `type_unite_propose`;
- `decision_pre_RUN_proposee`;
- initial risks;
- uncertainties;
- recommended `controle_perimetre`;
- `alias_doublon_possible`;
- recommended relance;
- recommended audit;
- reason why RUN is not authorized.

`RoutingAgent` must not output:

- S-A;
- I-A;
- final `source_decisive`;
- `publication_ready`;
- final fiche;
- definitive fusion/scission;
- applied journal patch;
- launched RUN;
- real source audit;
- public publication status.

The default RoutingAgent posture is conservative: keep the unit provisional,
name the missing evidence, recommend audit or relance when needed and explain
why no RUN is authorized.

## 4. Feedback loops from architecture to agents

Architecture may return structured feedback after failed controls. This is an
architecture-to-agent feedback loop, not a license for architecture to invent
evidence or force a conclusion.

### A. Technical/contract failure

Examples:

- invalid JSON;
- missing required field;
- invalid enum;
- forbidden field;
- out-of-scope output.

Architecture returns structured feedback containing:

- failed control;
- reason;
- allowed values if relevant;
- repair mode;
- instruction to fix only invalid fields and not add new conclusions.

The repair target is narrow. The agent should correct the invalid contract or
field problem only. It must not use repair mode to add stronger evidence,
invent source support, change category for convenience or produce a new final
decision.

### B. Methodological failure or weak output

Examples:

- I-A proposed without central improvisation proof;
- platform used as original source;
- `fiche_pratique` forced where `fiche_cadre`/`fiche_famille` seems likely;
- prudence missing;
- contradiction ignored.

Architecture routes the failure to one of these allowed next steps:

- same agent repair;
- specialized agent;
- `SourceAuditAgent`;
- `ClassificationAgent`;
- `ContradictionAgent`;
- `ValidationReviewAgent`;
- structured blocking.

Architecture must not tell an agent to "make the test pass" by forcing
evidence. It must identify the failed rule and the allowed next step. The
architecture can block, route, ask for bounded repair or request specialized
review; it cannot convert weak evidence into strong evidence or decide the
musicological interpretation in place of an agent.

## 5. Recommended vocabulary, non-contractual

The names below are recommended pre-contract vocabulary. They are not active
enums, not final JSON enum names, not implemented runtime values and not a
contract. Future contracts may rename, split, merge or reject them after human
review.

Proof statuses:

```text
fait_atteste
fait_atteste_limite
mention_attestee
hypothese_conservee
indice_non_probant
insuffisant
```

Readiness statuses:

```text
ready_for_routing
ready_for_search
ready_for_RUN
ready_for_RUN_002
ready_for_validation_agentique
ready_for_journal_patch
publication_ready
```

Blocking statuses:

```text
blocked_source
blocked_perimetre
blocked_type_unite
blocked_contradiction
blocked_ethics
blocked_technical
blocked_scope
blocked_publication
blocked_journal_application
```

Audit statuses:

```text
needs_source_audit
needs_classification_audit
needs_improvisation_audit
needs_perimeter_audit
needs_ethics_audit
needs_publication_audit
needs_technical_audit
needs_journal_audit
```

These names are not final JSON enums and must not be treated as implemented
runtime values. `publication_ready` in this vocabulary is only a future
discussion label; it does not authorize publication or public export.

## 6. Relationship to previous docs

This document relates to the current documentation chain as follows:

- `RULES_IMPLEMENTATION_AUDIT_v0.2.3-auto.md` audited existing rule coverage.
- `PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md` clarified blockers before
  any first prompt work.
- `PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md` remains the governing protocol
  for any future prompt lifecycle.
- `REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md` remains the architecture status
  review and guardrail summary.

Codex 023 audited rule coverage. Codex 024 clarified pre-prompt blockers.
Codex 025 maps responsibilities and rule levels before any prompt drafting.

This document does not supersede `PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md`.
It does not start prompt drafting, does not create a prompt, does not create a
prompt draft, does not approve runtime prompt loading and does not activate
OpenAI.

## 7. Current negative guarantees

This responsibility map leaves all existing runtime guardrails intact:

```text
- no production code change;
- no behavior change;
- no runtime prompt loading;
- no prompt body;
- no prompt draft;
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
