# Entry / Fiche Alignment Specification v0.2.3-auto

Status: Codex 044 docs/tests-only alignment specification.

This document aligns the current entry-centered repository vocabulary with the
future doctrine of documentary fiches. It is documentation/tests only. It does
not implement the fiche lifecycle, does not introduce `id_fiche`, does not
introduce `fiche_id` as a field, does not create a `Fiche` model, and does not
change runtime behavior. It adds no src runtime behavior change.

For explicit scope synchronization: Codex 044 does not modify `src/`.
Codex 044 does not modify `scripts/`. Codex 044 does not implement the fiche lifecycle.
Codex 044 does not change runtime behavior. Codex 044 creates no
Fiche model.

## 1. Purpose

The purpose is to make the boundary explicit between:

- the current repository implementation centered on `id_entree_original`;
- the existing v0.2.3 vocabulary around `type_unite_RUN`;
- the future documentary doctrine of fiches, fiche identifiers and fiche
  lifecycle.

This specification is a minimal alignment document. It prevents premature
implementation by recording which terms are current implementation, which terms
are doctrine, and which terms are future targets only.

## 2. Baseline and non-implementation scope

Baseline for Codex 044:

```text
Codex 001 to Codex 043 are expected merged into main.
User-reported main after PR #43 has 620 tests passing.
Coach-loop workflow tooling is frozen and ready for controlled local usage.
The repository is currently centered on id_entree_original.
There is no autonomous Fiche entity yet.
There is no id_fiche yet.
There is no full fiche lifecycle implementation yet.
```

Codex 044 scope is docs/tests only. It must not and does not:

- modify `src/`;
- modify `scripts/`;
- modify `data/`;
- modify runtime schemas or runtime contracts;
- process data;
- launch RUN;
- write the active journal;
- apply JournalPatch;
- write RUN artifacts;
- introduce categorization;
- add `id_fiche`;
- add `fiche_id` as a code field;
- add a `Fiche` model.

## 3. Existing protocol v0.2.3 authority

The protocol v0.2.3 doctrine remains the authority for existing documentary
terms. It already documents entry originals, `fiche_pratique`, `fiche_cadre`,
`fiche_famille`, `mecanisme_passerelle`, alias/doublon,
`controle_perimetre`, and `type_unite_RUN`.

This specification does not supersede that protocol. It aligns the repository
with the protocol vocabulary while preserving the current implementation
boundary. If a supplied lifecycle document such as
`alignement_cycle_de_vie_fiches_v_0_2_3_post_audit_codex.md` or
`protocole_cycle_de_vie_fiches_formalisations.md` is used later, it remains a
doctrinal appendix until a separate implementation mission is approved.

## 4. Current repo-centered-on-entry model

The current repository runtime and tests are organized around entries. Existing
objects such as `AgentTask`, `EntryState`, routing decisions, batch state,
evaluation records, `DeltaRecord` and `JournalPatchEntry` use
`id_entree_original` when they refer to project material.

`id_entree_original` remains the runtime anchor now. It is not deprecated by
this document. It is the stable bridge between current dry-run/mock-only
contracts and any future fiche lifecycle design.

There is no autonomous `Fiche` entity now. There is no `id_fiche` now. A future
`fiche_id` may become a target only after a dedicated lifecycle, migration and
schema decision.

## 5. Vocabulary alignment table

| Notion | Existing repo term | Current level | Doctrine retained | Integration stage | Code now? |
|---|---|---|---|---|---|
| entree originale | `id_entree_original`, `titre_original_exact` | Current entry anchor | The original entry remains the starting documentary input. | Current implementation | Yes, existing only |
| id_entree_original | `id_entree_original` | Runtime anchor | It remains the runtime anchor now. | Current implementation | Yes, unchanged |
| future fiche | final fiche is forbidden in current RoutingAgent docs | Future documentary entity | A fiche is a future documentary unit, not a current model. | Future lifecycle design | No |
| fiche_id | no current field; no `id_fiche` now | Absent | `fiche_id` is a future target, not an immediate code change. | Future migration only | No |
| type_unite_RUN | `type_unite_RUN` | Existing pre-RUN framing | Unit type must be explicit before any RUN posture. | Current vocabulary | Yes, existing only |
| future type_fiche | no current `type_fiche` field or enum | Future vocabulary | Must be mapped to `type_unite_RUN` before any field or enum is added. | Future mapping first | No |
| a_revoir | `a_verifier`, warnings, audit notes | Existing loose review posture | Should become oriented later, but must not be over-normalized now. | Future orientation design | No new code |
| objectif_reprise | no current field | Future review objective | Useful later to state why a case is reopened or repaired. | Future lifecycle design | No |
| alias | `alias_doublon`, `alerte_doublon` | Existing relation warning | Alias is a relation/review signal, not an automatic merge. | Current vocabulary, future refinement | Existing only |
| variante | `variantes_a_ne_pas_fusionner`, `sous_pistes` | Documented conservation signal | Variant material must not be collapsed into one fiche by default. | Current doctrine, future refinement | Existing only where already present |
| non_fiche_rattachee | no direct current field | Future relation vocabulary | A supporting non-fiche can be attached later without becoming a fiche. | Future doctrine only | No |
| controle_perimetre | `controle_perimetre`, `a_verifier` | Existing scope-control route | Scope control is not a final category or publication decision. | Current vocabulary | Yes, existing only |
| mecanisme_passerelle | `mecanisme_passerelle`, `alerte_passerelle` | Existing transversal route | Must not be erased or renamed abruptly. | Current vocabulary, future mapping | Existing only |
| fiche_cadre | `fiche_cadre` | Existing unit type | Documentary structuring frame, not a category. | Current vocabulary | Yes, existing only |
| fiche_famille | `fiche_famille` | Existing unit type | Useful documentary grouping, not vague uncertainty. | Current vocabulary | Yes, existing only |
| DeltaRecord | `DeltaRecord` | Existing precedent | Useful precedent for change trace, not a complete fiche changelog. | Current precedent, future changelog design | Existing only |
| JournalPatch | `JournalPatch` | Existing proposal object | Proposal boundary only; no automatic application. | Current boundary | Yes, existing only |
| categorization | routing/category wording in older docs | Out of scope now | Categorization is out of scope until the base is realized. | Later only | No |

