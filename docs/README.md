# Documentation active — dicoimpro v0.2.3-auto

Ce dossier contient les documents de conception et de pilotage pour la couche d'automatisation `v0.2.3-auto`.

## Hiérarchie active

En cas de contradiction, lire dans cet ordre :

```text
1. REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md
2. PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md
3. CONTRATS_JSON_v0.2.3-auto.md
4. STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md
5. SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md
6. FEUILLE_ROUTE_IMPLEMENTATION_SDK_v0.2.3-auto.md
7. AUDIT_CONCEPTION_AVANT_CODEX_v0.2.3-auto.md
8. CHECKLIST_VALIDATION_AVANT_CODEX_v0.2.3-auto.md
9. MISSIONS_CODEX_v0.2.3-auto.md
```

## Documents actifs

### `REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md`

Décisions stables, décisions provisoires, décisions rejetées.  
C'est le point d'entrée pour savoir ce qui est autorisé ou interdit.

### `PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md`

Plan général : doctrine, architecture, couches, agents/modules, workflow cible.

### `CONTRATS_JSON_v0.2.3-auto.md`

Contrats structurés attendus : `AgentTask`, `AgentResult`, `BatchState`, `JournalPatch`, etc.

### `STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md`

Stratégie de tests : tests unitaires, tests négatifs, golden set de prudence, fake adapter, reprise, exports.

### `SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md`

Spécification des adaptateurs : fake adapter, futur adaptateur OpenAI, registry, handoffs, traces.

### `FEUILLE_ROUTE_IMPLEMENTATION_SDK_v0.2.3-auto.md`

Phases de réalisation : contrats, fake adapter, dry-run, golden set, exports, adaptateur OpenAI.

### `AUDIT_CONCEPTION_AVANT_CODEX_v0.2.3-auto.md`

Audit de cohérence avant Codex. Contient les corrections à appliquer et le verdict Go/No-Go.

### `CHECKLIST_VALIDATION_AVANT_CODEX_v0.2.3-auto.md`

Checklist à vérifier avant toute délégation à Codex.

### `MISSIONS_CODEX_v0.2.3-auto.md`

Prompts de missions Codex bornées et testables.

## Document superseded

### `ARCHITECTURE_SDK_v0.2.3-auto.md`

Document exploratoire conservé comme trace. Ne pas l'utiliser comme référence principale.

## Règles non négociables

```text
- pas de RUN dans cette phase ;
- pas d'identification de candidats ;
- pas d'écriture directe dans le journal actif ;
- pas d'utilisation du PDF ancien par défaut ;
- pas d'appel OpenAI réel avant fake adapter + dry-run + golden set ;
- Codex ne modifie pas la doctrine ;
- JSON validé = vérité technique ;
- XLSX/CSV = vues lisibles ou opératoires.
```

## Prochaine étape recommandée

```text
Mission Codex 001 — Contrats Pydantic SDK
```

Mais uniquement après validation humaine rapide de :

```text
AUDIT_CONCEPTION_AVANT_CODEX_v0.2.3-auto.md
MISSIONS_CODEX_v0.2.3-auto.md
```
