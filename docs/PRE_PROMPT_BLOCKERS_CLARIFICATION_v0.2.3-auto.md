# Pre-prompt blockers clarification v0.2.3-auto

Status: Codex 024 clarification-only, pre-prompt, no runtime effect.

This document clarifies blockers identified by
`RULES_IMPLEMENTATION_AUDIT_v0.2.3-auto.md` before any first real prompt draft
is written. It is grounded in existing repository rules and does not create
new doctrine unrelated to those rules.

Relation to `RULES_IMPLEMENTATION_AUDIT_v0.2.3-auto.md`: Codex 023 identified
four ambiguity families that should block or constrain prompt drafting. Codex
024 records clarification posture for those blockers and leaves unresolved
points marked as "requires human decision".

Relation to `PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md`: this document does
not change the prompt lifecycle. No real prompt exists yet. No prompt is active
by default. No prompt may be consumed by `OpenAIAdapter` or CLI dry-run.

This document does not create a prompt, does not start prompt drafting, does
not create a prompt body, does not render or load prompts, does not activate
OpenAI, and does not change runtime behavior.

No real OpenAI/runtime activation exists.

## Shared posture

- Agents may propose structured outputs only.
- Deterministic validation, quality gates and human review remain separate from
  agent proposals.
- Repository-controlled terms are preferred over new vocabulary.
- If repository evidence is insufficient, the point is marked "requires human
  decision" rather than being invented here.
- These clarifications are documentation-only. They do not claim implementation
  coverage where no code or tests exist.

## 1. Attested fact vs hypothesis

### Existing ambiguity

Codex 023 found that "attested fact vs hypothesis" is not an explicit
repository rule, although existing docs already require explicit proof for
strong claims such as `S-A` and `I-A`, warn against source confusion, and
require prudence for fragile cultural or musicological information.

### Clarification proposed from existing doctrine

An attested fact is a statement that is explicitly supported by an identified
source or by a validated structured field inside the current authorized input.
It must remain tied to the source or field that supports it.

A hypothesis, inference, plausible but unverified statement, analogy or
generalization is not an attested fact. It may be preserved as uncertainty,
warning, audit note, question, or rationale for `controle_perimetre`, but it
must not be used as evidence for a strong classification.

Uncertainty must be represented explicitly in structured output fields such as
warnings, audit notes, prudence level, audit status, `run_interdit_raison`, or
future contract fields dedicated to uncertainty. A future agent must not fill
gaps by plausibility, cultural familiarity, title similarity, genre similarity,
or a likely but unverified source relationship.

This clarification is grounded in existing proof requirements for `S-A`,
`I-A`, source audit status, warnings, audit notes, and prudence. It does not
add a new runtime rule.

### Affected future agents

`RoutingAgent`, `SourceAuditAgent`, `ClassificationAgent`,
`ConservationAgent`, `SynthesisAgent`, `DeltaAgent`, `JournalPatchAgent`, and
`BatchReporter` are affected if they mention facts, uncertainty, classification
strength, or publication readiness.

### Effect on future contracts/tests

Future contracts/tests should distinguish:

```text
attested_fact
hypothesis_or_inference
uncertainty_note
source_or_field_ref
```

Exact field names and enum values are not implemented by this document and
require human decision before runtime use.

### Blocks RoutingAgent prompt draft?

Partially. A narrow `RoutingAgent` prompt draft can be safe if it only proposes
unit type and routing caution from supplied structured input, does not invent
facts, and uses uncertainty to defer or route to `controle_perimetre`. It must
not make source-backed factual claims unless those claims are already present
in the input.

### Blocks SourceAuditAgent or ClassificationAgent prompt draft?

Yes, for real source or classification work. `SourceAuditAgent` and
`ClassificationAgent` drafts should remain blocked until uncertainty and
attestation fields are represented in contracts/tests or explicitly accepted
as review-only prompt text by a human.

### Open questions

- Exact structured field names for attested facts and hypotheses require human
  decision.
- Whether hypothesis preservation belongs in `SourceAuditReport`,
  `ClassificationResult`, `ConservationRecord`, or a separate object requires
  human decision.

## 2. Source status mapping

### Existing ambiguity

Codex 023 found documented source roles but no complete source status mapping
implemented in current contracts/runtime. Existing repository evidence already
distinguishes source originale, plateforme d'acces, source decisive, source de
renfort, source contexte, source insuffisante, source legacy optionnelle, and
source audit statuses.

### Clarification proposed from existing doctrine

Use this mapping as clarification vocabulary for future review, not as a claim
of implemented enum coverage:

