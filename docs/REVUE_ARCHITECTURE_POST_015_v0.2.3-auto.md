# Revue architecture post-015 — dicoimpro v0.2.3-auto

Statut : revue documentaire post-Codex 015, synchronisee apres Codex 041.
Objet : consolider l'état courant, les garde-fous, les risques et les conditions
obligatoires avant tout futur travail sur un appel OpenAI reel ou sur des prompts actifs.

Cette revue ne change aucun comportement de production. Elle ne cree aucun prompt actif,
ne charge aucun prompt, ne rend aucun prompt et n'active aucun acces modele ou reseau.
Elle n'autorise aucun Codex SDK, aucun Codex CLI, aucune execution Codex,
aucune boucle autonome et aucune execution de prompt.

---

## 1. Etat d'implémentation courant

Etat attendu au moment de cette revue :

```text
Codex 001 a Codex 040 sont fusionnes dans main avant Codex 041.
pytest passe.
Etat courant de main avant Codex 019 : 252 tests passing.
Etat courant apres Codex 019 : 253 tests passing.
Etat courant de main avant Codex 020 : 253 tests passing.
Etat courant apres Codex 020 : 258 tests passing.
Etat courant apres Codex 021 : 258 tests passing (refactor tests/docs uniquement).
Etat courant apres Codex 022 : 258 tests passing (protocole documentaire uniquement).
Etat courant de main avant Codex 023 : 264 tests passing.
Etat courant apres Codex 023 : 270 tests passing (audit-only docs/tests uniquement).
Etat courant de main avant Codex 024 : 270 tests passing.
Etat courant apres Codex 024 : 278 tests passing (clarification-only docs/tests uniquement).
Etat courant de main avant Codex 025 : 278 tests passing.
Etat courant apres Codex 025 : 289 tests passing (docs/tests-only responsibility mapping).
Etat courant de main avant Codex 026 : 289 tests passing.
Etat courant apres Codex 026 : 302 tests passing (docs/tests-only RoutingAgent functional spec).
Etat courant de main avant Codex 027 : 302 tests passing.
Etat courant apres Codex 027 : 315 tests passing (docs/tests-only RoutingAgent prompt-readiness checklist).
Etat courant de main avant Codex 028 : 315 tests passing.
Etat courant apres Codex 028 : 331 tests passing (docs/tests-only disabled RoutingAgent prompt draft).
Etat courant de main avant Codex 029 : 331 tests passing.
Etat courant apres Codex 029 : 349 tests passing (docs/tests-only RoutingAgent prompt draft review gate).
Etat courant de main avant Codex 030 : 349 tests passing.
Etat courant apres Codex 030 : 362 tests passing (docs/tests-only synthetic review fixtures for the disabled RoutingAgent prompt draft).
Etat courant de main avant Codex 031 : 362 tests passing.
Etat courant apres Codex 031 : 383 tests passing (docs/tests-only static non-LLM fixture checker).
Etat courant de main avant Codex 032 : 383 tests passing.
Etat courant apres Codex 032 : 408 tests passing (docs/tests-only static expected-output evaluator).
Etat courant de main avant Codex 033 : 408 tests passing.
Etat courant apres Codex 033 : 445 tests passing (docs/tests-only static candidate-output comparator).
Etat courant de main avant Codex 034 : 445 tests passing.
Etat courant apres Codex 034 : 466 tests passing (docs/tests-only disabled prompt draft access boundary).
Etat courant de main avant Codex 035 : 466 tests passing.
Etat courant apres Codex 035 : 478 tests passing (docs/tests/scaffold-only coach loop output architecture).
Etat courant de main avant Codex 036 : 478 tests passing.
Etat courant apres Codex 036 : 493 tests passing (docs/tests/scripts scaffold-only local coach context collector and state machine).
Etat courant de main avant Codex 037 : 493 tests passing.
Etat courant apres Codex 037 : 513 tests passing (docs/tests/scripts local GPT stage runner).
Etat courant de main avant Codex 038 : 513 tests passing.
Etat courant apres Codex 038 : 535 tests passing (docs/tests/scripts manual Codex handoff bridge).
Etat courant de main avant Codex 039 : 535 tests passing.
Etat courant apres Codex 039 : 555 tests passing (docs/tests/scripts autonomy policy and pre-merge verify gate).
Etat courant de main avant Codex 040 : 555 tests passing.
Etat courant apres Codex 040 : 576 tests passing (docs/tests/scripts guarded PR verification and optional auto-merge runner).
Etat courant de main avant Codex 041 : 576 tests passing.
Le dry-run CLI manuel post-015 a été validé par l'utilisateur.
Les fixtures PromptPackage metadata-only sont présentes et désactivées.
Codex 019 ajoute le smoke test CLI dry-run fake-only end-to-end.
Codex 020 ajoute les tests de garde-fous runtime fake-only/mock-only.
Codex 021 sanitise/refactore uniquement les tests/docs de garde-fous CLI/runtime.
Codex 022 ajoute le protocole documentaire de controle pour future activation de prompts reels, sans creation de prompt.
Codex 023 ajoute un audit-only des regles existantes vs couverture d'implementation courante, sans nouvelle doctrine ni activation runtime.
Codex 024 ajoute une clarification-only des blockers pre-prompt issus de Codex 023, sans doctrine nouvelle ni activation runtime.
Codex 025 ajoute une responsibility map docs/tests-only des niveaux de regles, agents, architecture SDK et actions externes interdites par defaut, sans prompt ni contrat runtime.
Codex 026 ajoute une functional spec docs/tests-only du futur RoutingAgent, pre-prompt et non-runtime, sans prompt ni contrat runtime.
Codex 027 ajoute une prompt-readiness checklist docs/tests-only du futur prompt draft RoutingAgent desactive, pre-draft et non-runtime, sans prompt ni contrat runtime.
Codex 028 ajoute un disabled documentation-only RoutingAgent prompt draft, draft_documented, desactive, non-runtime et non-consumed, sans prompt actif ni contrat runtime.
Codex 029 ajoute un review gate docs/tests-only du RoutingAgent prompt draft desactive, documentation-only, non-runtime, non-consuming, non-activation, non-approval, pre-mock et pre-runtime, sans activation ni consommation du prompt.
Codex 030 ajoute des synthetic review fixtures docs/tests-only pour le RoutingAgent prompt draft desactive, documentation/test-only, non-runtime, non-consuming, non-activation, non-approval et mock-review-only au sens de revue statique, sans activation, approbation, chargement, rendu, execution ou consommation du prompt.
Codex 031 ajoute un static non-LLM fixture checker docs/tests-only pour les fixtures synthetiques du prompt draft RoutingAgent desactive, documentation/test-only, test-only, non-runtime, non-consuming, non-activation, non-approval et fixture-shape/guardrail-only, sans activation, approbation mock, approbation runtime, consommation CLI, approbation OpenAI/RUN, chargement, rendu, execution ou consommation du prompt.
Codex 032 ajoute un static expected-output evaluator docs/tests-only pour les cas synthetiques RoutingAgent, documentation/test-only, test-only, static, non-LLM, non-runtime, non-consuming, non-activation, non-approval et expected-output-fixture-only, sans activation, approbation mock, approbation runtime, consommation CLI, approbation OpenAI/RUN, chargement, rendu, execution ou consommation du prompt, sans scoring de sortie modele.
Codex 033 ajoute un static candidate-output comparator docs/tests-only pour les cas synthetiques RoutingAgent, documentation/test-only, test-only, static, non-LLM, deterministic fake candidate provider, non-runtime, non-consuming, non-activation, non-approval et candidate-output-comparator-only, sans activation, approbation mock, approbation runtime, consommation CLI, approbation OpenAI/RUN, chargement, rendu, execution ou consommation du prompt, sans scoring de sortie modele et sans presenter le fake provider comme comportement RoutingAgent.
Codex 034 ajoute un disabled prompt draft access boundary docs/tests-only pour le RoutingAgent prompt draft desactive, documentation/test-only, test-only, plain markdown inspection only, non-runtime, non-consuming, non-rendering, non-execution, non-activation, non-approval et non-LLM, sans activation, approbation mock, approbation runtime, consommation CLI, approbation OpenAI/RUN, chargement, rendu, execution ou consommation du prompt comme executable, sans scoring de sortie modele.
Codex 035 ajoute une architecture de sorties docs/tests/scaffold-only pour un futur coach loop local GPT-5.5 Thinking / Codex, avec guidance .dicoimpro, schema de sortie de stage, exemple d'etat workflow et documentation, sans API implementation, sans Codex SDK implementation, sans autonomous loop, sans activation/rendu/execution/consommation de prompt, sans RUN, sans journal/JournalPatch, sans donnees reelles, sans publication ni changement de comportement.
Codex 036 ajoute un scaffold docs/tests/scripts-only pour le collecteur local de contexte et la state machine transition_gate du futur coach loop GPT-5.5 Thinking / Codex, sans API calls, sans Codex SDK, sans Codex CLI, sans autonomous loop, sans prompt execution, sans RUN, sans journal/JournalPatch, sans real data, sans PR/merge automation, sans production code ni changement de comportement.
Codex 037 ajoute un runner local GPT-5.5 Thinking docs/tests/scripts pour le coach loop, avec preparation de prompt, API OpenAI Responses uniquement explicite via --execute-api et OPENAI_API_KEY, validation de stage note, extraction transition_gate/next_prompt et update d'etat local uniquement via transition_gate, sans appel API par defaut, sans OpenAI runtime dans l'application dicoimpro, sans Codex SDK/CLI, sans autonomous loop, sans RUN, sans journal/JournalPatch, sans real data, sans PR/merge automation dans les scripts, sans src runtime behavior change.
Codex 038 ajoute un manual Codex handoff bridge docs/tests/scripts pour le coach loop, avec packaging local de next_prompt/codex_prompt en handoff packets, archive de retours Codex fournis manuellement, validation PR/tests/diff-check/files/guardrail et extraction PR URL, sans Codex SDK/CLI, sans execution Codex depuis les scripts repository, sans OpenAI call, sans autonomous loop, sans PR/merge automation dans les scripts repository, sans RUN, sans journal/JournalPatch, sans real data, sans publication, sans src runtime behavior change.
Codex 039 ajoute une autonomy policy and pre-merge verify gate docs/tests/scripts pour le coach-loop program, avec modelisation stop_human, auto_local, auto_external_with_budget et auto_merge_after_verify, merge manual by default, decisions depuis supplied verification reports, sans real merge, sans GitHub API, sans git/gh execution, sans Codex SDK/CLI, sans autonomous full loop, sans RUN, sans journal/JournalPatch, sans real data, sans publication, sans src runtime behavior change.
Codex 040 ajoute un guarded PR verification and optional auto-merge runner docs/tests/scripts pour le coach-loop program, avec build de pre_merge_report depuis PR evidence, decision through autonomy policy et merge execution seulement avec --execute-merge plus auto_after_verify apres fresh verify gate et stable head SHA, sans OpenAI runtime dans l'application, sans Codex SDK/CLI, sans autonomous full loop, sans RUN, sans journal/JournalPatch, sans real data, sans publication, sans src runtime behavior change.
Codex 041 ajoute un semi-automatic coach-loop runner docs/tests/scripts, avec orchestration context collection, GPT stage execution through explicit coach_step boundary, transition_gate validation, bounded auto-reflection, Codex handoff, Codex return resume, PR verification et guarded merge delegation, sans Codex SDK/CLI, sans automatic Codex execution, sans unbounded autonomous loop, sans RUN, sans journal/JournalPatch, sans real data, sans publication, sans src runtime behavior change.
```

