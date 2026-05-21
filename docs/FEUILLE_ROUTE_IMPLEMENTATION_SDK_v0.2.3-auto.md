# FEUILLE_ROUTE_IMPLEMENTATION_SDK_v0.2.3-auto

Statut : feuille de route opérationnelle après conception  
Objet : transformer les documents d'architecture en étapes d'implémentation contrôlées, sans dérive vers le traitement manuel des entrées.

---

## 0. Règle de gouvernance

Aucune phase ne doit commencer tant que la précédente n'a pas ses critères de passage validés.

On distingue :

```text
conception validée
contrats implémentés
tests de prudence verts
fake adapter vert
orchestration dry-run verte
adaptateur OpenAI prêt
batch réel autorisé
publication consolidée autorisée
```

Une réussite technique ne vaut pas validation intellectuelle.

---

## 1. État actuel du dépôt

### 1.1 À garder comme socle technique

```text
src/dico_impro/manifest.py
src/dico_impro/models.py
src/dico_impro/validators.py
src/dico_impro/journal.py
src/dico_impro/journal_reader.py
src/dico_impro/cli.py
```

Raison : ces modules posent déjà les garde-fous minimaux : manifest, validation, JournalPatch, lecture journal en lecture seule, CLI de contrôle.

### 1.2 À considérer comme exploratoire

```text
src/dico_impro/orchestrator.py
docs/ARCHITECTURE_SDK_v0.2.3-auto.md
```

Raison : ces fichiers ont été créés avant consolidation du plan. Ils peuvent être réutilisés, mais ils ne doivent pas piloter la suite sans réalignement.

### 1.3 Documents de conception à traiter comme références provisoires

```text
docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md
docs/CONTRATS_JSON_v0.2.3-auto.md
docs/STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md
docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md
```

Ces documents définissent l'état cible avant implémentation.

---

## 2. Phase A — Validation documentaire

### Objectif

Relire et stabiliser les documents de conception avant tout nouveau code structurant.

### Livrables

```text
PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md validé
CONTRATS_JSON_v0.2.3-auto.md validé
STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md validé
SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md validé
FEUILLE_ROUTE_IMPLEMENTATION_SDK_v0.2.3-auto.md validée
```

### Points à arbitrer

```text
liste finale des agents
liste finale des contrats Pydantic
statut exact du vieux PDF
format minimal des traces
périmètre du fake adapter
critères avant appel modèle réel
```

### Critère de passage

Aucun désaccord méthodologique majeur non tranché.

---

## 3. Phase B — Contrats Pydantic

### Objectif

Transformer les contrats JSON validés en modèles Pydantic stricts.

### Modules à créer ou réaligner

```text
src/dico_impro/contracts/common.py
src/dico_impro/contracts/project_state.py
src/dico_impro/contracts/sources.py
src/dico_impro/contracts/classification.py
src/dico_impro/contracts/agents.py
src/dico_impro/contracts/batch.py
```

### Objets prioritaires

```text
EntryState
ConservationRecord
SourceRecord
SourceAuditReport
ClassificationResult
Run002Request
AuditQueueRecord
AgentContract
AgentTask
AgentResult
BatchState
BatchReport
GoldenSetCase
```

### Tests

```text
tests/test_contracts_common.py
tests/test_contracts_sources.py
tests/test_contracts_agents.py
tests/test_contracts_batch.py
tests/test_golden_set_case.py
```

### Critères de passage

```text
pytest vert
objets invalides rejetés
objets minimaux valides acceptés
aucun extra incontrôlé sauf décision explicite
```

---

## 4. Phase C — Agent registry + fake adapter

### Objectif

Préparer la mécanique agent sans appel OpenAI réel.

### Modules à créer

```text
src/dico_impro/agents/registry.py
src/dico_impro/agents/adapters/base.py
src/dico_impro/agents/adapters/fake.py
src/dico_impro/agents/quality_gates.py
```

### Tests

```text
tests/test_agent_registry.py
tests/test_fake_adapter.py
tests/test_agent_quality_gates.py
```

### Scénarios fake adapter

```text
success_valid
success_with_warning
schema_invalid
non_parseable_output
protocol_violation
source_confusion
publication_blocking
run_002_required
```

### Critères de passage

```text
aucun appel réseau
aucun appel modèle réel
résultats fake convertis en AgentResult
payloads validés
erreurs classées récupérables ou bloquantes
```

---

## 5. Phase D — Orchestration dry-run

### Objectif

Tester le flux système complet sans produire de RUN ni appeler de modèle réel.

### Modules à créer ou réaligner

```text
src/dico_impro/orchestration/pipeline.py
src/dico_impro/orchestration/batch_state.py
src/dico_impro/orchestration/task_builder.py
src/dico_impro/orchestration/dry_run.py
```

### Commande cible

```text
dico-impro plan-batch --dry-run
```

### Ce que la commande doit faire

```text
charger manifest
charger état projet
vérifier garde-fous
charger stratégie de lot explicite
construire AgentTask[]
simuler appels avec fake adapter
valider AgentResult[]
produire BatchState
produire BatchReport simulé
ne modifier aucun fichier source
```

### Ce que la commande ne doit pas faire

```text
choisir manuellement les candidats
lancer RUN_001
lancer RUN_002
écrire journal
utiliser PDF ancien
publier fiche finale
```

### Critères de passage

```text
batch dry-run vert
BatchState produit
BatchReport produit
aucune écriture non autorisée
```

---

