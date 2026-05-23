# Rules implementation audit v0.2.3-auto

Status: Codex 023 audit-only document.

This document is an audit of existing repository rules and current implementation
coverage. It is not new doctrine. It does not rewrite the protocol, does not
create prompt bodies, does not start prompt drafting, does not render or load
prompts, does not activate OpenAI, and does not change runtime behavior.

No real prompt exists yet. No real OpenAI/runtime activation exists.

Evidence scope: repository documentation, contracts, tests, fixtures and source
code present in this repository. If a rule is known from project doctrine but is
not evidenced by repository docs or code, it is marked as "not found in
repository evidence" instead of being invented here.

Codex 024 follow-up: `PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md`
clarifies the pre-prompt blockers identified below. That clarification is
documentation-only and does not change the implementation coverage statuses in
this audit.

## Status taxonomy

```text
implemented
partially_implemented
documented_only
tested_guardrail_only
missing
ambiguous
out_of_scope_for_v0.2.3_auto
```

## Audit matrix

| Rule area | Existing rule / principle | Existing source document or code reference inside repository | Current implementation status | Affected agents or components | Risk if not covered | Recommended next action |
|---|---|---|---|---|---|---|
| Agent autonomy | Agents may produce bounded structured objects, but they do not govern workflow, state, rules, journal or publication. | `docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md` D-002; `docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md` sections 0, 1, 5; `src/dico_impro/agents/registry.py`; `src/dico_impro/contracts/agents.py` | partially_implemented | `AgentRegistry`, `AgentContract`, `AgentTask`, orchestrator | An agent could become an implicit authority outside deterministic validation. | Keep all future prompt or adapter work behind explicit contracts and registry validation; add runtime checks only in a future behavior-changing mission. |
| Agent autonomy | Agents must not write the active journal directly; a `JournalPatch` is only a proposed separate object. | `docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md` D-004; `docs/CONTRATS_JSON_v0.2.3-auto.md` section 12; `src/dico_impro/journal.py`; `tests/test_journal_patch.py` | partially_implemented | `JournalPatch`, `validate_journal_patch`, JSON export, CLI dry-run | Silent journal mutation would break auditability and reversibility. | Maintain the current separation; no JournalPatch application before a dedicated future approval path. |
| Agent autonomy | Publication consolidee is separate and must not be decided by an agent alone. | `docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md` D-002 and P-004; `docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md` section 11; `src/dico_impro/validators.py`; `src/dico_impro/agents/quality_gates.py` | partially_implemented | validators, quality gates, `BatchReport` | A model could present a provisional result as publishable truth. | Keep publication out of runtime; any future publication path must have separate human approval and tests. |
| Agent autonomy | Codex may implement bounded reversible work, not decide project doctrine. | `docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md` D-008; `docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md` section 13 | documented_only | Codex missions, docs sync | Documentation or tests could drift into doctrine creation. | Continue treating docs/tests changes as synchronization or audit unless a human explicitly approves doctrine changes. |
| Agent autonomy | Agents must escalate protocol violations, forbidden files, source confusion and publication blocking. | `docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md` section 6; `src/dico_impro/agents/quality_gates.py`; `tests/test_agent_quality_gates.py` | partially_implemented | quality gates, fake adapter, execution wrapper | Severe failures could be downgraded to warnings. | Expand only with targeted future tests when new runtime paths exist. |
| Selection / candidate handling | No autonomous candidate selection by default. | `docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md` R-002; `docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md` section 10; `docs/PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md` sections 3 and 7; `tests/test_runtime_boundaries.py` | tested_guardrail_only | CLI dry-run, prompt protocol, runtime boundary tests | The system could process entries outside the intended batch strategy. | Keep the guardrail wording unchanged; add behavior only after explicit scope policy is approved. |
| Selection / candidate handling | Current dry-run accepts explicit scope only. | `src/dico_impro/orchestration/scope.py`; `src/dico_impro/orchestration/dry_run.py`; `src/dico_impro/cli.py`; `tests/test_orchestration_scope.py`; `tests/test_cli_dry_run.py` | implemented | `ExplicitScope`, CLI `plan-batch --dry-run`, task builder | Entry processing could become implicit or non-replayable. | Preserve explicit-scope-only behavior until a future strategy-of-lot mission. |
| Selection / candidate handling | No real entry processing unless explicitly authorized. | `docs/REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md` sections 2-4; `docs/PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md`; `tests/test_cli_dry_run_smoke.py`; `tests/test_runtime_boundaries.py` | tested_guardrail_only | CLI dry-run, mock OpenAI planning, prompt fixtures | Test fixtures could be mistaken for production processing. | Keep test scopes synthetic and temporary; do not connect to real project data in prompt drafts. |
| Selection / candidate handling | Already-treated or locked entries must not be treated as new. | `docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md` D-005; `docs/CONTRATS_JSON_v0.2.3-auto.md` section 2; `src/dico_impro/contracts/project_state.py`; `src/dico_impro/journal_reader.py`; `tests/test_journal_reader.py` | partially_implemented | `EntryState`, journal reader guards | Previously treated entries could be reopened as new work. | Block any real batch or prompt draft that needs project-state routing until this is wired into orchestration. |
| Sources | Distinguish source originale from plateforme d'acces. | `docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md` sections 1 and 6.4; `docs/CONTRATS_JSON_v0.2.3-auto.md` sections 5-6; `docs/STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md` sections 1.3 and 4.1 | documented_only | future `SourceAuditAgent`, future source contracts | A platform could be promoted into decisive documentary evidence. | Treat as a prompt-drafting blocker for any source-audit or classification prompt. |
| Sources | Source roles include decisive, reinforcement/context, access/platform and insufficient source roles. | `docs/CONTRATS_JSON_v0.2.3-auto.md` sections 5-6; `docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md` sections 6.1 and 13.3 | documented_only | future `SourceRecord`, future `SourceAuditReport` | Weak evidence could support strong classification. | Implement source contracts and tests before source-aware prompt drafting. |
| Sources | Source audit is required before strong claims such as S-A. | `docs/CONTRATS_JSON_v0.2.3-auto.md` sections 6-8; `src/dico_impro/validators.py`; `tests/test_validation_rules.py` | partially_implemented | validators, `ClassificationInput`, `SourceAuditInput` | S-A could pass without adequate evidence. | Current deterministic S-A downgrade can be carried forward; full source audit remains missing. |
| Sources | Source approval, rejection and prudence states are expected but not fully formalized. | `docs/STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md` section 4.1; `docs/CONTRATS_JSON_v0.2.3-auto.md` `audit_source_status` values | ambiguous | future source audit, quality gates | The difference between rejected, insufficient and prudent acceptance could be inconsistent. | Clarify existing repository docs before source-audit prompt drafting; do not infer new states here. |
| Sources | Source archiving expectations are present at a high level; archives RUN are not active sources. | `docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md` D-006; `docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md` section 9 | documented_only | manifest, future source storage, future source audit | Historical outputs could be reused as documentary evidence. | Keep archives out of runtime source inputs; define source archive mechanics in a future explicit doc/code mission. |
| Sources | Old PDF is not a default or decisive source. | `docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md` D-007; `docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md` section 3.3; `tests/test_runtime_boundaries.py` | tested_guardrail_only | task builder, runtime boundary tests, prompt protocol | Legacy content could bias source assessment. | Keep old PDF forbidden in prompt context and dry-run paths. |
| Information quality | Attested fact vs hypothesis is a required distinction in the mission brief, but the exact wording was not found in repository evidence. | not found in repository evidence; closest evidence is explicit proof requirements in `docs/CONTRATS_JSON_v0.2.3-auto.md` section 7 and `docs/REGLES_VALIDATION_v0.2.3-auto.md` | missing | future classification and source audit | The system could fill uncertain facts by plausibility. | Prompt drafting that classifies factual claims should block until this distinction is documented or mapped to existing proof fields. |
| Information quality | Explicit uncertainty and no filling gaps by plausibility are implied by prudence docs, but not fully encoded. | `docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md` sections 1, 2, 9; `docs/STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md` sections 0 and 8 | documented_only | future prompts, validators, golden set | Plausible but unattested content could be accepted as fact. | Carry the conservative wording into future reviews; do not encode new semantics in this audit. |
| Information quality | Fragile cultural/musicological information requires prudence and anti-reduction checks. | `docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md` sections 1, 9, 12; `docs/STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md` sections 2 and 8; `tests/test_golden_set_prudence.py` | partially_implemented | fake golden set, quality gates, future routing/conservation | Complex practices could be flattened into fiche pratique entries. | Keep first prompt scope narrow; semantic anti-reduction remains incomplete. |
| Information quality | Warnings and audit notes must be preserved as structured metadata. | `src/dico_impro/contracts/agents.py`; `src/dico_impro/agents/adapters/openai_contracts.py`; `src/dico_impro/agents/evaluation.py`; `tests/test_openai_client_contracts.py`; `tests/test_agent_evaluation_records.py` | implemented | `AgentResult`, `OpenAIClientResponse`, evaluation records | Warnings could be lost or treated as final decisions. | Maintain structured warnings/audit notes for all future adapters. |
| Information quality | DELTA records are expected when decision/status changes between passes. | `docs/CONTRATS_JSON_v0.2.3-auto.md` section 10; `docs/REGLES_VALIDATION_v0.2.3-auto.md`; `src/dico_impro/models.py`; `tests/test_journal_patch.py` | partially_implemented | `DeltaRecord`, future delta builder | Decision changes could become unauditable. | Do not claim DELTA automation exists; implement a delta builder only in a future behavior-changing mission. |
| Categorization and unit type | Unit types include fiche pratique, fiche-cadre, fiche-famille, mecanisme-passerelle and alias/doublon. | `docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md` section 2; `docs/CONTRATS_JSON_v0.2.3-auto.md` section 3; `src/dico_impro/models.py` `TypeUniteRun` | partially_implemented | `RoutingDecision`, dry-run expected schema | Routing may look complete while semantic routing is absent. | A first RoutingAgent prompt draft may carry these existing enum names, but must not decide real entries. |
| Categorization and unit type | Hors perimetre is requested by the mission brief, but no direct controlled value was found. | not found in repository evidence; closest terms are `controle_perimetre` in docs and `TypeUniteRun` | ambiguous | routing, validation, future prompt contracts | A future prompt could invent a new category or misuse controle_perimetre. | Clarify whether hors perimetre maps to existing controle_perimetre before prompt drafting. |
| Categorization and unit type | `type_unite_RUN` is required before RUN; RUN possible does not imply fiche pratique ready. | `docs/CONTRATS_JSON_v0.2.3-auto.md` section 3; `docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md` sections 2 and 9; `src/dico_impro/models.py` `RoutingDecision` | partially_implemented | routing, dry-run task schema | A RUN could be launched on an unstable or wrong unit type. | Safe to carry as a RoutingAgent constraint later; still no RUN path exists. |
| Categorization and unit type | Fiche famille, fiche-cadre and mechanisms must not be forced into fiche pratique by default. | `docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md` sections 2, 6.1, 10; `docs/STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md` sections 2.2-2.4 | documented_only | future RoutingAgent, future ConservationAgent | Cultural or structural nuance could be lost. | Treat as a required review item for RoutingAgent prompt drafting. |
| Decision and approval | Proposed decisions and validated decisions are separate. | `docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md` sections 4, 5.5, 11; `docs/CONTRATS_JSON_v0.2.3-auto.md` sections 7-8 and 11; `src/dico_impro/validators.py` | partially_implemented | validators, final provisional decision model | A proposed model output could be treated as validated. | Keep deterministic validation between agent output and any exported decision. |
| Decision and approval | Human review is required for some risks, but no human-review workflow exists. | `docs/CONTRATS_JSON_v0.2.3-auto.md` sections 12-13; `docs/PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md` section 4; `src/dico_impro/contracts/project_state.py` `AuditQueueRecord` | partially_implemented | audit queue, prompt activation protocol | Review-required cases may have no operational route. | Do not present audit queue contracts as a working review workflow. |
| Decision and approval | Acceptation avec prudence exists as a state, but is not end-to-end behavior. | `src/dico_impro/models.py` `StatutTraitement` and `DecisionFinaleProvisoire`; `docs/CONTRATS_JSON_v0.2.3-auto.md` sections 1 and 11 | partially_implemented | final provisional decision, journal patch model | Prudence labels could be inconsistent. | Keep status names but avoid claiming publication readiness from them. |
| Decision and approval | Blocked / needs audit / ready states exist in pieces. | `src/dico_impro/agents/quality_gates.py`; `src/dico_impro/contracts/batch.py`; `docs/CONTRATS_JSON_v0.2.3-auto.md` sections 13, 17, 18 | ambiguous | quality gates, batch state, audit queue | Different components may use different readiness language. | Clarify status mapping before first prompt that emits status-like decisions. |
| Decision and approval | No S-A without decisive source and verification. | `docs/CONTRATS_JSON_v0.2.3-auto.md` section 8; `docs/REGLES_VALIDATION_v0.2.3-auto.md`; `src/dico_impro/validators.py`; `tests/test_validation_rules.py` | implemented | deterministic validator, classification input | Strong source status could be overclaimed. | This rule can safely be carried into future prompt review, while validation remains deterministic. |
| Decision and approval | No I-A without explicit evidence of central improvisation. | `docs/CONTRATS_JSON_v0.2.3-auto.md` section 7; `docs/REGLES_VALIDATION_v0.2.3-auto.md`; `src/dico_impro/validators.py`; `tests/test_validation_rules.py` | implemented | deterministic validator, classification input | Improvisation centrality could be overclaimed. | This rule can safely be carried into future prompt review, while validation remains deterministic. |
| Archiving / traceability | JSON structured output is the technical truth; XLSX/CSV are readable views, not the source of truth. | `docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md` D-003; `docs/CONTRATS_JSON_v0.2.3-auto.md` principle; `src/dico_impro/exports/json_exporter.py`; `tests/test_exports_json.py` | partially_implemented | JSON exporter, batch artifacts | Human-readable exports could be mistaken for canonical state. | Keep current automation JSON-only; do not add XLSX/CSV in this audit. |
| Archiving / traceability | Trace metadata must be deterministic and auditable. | `src/dico_impro/agents/tracing.py`; `tests/test_agent_tracing.py`; `tests/test_cli_dry_run_smoke.py` | implemented | trace metadata, evaluation records, JSON exports | Outputs could become hard to reproduce or audit. | Preserve deterministic hashing and raw trace references. |
| Archiving / traceability | Evaluation records must bind task, result, quality gate and trace metadata. | `src/dico_impro/agents/evaluation.py`; `src/dico_impro/agents/execution.py`; `tests/test_agent_evaluation_records.py`; `tests/test_agent_execution_wrapper.py` | implemented | execution wrapper, evaluation records | Quality decisions could become detached from source task/result. | Continue emitting evaluation records with JSON exports. |
| Archiving / traceability | Batch scope must remain explicit and auditable. | `src/dico_impro/orchestration/scope.py`; `src/dico_impro/contracts/batch.py`; `tests/test_orchestration_scope.py`; `tests/test_batch_summary_builders.py` | implemented | `ExplicitScope`, `BatchState`, `BatchReport` | Batch output could be unreplayable. | Maintain explicit scope in all prompt/mock review paths. |
| Archiving / traceability | Auditability and reversibility are target principles; replay and full reversal are not fully implemented. | `docs/CONTRATS_JSON_v0.2.3-auto.md` general principles; `src/dico_impro/contracts/batch.py`; `src/dico_impro/orchestration/batch_summary.py` | partially_implemented | batch state/report, JSON exports | Recovery from failures may be manual or incomplete. | Do not claim replay/reversal automation beyond current recorded metadata. |
| Archiving / traceability | Active journal is steering/read-only reference, not documentary source. | `docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md` D-004; `docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md` section 9; `src/dico_impro/journal_reader.py` | partially_implemented | journal reader, CLI guard command | Journal state could be confused with source evidence. | Keep active journal out of dry-run and prompt context unless a future explicit mission scopes read-only state access. |