Résumé des couches déjà matérialisées :

```text
Codex 001 - contrats Pydantic SDK : AgentTask, AgentResult, BatchState, BatchReport et garde-fous de base.
Codex 002 - registry, fake adapter et quality gates locaux, sans appel OpenAI.
Codex 003 - dry-run en mémoire sur ExplicitScope uniquement.
Codex 004 - exports JSON déterministes du résultat de dry-run.
Codex 005 - CLI dry-run plan-batch avec écriture des exports JSON.
Codex 006 - golden set de prudence et scénarios d'erreur conservateurs.
Codex 007 - evaluation records par tâche/résultat et validation minimale des payloads avant futur adaptateur OpenAI.
Codex 008 - payload validation bloquante intégrée aux quality gates.
Codex 009 - trace metadata déterministe par tâche/résultat.
Codex 010 - squelette OpenAIAdapter désactivé par défaut, mock-only, sans appel OpenAI/réseau réel.
Codex 011 - wrapper local d'exécution agent avec payload validation, quality gates, trace metadata et AgentEvaluationRecord.
Codex 012 - planification batch mock-only via OpenAIAdapter injecté et wrapper d'exécution, sans CLI ni appel OpenAI/réseau réel.
Codex 013 - construction partagée BatchState/BatchReport pour dry-run et planification OpenAI mock-only, sans changement de comportement.
Codex 014 - contrat strict OpenAIClientResponse pour clients mock injectés, sans appel OpenAI/réseau réel ni champs prompt/modèle/API.
Codex 015 - contrat strict PromptPackage metadata-only pour futurs packages prompts, désactivé par défaut, sans prompt réel/rendu/chargement ni appel OpenAI/réseau.
Codex 016 - revue architecture post-015 documentation-only, sans changement de code ni activation OpenAI/prompt/source/RUN.
Codex 017 - fixtures PromptPackage metadata-only désactivées pour tests, sans prompt réel/rendu/chargement ni activation OpenAI/prompt.
Codex 018 - contrôles de synchronisation documentation/tests, sans changement de comportement ni activation OpenAI/prompt/source/RUN.
Codex 019 - smoke test CLI dry-run fake-only end-to-end, sans prompt réel, OpenAI/réseau réel, data/local_files, journal actif, RUN, XLSX/CSV ni sélection de candidats.
Codex 020 - tests de garde-fous runtime pour les chemins autorisés fake-only/mock-only, sans intégration interdite ni données projet.
Codex 021 - sanitisation/refactor tests/docs des garde-fous CLI/runtime, sans nouvelle capacité fonctionnelle ni changement de comportement.
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
Codex 032 - docs/tests-only static expected-output evaluator for the synthetic RoutingAgent review cases, documentation/test-only, test-only, static, non-LLM, non-runtime, non-consuming, non-activation, non-approval and expected-output-fixture-only, without prompt activation, mock execution approval, runtime approval, CLI consumption, OpenAI approval, RUN approval, prompt loading, rendering, execution or consumption, model output scoring, without prompts.py, production code, final JSON contracts, runtime enums, real agents, OpenAI/network calls, active journal mutation or behavior change.
Codex 033 - docs/tests-only static candidate-output comparator for the synthetic RoutingAgent review cases, documentation/test-only, test-only, static, non-LLM, deterministic fake candidate provider, non-runtime, non-consuming, non-activation, non-approval and candidate-output-comparator-only, without prompt activation, mock execution approval, runtime approval, CLI consumption, OpenAI approval, RUN approval, prompt loading, rendering, execution or consumption, model output scoring, without presenting the fake provider as RoutingAgent behavior, without prompts.py, production code, final JSON contracts, runtime enums, real agents, OpenAI/network calls, active journal mutation, real candidate selection or behavior change.
Codex 034 - docs/tests-only disabled prompt draft access boundary for the disabled RoutingAgent prompt draft, documentation/test-only, test-only, plain markdown inspection only, non-runtime, non-consuming, non-rendering, non-execution, non-activation, non-approval and non-LLM, without prompt activation, mock execution approval, runtime approval, CLI consumption, OpenAI approval, RUN approval, prompt loading, rendering, execution or consumption as an executable prompt, model output scoring, without prompts.py, production code, final JSON contracts, runtime enums, real agents, OpenAI/network calls, RUN launch, real candidate selection, real project data processing, active journal read/write, JournalPatch application, XLSX/CSV export, old PDF usage or behavior change.
Codex 035 - docs/tests/scaffold-only local GPT-5.5 Thinking / Codex coach loop output architecture, with .dicoimpro guidance, stage output schema, workflow state example and workflow documentation, without production code, API call implementation, Codex SDK implementation, autonomous loop, prompt activation/rendering/execution/consumption, OpenAI runtime activation, RUN, journal read/write, JournalPatch application, real data processing, publication, XLSX/CSV export, old PDF usage or behavior change.
Codex 036 - docs/tests/scripts scaffold-only local coach context collector and state machine, without API calls, Codex SDK, autonomous loop, prompt execution, RUN, journal, JournalPatch, real data, production code or behavior change.
Codex 037 - docs/tests/scripts local GPT-5.5 Thinking stage runner for coach loop, explicit API only, no API calls by default, no Codex SDK/CLI, no autonomous loop, no src runtime behavior change.
Codex 038 - docs/tests/scripts manual Codex handoff bridge for coach loop, packaging next_prompt/codex_prompt into handoff packets and archiving Codex returns, without Codex SDK/CLI, autonomous loop, repository-script PR/merge automation, RUN, journal, JournalPatch, real data, src runtime behavior change.
Codex 039 - docs/tests/scripts autonomy policy and pre-merge verify gate for the coach-loop program, with stop_human, auto_local, auto_external_with_budget and auto_merge_after_verify decision modeling, without real merge, GitHub API, git/gh execution, Codex SDK/CLI, autonomous full loop, RUN, journal, JournalPatch, real data or src runtime behavior change.
Codex 040 - docs/tests/scripts guarded PR verification and optional auto-merge runner for the coach-loop program, building pre_merge_report from PR evidence, deciding through autonomy policy and executing merge only with --execute-merge plus auto_after_verify, without OpenAI/GPT/Codex SDK/CLI, autonomous full loop, RUN, journal, JournalPatch, real data or src runtime behavior change.
Codex 041 - docs/tests/scripts semi-automatic coach-loop runner orchestrating context collection, GPT stage execution, transition_gate validation, bounded auto-reflection, Codex handoff, Codex return resume, PR verification and guarded merge delegation, without Codex SDK/CLI, automatic Codex execution, unbounded autonomous loop, RUN, journal, JournalPatch, real data or src runtime behavior change.
```

