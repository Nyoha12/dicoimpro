# Audit métier post-coach-loop v0.2.3-auto

## 1. Purpose

Codex 044 est un audit-only docs/tests, sans nouvelle couche workflow. Il ne
cree aucune nouvelle couche de workflow, n'implemente aucune categorisation et n'implemente aucune
reclassification.

L'objectif est une cartographie decision-oriented pour Codex 045 : etat des
sources/fichiers, journaux, schemas, categorisation et recategorisation apres
le gel du coach-loop.

## 2. Baseline after Codex 043

Etat attendu : Codex 001-043 sont fusionnes dans `main`. Etat rapporte par
l'utilisateur apres merge PR #43 : main a 620 tests passing.

Le coach-loop Codex 035-043 est gele comme workflow de developpement local
controle. Ce coach-loop n'est pas le moteur metier dicoimpro complet pour
constitution de base, categorisation, journal handling ou reclassification
controlee.

## 3. Scope and prohibitions

Scope Codex 044 : docs/tests only. Les modifications autorisees sont ce document
d'audit, son test documentaire, et la synchronisation documentaire si necessaire.

Prohibitions absolues confirmees :

- no RUN ;
- no journal write ;
- no JournalPatch creation or application ;
- no real data processing ;
- no source discovery activation ;
- no candidate selection ;
- no categorization execution ;
- no reclassification execution ;
- no export ;
- no XLSX/CSV modification ;
- no src/scripts modification ;
- no production behavior change.

Codex 044 ne modifie pas `src/**`, ne modifie pas `scripts/**`, ne lit pas le
contenu des XLSX/CSV comme donnees metier et ne promeut aucun ancien journal,
RUN archive ou artefact genere en source active.

## 4. Files inspected

Inspected read-only areas :

- `data_manifest.yaml` ;
- `docs/README.md` ;
- `docs/CONTRATS_JSON_v0.2.3-auto.md` ;
- `docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md` ;
- `docs/REGLES_VALIDATION_v0.2.3-auto.md` ;
- `docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md` ;
- `docs/REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md` ;
- coach-loop docs Codex 035-043 ;
- `src/dico_impro/models.py` ;
- `src/dico_impro/validators.py` ;
- `src/dico_impro/journal.py` ;
- `src/dico_impro/journal_reader.py` ;
- `src/dico_impro/orchestrator.py` ;
- `src/dico_impro/orchestration/*` ;
- `src/dico_impro/exports/json_exporter.py` ;
- `src/dico_impro/cli.py` ;
- tests covering manifest, journal reader, JournalPatch, validation rules,
  dry-run, exports and documentation sync.

Inspected file families by listing only, without treating real entries :

- `data/local_files/*` file names from manifest/listing ;
- `data/active_journal/.gitkeep` ;
- `data/active_sources/.gitkeep` ;
- `data/archives_non_actives/.gitkeep` ;
- `data/outputs/.gitkeep` ;
- `data/tmp/*` generated test artifacts ;
- `.dicoimpro/runs/*` generated coach-loop run artifacts.

Modified files are limited to this audit document, the documentary test, and
documentation sync files. Expected area not found: no tracked `schemas/`
directory was found in the repository file list.

## 5. Sources and files inventory

