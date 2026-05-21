# MISSIONS_CODEX_v0.2.3-auto

Statut : cadrage opérationnel des interventions Codex  
Objet : fournir des missions prêtes à donner à Codex, bornées, testables, sans dérive méthodologique.

---

## 0. Règles générales pour Codex

Codex est autorisé à modifier le code, mais pas à modifier la doctrine.

Codex doit respecter les documents suivants, dans cet ordre de priorité :

```text
1. docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md
2. docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md
3. docs/CONTRATS_JSON_v0.2.3-auto.md
4. docs/STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md
5. docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md
6. docs/FEUILLE_ROUTE_IMPLEMENTATION_SDK_v0.2.3-auto.md
7. docs/AUDIT_CONCEPTION_AVANT_CODEX_v0.2.3-auto.md
8. docs/MISSIONS_CODEX_v0.2.3-auto.md
```

Codex ne doit pas :

```text
lancer de RUN
identifier des candidats
modifier le journal actif
modifier les fichiers dans data/local_files
utiliser le PDF ancien par défaut
changer les enums méthodologiques sans demande explicite
supprimer des garde-fous pour faire passer les tests
ajouter un appel OpenAI réel avant la phase prévue
```

Toute mission Codex doit finir par :

```text
pytest
résumé des fichiers modifiés
résumé des choix techniques
liste des points non tranchés
```

---

## 1. Mission Codex 001 — Contrats Pydantic SDK

### Prompt à donner

```text
Tu travailles dans le repo dicoimpro.

Objectif : implémenter les contrats Pydantic de base pour la couche SDK v0.2.3-auto.

Lis d'abord, dans cet ordre :
- docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md
- docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md
- docs/CONTRATS_JSON_v0.2.3-auto.md
- docs/STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md
- docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md
- docs/FEUILLE_ROUTE_IMPLEMENTATION_SDK_v0.2.3-auto.md
- docs/AUDIT_CONCEPTION_AVANT_CODEX_v0.2.3-auto.md

À faire :
1. Créer un package src/dico_impro/contracts/.
2. Implémenter les modèles Pydantic stricts suivants :
   - GoldenSetCase
   - AgentContract
   - AgentTask
   - AgentResult
   - BatchState
   - BatchReport
   - EntryState
   - AuditQueueRecord
3. Réutiliser les modèles existants dans src/dico_impro/models.py quand c'est pertinent, sans casser les tests existants.
4. Ajouter des tests unitaires pour objets valides et invalides.
5. Utiliser des valeurs machine ASCII dans les nouveaux enums/contrats :
   - accepte_avec_prudence, pas accepté_avec_prudence ;
   - a_revoir, pas à_revoir ;
   - publication_bloquee, pas publication_bloquée.
   Si un label humain accentué est nécessaire, ajouter un champ label ou description séparé.
6. Ne pas modifier models.py sauf nécessité minimale ; préférer créer contracts/ et préserver la compatibilité existante.
7. Ne pas créer AgentRegistry, FakeAdapter, OpenAIAdapter ou orchestration dans cette mission.
8. Ne pas créer SourceDiscoveryAgent.
9. Ne pas ajouter d'appel OpenAI.
10. Ne pas ajouter de logique de sélection de candidats.
11. Ne pas modifier les fichiers data/local_files.
12. Ne pas affaiblir les règles existantes.

Critères de réussite :
- pytest passe ;
- les objets invalides sont rejetés ;
- les objets minimaux valides sont acceptés ;
- les tests existants restent verts ;
- aucun appel réseau ;
- aucun fichier source local n'est modifié.
```

### Fichiers attendus

```text
src/dico_impro/contracts/__init__.py
src/dico_impro/contracts/common.py
src/dico_impro/contracts/agents.py
src/dico_impro/contracts/batch.py
src/dico_impro/contracts/project_state.py
tests/test_contracts_agents.py
tests/test_contracts_batch.py
tests/test_contracts_project_state.py
```

### Critères d'acceptation

```text
pytest vert
aucun appel réseau
aucune écriture data/local_files
aucune modification du journal
aucune suppression de tests existants
valeurs machine ASCII dans les nouveaux contrats
```

