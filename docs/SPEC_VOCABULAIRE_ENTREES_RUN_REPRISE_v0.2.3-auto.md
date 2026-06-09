# Entry RUN Reprise Vocabulary Specification v0.2.3-auto

Status: Codex 045 docs/tests-only vocabulary alignment specification.

This document records the minimal vocabulary needed before any future
implementation around entry state, pre-RUN unit type, review/reprise posture
and safe alignment with future documentary fiches. It is documentation/tests
only. It does not implement runtime behavior, does not add fields, does not add
enums, does not process data and does not launch any RUN.

Codex 045 is vocabulary alignment, not runtime implementation.

## 1. Purpose

This is Codex 045.

Codex 045 is docs/tests-only. Its purpose is to align vocabulary around:

- the current entry-centered repository;
- `type_unite_RUN` as pre-RUN framing;
- review and reprise posture vocabulary;
- safe future alignment with documentary fiches.

This specification is not a runtime implementation, not a new fiche lifecycle,
not categorization and not a RUN mission.

## 2. Baseline after Codex 044

Baseline before Codex 045:

```text
Codex 001 to Codex 044 are merged into main.
Main before Codex 045 has 628 tests passing, user-reported after PR #45 merge.
Codex 044 / PR #45 added SPEC_ALIGNEMENT_ENTREES_FICHES_v0.2.3-auto.md.
The repository remains centered on id_entree_original.
There is no autonomous Fiche entity.
There is no id_fiche.
There is no fiche_id runtime field.
There is no type_fiche runtime field or enum.
There is no full fiche lifecycle implementation.
Coach-loop workflow tooling is frozen and remains workflow-only.
```

`id_entree_original` remains the runtime anchor. Codex 045 does not deprecate
it and does not introduce a competing fiche identifier.

## 3. Relation to SPEC_ALIGNEMENT_ENTREES_FICHES

Codex 045 depends on Codex 044 and on
`SPEC_ALIGNEMENT_ENTREES_FICHES_v0.2.3-auto.md`.

Codex 045 must not loosen Codex 044 boundaries. The future documentary fiche
doctrine remains future-only unless a later mission explicitly approves runtime
work.

Future `type_fiche` remains future-only. Future `type_fiche` must be mapped to
`type_unite_RUN` before any field, enum, runtime contract or schema value is
added.

## 4. Existing vocabulary map

| Vocabulary | Current role | Current evidence level | Future interpretation | Code now? |
|---|---|---|---|---|
| `id_entree_original` | Current runtime anchor for entry-centered objects. | Existing runtime field in contracts/models and tests. | Bridge between current entry work and any later fiche identity design. | Existing only; unchanged. |
| `titre_original_exact` | Current exact original title carried with entry objects. | Existing runtime field in contracts/models and tests. | Human-readable anchor for future mapping and review. | Existing only; unchanged. |
| `type_unite_RUN` | Required pre-RUN unit framing. | Existing runtime field and protocol term. | Mapping source for any later `type_fiche`. | Existing only; unchanged. |
| `fiche_pratique` | Existing `type_unite_RUN` value. | Existing runtime enum value and protocol term. | Possible future documentary fiche type after mapping, not automatically ready when RUN is possible. | Existing only; unchanged. |
| `fiche_cadre` | Existing `type_unite_RUN` value for a structuring frame. | Existing runtime enum value and protocol term. | Documentary structuring frame, not a category. | Existing only; unchanged. |
| `fiche_famille` | Existing `type_unite_RUN` value for comparative grouping. | Existing runtime enum value and protocol term. | Documentary grouping that preserves variants or related objects, not vague uncertainty. | Existing only; unchanged. |
| `mecanisme_passerelle` | Existing `type_unite_RUN` and pre-RUN route for transversal mechanism/passerelle material. | Existing runtime enum value, protocol term and synthetic review vocabulary. | Descriptor/relation by default; autonomous mechanism fiche is exceptional and future-only. | Existing only; unchanged. |
| `alias_doublon` | Existing route for possible alias, doublon, variant or alternate angle review. | Existing runtime enum value and protocol term. | Relation/review signal, not automatic merge or deletion. | Existing only; unchanged. |
| `controle_perimetre` | Existing scope-control route. | Existing runtime enum value and protocol term. | Scope-control posture, not final exclusion and not a category. | Existing only; unchanged. |
| `a_verifier` | Existing uncertainty/review posture. | Existing runtime enum value and protocol/review vocabulary. | Review signal that may orient future reprise without becoming a broad category. | Existing only; unchanged. |
| `a_revoir` | Existing review/reprise vocabulary in docs and treatment status vocabulary, with accent/ASCII variants in human and runtime contexts. | Existing loose runtime/documentary vocabulary, not a full state machine. | Future oriented review posture after separate mapping. | No new enum or field. |
| `run_autorise` | Current RUN authorization boolean when routing decisions exist. | Present in current runtime model. | Guard for RUN posture; true does not mean fiche ready. | Existing only; unchanged. |
| `run_interdit_raison` | Current reasons explaining why RUN is not authorized. | Present in current runtime model and synthetic review vocabulary. | Future reprise/review reasons may align to it, but not as automatic RUN triggers. | Existing only; unchanged. |
| `DeltaRecord` | Current record for meaningful change tied to `id_entree_original`. | Existing runtime model and documentation precedent. | Precedent for a future changelog, not a full fiche changelog now. | Existing only; unchanged. |
| `JournalPatch` | Current proposal object boundary for journal changes. | Existing runtime model and guardrails. | Proposal boundary only; no automatic application. | Existing only; unchanged. |
| `type_fiche` | Absent from current runtime. | Future-only vocabulary from Codex 044 alignment. | Must be mapped to `type_unite_RUN` before any field or enum. | No. |
| `fiche_id` | Absent from current runtime. | Future-only identifier target from Codex 044 alignment. | Later identity/migration topic only. | No. |
| `categorization` | Explicitly out of scope for Codex 045. | Existing caution vocabulary in prior docs; not a Codex 045 action. | Much later, after base realization and separate approval. | No. |