## 6. type_unite_RUN vs future type_fiche

`type_unite_RUN` is the existing pre-RUN framing. It expresses the kind of unit
that would be considered before any RUN posture. It is not a complete future
fiche ontology.

Future `type_fiche` must be mapped to `type_unite_RUN` before any field, enum,
schema value or runtime contract is added. That mapping must answer at least:

- which existing `type_unite_RUN` values map directly;
- which values remain routing-only or scope-control-only;
- whether `mecanisme_passerelle` stays a relation/descriptor by default;
- how `fiche_cadre` and `fiche_famille` remain documentary structures rather
  than broad categories.

Codex 044 adds no `type_fiche` field or enum.

## 7. a_revoir and objective of reprise

The current repository already has loose review language such as `a_verifier`,
warnings, audit notes and review recommendations. That is enough for now.

Future doctrine may orient `a_revoir` with an `objectif_reprise`, meaning the
reason a case should be reopened or repaired. That future orientation should
help distinguish perimeter review, alias review, source review, variant review,
mechanism review and fiche-family review.

This must not be over-normalized now. Codex 044 adds no `a_revoir` enum, no
`objectif_reprise` field and no lifecycle state machine.

## 8. Alias / variante / non-fiche / controle_perimetre alignment

Alias and doublon remain review signals. They must not cause automatic merge,
delete, scission, journal write or RUN.

Variantes are related but distinct material that may need preservation. They
must not be collapsed into one `fiche_pratique` by default.

`non_fiche_rattachee` is future doctrine only. It can later describe material
that supports or relates to a fiche without becoming an autonomous fiche.

`controle_perimetre` remains the safe scope-control route for unclear or
possibly out-of-scope material. It is not a final category and does not produce
a final fiche.

## 9. Mecanisme / passerelle alignment

`mecanisme_passerelle` is already useful repository vocabulary. It must not be
erased or renamed abruptly.

In future doctrine, a mecanisme is a descriptor or relation by default. An
autonomous mechanism fiche is exceptional and later. It requires a separate
decision because it changes the boundary between a documentary fiche and a
cross-fiche relation.

Codex 044 adds no autonomous mechanism fiche behavior.

## 10. Fiche_cadre and fiche_famille alignment

`fiche_cadre` is a documentary structuring frame. It can hold a broad system,
tradition, methodological frame, repertoire or domain that organizes practices.
It is not a category label.

`fiche_famille` is a useful documentary grouping for related variants or
sub-objects that must not be flattened into one `fiche_pratique`. It is not a
vague uncertainty bucket.

Both terms remain current vocabulary, but Codex 044 does not turn them into a
fiche lifecycle.

## 11. DeltaRecord and future changelog boundary

`DeltaRecord` is a useful precedent because it traces significant changes tied
to `id_entree_original`. It is not a complete future fiche changelog.

A future fiche changelog would need explicit boundaries for fiche identity,
entry relationship, lifecycle transitions, human review, source changes and
JournalPatch proposals. Codex 044 does not implement that changelog.

JournalPatch remains a proposal boundary. It is not applied automatically and
Codex 044 does not add JournalPatch application.

## 12. Integration trajectory, explicitly non-binding

The following trajectory is non-binding and must not be read as an implementation
plan:

1. Document a mapping from future `type_fiche` to existing `type_unite_RUN`.
2. Document a future fiche lifecycle boundary.
3. Decide whether `fiche_id` is the accepted identifier name and how it relates
   to `id_entree_original`.
4. Define migration and changelog rules before any runtime field exists.
5. Only then consider schema or runtime changes in a separate Codex.

No step above is authorized by Codex 044.

## 13. Out-of-scope list

Out of scope for Codex 044:

- fiche lifecycle implementation;
- `id_fiche`;
- `fiche_id` as code field;
- `Fiche` model;
- runtime `src/` behavior;
- scripts changes;
- runtime schema changes;
- data processing;
- RUN;
- active journal read/write;
- JournalPatch application;
- categorization;
- source discovery;
- candidate selection;
- XLSX/CSV modification or export;
- generated `.dicoimpro/runs/*` artifacts;
- any active journal artifact.

## 14. Minimal future Codex candidates

Possible future Codex candidates, all requiring separate approval:

- docs-only mapping from `type_fiche` to `type_unite_RUN`;
- docs-only fiche lifecycle glossary;
- docs-only `a_revoir` / `objectif_reprise` orientation matrix;
- docs-only DeltaRecord vs fiche changelog boundary;
- later schema proposal for fiche identity after the mapping exists;
- later runtime implementation after the schema proposal is accepted.

These are candidates only. They do not authorize implementation now.

## 15. Final verdict

GO for docs/tests alignment.

NO-GO for fiche lifecycle implementation, `id_fiche`, runtime `fiche_id`,
`Fiche` model, runtime changes, script changes, data processing, RUN, journal
write, JournalPatch application and categorization.

`id_entree_original` remains the runtime anchor now. `fiche_id` is a future
target only. Future `type_fiche` must be mapped to `type_unite_RUN` before any
field or enum is added.