## 2. Statut du dry-run CLI manuel

Le dry-run CLI manuel post-015 est validé par l'utilisateur.

Chemin validé :

```text
scope JSON explicite
-> dico-impro plan-batch --dry-run
-> orchestration in-memory
-> FakeAgentAdapter
-> quality gates
-> BatchState / BatchReport
-> exports JSON uniquement
```

Garde-fous confirmés pour ce chemin :

```text
- dry-run obligatoire ;
- scope explicite uniquement ;
- aucun accès data/local_files ;
- aucune lecture ou écriture du journal actif ;
- aucun RUN ;
- aucune sélection de candidats ;
- aucun appel OpenAI réel ;
- aucun appel réseau ;
- aucune exportation XLSX/CSV.
```

## 3. Chemins actuellement autorisés

Les seuls chemins runtime autorises apres Codex 041 restent ceux de Codex 020, Codex 021 et Codex 022 :

```text
1. fake CLI dry-run ;
2. mock OpenAI planning via client injecté uniquement ;
3. validation metadata-only de PromptPackage.
```

Ces chemins restent locaux, deterministes, sans OpenAI reel, sans reseau, sans prompt actif,
sans source discovery et sans écriture dans le journal actif.

Codex 035, Codex 036, Codex 037, Codex 038, Codex 039, Codex 040 et Codex 041 ne modifient aucun chemin runtime autorise.
Le scaffold coach loop Codex 035 reste workflow architecture documentation/tests
only. Les scripts locaux Codex 036, Codex 037, Codex 038, Codex 039, Codex 040 et Codex 041 sont workflow tooling scripts
only. Aucun de ces scaffolds ne donne une autorisation runtime nouvelle.

Les scripts sous `scripts/` ajoutes par Codex 036 sont uniquement des utilitaires
locaux de scaffold workflow. Ils ne lancent pas OpenAI, Codex SDK, Codex CLI,
reseau, GitHub API, RUN, journal ou JournalPatch.

Le chemin local coach GPT API ajoute par Codex 037 est workflow tooling only. Il
peut appeler OpenAI uniquement par commande explicite `--execute-api` avec
`OPENAI_API_KEY`, hors runtime dicoimpro. OpenAI runtime dans l'application
dicoimpro reste interdit.

Le manual Codex handoff bridge ajoute par Codex 038 est workflow tooling only.
Repository scripts do not call Codex SDK/CLI. Repository scripts do not execute
Codex. Repository scripts do not create PRs or merge PRs. External Codex
finalization may create PRs only by explicit user workflow prompt and only
after checks pass. Merge remains human-controlled after GPT review.

Le verify gate Codex 039 est workflow tooling only. Auto-merge is now a policy
possibility, not an implemented merge action. Codex 039 only decides from
supplied verification reports. Il n'appelle pas GitHub API, gh, git, OpenAI,
GPT, Codex SDK ou Codex CLI, ne fait aucun real merge et ne cree aucune boucle
autonome complete.

scripts/coach_pr_verify.py is the only newly authorized real merge-capable workflow script.
`scripts/coach_pr_verify.py` is the only newly authorized real merge-capable workflow script
apres Codex 040. Il construit un pre_merge_report depuis PR evidence, appelle
la policy d'autonomie locale, et ne peut executer un merge que via flags
explicites, `merge_mode: auto_after_verify`, verify gate complet et head SHA
stable avec match-head-commit. External Codex implementing this repository
change must not merge PR #40.

coach_loop.py orchestre uniquement les workflow tools locaux.
`scripts/coach_loop.py` orchestre uniquement les workflow tools locaux apres
Codex 041. GPT calls are only delegated to coach_step.py with --execute-api.
Merge is only delegated to coach_pr_verify.py with --execute-merge and
auto_after_verify. Codex execution remains manual handoff.

## 4. Chemins actuellement interdits

Sont explicitement interdits dans l'état post-015 :

```text
- appel OpenAI réel ;
- appel réseau ;
- Codex SDK ;
- Codex CLI ;
- execution Codex depuis les scripts repository ;
- GitHub API ;
- git/gh execution hors boundary explicite `scripts/coach_pr_verify.py` ;
- real merge hors `scripts/coach_pr_verify.py --execute-merge` et verify gate complet ;
- rendu ou chargement de prompt ;
- execution ou consommation de prompt ;
- prompts.py ;
- SourceDiscoveryAgent ;
- RUN ;
- sélection de candidats ;
- écriture dans le journal actif ;
- accès data/local_files ;
- usage par défaut de l'ancien PDF ;
- export XLSX/CSV dans la couche d'automatisation ;
- application de JournalPatch.
- publication.
```