## 6. Phase E — Golden set de prudence

### Objectif

Vérifier que le système garde les prudences calibrées.

### Fixtures à créer

```text
tests/fixtures/golden_set/post005_026_030_032.yaml
tests/fixtures/golden_set/fiches_familles.yaml
tests/fixtures/golden_set/controles_perimetre.yaml
tests/fixtures/golden_set/mecanismes_passerelles.yaml
tests/fixtures/golden_set/alias_doublons.yaml
```

### Tests

```text
tests/test_golden_set_post005.py
tests/test_golden_set_prudence.py
tests/test_anti_reduction_culturelle.py
```

### Critères de passage

```text
026/030 non retraités comme nouveaux
032 non RUN fait
familles non réduites par défaut
contrôles périmètre non publiables directement
mécanismes/passerelles non isolés abusivement
alias/doublons bloqués avant résolution
```

---

## 7. Phase F — Exports

### Objectif

Produire les artefacts de sortie sans toucher aux sources.

### Modules à créer

```text
src/dico_impro/exports/json_exporter.py
src/dico_impro/exports/xlsx_exporter.py
src/dico_impro/exports/csv_exporter.py
src/dico_impro/exports/report_writer.py
```

### Artefacts attendus

```text
master.json
batch_report.json
journal_patch.json
audit_queue.json
export_lisible.xlsx
export_light.csv
logs
```

### Tests

```text
tests/test_exports_json.py
tests/test_exports_xlsx.py
tests/test_exports_csv.py
tests/test_export_no_source_mutation.py
```

### Critères de passage

```text
JSON parseable
XLSX lisible
CSV léger
nombres cohérents
JournalPatch séparé
aucune source modifiée
```

---

## 8. Phase G — Adaptateur OpenAI / Agents SDK

### Objectif

Brancher les vrais appels modèle, sous les mêmes contrats que le fake adapter.

### Modules à créer

```text
src/dico_impro/agents/adapters/openai.py
src/dico_impro/agents/prompts.py
src/dico_impro/agents/trace_refs.py
```

### Conditions avant démarrage

```text
contrats verts
fake adapter vert
dry-run vert
golden set vert
exports verts
journal garde-fous verts
aucune écriture journal possible
```

### Tests

Les tests automatisés ne doivent pas dépendre d'un appel modèle réel.

Créer seulement :

```text
tests/test_openai_adapter_contract_shape.py
tests/test_prompts_forbidden_actions.py
```

### Critères de passage

```text
l'adaptateur respecte AgentAdapter
sorties passées par AgentResult
schéma attendu imposé
fichiers interdits exclus
traces référencées
```

---

## 9. Phase H — Premier batch réel contrôlé

### Objectif

Exécuter un batch minimal explicitement autorisé.

### Conditions

```text
stratégie de lot validée
scope explicite
mode dry-run réussi sur le même scope
humain prévenu des risques
aucune écriture journal directe
sorties séparées
```

### Sortie attendue

```text
répertoire batch complet
master.json
BatchReport
AuditQueue éventuelle
JournalPatch éventuel
aucune modification sources
```

### Critère de passage

Le résultat est relisible, auditable, et peut être rejeté sans perte.

---

## 10. Phase I — Application contrôlée de JournalPatch

### Objectif

Définir une procédure séparée pour appliquer un patch journal.

Cette phase ne doit pas être mélangée avec la production du batch.

Conditions :

```text
JournalPatch valide
humain ou procédure validée
backup du journal
rapport d'application
contrôle post-application
```

Ce n'est pas une priorité immédiate.

---

## 11. Découpage recommandé pour Codex

Codex doit recevoir des missions courtes et vérifiables.

### Mission Codex 1

```text
Implémente les contrats Pydantic AgentContract, AgentTask, AgentResult, BatchState, BatchReport et GoldenSetCase selon docs/CONTRATS_JSON_v0.2.3-auto.md. Ajoute les tests unitaires correspondants. Ne modifie pas la logique de pipeline. Ne crée aucun appel OpenAI.
```

### Mission Codex 2

```text
Crée AgentRegistry et FakeAgentAdapter selon docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md. Ajoute les scénarios fake success_valid, schema_invalid, non_parseable_output et protocol_violation. Tests uniquement locaux, aucun appel réseau.
```

### Mission Codex 3

```text
Crée un dry-run minimal d'orchestration qui consomme des AgentTask simulées et produit BatchState + BatchReport. Ne sélectionne pas de candidats ; utilise un scope fourni explicitement en fixture.
```

### Mission Codex 4

```text
Crée les exports JSON de batch : master.json, batch_report.json, journal_patch.json et audit_queue.json. Aucun XLSX à ce stade. Vérifie qu'aucune source n'est modifiée.
```

---

## 12. Points d'arrêt obligatoires

Arrêter et réviser si :

```text
un agent commence à décider le workflow
une étape traite des candidats sans stratégie explicite
un fichier source est modifié
une archive devient source active
le PDF ancien est utilisé par défaut
une fiche famille devient fiche pratique par facilité
un test passe en affaiblissant une règle méthodologique
Codex invente une catégorie ou change une enum
```

---

## 13. Prochaine action recommandée

Avant code : relire les cinq documents de conception.

Ensuite, première implémentation sûre :

```text
Phase B, Mission Codex 1 ou implémentation manuelle équivalente.
```

Elle est sûre car elle ne lance pas d'agent, ne lit pas de nouvelles données, ne choisit aucun candidat et ne modifie aucun fichier source.