## 5. type_unite_RUN boundary

`type_unite_RUN` is pre-RUN framing.

`type_unite_RUN` is not a final fiche type. It must not be replaced by
`type_fiche`.

Future `type_fiche` must be mapped to `type_unite_RUN` before any runtime
change. No `type_fiche` is added now. No `type_fiche` runtime field or enum is
added now.

## 6. RUN possible != fiche ready

RUN possible != fiche ready.

RUN possible does not mean `fiche_pratique` ready. RUN possible does not mean
fiche lifecycle complete. RUN possible does not mean categorization.

`type_unite_RUN` is required before a RUN posture. Codex 045 launches no RUN.

## 7. a_verifier, a_revoir and controle_perimetre

`a_verifier` is uncertainty/review posture.

`a_revoir` exists as review/reprise vocabulary, but it is not yet a full
runtime state machine. Future `a_revoir` should be oriented, but must not be
over-normalized now.

`controle_perimetre` is scope-control. It is a scope-control route, not final
exclusion and not a category.

Codex 045 does not add a new enum now.

## 8. Future reprise orientation

`raison_a_revoir` and `objectif_reprise` are future alignment concepts.

They remain docs-only in Codex 045. They are not runtime fields yet. They must
not trigger automatic RUN.

Future reprise orientation may clarify why a case needs review, such as scope,
source, alias, variant, mechanism, fiche-cadre or fiche-family review. That
future orientation requires a separate mapping/spec before any implementation.

## 9. Alias, variante, non-fiche and rattachement

Alias/doublon already exists as protocol vocabulary or alert.

`variante` must not be collapsed into `alias_doublon` by default. A variant can
need preservation, notes, a sous-piste or later documentary grouping without
becoming an automatic duplicate.

`non_fiche_rattachee` is future doctrine, not current runtime state.

No merge, delete, fusion, scission or fiche creation is authorized by Codex
045. No relation graph is added.

## 10. mecanisme_passerelle, fiche_cadre and fiche_famille

`mecanisme_passerelle` must not be erased or renamed abruptly.

Mechanism as descriptor/relation by default is future doctrine. An autonomous
mechanism fiche is exceptional and future-only.

`fiche_cadre` is a documentary structuring frame, not a category.

`fiche_famille` is useful documentary grouping, not vague uncertainty.

Codex 045 makes no runtime changes.

## 11. DeltaRecord and JournalPatch boundaries

`DeltaRecord` is precedent for future changelog, not current fiche changelog.
It is not a full fiche changelog.

`JournalPatch` is proposal boundary, not automatic application.

Codex 045 does not implement changelog. Codex 045 does not apply
`JournalPatch`. Codex 045 performs no JournalPatch application.

## 12. ASCII and accent vocabulary policy

Vocabulary may appear with accents in human docs and ASCII in runtime
contracts. Examples include human `a revoir` / `a_revoir` discussion and
runtime-safe ASCII names used by contracts.

Codex 045 must not normalize code values. Future normalization requires a
separate mapping/spec.

Codex 045 does not modify enums or runtime values now.

## 13. Out of scope

Out of scope for Codex 045:

- no `src/`;
- no `scripts/`;
- no `data/`;
- no `schemas/`;
- no runtime contracts;
- no `id_fiche`;
- no `fiche_id`;
- no `fiche_id` field;
- no `Fiche` model;
- no `type_fiche` runtime;
- no `type_fiche` runtime field or enum;
- no RUN;
- no journal write;
- no active journal read/write;
- no `JournalPatch` application;
- no data processing;
- no categorization;
- no source discovery;
- no candidate selection;
- no export;
- no XLSX/CSV modification;
- no XLSX/CSV export;
- no old PDF usage;
- no generated `.dicoimpro/runs/*` artifacts;
- no publication.

## 14. Minimal future sequence

Next possible work after Codex 045 may be docs-only mapping/type vocabulary or
docs-only `a_revoir` orientation.

Any runtime implementation requires separate approval.

`id_fiche` / `fiche_id` belongs later. Categorization belongs much later after
base realization.

## 15. Final verdict

GO for docs/tests vocabulary alignment.

NO-GO for runtime implementation, Fiche model, `id_fiche`, `fiche_id`,
`type_fiche` runtime, RUN, journal write, JournalPatch application and
categorization.

Codex 045 keeps `id_entree_original` as the runtime anchor and preserves Codex
044 boundaries.