| Classification | Files or families | Evidence | Decision note |
| --- | --- | --- | --- |
| `source_active_permanente` | `PROTOCOLE_BASE_IMPROVISATION_v0.2.3 (1).md` | `data_manifest.yaml` status `protocol_active`, role `methodological_protocol`, required | Active methodological source, not a generated artifact. |
| `source_active_permanente` | `DICTIONNAIRE_DONNEES_IMPROVISATION_v0.2.3 (1).xlsx` | Manifest status `data_dictionary_active`, role `schema_and_columns_reference`, required | Active schema/columns reference; Codex 044 did not read or modify XLSX content. |
| `source_active_permanente` | `improvisation_musicale_base_collecte_001_300_ENRICHIE (1).xlsx` | Manifest status `base_001_300_active`, role `original_entries_base`, required | Active base reference; no real entry processing occurred. |
| `source_temporaire_de_pilotage` | `TRIAGE_STRUCTUREL_300_CONSERVATOIRE_v0.2.2.xlsx` | Manifest status `triage_conservatoire_temporaire`, role `non_validating_conservative_triage` | Temporary steering source, not validating authority. |
| `source_temporaire_de_pilotage` | `JOURN_PILOT_ACTIF_TEMP_v0.2.3_POST005_RUN002_026030_NON_SOURCE.xlsx` | Manifest status `active_temporary_steering_journal_readonly`, layer `steering_journal`, `may_be_written_directly_by_pipeline: false` | Active temporary read-only steering journal, not a source of documentary proof. |
| `archive` | `data/archives_non_actives/*` | Manifest `archives_non_actives.policy` says RUN archives document execution and do not replace active base/triage/protocol/journal/sources | RUN archives are not active sources by default. |
| `fichier_remplacé` | `JOURNAL_ENTREES_TRAITEES_v0.2.3_MAJ_MINI_RUN_004_CORRIGE_STRUCTURE (2) (1).xlsx` | Manifest `ignored_local_files` says old steering journal preserved locally and replaced by post-005 journal | Replaced journal; forbidden as current routing authority by default. |
| `fichier_remplacé` | `docs/ARCHITECTURE_SDK_v0.2.3-auto.md` | README marks it as document superseded | Conserved as historical trace, not active reference. |
| `interdit_par_défaut` | `Improvisation musicale mondiale.pdf` | Manifest status `legacy_optional_reference`, requires explicit activation, old reference not default/decisive | Old PDF not active by default. |
| `interdit_par_défaut` | XLSX/CSV modification paths | Project doctrine and Codex 044 scope | XLSX/CSV are not to be modified by this audit. |
| `artefact_généré` | `.dicoimpro/runs/*` | Coach-loop generated run artifacts, ignored locally | Not active sources, not committed, not promoted. |
| `artefact_généré` | `data/tmp/*`, `.codex_tmp*`, `.pytest_cache`, `__pycache__`, generated JSON outputs | Test/runtime artifact families | Not active sources by default. |
| `statut_ambigu` | `data/active_journal/.gitkeep`, `data/active_sources/.gitkeep` | Placeholders only; no active data file is proven by placeholder name | A file name or directory name alone is not proof of active status. |
| `statut_ambigu` | Any local file not covered by manifest or explicit documentation evidence | Manifest warns only `file_name + status + role + flags` is authority | Human decision required before promotion. |

Rules applied: a file name alone is not proof of active status; a RUN archive is
not an active source by default; a generated artifact is not an active source by
default; an old export, old PDF, old journal or old RUN file is not active by
default; unresolved status is `statut_ambigu`.

## 6. Sources/files verdict

Verdict: the repository contains manifest-backed active permanent sources and
temporary steering sources, but it also contains replaced, archived, generated
and ambiguous file families that must not be promoted by assumption.

Human decisions required before Codex 045 if any work touches real data:

- confirm whether the manifest remains the sole authority for active source
  status ;
- confirm that the temporary steering journal is still the intended read-only
  operational reference ;
- decide how to handle placeholder directories and any local files absent from
  the manifest ;
- reaffirm that RUN archives, generated artifacts, old exports, old PDF and old
  journals remain inactive unless explicitly activated.

Primary risks: silent source promotion, data contamination from old RUN/archive
files, and accidental use of a generated artifact as business evidence.

## 7. Journal inventory

Journal-like evidence found:

- `JOURN_PILOT_ACTIF_TEMP_v0.2.3_POST005_RUN002_026030_NON_SOURCE.xlsx`:
  manifest-declared active temporary steering journal, read-only, non-source,
  post-005/RUN_002 partial project state.
- Canonical manifest label:
  `JOURNAL_PILOTAGE_ACTIF_TEMP_v0.2.3_POST005_RUN002_026030_NON_SOURCE_DOC.xlsx`.
- `JOURNAL_ENTREES_TRAITEES_v0.2.3_MAJ_MINI_RUN_004_CORRIGE_STRUCTURE (2) (1).xlsx`:
  old steering journal preserved locally but replaced by the post-005 journal.