Ces interdictions s'appliquent aussi aux tests, scripts, fixtures et chemins CLI, sauf
autorisation explicite dans une mission future dédiée.

Le scaffold coach loop Codex 035, le scaffold context/state Codex 036, le
runner stage Codex 037, le handoff bridge Codex 038, le verify gate Codex 039, le PR verify runner Codex 040 et le loop runner Codex 041 ne les changent pas : ils n'autorisent pas OpenAI runtime
dans l'application dicoimpro, prompt activation/rendering/execution dans le
runtime dicoimpro, autonomous loop, unbounded autonomous loop, autonomous full loop, Codex SDK, Codex CLI, automatic Codex execution, execution Codex hors handoff manuel, GitHub API, git/gh execution hors boundary Codex 040, real merge hors boundary Codex 040, RUN, journal
read/write, JournalPatch, real data processing, publication, PR/merge
automation dans les scripts repository, XLSX/CSV export, old PDF usage ou
behavior change.

Codex 035 n'autorise pas OpenAI runtime. Codex 036 n'autorise pas OpenAI
runtime non plus. Codex 037 n'autorise pas OpenAI runtime dans l'application
dicoimpro. Codex 038 n'autorise pas OpenAI runtime, Codex SDK/CLI, execution
Codex, RUN, journal, JournalPatch, real data, publication ou PR/merge
automation dans les scripts repository. Codex 039 n'autorise pas OpenAI
runtime, GitHub API, gh, git, real merge, Codex SDK/CLI, autonomous full loop,
RUN, journal, JournalPatch, real data, publication ou src runtime behavior
change.

Codex 040 autorise uniquement `scripts/coach_pr_verify.py` comme workflow
script de verification PR et merge guarded. Ce script peut appeler localement
`gh` pour collecter PR metadata/checks/diff/files, peut appeler `gh pr merge`
seulement avec `--execute-merge`, `merge_mode: auto_after_verify`, verify gate
complet et stable head SHA, et peut appeler `git`/`pytest` seulement apres un
merge execute pour la validation post-merge. Cela n'autorise aucun push to main,
aucun tag/release, aucun destructive auto-repair, aucun GitHub API direct,
aucun OpenAI runtime inside dicoimpro application, aucun Codex SDK/CLI, aucun
autonomous full loop, aucun RUN, journal, JournalPatch, real data, publication
ou src runtime behavior change.

Codex 041 autorise uniquement `scripts/coach_loop.py` comme semi-automatic
coach-loop runner workflow tooling. `coach_loop.py` orchestre context
collection, GPT stage preparation/execution, transition_gate validation,
autonomy decisions, bounded auto-reflection, Codex handoff, Codex return
resume, PR verification et guarded merge delegation. GPT calls are only
delegated to coach_step.py with --execute-api. Merge is only delegated to
coach_pr_verify.py with --execute-merge and auto_after_verify. Codex execution
remains manual handoff. Cela n'autorise aucun Codex SDK/CLI, automatic Codex
execution, unbounded autonomous loop, RUN, journal, JournalPatch, real data,
publication ou src runtime behavior change.

## 5. Couches d'architecture

### Contracts

Les contrats Pydantic restent la frontière technique principale. Les objets structurés
validés sont la source de vérité technique pour les tâches, résultats, états de batch,
rapports et réponses client mock.

### Agent registry

Le registry contrôle la résolution des adaptateurs d'agents. Le chemin actif reste local
et fake pour le CLI. Il ne doit pas devenir un point d'activation implicite d'OpenAI.

### Adapters

Le FakeAgentAdapter est le seul adaptateur opérationnel pour le dry-run CLI. Le squelette
OpenAIAdapter reste désactivé par défaut et limité aux clients mock injectés dans les tests.

### Payload validation

La validation de payload bloque les charges incohérentes avant exécution. Elle doit rester
bloquante pour tout futur chemin OpenAI.

### Quality gates

Les quality gates matérialisent les refus conservateurs et les erreurs de protocole. Ils
restent obligatoires avant toute production d'état ou d'export.

### Trace metadata

Les métadonnées de trace sont déterministes et auditables. Elles doivent accompagner les
tâches, résultats et évaluations sans inclure de secret, prompt réel ou donnée source réelle.

### Execution wrapper

Le wrapper d'exécution local assemble validation de payload, adaptateur injecté, quality
gates, trace metadata et evaluation record. Il ne doit pas contourner les validations.

### Orchestration

L'orchestration actuelle travaille sur ExplicitScope ou sur planification mock-only
injectée. Elle ne découvre pas de sources, ne sélectionne pas de candidats et ne lance
aucun RUN.

### JSON export

Les exports JSON sont la seule sortie automatisée actuelle. Ils sont destinés à l'audit
technique du dry-run et ne valent pas publication projet.

### CLI

Le CLI expose le dry-run fake uniquement. Il ne doit pas exposer la planification OpenAI
mock-only, ni aucun futur chemin OpenAI réel, sans protocole d'activation explicite.

### PromptPackage metadata contract

PromptPackage est strictement metadata-only et disabled-only. Le contrat peut valider les
métadonnées d'un futur package, mais ne doit pas contenir, lire, charger ou rendre un corps
de prompt.

### PromptPackage test fixtures

Les fixtures PromptPackage de tests restent strictement metadata-only et disabled-only.
Elles ne contiennent aucun prompt reel, aucun champ prompt inline, aucun rendu de prompt
et aucun chargement de prompt hors lecture JSON de metadata par les tests.

### Prompt activation protocol

`PROMPT_ACTIVATION_PROTOCOL_v0.2.3-auto.md` definit le controle documentaire
pour de futurs prompts reels. Codex 022 n'ajoute aucun corps de prompt, ne charge
aucun prompt, ne rend aucun prompt, n'active pas OpenAI et ne change aucun chemin
runtime autorise.

### Rules implementation audit

`RULES_IMPLEMENTATION_AUDIT_v0.2.3-auto.md` audite les regles existantes vs
la couverture d'implementation courante. Codex 023 est audit-only : il ne cree
pas de doctrine, ne demarre pas la redaction de prompt, ne cree aucun prompt
reel, ne charge aucun prompt, ne rend aucun prompt, n'active pas OpenAI et ne
change aucun chemin runtime autorise.

### Pre-prompt blockers clarification

`PRE_PROMPT_BLOCKERS_CLARIFICATION_v0.2.3-auto.md` clarifie les blockers
pre-prompt identifies par l'audit Codex 023. Codex 024 est clarification-only :
il ne cree pas de doctrine nouvelle, ne demarre pas la redaction de prompt, ne
cree aucun prompt reel, ne charge aucun prompt, ne rend aucun prompt, n'active
pas OpenAI et ne change aucun chemin runtime autorise.

### Agent architecture responsibility map

`AGENT_ARCHITECTURE_RESPONSIBILITY_MAP_v0.2.3-auto.md` cartographie les
responsabilites entre finalite qualite de base, categorisation/labels de
qualite, processus agentique, regles par agent, architecture SDK et actions
externes interdites par defaut. Codex 025 est docs/tests-only : il ne cree pas
de prompt reel, ne demarre pas la redaction de prompt, ne cree pas de contrat
JSON final ni d'enum runtime, n'active pas OpenAI et ne change aucun chemin
runtime autorise.

### RoutingAgent functional spec

`ROUTING_AGENT_FUNCTIONAL_SPEC_v0.2.3-auto.md` definit le perimetre
fonctionnel pre-prompt du futur RoutingAgent : routage/aiguillage conservateur,
entrees et sorties conceptuelles, sorties interdites, categories de routage,
posture RUN, recommandations relance/audit et compatibilite avec les feedbacks
architecture. Codex 026 est docs/tests-only : il ne cree pas de prompt reel, ne
demarre pas la redaction de prompt, ne cree pas de prompt draft, de prompt body,
de contrat JSON final ni d'enum runtime, n'active pas OpenAI et ne change aucun
chemin runtime autorise.

