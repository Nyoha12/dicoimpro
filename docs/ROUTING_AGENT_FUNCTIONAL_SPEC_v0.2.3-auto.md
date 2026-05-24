# RoutingAgent functional specification v0.2.3-auto

Status: Codex 026 pre-prompt functional specification.

Scope: documentation/tests only. This document is non-runtime, non-prompt,
non-contract, non-final enum and pre-implementation. It defines the functional
perimeter of a future `RoutingAgent` before prompt drafting. It does not create
a real prompt, does not create a prompt draft, does not create prompt bodies,
does not create `docs/prompts/drafts` content, does not create `prompts.py`,
does not create final JSON contracts, does not create runtime enums, does not
implement agents, does not activate OpenAI, does not perform network calls and
does not change runtime behavior.

No real prompt exists yet. No runtime prompt loading or OpenAI activation
exists. This specification authorizes no RUN, no candidate selection, no real
entry processing, no active journal read/write, no JournalPatch application, no
XLSX/CSV export and no old PDF usage.

## 1. Purpose of RoutingAgent

`RoutingAgent` is a conservative routing/aiguillage agent. Its role is to make
an early, limited, reversible orientation proposal before any RUN.

It exists to answer:

- what kind of unit this entry probably is;
- whether standard documentary processing is possible;
- whether perimeter control is needed;
- whether the item looks like a possible alias/doublon;
- whether it looks like `fiche_pratique`, `fiche_cadre`, `fiche_famille`,
  `mecanisme_passerelle`, `controle_perimetre` or `a_verifier`;
- what uncertainty, relance or audit should be surfaced before any RUN.

`RoutingAgent` is not a source auditor, not a classifier, not a publisher, not
a JournalPatch applier, not a RUN executor and not a validation agent. It does
not decide final source status, final classification, publication readiness,
journal mutation or external action.

## 2. Allowed Conceptual Inputs

A future `RoutingAgent` may operate only on supplied structured input. Allowed
conceptual inputs may include:

- entry id;
- entry label;
- minimal existing metadata supplied by explicit scope;
- authorized steering context if provided by architecture;
- known already-treated status if supplied by architecture;
- allowed `type_unite` vocabulary;
- allowed `decision_pre_RUN` vocabulary;
- project guardrails;
- no active journal write access.

Input limits:

- `RoutingAgent` must not fetch external sources.
- `RoutingAgent` must not browse.
- `RoutingAgent` must not inspect `data/local_files` unless future architecture
  explicitly supplies authorized input.
- `RoutingAgent` must not infer from unavailable project data.
- `RoutingAgent` operates only on supplied structured input.
- `RoutingAgent` has no active journal write access and no implicit active
  journal read access.

## 3. Allowed Conceptual Outputs

A future `RoutingAgent` may recommend conceptual fields such as:

- `type_unite_propose`;
- `decision_pre_RUN_proposee`;
- confidence / uncertainty note;
- `risks_initiaux`;
- `controle_perimetre_recommande`;
- `alias_doublon_possible`;
- `relance_recommandee`;
- `audit_recommande`;
- `run_autorise_provisoirement`;
- `run_interdit_raison`;
- `justification_courte`;
- `trace_notes`.

These are recommended conceptual fields, not final contracts or runtime enums.
They do not create final JSON contracts, active enum values or runtime behavior.

## 4. Forbidden Outputs

`RoutingAgent` must not output:

- S-A;
- I-A;
- final D/S/I/C/E status;
- final `source_decisive`;
- final source audit;
- `publication_ready`;
- final fiche;
- definitive fusion/scission;
- applied journal patch;
- launched RUN;
- active journal modification;
- source publication status;
- final classification;
- old PDF source use;
- candidate selection outside explicit scope.

Forbidden-output examples also include any claim that a JournalPatch was
applied, any claim that RUN was launched, any declaration that a fiche is final,
and any final source_decisive status.

## 5. Routing Categories and Conservative Behavior

`RoutingAgent` must prefer conservative routing over forced `fiche_pratique`.
When the supplied input is weak, ambiguous or broad, the agent should surface
uncertainty instead of collapsing the item into a simple practice fiche.

### `fiche_pratique`

Possible only if the object appears unitary, identifiable and not obviously a
broader frame, family, mechanism or perimeter issue. This is a provisional
orientation, not a final classification.

### `fiche_cadre`

For broad systems, frameworks, traditions, repertoires, modal systems,
pedagogical/methodological frames or large structured domains that may contain
practices but are not one simple practice.

### `fiche_famille`

For groups of related but distinct practices, variants or sub-objects that
should not be collapsed into one `fiche_pratique`.

### `mecanisme_passerelle`

For transversal processes, mechanisms, techniques or concepts present across
multiple practices and not tied to one local practice.

### `controle_perimetre`

For uncertain scope, non-musical ambiguity, unclear improvisation relevance,
unstable object or possible outside-scope issue.

### `alias_doublon`

For possible duplicate, transliteration, variant naming, alias or relation
issue. `RoutingAgent` may flag `alias_doublon_possible`; it must not make a
definitive merge, fusion, deletion or scission decision.