## Current implementation coverage

| Component | Current coverage | Status | Evidence |
|---|---|---|---|
| Pydantic contracts | Core versioned contracts exist for agents, batch, project state and some legacy models. Full `SourceRecord`, full `SourceAuditReport`, `ConservationRecord` and `Run002Request` are not implemented as first-class contracts. | partially_implemented | `src/dico_impro/contracts/*`; `src/dico_impro/models.py`; `tests/test_contracts_*.py` |
| Orchestration | Current orchestration is explicit-scope fake dry-run plus mock OpenAI planning with injected client. It does not discover candidates, process real entries or launch RUN. | implemented | `src/dico_impro/orchestration/scope.py`; `src/dico_impro/orchestration/dry_run.py`; `src/dico_impro/orchestration/mock_openai_plan.py` |
| Quality gates | Gates classify payload validation failures, recoverable errors, prudence, blocking source confusion and publication blocking. They do not implement full musicological semantics. | partially_implemented | `src/dico_impro/agents/quality_gates.py`; `tests/test_agent_quality_gates.py` |
| Payload validation | Minimal payload checks require matching `object_type` and `schema_version`. | implemented | `src/dico_impro/agents/payload_validation.py`; `tests/test_agent_payload_validation.py` |
| Fake adapter | Deterministic scenarios cover success, warning, schema invalid, non-parseable output, protocol violation, source confusion, publication blocking and RUN_002 required. | implemented | `src/dico_impro/agents/adapters/fake.py`; `tests/test_fake_adapter.py` |
| OpenAIAdapter skeleton | Disabled by default, no OpenAI package import, injected mock client only when explicitly enabled in tests. No real API call path. | implemented | `src/dico_impro/agents/adapters/openai.py`; `tests/test_openai_adapter_skeleton.py`; `tests/test_runtime_boundaries.py` |
| PromptPackage contracts and fixtures | Metadata-only and disabled-only contract and fixtures exist. Inline prompt fields are forbidden. | implemented | `src/dico_impro/agents/prompt_contracts.py`; `tests/fixtures/prompt_packages/*.json`; `tests/test_prompt_contracts.py`; `tests/test_prompt_package_fixtures.py` |
| CLI dry-run | `plan-batch --dry-run` consumes a caller-supplied scope and writes JSON exports to the requested output directory. | implemented | `src/dico_impro/cli.py`; `tests/test_cli_dry_run.py`; `tests/test_cli_dry_run_smoke.py` |
| JSON exports | JSON export exists for dry-run audit artifacts. XLSX/CSV export is not active. | implemented | `src/dico_impro/exports/json_exporter.py`; `tests/test_exports_json.py` |
| Docs sync tests | Sync tests check current Codex status lines, doc presence and prompt/runtime boundaries. | implemented | `tests/test_docs_sync.py`; `tests/test_prompt_activation_protocol.py` |
| Runtime boundary tests | Tests guard fake-only CLI dry-run, mock-only injected OpenAI planning, no prompt consumption, no `prompts.py`, no direct OpenAI/network integration. | tested_guardrail_only | `tests/test_runtime_boundaries.py`; `tests/helpers/runtime_guards.py` |
| Prompt activation protocol | Protocol-only document exists for future prompt introduction. It is not runtime activation and contains no prompt body. | documented_only | `docs/PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md`; `tests/test_prompt_activation_protocol.py` |
| SourceDiscoveryAgent | Explicitly forbidden / suspended. No implementation exists. | out_of_scope_for_v0.2.3_auto | `docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md`; `docs/PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md`; `tests/test_runtime_boundaries.py` |