### RoutingAgent prompt-readiness checklist

`ROUTING_AGENT_PROMPT_READINESS_CHECKLIST_v0.2.3-auto.md` verifie le dernier
gate documentaire avant un futur prompt draft RoutingAgent desactive. Codex 027
est docs/tests-only : il ne cree pas de prompt reel, ne demarre pas la
redaction de prompt, ne cree pas de prompt draft, de prompt body, de contenu
`docs/prompts/drafts`, de contrat JSON final ni d'enum runtime, n'active pas
OpenAI et ne change aucun chemin runtime autorise.

### RoutingAgent prompt draft

`docs/prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md` est le
disabled documentation-only RoutingAgent prompt draft de Codex 028. Son statut
est `draft_documented`, son activation_status est `disabled`, et il reste
non-runtime, non-consumed, not approved for mock, runtime, CLI or real OpenAI.
Il ne cree pas de prompt actif, ne charge pas de prompt, ne rend pas de prompt,
ne cree pas `prompts.py`, ne cree pas de contrat JSON final ni d'enum runtime,
n'active pas OpenAI et ne change aucun chemin runtime autorise.

### RoutingAgent prompt draft review gate

`ROUTING_AGENT_PROMPT_DRAFT_REVIEW_GATE_v0.2.3-auto.md` est le review gate
docs/tests-only de Codex 029 pour le disabled RoutingAgent prompt draft de
Codex 028. Il verifie la coherence documentaire du draft comme document
desactive et reste documentation-only, non-runtime, non-consuming,
non-activation, non-approval, pre-mock et pre-runtime. Il n'active pas le
prompt, ne l'approuve pas pour mock, runtime, CLI, OpenAI reel ou RUN, ne
charge pas, ne rend pas et ne consomme pas le prompt, ne cree pas `prompts.py`,
ne cree pas de contrat JSON final ni d'enum runtime, n'active pas OpenAI et ne
change aucun chemin runtime autorise.

### RoutingAgent synthetic review fixtures

`ROUTING_AGENT_SYNTHETIC_REVIEW_FIXTURES_v0.2.3-auto.md` documente les
fixtures Codex 030 docs/tests-only de revue synthetique statique pour le
disabled RoutingAgent prompt draft. Ces fixtures sont documentation/test-only,
non-runtime, non-consuming, non-activation, non-approval et mock-review-only au
sens de revue statique sans execution du prompt. Elles n'activent pas le
prompt, ne l'approuvent pas pour mock, runtime, CLI, OpenAI reel ou RUN, ne
chargent pas, ne rendent pas, n'executent pas et ne consomment pas le prompt,
ne creent pas `prompts.py`, ne creent pas de contrat JSON final ni d'enum
runtime, n'activent pas OpenAI et ne changent aucun chemin runtime autorise.

### RoutingAgent static fixture checker

`ROUTING_AGENT_STATIC_FIXTURE_CHECKER_v0.2.3-auto.md` documente le checker
Codex 031 docs/tests-only static non-LLM pour les fixtures synthetiques du
disabled RoutingAgent prompt draft. Le helper
`tests/helpers/routing_agent_static_fixture_checker.py` est test-only,
fixture-shape/guardrail-only, non-runtime, non-consuming, non-activation et
non-approval. Il ne doit pas etre importe depuis `src/`, utilise par le CLI,
`OpenAIAdapter`, mock planning ou runtime, ni transformer les fixtures en
contrats JSON finaux ou enums runtime. Il ne charge pas, ne rend pas, n'execute
pas et ne consomme pas le prompt, n'appelle pas OpenAI, n'appelle pas le
reseau, ne lance pas RUN, ne lit pas et n'ecrit pas le journal actif, n'applique
pas JournalPatch et ne change aucun chemin runtime autorise.

### RoutingAgent static expected-output evaluator

`ROUTING_AGENT_STATIC_EXPECTED_OUTPUT_EVALUATOR_v0.2.3-auto.md` documente
l'evaluateur Codex 032 docs/tests-only static expected-output evaluator pour
les cas synthetiques RoutingAgent de Codex 030. Le helper
`tests/helpers/routing_agent_static_expected_output_evaluator.py` est
test-only, static, non-LLM, expected-output-fixture-only, non-runtime,
non-consuming, non-activation et non-approval. Il charge uniquement les fixtures
JSON de tests, verifie les metadata, les flags negatifs, les case IDs, les
champs conceptuels autorises, les forbidden absences et les attentes
synthetiques faites main. Il ne genere pas de sortie, ne charge pas, ne rend
pas, n'execute pas et ne consomme pas le prompt, ne score pas de sortie modele,
n'appelle pas OpenAI, n'appelle pas le reseau, ne lance pas RUN, ne lit pas et
n'ecrit pas le journal actif, n'applique pas JournalPatch, ne cree pas de
contrat JSON final ni d'enum runtime et ne change aucun chemin runtime autorise.

### RoutingAgent static candidate-output comparator

`ROUTING_AGENT_STATIC_CANDIDATE_OUTPUT_COMPARATOR_v0.2.3-auto.md` documente
le comparator Codex 033 docs/tests-only static candidate-output comparator
pour les cas synthetiques RoutingAgent. Le helper
`tests/helpers/routing_agent_static_candidate_output_comparator.py` est
test-only, static, non-LLM, candidate-output-comparator-only, non-runtime,
non-consuming, non-activation et non-approval. Il charge uniquement les
fixtures JSON de tests, verifie les metadata, les flags negatifs, les case IDs,
les champs conceptuels autorises, les PASS/FAIL synthetiques et les diagnostics
attendus. Le deterministic fake candidate provider ne doit pas etre presente
comme comportement RoutingAgent : il retourne seulement des candidate outputs
synthetiques faits main. Le comparator ne genere pas de sortie modele, ne
charge pas, ne rend pas, n'execute pas et ne consomme pas le prompt, ne score
pas de sortie modele, n'appelle pas OpenAI, n'appelle pas le reseau, ne lance
pas RUN, ne lit pas et n'ecrit pas le journal actif, n'applique pas
JournalPatch, ne selectionne pas de candidats reels, ne cree pas de contrat
JSON final ni d'enum runtime et ne change aucun chemin runtime autorise.

### RoutingAgent disabled prompt draft access boundary

`ROUTING_AGENT_DISABLED_PROMPT_DRAFT_ACCESS_BOUNDARY_v0.2.3-auto.md`
documente le boundary Codex 034 docs/tests-only disabled prompt draft access
boundary pour le RoutingAgent prompt draft desactive. Le helper
`tests/helpers/routing_agent_disabled_prompt_draft_boundary_checker.py` est
test-only, standard-library-only, plain markdown inspection only, non-runtime,
non-consuming, non-rendering, non-execution, non-activation, non-approval et
non-LLM. Il lit le prompt draft desactive comme markdown de documentation en
tests, verifie les marqueurs disabled/status/denial, verifie l'absence de
langage positif d'approbation, verifie que `src/` ne reference pas le draft,
les fixtures ou les helpers statiques, et verifie que `src/` ne contient pas
de noms de chargement runtime de prompt. Il ne charge pas, ne rend pas,
n'execute pas et ne consomme pas le prompt comme executable, ne score pas de
sortie modele, n'appelle pas OpenAI, n'appelle pas le reseau, ne lance pas
RUN, ne traite pas de donnees projet reelles, ne lit pas et n'ecrit pas le
journal actif, n'applique pas JournalPatch, ne selectionne pas de candidats
reels, ne cree pas `prompts.py`, de contrat JSON final ni d'enum runtime et ne
change aucun chemin runtime autorise.