- `data/active_journal/.gitkeep`: placeholder only, not an active journal file.
- `.dicoimpro/runs/*`: coach-loop run artifacts, not journals.
- `data/archives_non_actives/*`: RUN archives, not current journals by default.

Code evidence:

- `src/dico_impro/journal_reader.py` can read XLSX journal records if invoked
  by CLI/tests, and validates post-005 guard conditions.
- `src/dico_impro/journal.py` validates proposed `JournalPatch` objects but
  does not write the active journal.
- Tests cover journal reader behavior through temporary synthetic workbooks and
  JournalPatch validation without writing real journals.

## 8. Journal verdict

journal_actif_identifié: yes

nom_du_journal_actif:
`JOURN_PILOT_ACTIF_TEMP_v0.2.3_POST005_RUN002_026030_NON_SOURCE.xlsx`

evidence:

- `data_manifest.yaml` status `active_temporary_steering_journal_readonly` ;
- manifest flags `may_be_written_directly_by_pipeline: false` and
  `publication_authority: false` ;
- `docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md` decision D-005 ;
- `tests/test_manifest.py` expectations for a single steering journal ;
- journal reader/post-005 guards in code and tests.

journaux_remplacés_ou_conservés:

- `JOURNAL_ENTREES_TRAITEES_v0.2.3_MAJ_MINI_RUN_004_CORRIGE_STRUCTURE (2) (1).xlsx`.

journaux_interdits_par_défaut:

- old MINI_RUN_004 journal ;
- any generated RUN/journal artifact ;
- `.dicoimpro/runs/*` ;
- `data/active_journal/.gitkeep` as a placeholder, not a file authority.

décision_humaine_requise: yes, before RUN, JournalPatch, journal write, or data
processing. The active temporary steering journal is identified for audit
purposes, but Codex 044 does not authorize operational journal use or mutation.

## 9. Schema inventory

| Schema area | Status | Evidence | Notes |
| --- | --- | --- | --- |
| raw entry | documented only / ambiguous | `CONTRATS_JSON` describes `EntryState`; active base XLSX exists | No standalone tracked schema file in `schemas/`; real entries not processed. |
| candidate entry | documented only / partial | Routing docs, `ExplicitScope`, dry-run task builder | Candidate selection is explicitly forbidden by default. |
| validated fiche | partial | `TypeUniteRun`, `StatutUniteClassable`, validation models | Models exist, but no full real-data fiche constitution engine. |
| category | partial | `TypeUniteRun`, `Indices`, validation docs | Some enums and validation guardrails exist; full taxonomy/rules incomplete. |
| source/proof | partial | `SourceAuditInput`, `ValidationReport`, rules V-S/V-I/V-C | Source proof validation is partial and deterministic, not full source audit. |
| validation status | implemented partially | `StatutTraitement`, `PublicationStatus`, `AuditStatus`, tests | Useful guards exist for validation/publication status. |
| journal patch | partial | `JournalPatch`, `JournalPatchEntry`, `validate_journal_patch`, tests | Proposal validation exists; application/write remains forbidden. |
| export | implemented for dry-run JSON only | `json_exporter.py`, export tests | XLSX/CSV export remains forbidden; JSON export is not publication. |

## 10. Categorization inventory

Category-like structures found:

- Unit type enum `TypeUniteRun`: `fiche_pratique`, `fiche_cadre`,
  `fiche_famille`, `mecanisme_passerelle`, `controle_perimetre`,
  `alias_doublon`.
- Classability/status enums: `StatutUniteClassable`, `StatutTraitement`,
  `DecisionPreRun`, `DecisionFinaleProvisoire`, `PublicationStatus`,
  `AuditStatus`.
- Quality/proof indices `D`, `S`, `I`, `C`, `E` in `Indices`.
- `ClassificationInput` and deterministic `validate_classification` guardrails.
- Documentation for routing, conservation, source audit, classification result,
  delta records and JournalPatch.

Categorization shape:

- flat enums are implemented for unit types and statuses ;
- hierarchy is not established as executable taxonomy ;
- multi-category assignment is not established as executable behavior ;
- category membership rules are partial and primarily guardrail-based ;
- source, validation status, unit type and family/technique concepts should not
  be conflated.