```text
source_originale
  The underlying source or originating institution/work that carries the
  relevant evidence. It is not merely the host or access path.

plateforme_acces
  A website, database, library platform, search result, mirror, repository, or
  access layer. It may help locate evidence but must not be treated as source
  originale or decisive source by itself.

decisive_source
  A source that directly supports the claim being made and can support strong
  source status only when independent verification requirements are also met.

complementary_or_reinforcement_source
  A source that supports or corroborates context, but is not sufficient alone
  for a strong source classification.

contextual_source
  A source that helps understand context, terminology, geography, history or
  relation, but does not prove the specific classification claim.

insufficient_source
  A source that is relevant but too weak, broad, ambiguous, indirect or
  incomplete to support the proposed claim.

rejected_or_unusable_source
  A source or reference that cannot be used for the current claim because it is
  the wrong object, a platform confused with a source, legacy-only material used
  as decisive by default, a RUN archive used as documentary source, or otherwise
  incompatible with repository guardrails.

accepted_with_caution
  A source can be usable with explicit limits. This is a prudence state, not a
  publication approval and not automatic support for S-A or I-A.
```

Effects:

- `S-A` remains blocked without decisive source and independent verification.
- `I-A` remains blocked without explicit evidence of central improvisation.
- Platform/access confusion must produce warning, audit note, downgrade,
  `needs_audit`, or blocking quality gate depending on severity.
- Contextual, complementary, insufficient, rejected, or caution-only evidence
  must not be silently promoted into decisive support.
- Source status must be attached to the specific claim it supports; a global
  source cannot be reused as proof for a different entry without justification.

### Affected future agents

`SourceAuditAgent` is the primary affected future agent. `ClassificationAgent`,
`RoutingAgent`, `SynthesisAgent`, `DeltaAgent`, and `BatchReporter` are affected
when they consume or report source status.

### Effect on future contracts/tests

Future contracts/tests should make source role, support strength, limitations,
and rejection/caution explicit. They should include negative cases for:

```text
plateforme_acces used as source_originale
legacy optional source used as decisive by default
RUN archive used as documentary source
contextual source used as decisive source
insufficient source used to support S-A or I-A
accepted_with_caution treated as publication approval
```

Exact enum names require human decision before implementation. Current code
does not implement full source status mapping.

### Blocks RoutingAgent prompt draft?

No, if the first `RoutingAgent` draft does not audit sources or claim source
status. It may say that source status is not evaluated and route uncertain
cases conservatively.

### Blocks SourceAuditAgent or ClassificationAgent prompt draft?

Yes. `SourceAuditAgent` prompt drafting should remain blocked until the source
status mapping is accepted by a human and reflected in a future contract/test
plan. `ClassificationAgent` prompt drafting should remain blocked for strong
classification output until it can consume source status safely.

### Open questions

- Exact source status enum names require human decision.
- Whether `accepted_with_caution` is a source status, audit status, or
  publication status requires human decision.
- The threshold for a source to become decisive requires human decision per
  future contract.

## 3. hors_perimetre vs controle_perimetre

### Existing ambiguity

Codex 023 found that `hors_perimetre` is requested as a blocker family, but no
direct controlled value exists in repository code. The existing repository term
is `controle_perimetre`, with related values such as
`controle_perimetre_avant_RUN` and `a_verifier`.

### Clarification proposed from existing doctrine

For the current repository state, `hors_perimetre` is not a final category and
not a controlled output value. It is a possible observation that a case may be
outside the current project scope, but current structured output should express
that conservatively with existing repository terms:

```text
type_unite_RUN = controle_perimetre
decision_pre_RUN = controle_perimetre_avant_RUN
statut_unite_classable = a_verifier
run_autorise = false
run_interdit_raison includes scope uncertainty
```

A future agent may say, in a structured warning or rationale, that an item
appears possibly outside scope and requires scope control. It must not invent a
new `hors_perimetre` enum, final category, publication state, or exclusion rule
unless a later human decision adds that controlled value.

### Affected future agents

`RoutingAgent` is the primary affected future agent. `ConservationAgent`,
`ClassificationAgent`, `SynthesisAgent`, `BatchReporter`, and future audit
components may consume the result.

### Effect on future contracts/tests

Future contracts/tests should verify that possible out-of-scope cases use
existing `controle_perimetre` terms unless a later contract adds
`hors_perimetre`. Negative tests should reject invented enum values in current
contracts.

### Blocks RoutingAgent prompt draft?

No, if the draft uses only existing repository-controlled terms and treats
possible out-of-scope cases as `controle_perimetre` or `a_verifier` with
`run_autorise = false`. It blocks any `RoutingAgent` draft that wants to emit
`hors_perimetre` as a controlled value or final category.

### Blocks SourceAuditAgent or ClassificationAgent prompt draft?

Partially. It does not block a prompt that only consumes an existing
`controle_perimetre` result. It blocks prompts that would classify or publish a
case that has unresolved perimeter control.