---

## 2. Mission Codex 002 — AgentRegistry + FakeAgentAdapter

### Prérequis

Mission 001 terminée, relue et tests verts.

### Prompt à donner

```text
Tu travailles dans le repo dicoimpro.

Objectif : créer la mécanique agent locale sans appel OpenAI réel.

Lis :
- docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md
- docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md
- docs/CONTRATS_JSON_v0.2.3-auto.md
- docs/FEUILLE_ROUTE_IMPLEMENTATION_SDK_v0.2.3-auto.md
- docs/AUDIT_CONCEPTION_AVANT_CODEX_v0.2.3-auto.md

À faire :
1. Créer AgentRegistry.
2. Créer une interface AgentAdapter.
3. Créer FakeAgentAdapter.
4. Simuler les scénarios :
   - success_valid
   - success_with_warning
   - schema_invalid
   - non_parseable_output
   - protocol_violation
   - source_confusion
   - publication_blocking
   - run_002_required
5. Convertir chaque réponse fake en AgentResult.
6. Ajouter les tests correspondants.

Interdictions :
- aucun appel OpenAI ;
- aucun appel réseau ;
- aucune sélection de candidats ;
- aucune écriture journal ;
- aucune modification data/local_files ;
- ne pas implémenter SourceDiscoveryAgent ;
- ne pas transformer Validation, DeltaBuilder, JournalPatchBuilder ou BatchReporter en agents autonomes.

Critères de réussite :
- pytest passe ;
- chaque scénario fake est testé ;
- les erreurs sont classées récupérables ou bloquantes.
```

### Fichiers attendus

```text
src/dico_impro/agents/__init__.py
src/dico_impro/agents/registry.py
src/dico_impro/agents/adapters/__init__.py
src/dico_impro/agents/adapters/base.py
src/dico_impro/agents/adapters/fake.py
src/dico_impro/agents/quality_gates.py
tests/test_agent_registry.py
tests/test_fake_adapter.py
tests/test_agent_quality_gates.py
```

---

## 3. Mission Codex 003 — Orchestration dry-run avec scope fourni

### Prérequis

Missions 001 et 002 terminées, relues et tests verts.

### Prompt à donner

```text
Tu travailles dans le repo dicoimpro.

Objectif : créer une orchestration dry-run minimale qui prépare et simule un lot à partir d'un scope explicitement fourni.

Important : ne pas sélectionner les candidats automatiquement. Le scope est fourni par fixture ou argument.

À faire :
1. Créer un module d'orchestration dry-run.
2. Charger le manifest.
3. Vérifier les garde-fous existants.
4. Lire un scope fourni en fixture.
5. Construire des AgentTask.
6. Exécuter FakeAgentAdapter.
7. Produire BatchState et BatchReport.
8. Ajouter une commande CLI : dico-impro plan-batch --dry-run --scope <fichier>.
9. Ajouter tests sans appel modèle.

Interdictions :
- pas d'identification de candidats ;
- pas de RUN ;
- pas d'appel OpenAI ;
- pas d'écriture journal ;
- pas d'utilisation PDF ancien.

Critères de réussite :
- pytest passe ;
- dry-run produit BatchState + BatchReport ;
- un scope fourni est respecté strictement ;
- aucune source n'est modifiée.
```

### Fichiers attendus

```text
src/dico_impro/orchestration/__init__.py
src/dico_impro/orchestration/dry_run.py
src/dico_impro/orchestration/task_builder.py
src/dico_impro/orchestration/batch_state.py
tests/fixtures/scopes/scope_minimal.yaml
tests/test_orchestration_dry_run.py
```

---

## 4. Mission Codex 004 — Exports JSON de batch

### Prérequis

Mission 003 terminée et tests verts.

### Prompt à donner

