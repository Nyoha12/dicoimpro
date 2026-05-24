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
11. PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md
12. RULES_IMPLEMENTATION_AUDIT_v0.2.3-auto.md
13. PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md
14. AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md
15. ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md
16. ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md
17. prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md
18. ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md
19. ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES_v0.2.3-auto.md
20. ROUTING_AGENT_STATIC_FIXTURE_CHECKER_v0.2.3-auto.md
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

### `PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md`

Protocole documentaire de controle avant tout futur prompt reel : statuts,
revue humaine, stockage, versionnement et maintien de la desactivation runtime.

### `RULES_IMPLEMENTATION_AUDIT_v0.2.3-auto.md`

Audit Codex 023 audit-only : regles existantes vs couverture d'implementation
courante. Ne cree pas de doctrine, ne demarre pas la redaction de prompt et
n'active aucun comportement runtime.

### `PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md`

Clarification Codex 024 clarification-only des blockers pre-prompt issus de
l'audit Codex 023. Ne cree pas de doctrine nouvelle, ne demarre pas la redaction
de prompt et n'active aucun comportement runtime.

### `AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md`

Carte Codex 025 docs/tests-only des responsabilites entre niveaux de regles,
raisonnement agentique, architecture SDK et actions externes interdites par
defaut. Ne cree pas de prompt, ne demarre pas la redaction de prompt, ne cree
pas de contrat JSON final ni d'enum runtime et n'active aucun comportement
runtime.

### `ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md`

Specification Codex 026 docs/tests-only du perimetre fonctionnel pre-prompt du
futur RoutingAgent. Definit le routage/aiguillage conservateur, les entrees et
sorties conceptuelles, les sorties interdites, la posture RUN, les
recommandations relance/audit et la compatibilite avec le feedback
architecture. Ne cree pas de prompt reel, ne demarre pas la redaction de prompt,
ne cree pas de prompt draft, de prompt body, de contrat JSON final ni d'enum
runtime et n'active aucun comportement OpenAI/runtime.

### `ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md`

Checklist Codex 027 docs/tests-only de prompt-readiness avant le prompt draft
RoutingAgent desactive de Codex 028. Verifie les conditions pre-draft,
non-runtime, non-prompt, non-contract, pre-implementation. Codex 027 ne cree
pas de prompt reel, ne demarre pas la redaction de prompt, ne cree pas de
prompt draft, de prompt body, de contenu `docs/prompts/drafts`, de contrat JSON
final ni d'enum runtime et n'active aucun comportement OpenAI/runtime.

### `prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md`

Draft Codex 028 disabled documentation-only RoutingAgent prompt draft. Statut
`draft_documented`, activation_status `disabled`, non-runtime, non-consumed,
not approved for mock, runtime, CLI or real OpenAI. Ce draft n'est pas charge,
rendu ou consomme par le runtime, ne cree pas de prompt actif, ne cree pas
`prompts.py`, ne cree pas de contrat JSON final ni d'enum runtime et n'active
aucun comportement OpenAI/runtime.

### `ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md`

Review gate Codex 029 docs/tests-only du prompt draft RoutingAgent desactive de
Codex 028. Verifie la coherence documentaire du draft comme document desactive,
documentation-only, non-runtime, non-consuming, non-activation, non-approval,
pre-mock et pre-runtime. N'active pas le prompt, ne l'approuve pas pour mock,
runtime, CLI, OpenAI reel ou RUN, ne charge pas, ne rend pas et ne consomme pas
le prompt, ne cree pas `prompts.py`, de contrat JSON final ni d'enum runtime et
n'active aucun comportement OpenAI/runtime.

### `ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES_v0.2.3-auto.md`

Fixtures Codex 030 docs/tests-only de revue synthetique statique pour le
prompt draft RoutingAgent desactive. Ajoute des cas synthetiques
documentation/test-only, non-runtime, non-consuming, non-activation,
non-approval et mock-review-only au sens de revue statique sans execution du
prompt. N'active pas le prompt, ne l'approuve pas pour mock, runtime, CLI,
OpenAI reel ou RUN, ne charge pas, ne rend pas, n'execute pas et ne consomme
pas le prompt, ne cree pas `prompts.py`, de contrat JSON final ni d'enum
runtime et n'active aucun comportement OpenAI/runtime.