### Open questions

- Whether `hors_perimetre` should become a future controlled enum value
  requires human decision.
- If added later, its relation to exclusion, reserve, audit queue, and
  publication status requires human decision.

## 4. Unified decision readiness semantics

### Existing ambiguity

Codex 023 found that ready, blocked, needs audit, human review, caution,
publication readiness, proposed decision and validated decision are spread
across validation status, quality gates, batch status, audit queue and final
provisional decision language.

### Clarification proposed from existing doctrine

Use the following semantics for future documentation and prompt review. These
are clarifications, not implemented runtime behavior.

```text
proposed_decision
  An agent-produced recommendation. It is never final by itself.

validated_decision
  A decision accepted by deterministic validation, quality gates and any
  required human review for the relevant stage.

ready
  Ready for the next controlled internal step only. It does not mean
  publication-ready.

blocked
  Current processing path cannot proceed safely without correction, audit, or
  human decision. Existing quality gates already have blocking classification.

needs_audit
  Requires structured audit review because evidence, source status, protocol
  consistency, perimeter, or prudence is unresolved. Processing may or may not
  continue depending on severity.

needs_human_review
  Requires explicit human review before a status transition, prompt lifecycle
  transition, publication decision, JournalPatch application, or any real
  runtime activation.

accepted_with_caution
  Accepted only with explicit prudence, warning, audit note or limitation. It
  is not publication approval and does not erase uncertainty.

publication_ready
  Not available in the current runtime. Publication is a separate future stage
  and cannot be inferred from a dry-run, agent proposal, source caution, or
  accepted_with_caution state.

not_publication_ready
  Any state with unresolved source status, perimeter, audit, RUN_002, delta,
  publication blocking, human review need, or prompt/runtime guardrail issue.
```

Mapping posture:

- Future agent outputs should use proposed wording unless a contract explicitly
  says otherwise.
- Quality gates can classify `ok`, `prudence`, `recoverable`, or `blocking`,
  but that is not publication approval.
- Batch reports summarize processing status and counts, not public release.
- Audit queue entries represent review needs, not rejection by default.
- JournalPatch proposals are proposed updates only and must not be applied by
  default.

### Affected future agents

All future agents are affected when they emit decisions, readiness, audit needs,
publication status, or journal patch proposals. `RoutingAgent`,
`SourceAuditAgent`, `ClassificationAgent`, `SynthesisAgent`, `DeltaAgent`,
`JournalPatchAgent`, and `BatchReporter` are especially affected.

### Effect on future contracts/tests

Future contracts/tests should keep proposed and validated states separate and
reject prompts or runtime paths that equate:

```text
agent proposal = validated decision
quality_gate ok = publication_ready
accepted_with_caution = publication approval
audit queue = automatic rejection
journal patch proposal = journal patch application
```

Exact field names and enum mapping require human decision before implementation.

### Blocks RoutingAgent prompt draft?

No, if the first `RoutingAgent` draft emits only proposed routing decisions,
never publication readiness, and explicitly leaves validation to deterministic
gates and review.

### Blocks SourceAuditAgent or ClassificationAgent prompt draft?

Yes, for any prompt that emits readiness, publication, final classification, or
validated decision language. Source and classification prompts remain blocked
until proposed vs validated decision semantics are reflected in their contracts
and tests or explicitly accepted for review-only drafting by a human.

### Open questions

- Exact enum names for `ready`, `blocked`, `needs_audit`,
  `needs_human_review`, `accepted_with_caution`, `publication_ready`, and
  `not_publication_ready` require human decision.
- Which states belong in agent payloads, quality gates, batch report, audit
  queue, final provisional decision, or JournalPatch proposal requires human
  decision.

## Safe for first RoutingAgent draft

The following is safe for a future first `RoutingAgent` draft only after an
explicit prompt-drafting mission, and only as prompt review content:

- use existing repository-controlled routing terms;
- output proposed routing decisions only;
- avoid source audit and classification claims;
- mark uncertainty explicitly;
- use `controle_perimetre` / `a_verifier` for possible out-of-scope cases;
- set or recommend no RUN by default;
- avoid publication readiness language;
- keep all validation, audit, human review and publication decisions outside
  the agent.

This document does not create that draft.

## Still requires human decision

- Exact structured fields for attested facts, hypotheses and uncertainty.
- Exact source status enums and thresholds for decisive source status.
- Whether `accepted_with_caution` is a source status, audit status,
  publication status, or a cross-cutting prudence marker.
- Whether `hors_perimetre` should become a future controlled enum value.
- Unified enum or field mapping for ready, blocked, needs audit, human review,
  caution, publication readiness, proposed decision and validated decision.
- Which future contracts/tests own each clarified concept.
