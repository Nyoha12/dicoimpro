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
10. REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md
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

### `REVUE_ARCHITECTURE_POST_015_v0.2.3-auto.md`

Revue documentaire post-Codex 015 : état courant, garde-fous, risques et conditions
avant tout futur travail OpenAI réel ou prompt réel.

## Document superseded

### `ARCHITECTURE_SDK_v0.2.3-auto.md`

Document exploratoire conservé comme trace. Ne pas l'utiliser comme référence principale.

## Etat courant

```text
Codex 001 - contrats Pydantic SDK : AgentTask, AgentResult, BatchState, BatchReport et garde-fous de base.
Codex 002 - registry, fake adapter et quality gates locaux, sans appel OpenAI.
Codex 003 - dry-run en memoire sur ExplicitScope uniquement.
Codex 004 - exports JSON deterministes du resultat de dry-run.
Codex 005 - CLI dry-run plan-batch avec ecriture des exports JSON.
Codex 006 - golden set de prudence et scenarios d'erreur conservateurs.
Codex 007 - evaluation records par tache/resultat et validation minimale des payloads avant futur adaptateur OpenAI.
Codex 008 - payload validation bloquante integree aux quality gates.
Codex 009 - trace metadata deterministe par tache/resultat.
Codex 010 - squelette OpenAIAdapter desactive par defaut, mock-only, sans appel OpenAI/reseau reel.
Codex 011 - wrapper local d'execution agent avec payload validation, quality gates, trace metadata et AgentEvaluationRecord, sans appel OpenAI/reseau reel.
Codex 012 - planification batch mock-only via OpenAIAdapter injecte et wrapper d'execution, sans CLI ni appel OpenAI/reseau reel.
Codex 013 - construction partagee BatchState/BatchReport pour dry-run et planification OpenAI mock-only, sans changement de comportement.
Codex 014 - contrat strict OpenAIClientResponse pour clients mock injectes, sans appel OpenAI/reseau reel ni champs prompt/modele/API.
Codex 015 - contrat strict PromptPackage metadata-only pour futurs packages prompts, desactive par defaut, sans prompt reel/rendu/chargement ni appel OpenAI/reseau.
Codex 016 - revue architecture post-015 documentation-only, sans changement de code ni activation OpenAI/prompt/source/RUN.
Codex 017 - fixtures PromptPackage metadata-only desactivees pour tests, sans prompt reel/rendu/chargement ni activation OpenAI/prompt.
Codex 018 - controles de synchronisation documentation/tests, sans changement de comportement ni activation OpenAI/prompt/source/RUN.
Codex 019 - smoke test CLI dry-run fake-only end-to-end, sans prompt reel, OpenAI/reseau reel, data/local_files, journal actif, RUN, XLSX/CSV ni selection de candidats.
Codex 020 - tests de garde-fous runtime pour les chemins autorises fake-only/mock-only, sans integration interdite ni donnees projet.
```

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