### Coach loop output architecture scaffold

`WORKFLOW_GPT_CODEX_COACH_LOOP_v0.2.3-auto.md` documente Codex 035 :
architecture docs/tests/scaffold-only des sorties pour un futur coach loop
local GPT-5.5 Thinking / Codex. Les fichiers `.dicoimpro/COACH_GUIDANCE.md`,
`.dicoimpro/STAGE_OUTPUT_SCHEMA.md`, `.dicoimpro/WORKFLOW_STATE.example.json`
et `.dicoimpro/runs/.gitkeep` servent uniquement de guidance, schema, exemple
d'etat et emplacement reserve.

Ce scaffold definit le role de GPT-5.5 Thinking comme coach/strategist, le role
de Codex comme executor, le role futur du script Python comme transport layer,
les stages, reflections ciblees, transition_gate, next_prompt et paquets de
contexte repo. Il ne cree aucun prompt actif, ne charge pas, ne rend pas,
n'execute pas et ne consomme pas de prompt, n'appelle pas OpenAI, n'utilise pas
Codex SDK, ne lance pas RUN, ne lit pas et n'ecrit pas le journal actif,
n'applique pas JournalPatch, ne traite pas de donnees reelles, ne publie pas,
n'exporte pas XLSX/CSV, n'utilise pas l'ancien PDF et ne change aucun chemin
runtime autorise.

### Coach context state machine scaffold

`WORKFLOW_COACH_CONTEXT_STATE_MACHINE_v0.2.3-auto.md` documente Codex 036 :
scaffold docs/tests/scripts-only pour transformer l'architecture de sorties
Codex 035 en fichiers locaux et utilitaires deterministes. `scripts/coach_state.py`
lit et valide l'etat workflow, initialise `.dicoimpro/WORKFLOW_STATE.local.json`,
cree des dossiers de run et applique transition_gate sans decider la maturite
arbitrairement. `scripts/coach_collect_context.py` collecte un contexte repo
local filtre dans `.dicoimpro/runs/<run_id>/00_context.md`.

Ces scripts sont des utilitaires locaux de scaffold workflow seulement. Ils
n'appellent pas OpenAI, Codex SDK, Codex CLI, reseau, GitHub API, pytest par
defaut, RUN, journal ou JournalPatch. Ils n'activent pas, ne rendent pas,
n'executent pas et ne consomment pas de prompt. Ils ne creent pas de boucle
autonome, n'automatisent pas les PR ou merges, ne traitent pas de donnees
reelles, ne selectionnent pas de candidats, n'exportent pas XLSX/CSV,
n'utilisent pas l'ancien PDF et ne changent aucun chemin runtime autorise.

### Coach GPT stage runner

`WORKFLOW_COACH_GPT_STAGE_RUNNER_v0.2.3-auto.md` documente Codex 037 : runner
local docs/tests/scripts pour un stage GPT-5.5 Thinking du futur coach loop.
`scripts/coach_step.py` prepare un prompt de stage depuis COACH_GUIDANCE,
STAGE_OUTPUT_SCHEMA, l'etat workflow, le paquet de contexte, une note
precedente optionnelle et une instruction optionnelle.

Le runner n'appelle jamais l'API par defaut. Le chemin API est explicite :
`--execute-api` et `OPENAI_API_KEY` sont obligatoires. L'import OpenAI SDK est
lazy/dynamic et intervient uniquement dans le chemin d'execution API. Les tests
n'appellent jamais l'API et ne requierent pas le package OpenAI.

Ce chemin local coach GPT API est workflow tooling only. Il n'est pas le runtime
applicatif dicoimpro, n'est pas une execution RoutingAgent, n'active aucun
prompt dans `src/`, ne rend pas et n'execute pas de prompt dans le runtime
dicoimpro. Il ne cree pas de Codex SDK/CLI integration, pas de boucle autonome,
pas de RUN, pas de lecture/ecriture journal actif, pas de JournalPatch, pas de
traitement de donnees reelles, pas de publication, pas d'export XLSX/CSV, pas
d'utilisation de l'ancien PDF, pas d'automatisation PR/merge dans les scripts
repository et aucun changement de comportement production.

### Coach Codex handoff bridge

`WORKFLOW_COACH_CODEX_HANDOFF_BRIDGE_v0.2.3-auto.md` documente Codex 038 :
manual Codex handoff bridge docs/tests/scripts pour le futur coach loop.
`scripts/coach_codex_handoff.py` lit une coach stage note locale, extrait
front matter, transition_gate, next_prompt et next_prompt_type, valide
l'eligibilite du handoff, construit un paquet markdown autonome pour collage
manuel dans Codex, archive un retour Codex fourni manuellement, valide ce
retour et extrait une PR URL si presente.

Ce bridge est workflow tooling only. Repository scripts do not call Codex
SDK/CLI, do not execute Codex, do not call OpenAI, do not call GPT, do not call
GitHub API, do not create PRs or merge PRs, and do not run an autonomous loop.
External Codex finalization may create PRs only by explicit user workflow
prompt after checks pass. Merge remains human-controlled after GPT review.

Ce bridge ne modifie aucun chemin runtime autorise, n'active aucun prompt dans
`src/`, ne rend pas et n'execute pas de prompt dans le runtime dicoimpro, ne
lance pas RUN, ne lit pas et n'ecrit pas le journal actif, n'applique pas
JournalPatch, ne traite pas de donnees reelles, ne publie pas, n'exporte pas
XLSX/CSV, n'utilise pas l'ancien PDF et ne change aucun comportement
production.

### Coach autonomy verify gate

`WORKFLOW_COACH_AUTONOMY_VERIFY_GATE_v0.2.3-auto.md` documente Codex 039 :
autonomy policy and pre-merge verify gate docs/tests/scripts pour le futur
coach-loop program. `.dicoimpro/WORKFLOW_AUTONOMY_POLICY.example.json` encode
les niveaux `stop_human`, `auto_local`, `auto_external_with_budget` et
`auto_merge_after_verify`. `scripts/coach_autonomy.py` valide cette policy,
decide l'autonomie d'un transition_gate, decide l'auto-reflection, evalue un
budget API fourni, valide un pre-merge report fourni et decide si auto-merge
serait allowed, blocked ou stop_human.

Auto-merge is now a policy possibility, not an implemented merge action. Merge
reste manual by default. Auto-merge serait possible uniquement avec
`merge_mode: auto_after_verify` et seulement apres verify gate complet. Codex
039 only decides from supplied verification reports.

Ce gate est workflow tooling only. Il n'appelle pas GitHub API, gh, git,
pytest, OpenAI, GPT, Codex SDK ou Codex CLI. Il ne fait aucun real merge, ne
push aucune branche, ne cree aucun commit depuis les scripts repository et ne
cree aucune autonomous full loop.

Ce gate ne modifie aucun chemin runtime autorise, n'active aucun prompt dans
`src/`, ne rend pas et n'execute pas de prompt dans le runtime dicoimpro, ne
lance pas RUN, ne lit pas et n'ecrit pas le journal actif, n'applique pas
JournalPatch, ne traite pas de donnees reelles, ne publie pas, n'exporte pas
XLSX/CSV, n'utilise pas l'ancien PDF et ne change aucun comportement
production.

### Coach PR verify merge runner