### `ROUTING_AGENT_STATIC_FIXTURE_CHECKER_v0.2.3-auto.md`

Checker Codex 031 docs/tests-only static non-LLM pour les fixtures
synthetiques du prompt draft RoutingAgent desactive. Ajoute un helper
test-only sous `tests/helpers` et des tests statiques de forme/couverture,
documentation/test-only, non-runtime, non-consuming, non-activation et
non-approval. N'active pas le prompt, ne l'approuve pas pour mock, runtime,
CLI, OpenAI reel ou RUN, ne charge pas, ne rend pas, n'execute pas et ne
consomme pas le prompt, ne cree pas `prompts.py`, de contrat JSON final ni
d'enum runtime et n'active aucun comportement OpenAI/runtime.

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
Codex 021 - sanitisation/refactor tests/docs des garde-fous CLI/runtime, sans nouvelle capacite fonctionnelle ni changement de comportement.
Codex 022 - protocole documentaire de controle pour future activation de prompts reels, sans creation de prompt ni activation OpenAI/runtime.
Codex 023 - audit-only des regles existantes vs couverture d'implementation courante, sans nouvelle doctrine, sans prompt reel, sans redaction de prompt commencee ni activation OpenAI/runtime.
Codex 024 - clarification-only des blockers pre-prompt issus de Codex 023, sans doctrine nouvelle, sans prompt reel, sans redaction de prompt commencee ni activation OpenAI/runtime.
Codex 025 - docs/tests-only responsibility mapping des niveaux de regles, agents, architecture SDK et actions externes interdites par defaut, sans prompt reel, sans redaction de prompt commencee, sans contrat JSON final ni enum runtime et sans activation OpenAI/runtime.
Codex 026 - docs/tests-only RoutingAgent functional spec pre-prompt du routage/aiguillage conservateur, sans prompt reel, sans redaction de prompt commencee, sans prompt draft, sans prompt body, sans contrat JSON final ni enum runtime et sans activation OpenAI/runtime.
Codex 027 - docs/tests-only RoutingAgent prompt-readiness checklist pre-draft du futur prompt draft desactive, sans prompt reel, sans redaction de prompt commencee, sans prompt draft, sans prompt body, sans contenu docs/prompts/drafts, sans contrat JSON final ni enum runtime et sans activation OpenAI/runtime.
Codex 028 - disabled documentation-only RoutingAgent prompt draft `draft_documented` et desactive, sous docs/prompts/drafts, non-runtime, non-consumed, sans prompt actif, sans runtime loading, sans prompts.py, sans contrat JSON final ni enum runtime et sans activation OpenAI/runtime.
Codex 029 - docs/tests-only RoutingAgent prompt draft review gate, documentation-only, non-runtime, non-consuming, non-activation, non-approval, pre-mock et pre-runtime, sans activation, approbation, chargement, rendu ou consommation du prompt, sans prompts.py, sans contrat JSON final ni enum runtime et sans activation OpenAI/runtime.
Codex 030 - docs/tests-only synthetic review fixtures for the disabled RoutingAgent prompt draft, documentation/test-only, non-runtime, non-consuming, non-activation, non-approval and mock-review-only as static synthetic review, without prompt activation, mock execution approval, runtime approval, loading, rendering, execution or consumption, without prompts.py, final JSON contracts, runtime enums or OpenAI/runtime activation.
Codex 031 - docs/tests-only static non-LLM fixture checker for the synthetic review fixtures of the disabled RoutingAgent prompt draft, documentation/test-only, test-only, non-runtime, non-consuming, non-activation, non-approval and fixture-shape/guardrail-only, without prompt activation, mock execution approval, runtime approval, CLI consumption, OpenAI approval, RUN approval, prompt loading, rendering, execution or consumption, without prompts.py, production code, final JSON contracts, runtime enums, real agents, OpenAI/network calls, active journal mutation or behavior change.
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