## Summary verdict

### Congruent rules

- Deterministic orchestration owns workflow and validation; agents produce
  structured outputs only.
- Current runtime paths are fake-only or injected-mock-only.
- CLI dry-run requires explicit scope and exports JSON only.
- PromptPackage is metadata-only and disabled-only.
- No active prompt, real OpenAI call, network call, RUN, candidate selection,
  active journal write, JournalPatch application, SourceDiscoveryAgent,
  data/local_files access, XLSX export or CSV export is currently authorized.

### Duplicated but coherent rules

- No direct journal writing appears in the decision register, contracts,
  adapter spec, tests and runtime boundary docs.
- Old PDF not default source appears in the decision register, architecture,
  adapter spec and prompt activation protocol.
- JSON as technical truth appears in the decision register, contracts and JSON
  exporter tests.
- No candidate selection appears in the decision register, adapter spec,
  prompt activation protocol and runtime boundary tests.

### Ambiguous rules

- "Hors perimetre" is not found as a repository-controlled unit type; closest
  repository evidence is `controle_perimetre`.
- Source approval / rejection / prudence has documented direction, but no
  complete status mapping or runtime object.
- Blocked / needs audit / ready states exist across several components but do
  not have one consolidated status map.
- Attested fact vs hypothesis is not found as an explicit repository rule,
  although proof requirements for S-A and I-A exist.