Tests found:

- `tests/test_validation_rules.py` covers S/I/C downgrade and publication
  guardrails ;
- `tests/test_manifest.py` covers manifest source/journal status ;
- `tests/test_cli_dry_run.py` and export tests cover fake/dry-run boundaries ;
- static routing prompt fixture tests cover documentary prompt-review outputs,
  not executable business categorization.

## 11. Categorization verdict

categorisation_implémentée: partial

éléments_implémentés:

- Pydantic models/enums for several status and unit-type categories ;
- `ClassificationInput`, `SourceAuditInput`, `ValidationReport` ;
- deterministic guardrail validation in `validate_classification` ;
- tests for selected S/I/C/D validation rules ;
- fake dry-run scaffolding that avoids real data processing.

éléments_documentés_seulement:

- full RoutingAgent/source audit/classification agent behavior ;
- complete `ClassificationResult` and business categorization workflow ;
- category philosophy across family, technique, source, validation and unit type ;
- RUN_002 delta/journal patch workflow as operational business process ;
- prompt drafts and static fixtures for future agent behavior.

éléments_manquants:

- executable categorization over real entries ;
- authoritative taxonomy file with flat/hierarchical/multi-category decision ;
- complete membership criteria for every category ;
- source discovery and source audit execution ;
- tests proving end-to-end business categorization on controlled real-like data ;
- human approval workflow for category assignment.

tests_existants:

- `tests/test_validation_rules.py` ;
- `tests/test_manifest.py` ;
- `tests/test_journal_patch.py` ;
- `tests/test_cli_dry_run.py` ;
- `tests/test_exports_json.py` ;
- routing static fixture tests under `tests/`.

risques:

- confusing validation indices with business categories ;
- category drift without explicit taxonomy ;
- hidden promotion of documentary prompt fixtures into runtime behavior ;
- false confidence from dry-run/fake tests that do not process real entries.

Conclusion: categorization is executable only as partial validation guardrails.
It is not a complete business categorization engine.

## 12. Reclassification / recategorization inventory

Evidence found:

- `DeltaRecord` model exists in `src/dico_impro/models.py`.
- `JournalPatch` and `JournalPatchEntry` models exist.
- `validate_journal_patch` checks proposal shape, duplicate IDs, mandatory
  fields and direct-write prohibition.
- `CONTRATS_JSON` documents `DeltaRecord`, `FinalProvisionalDecision`,
  `JournalPatch`, audit queues and agent contracts.
- `REGLES_VALIDATION` includes `V-DELTA-001` and JournalPatch-related doctrine.
- Tests validate DeltaRecord availability and JournalPatch proposals.

Evidence not found as executable mechanism:

- no implemented detector of old categories impacted by a new entry,
  perspective or rule ;
- no targeted reopening engine for affected entries only ;
- no categorical diff proposal engine ;
- no executable mandatory-justification workflow beyond model fields ;
- no preservation/application workflow for previous vs new category state ;
- no accepted/rejected/to-review lifecycle implementation for category changes ;
- no journalized category-change application ;
- no non-regression guardrails specific to recategorization ;
- no decision locks implementation ;
- no tests covering end-to-end recategorization.

Vocabulary alone was not treated as proof of implementation.

## 13. Reclassification / recategorization verdict

verdict: partiellement_documentée

Justification: reclassification concepts are documented and partially modeled
through `DeltaRecord`, `JournalPatch` and validation rules, but the repository
does not contain an executable controlled recategorization mechanism. The
necessary chain for an `implémentée` verdict is incomplete: impacted category
detection, targeted reopening, categorical diff proposal, lifecycle validation,
journalized application, non-regression guardrails and tests are not present as
an operational workflow.

Codex 045 should not assume reclassification exists. If Codex 045 touches this
area, it should first specify the minimal recategorization contract and tests, or
keep the scope documentary if journal/source decisions remain unsettled.

## 14. Existing guardrails

Coach-loop guardrails:

- local workflow runner is controlled and frozen after Codex 043 ;
- API requires explicit `--execute-api` through `coach_step.py` ;
- Codex remains manual handoff ;
- merge is never default and requires `--execute-merge`,
  `auto_after_verify`, verify gate success and PR runner boundary ;