```text
Tu travailles dans le repo dicoimpro.

Objectif : générer les exports JSON d'un batch dry-run, sans XLSX pour l'instant.

À faire :
1. Créer un exporteur JSON.
2. Produire :
   - master.json
   - batch_report.json
   - journal_patch.json si présent
   - audit_queue.json si présente
3. Vérifier que les JSON sont parseables.
4. Vérifier que les nombres sont cohérents.
5. Vérifier qu'aucun fichier source n'est modifié.
6. Ajouter tests.

Interdictions :
- pas d'écriture journal ;
- pas de modification data/local_files ;
- pas d'appel OpenAI ;
- pas de XLSX dans cette mission.

Critères de réussite :
- pytest passe ;
- exports JSON valides ;
- aucun fichier source modifié ;
- JournalPatch reste un fichier séparé.
```

### Fichiers attendus

```text
src/dico_impro/exports/__init__.py
src/dico_impro/exports/json_exporter.py
tests/test_exports_json.py
```

---

## 5. Mission Codex 005 — Golden set de prudence

### Prérequis

Missions 001 à 004 terminées et tests verts.

### Prompt à donner

```text
Tu travailles dans le repo dicoimpro.

Objectif : créer les fixtures et tests du golden set de prudence. Ne pas retraiter les entrées ; les cas servent uniquement de tests anti-régression.

Lis :
- docs/STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md

À faire :
1. Créer des fixtures GoldenSetCase pour :
   - post005_026_030_032
   - fiches_familles
   - controles_perimetre
   - mecanismes_passerelles
   - alias_doublons
2. Ajouter les tests qui vérifient les attendus méthodologiques.
3. Ne pas lire les vrais fichiers pour décider les attendus.
4. Ne pas lancer de RUN.

Interdictions :
- ne pas inventer de nouvelles décisions de fond ;
- ne pas affaiblir les règles pour faire passer les tests ;
- ne pas utiliser le PDF ancien.

Critères de réussite :
- pytest passe ;
- les tests vérifient la prudence, pas la production de fiches ;
- chaque cas a expected_must et expected_must_not.
```

### Fichiers attendus

```text
tests/fixtures/golden_set/post005_026_030_032.yaml
tests/fixtures/golden_set/fiches_familles.yaml
tests/fixtures/golden_set/controles_perimetre.yaml
tests/fixtures/golden_set/mecanismes_passerelles.yaml
tests/fixtures/golden_set/alias_doublons.yaml
tests/test_golden_set_cases.py
```

---

## 6. Mission Codex 006 — Adaptateur OpenAI skeleton

### Prérequis

Missions 001 à 005 terminées, fake adapter et dry-run verts.

### Prompt à donner

```text
Tu travailles dans le repo dicoimpro.

Objectif : créer le squelette OpenAIAgentAdapter sans effectuer d'appel réseau dans les tests.

À faire :
1. Créer OpenAIAgentAdapter conforme à AgentAdapter.
2. Préparer la construction de requête depuis AgentContract + AgentTask.
3. Imposer expected_schema.
4. Exclure forbidden_files.
5. Ajouter tests de forme sans appel réel.
6. Ne pas mettre de clé API.
7. Ne pas lancer de vrai appel modèle.

Critères de réussite :
- pytest passe ;
- aucun test ne dépend du réseau ;
- l'adaptateur refuse un contrat sans schéma ;
- l'adaptateur refuse un fichier interdit.
```

### Fichiers attendus

```text
src/dico_impro/agents/adapters/openai.py
src/dico_impro/agents/prompts.py
tests/test_openai_adapter_contract_shape.py
tests/test_prompts_forbidden_actions.py
```

---

## 7. Prompt court pour vérification Codex après chaque mission

À demander après chaque mission :

```text
Résume :
1. fichiers modifiés ;
2. tests ajoutés ;
3. commandes exécutées ;
4. résultat pytest ;
5. limites ou points non tranchés ;
6. garantie que tu n'as pas modifié data/local_files ni ajouté d'appel OpenAI réel.
```

---

## 8. Stop conditions

Si Codex fait l'un des points suivants, arrêter la mission et revenir à la conception :

```text
modifie une règle méthodologique sans demande
lance un RUN
identifie automatiquement des candidats
écrit ou modifie le journal actif
utilise le PDF ancien par défaut
transforme un test de prudence en test de production de fiche
supprime des tests existants
introduit un appel réseau dans les tests
crée SourceDiscoveryAgent avant arbitrage explicite
transforme les modules déterministes en agents autonomes
```