### `a_verifier`

For insufficient information or unclear routing when no stronger safe route
exists.

## 6. RUN Posture

RUN possible does not mean fiche ready. A provisional RUN recommendation is not
publication readiness, not final validation and not a final fiche.

`type_unite_RUN` is mandatory before RUN. If a future output cannot name a
required `type_unite_RUN` through an authorized architecture contract,
`RoutingAgent` must recommend no RUN or a RUN-not-authorized decision.

`RoutingAgent` may recommend no RUN or RUN not authorized when routing is
unstable. It does not launch RUN. It does not decide RUN_002. It may recommend
future audit or relance before RUN.

## 7. Relance and Audit Recommendations

`RoutingAgent` may recommend relance or audit types conceptually and
non-contractually. Examples:

- `relance_perimetre`;
- `relance_alias_doublon`;
- `relance_categorisation`;
- `relance_fiche_cadre_vs_pratique`;
- `relance_fiche_famille`;
- `relance_mecanisme_passerelle`;
- `audit_routage`;
- `audit_classification_later`;
- `audit_source_later`.

These recommendation names are not final contracts or runtime enums.
`RoutingAgent` recommends relance/audit; it does not perform them.

## 8. Architecture Feedback Compatibility

This specification is compatible with
`AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md`. Future architecture may
return structured feedback to `RoutingAgent` after:

- invalid field;
- forbidden output;
- unsupported category;
- overstrong claim;
- attempt to output `publication_ready`;
- attempt to output S-A/I-A;
- attempt to authorize RUN without required `type_unite`;
- attempt to create final classification.

Architecture feedback must identify failed rule and allowed repair path. It
must not tell the agent to force evidence or "make the test pass". It may ask
for bounded repair of invalid fields, weaker wording, allowed categories,
structured blocking, relance or audit recommendation. It must not invent
evidence, force a positive route or convert uncertainty into final validation.

## 9. Positive and Negative Synthetic Examples

These examples are synthetic, non-project-specific and illustrative only. They
do not process real project entries, do not use current active journal data, do
not use old PDF data and do not select candidates.

### Positive synthetic examples

Broad modal/tradition-like label:

- supplied input: `entry_id="SYN-001"`, `entry_label="North-coast modal teaching system"`;
- conservative route: `fiche_cadre` probable;
- reason: broad system/framework wording, not one simple practice;
- guardrail: no forced `fiche_pratique`.

Group/family-like label:

- supplied input: `entry_id="SYN-002"`, `entry_label="Three variants of circle cue practice"`;
- conservative route: `fiche_famille` possible;
- reason: related variants should not be collapsed into one fiche.

Transversal technique-like label:

- supplied input: `entry_id="SYN-003"`, `entry_label="Layer-shift cueing technique"`;
- conservative route: `mecanisme_passerelle` possible;
- reason: technique could operate across multiple practices.

Unclear non-musical or scope-uncertain label:

- supplied input: `entry_id="SYN-004"`, `entry_label="Table setting protocol"`;
- conservative route: `controle_perimetre` / `a_verifier`;
- reason: supplied label does not show musical or improvisation relevance.

Possible duplicate/transliteration:

- supplied input: `entry_id="SYN-005"`, `entry_label="Lumo-tek"`,
  `authorized_context="possible relation to Lumotek"`;
- conservative route: `alias_doublon_possible`;
- reason: variant naming may require relation review;
- guardrail: no definitive merge.

### Negative synthetic examples

`RoutingAgent` must not emit I-A:

- forbidden output: `{"status": "I-A"}`;
- allowed repair: recommend `audit_classification_later` or `a_verifier`.

`RoutingAgent` must not emit S-A:

- forbidden output: `{"source_status": "S-A"}`;
- allowed repair: recommend `audit_source_later` without final source audit.

`RoutingAgent` must not say `publication_ready`:

- forbidden output: `{"publication_ready": true}`;
- allowed repair: remove the field and preserve only provisional routing notes.

`RoutingAgent` must not apply JournalPatch:

- forbidden output: `{"journal_patch_applied": true}`;
- allowed repair: no journal mutation; trace a routing note only.

`RoutingAgent` must not launch RUN:

- forbidden output: `{"launched_RUN": "RUN_002"}`;
- allowed repair: recommend no RUN or provisional RUN posture without execution.

`RoutingAgent` must not create a final fiche:

- forbidden output: a completed fiche body, final classification or final
  publication text;
- allowed repair: provide `justification_courte`, uncertainty and relance/audit
  recommendation only.

## 10. Relationship to Previous Docs

This specification references:

- `AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md`;
- `PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md`;
- `PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md`;
- `RULES_IMPLEMENTATION_AUDIT_v0.2.3-auto.md`;
- `REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md`.

Codex 025 mapped responsibilities. Codex 026 specifies the future
`RoutingAgent` functional perimeter. Codex 026 does not start prompt drafting.
Codex 026 does not supersede the prompt activation protocol. A future Codex may
create a disabled prompt draft only after this spec is reviewed.

## 11. Current Negative Guarantees

Codex 026 remains docs/tests only:

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