### Missing implementation coverage

- Full source contracts and runtime source audit are missing.
- ConservationRecord is documented but not implemented as a current Pydantic
  contract.
- Run002Request is documented but not implemented as a first-class contract.
- DELTA automation is missing; only `DeltaRecord` shape and minimal tests exist.
- Human review workflow is not implemented.
- Real prompt storage, rendering, loading and runtime consumption are missing
  by design.
- Real OpenAI integration is missing by design.

### Prompt-drafting blockers

The following should block prompt drafting until clarified or explicitly scoped:

- any prompt that touches source approval/rejection/prudence before source
  status semantics are mapped to repository evidence;
- any prompt that distinguishes attested facts from hypotheses before that rule
  is documented or mapped to existing proof fields;
- any prompt that emits "ready", "needs audit" or publication-like states before
  the status mapping is clarified;
- any prompt that would access active journal content, data/local_files, old PDF,
  archives RUN, real project entries or source discovery;
- any prompt that would select candidates, launch RUN, apply JournalPatch,
  create XLSX/CSV or activate OpenAI runtime.

### Rules safe to carry into the first RoutingAgent prompt draft

These are safe only as future review constraints, not as a prompt body in this
Codex 023 audit:

- structured JSON output only;
- explicit input contract and expected output schema;
- no candidate selection;
- no RUN;
- no active journal write;
- no data/local_files access;
- no old PDF use;
- distinguish fiche pratique, fiche-cadre, fiche-famille,
  mecanisme-passerelle, alias/doublon and controle_perimetre using existing
  repository terms only;
- `type_unite_RUN` before any RUN-related decision;
- RUN possible does not imply fiche pratique ready.

Codex 023 does not create that prompt draft.