- diagnostics are local-only ;
- unknown risk means `stop_human`.

Business/data guardrails:

- manifest authority for source status ;
- old PDF not default/decisive ;
- active temporary steering journal is read-only ;
- direct journal write is forbidden ;
- JournalPatch can be validated but not applied automatically ;
- dry-run uses explicit scope and fake adapters ;
- source discovery and candidate selection remain forbidden by default.

These workflow guardrails do not complete the business engine.

## 15. Gaps and risks

Critical gaps before real database constitution:

- source authority must be reaffirmed before any real processing ;
- journal operational status must be human-confirmed before RUN or JournalPatch ;
- no full executable categorization engine exists ;
- no executable controlled recategorization workflow exists ;
- no dedicated taxonomy source of truth is implemented ;
- no source discovery/candidate selection is authorized ;
- no XLSX/CSV export path is authorized for this block.

Risks:

- source status drift ;
- journal ambiguity at operation time ;
- category drift from partial guardrails ;
- silent reclassification without impact list ;
- data contamination from archives, generated files or old PDF ;
- treating coach-loop readiness as business-engine readiness.

## 16. Decision matrix for Codex 045

| Area | Current status | Evidence | Risk | Human decision required | Candidate Codex 045 action |
| --- | --- | --- | --- | --- | --- |
| Sources/files | Partial authority via manifest | Manifest statuses and roles | Archive/generated promotion | Yes if real data is touched | Create source-status confirmation doc/test, no RUN. |
| Active journal | Identified as temporary read-only for audit | Manifest, register D-005, tests | Operational ambiguity before writes | Yes before RUN/write/JournalPatch | Confirm journal policy or add read-only inventory test. |
| Schemas | Mixed partial/documented/missing | Models, docs, no `schemas/` dir | Contract drift | Yes for missing schema authority | Audit schema gap or define schema map only. |
| Categorization | Partial validation guardrails | Models, validators, tests | False completion assumption | Yes before implementation | Specify taxonomy/categorization contract, no real data. |
| Reclassification | `partiellement_documentée` | Delta/JournalPatch docs/models | Silent category changes | Yes | Draft recategorization contract/tests only. |
| Coach-loop | Frozen workflow tooling | Codex 035-043 docs/tests/scripts | Confused with business engine | No for local tooling use | Do not extend unless separately requested. |

## 17. Recommended next implementation sequence

Minimal next steps:

1. Confirm the active source/journal authority from `data_manifest.yaml` with a
   human decision record.
2. If journal/source status is still unsettled, keep Codex 045 as docs/tests
   audit or contract work only.
3. Define a minimal taxonomy/categorization contract before implementing any
   categorization execution.
4. Define a controlled recategorization contract before any JournalPatch or
   category-change application.
5. Only after explicit source/journal decisions, consider a harmless synthetic
   or fixture-only implementation step.

Do not propose RUN or data processing until journal/source status is clear.

## 18. Codex 045 candidate scope

Smallest safe Codex 045 candidate scope: docs/tests-only source and journal
authority confirmation, plus a schema/taxonomy decision record for future
categorization. This depends on the four verdicts:

- sources/files need human confirmation before real processing ;
- journal status is identified for audit but still requires human decision
  before operational writes or RUN ;
- categorization is partial ;
- reclassification is `partiellement_documentée`.

If the active journal or source authority is disputed or ambiguous at decision
time, Codex 045 must not be RUN/data-processing work.

## 19. Final guarantees

Codex 044 guarantees:

- no RUN performed ;
- no journal write ;
- no JournalPatch created or applied ;
- no real data processed ;
- no export produced ;
- no src/** modified ;
- no scripts/** modified ;
- no XLSX/CSV modified ;
- no categorization implemented ;
- no reclassification implemented ;
- no archive promoted to active source ;
- no old journal promoted to active journal ;
- no old PDF usage authorized ;
- no publication authorized ;
- no source discovery, candidate selection or dictionary entry processing
  authorized ;
- audit is a cartography for Codex 045.