`WORKFLOW_COACH_PR_VERIFY_MERGE_RUNNER_v0.2.3-auto.md` documente Codex 040 :
guarded PR verification and optional auto-merge runner docs/tests/scripts pour
le coach-loop program. `scripts/coach_pr_verify.py` parse une PR URL, collecte
PR metadata, files, checks et diff via local `gh`, valide un Codex return
archive, construit un `pre_merge_report`, appelle `scripts/coach_autonomy.py`
pour decider, et ecrit les rapports locaux sous `.dicoimpro/runs/<run_id>/`.

scripts/coach_pr_verify.py is the only newly authorized real merge-capable workflow script.
`scripts/coach_pr_verify.py` is the only newly authorized real merge-capable workflow script.
Merge requires explicit flags and verify gate: `--execute-merge`,
`merge_mode: auto_after_verify`, decision allowed, autonomy level
`auto_merge_after_verify`, PR mergeable, stable head SHA and match-head-commit.
External Codex implementing this repository change must not merge PR #40.

Ce runner est workflow tooling only. Il n'appelle pas OpenAI, GPT, Codex SDK ou
Codex CLI, n'execute pas Codex, ne cree pas de boucle autonome complete et ne
modifie aucun chemin runtime autorise. Il n'active aucun prompt dans `src/`, ne
rend pas et n'execute pas de prompt dans le runtime dicoimpro, ne lance pas
RUN, ne lit pas et n'ecrit pas le journal actif, n'applique pas JournalPatch,
ne traite pas de donnees reelles, ne publie pas, n'exporte pas XLSX/CSV,
n'utilise pas l'ancien PDF et ne change aucun comportement production.

### Coach loop runner

`WORKFLOW_COACH_LOOP_RUNNER_v0.2.3-auto.md` documente Codex 041 :
semi-automatic coach-loop runner docs/tests/scripts pour le futur coach-loop
program. `scripts/coach_loop.py` orchestre les briques existantes : context
collection, GPT stage preparation/execution through explicit coach_step
boundary, transition_gate validation, autonomy decisions, bounded
auto-reflection, Codex handoff, Codex return resume, PR verification and
guarded merge delegation.

Ce runner est workflow tooling only. Il n'appelle pas OpenAI directement. GPT
calls are only delegated to coach_step.py with --execute-api. Il n'execute pas
Codex, n'appelle pas Codex SDK/CLI et ne cree aucune automatic Codex execution.
Codex execution remains manual handoff. Merge is only delegated to
coach_pr_verify.py with --execute-merge and auto_after_verify, and merge is
never default.

Ce runner ne modifie aucun chemin runtime autorise, n'active aucun prompt dans
`src/`, ne rend pas et n'execute pas de prompt dans le runtime dicoimpro, ne
lance pas RUN, ne lit pas et n'ecrit pas le journal actif, n'applique pas
JournalPatch, ne traite pas de donnees reelles, ne publie pas, n'exporte pas
XLSX/CSV, n'utilise pas l'ancien PDF et ne change aucun comportement
production.

## 6. Verdict Go/No-Go

```text
GO    - documentation et fixtures metadata désactivées ;
GO    - tests supplémentaires mock-only ;
NO-GO - OpenAI réel ;
NO-GO - prompt actif/consomme ;
NO-GO - Codex SDK ;
NO-GO - Codex CLI ;
NO-GO - execution Codex depuis les scripts repository ;
NO-GO - automatic Codex execution ;
NO-GO - GitHub API ;
NO-GO - git/gh execution hors boundary explicite Codex 040 ;
NO-GO - real merge hors --execute-merge plus verify gate complet ;
NO-GO - PR/merge automation dans les scripts repository ;
NO-GO - unbounded autonomous loop ;
NO-GO - autonomous full loop ;
NO-GO - boucle autonome ;
NO-GO - source discovery ;
NO-GO - RUN.
```

Ce verdict ne donne aucune autorisation implicite pour activer un chemin modèle, prompt,
source ou journal.

## 7. Risques restants

```text
- les docs peuvent dériver de l'implémentation ;
- le chemin mock OpenAI ne doit pas être exposé dans le CLI ;
- PromptPackage doit rester désactivé jusqu'à une future mission explicite d'activation runtime ;
- la politique sans accès aux données réelles repose maintenant sur des garde-fous de tests runtime qui doivent rester synchronisés.
```

## 8. Conditions obligatoires avant toute intégration OpenAI réelle

Avant toute intégration OpenAI réelle, toutes les conditions suivantes sont requises :

```text
- approbation humaine explicite ;
- branche séparée ;
- aucune activation par défaut ;
- client injecté uniquement ;
- contrat de réponse structurée ;
- validation de payload bloquante ;
- quality gates ;
- trace metadata ;
- aucune écriture journal ;
- aucune sélection de candidats ;
- aucune source discovery ;
- tests prouvant la désactivation par défaut.
```

Ces conditions sont cumulatives. L'absence d'une seule condition maintient le statut NO-GO.

## 9. Prochaines étapes recommandées

```text
1. Codex 017 a ajouté les fixtures PromptPackage metadata-only, désactivées ; ce point est courant et complété.
2. Codex 018 a ajouté les contrôles de synchronisation documentation/tests ; ce point est courant et complété.
3. Codex 019 ajoute le smoke test CLI dry-run fake-only end-to-end ; ce point est courant et complété.
4. Codex 020 ajoute les tests de garde-fous runtime fake-only/mock-only ; ce point est courant et complété.
5. Codex 021 sanitise/refactore uniquement les tests/docs des garde-fous CLI/runtime, sans nouvelle capacité fonctionnelle ; ce point est courant et complété.
6. Codex 022 ajoute le protocole documentaire de controle pour future activation de prompts reels, sans creation de prompt ni activation OpenAI/runtime ; ce point est courant et complété.
7. Codex 023 ajoute un audit-only des regles existantes vs couverture d'implementation courante, sans nouvelle doctrine, sans prompt reel, sans redaction de prompt commencee ni activation OpenAI/runtime ; ce point est courant et complété.
8. Codex 024 ajoute une clarification-only des blockers pre-prompt issus de Codex 023, sans doctrine nouvelle, sans prompt reel, sans redaction de prompt commencee ni activation OpenAI/runtime ; ce point est courant et complété.
9. Codex 025 ajoute une responsibility map docs/tests-only des niveaux de regles, agents, architecture SDK et actions externes interdites par defaut, sans prompt reel, sans redaction de prompt commencee, sans contrat JSON final ni enum runtime et sans activation OpenAI/runtime ; ce point est courant et complété.
10. Codex 026 ajoute une RoutingAgent functional spec docs/tests-only et pre-prompt du routage/aiguillage conservateur, sans prompt reel, sans redaction de prompt commencee, sans prompt draft, sans prompt body, sans contrat JSON final ni enum runtime et sans activation OpenAI/runtime ; ce point est courant et complété.
11. Codex 027 ajoute une RoutingAgent prompt-readiness checklist docs/tests-only et pre-draft du futur prompt draft desactive, sans prompt reel, sans redaction de prompt commencee, sans prompt draft, sans prompt body, sans contenu docs/prompts/drafts, sans contrat JSON final ni enum runtime et sans activation OpenAI/runtime ; ce point est courant et complété.
12. Codex 028 ajoute un disabled documentation-only RoutingAgent prompt draft `draft_documented` et desactive, sous docs/prompts/drafts, non-runtime, non-consumed, sans prompt actif, sans runtime loading, sans prompts.py, sans contrat JSON final ni enum runtime et sans activation OpenAI/runtime ; ce point est courant et complété.
13. Codex 029 ajoute un RoutingAgent prompt draft review gate docs/tests-only, documentation-only, non-runtime, non-consuming, non-activation, non-approval, pre-mock et pre-runtime, sans activation, approbation, chargement, rendu ou consommation du prompt, sans prompts.py, sans contrat JSON final ni enum runtime et sans activation OpenAI/runtime ; ce point est courant et complété.
14. Codex 030 ajoute des synthetic review fixtures docs/tests-only pour le RoutingAgent prompt draft desactive, documentation/test-only, non-runtime, non-consuming, non-activation, non-approval et mock-review-only au sens de revue statique, sans activation, approbation mock, approbation runtime, chargement, rendu, execution ou consommation du prompt, sans prompts.py, contrat JSON final, enum runtime ni activation OpenAI/runtime ; ce point est courant et complété.
15. Codex 031 ajoute un static non-LLM fixture checker docs/tests-only pour les fixtures synthetiques du RoutingAgent prompt draft desactive, documentation/test-only, test-only, non-runtime, non-consuming, non-activation, non-approval et fixture-shape/guardrail-only, sans activation, approbation mock, approbation runtime, consommation CLI, approbation OpenAI/RUN, chargement, rendu, execution ou consommation du prompt, sans prompts.py, code production, contrat JSON final, enum runtime, agents reels, appel OpenAI/reseau, mutation du journal actif ni changement de comportement ; ce point est courant et complété.
16. Codex 032 ajoute un static expected-output evaluator docs/tests-only pour les cas synthetiques RoutingAgent, documentation/test-only, test-only, static, non-LLM, non-runtime, non-consuming, non-activation, non-approval et expected-output-fixture-only, sans activation, approbation mock, approbation runtime, consommation CLI, approbation OpenAI/RUN, chargement, rendu, execution ou consommation du prompt, sans scoring de sortie modele, sans prompts.py, code production, contrat JSON final, enum runtime, agents reels, appel OpenAI/reseau, mutation du journal actif ni changement de comportement ; ce point est courant et complété.
17. Codex 033 ajoute un static candidate-output comparator docs/tests-only pour les cas synthetiques RoutingAgent, documentation/test-only, test-only, static, non-LLM, deterministic fake candidate provider, non-runtime, non-consuming, non-activation, non-approval et candidate-output-comparator-only, sans activation, approbation mock, approbation runtime, consommation CLI, approbation OpenAI/RUN, chargement, rendu, execution ou consommation du prompt, sans scoring de sortie modele, sans presenter le fake provider comme comportement RoutingAgent, sans prompts.py, code production, contrat JSON final, enum runtime, agents reels, appel OpenAI/reseau, mutation du journal actif, selection de candidats reels ni changement de comportement ; ce point est courant et complété.
18. Codex 034 ajoute un disabled prompt draft access boundary docs/tests-only pour le RoutingAgent prompt draft desactive, documentation/test-only, test-only, plain markdown inspection only, non-runtime, non-consuming, non-rendering, non-execution, non-activation, non-approval et non-LLM, sans activation, approbation mock, approbation runtime, consommation CLI, approbation OpenAI/RUN, chargement, rendu, execution ou consommation du prompt comme executable, sans scoring de sortie modele, sans prompts.py, code production, contrat JSON final, enum runtime, agents reels, appel OpenAI/reseau, lancement RUN, traitement de donnees projet reelles, lecture/ecriture du journal actif, application JournalPatch, export XLSX/CSV, ancien PDF ni changement de comportement ; ce point est courant et complété.
19. Codex 035 ajoute une architecture docs/tests/scaffold-only du futur coach loop local GPT-5.5 Thinking / Codex, avec guidance .dicoimpro, schema de sortie de stage, exemple d'etat workflow et documentation, sans API implementation, sans Codex SDK implementation, sans autonomous loop, sans activation/rendu/execution/consommation de prompt, sans OpenAI runtime, sans RUN, sans journal/JournalPatch, sans donnees reelles, sans publication, sans export XLSX/CSV, sans ancien PDF ni changement de comportement ; ce point est courant et complété.
20. Codex 036 ajoute un scaffold docs/tests/scripts-only local coach context collector and state machine, avec etat local ignore, dossiers de run, paquets de contexte markdown filtres et application deterministe de transition_gate, sans API calls, sans Codex SDK, sans Codex CLI, sans autonomous loop, sans prompt activation/rendering/execution/consumption, sans RUN, sans journal/JournalPatch, sans real data, sans PR/merge automation, sans production code ni changement de comportement ; ce point est courant et complété.
21. Codex 037 ajoute un runner local GPT-5.5 Thinking docs/tests/scripts pour le coach loop, explicit API only, no API calls by default, avec import OpenAI lazy/dynamic, validation de stage notes, extraction transition_gate/next_prompt et update d'etat local seulement via transition_gate, sans OpenAI runtime dans l'application dicoimpro, sans Codex SDK/CLI, sans autonomous loop, sans RUN, sans journal/JournalPatch, sans real data, sans PR/merge automation dans les scripts, sans src runtime behavior change ; ce point est courant et complété.
22. Codex 038 ajoute un manual Codex handoff bridge docs/tests/scripts pour le coach loop, avec packaging next_prompt/codex_prompt en handoff packets, archive de retours Codex fournis manuellement, validation PR/tests/diff-check/files/guardrail et extraction PR URL, sans Codex SDK/CLI, sans execution Codex depuis les scripts repository, sans OpenAI call, sans GPT call, sans autonomous loop, sans repository-script PR/merge automation, sans RUN, sans journal/JournalPatch, sans real data, sans publication, sans src runtime behavior change ; ce point est courant et complété.
23. Codex 039 ajoute une autonomy policy and pre-merge verify gate docs/tests/scripts pour le coach-loop program, avec stop_human, auto_local, auto_external_with_budget et auto_merge_after_verify decision modeling, merge manual by default, auto-merge comme policy possibility only after complete verify gate, decisions depuis supplied verification reports, sans real merge, sans GitHub API, sans git/gh execution, sans Codex SDK/CLI, sans autonomous full loop, sans RUN, sans journal/JournalPatch, sans real data, sans publication, sans src runtime behavior change ; ce point est courant et complété.
24. Codex 040 ajoute un guarded PR verification and optional auto-merge runner docs/tests/scripts pour le coach-loop program, avec pre_merge_report depuis PR evidence, decision through autonomy policy et merge execution seulement avec --execute-merge plus auto_after_verify apres fresh verify gate et stable head SHA, sans OpenAI/GPT/Codex SDK/CLI, sans autonomous full loop, sans RUN, sans journal/JournalPatch, sans real data, sans publication, sans src runtime behavior change ; ce point est courant et complété.
25. Codex 041 ajoute un semi-automatic coach-loop runner docs/tests/scripts, orchestrating context collection, GPT stage execution, transition_gate validation, bounded auto-reflection, Codex handoff, Codex return resume, PR verification and guarded merge delegation, without Codex SDK/CLI, automatic Codex execution, unbounded autonomous loop, RUN, journal, JournalPatch, real data, publication or src runtime behavior change ; ce point est courant et complété.
26. Maintenir un contrôle de synchronisation documentation/tests.
```

Ces étapes restent documentaires ou mock-only. Elles ne doivent pas introduire de prompt
actif, de prompt body consomme, de rendu/chargement/execution de prompt dans le
runtime dicoimpro, d'appel OpenAI reel par defaut, de Codex SDK, de Codex CLI,
d'execution Codex depuis les scripts repository, d'automatic Codex execution, de GitHub API, de git/gh execution hors boundary Codex 040, de real merge hors --execute-merge plus verify gate complet, de boucle autonome, d'unbounded autonomous loop, d'autonomous full loop, de lecture de donnees reelles, de publication, de RUN,
d'application de JournalPatch, de source discovery, de selection de candidats,
de contrat JSON final, d'enum runtime, d'ancien PDF actif, d'export XLSX/CSV ou
d'automatisation PR/merge dans les scripts repository.
