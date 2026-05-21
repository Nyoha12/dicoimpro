# PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto

Statut : document de conception avant implémentation SDK  
Objet : concevoir le système de production automatisée de la base `dico impro`, sans lancer de RUN, sans identifier manuellement de candidats, sans modifier le journal actif.

---

## 0. Décision de méthode

On ne part pas des outils.

L'ordre de conception est :

```text
1. intention du projet
2. philosophie de catégorisation
3. architecture de production
4. contrats de données
5. Agents SDK / Responses API
6. implémentation Python
7. tests de prudence
8. production par lots
```

Ce document prime sur les bouts de code exploratoires déjà présents dans le dépôt tant qu'il n'a pas été validé.

---

## 1. Intention du projet

Le projet ne consiste pas seulement à classer des musiques improvisées.

Il s'agit de construire une base rigoureuse sur des pratiques, cadres, familles, procédés et mécanismes d'improvisation musicale mondiale, en évitant :

- l'écrasement de pratiques humaines subtiles sous des catégories trop larges ;
- la confusion entre oralité, variation, rituel, performance et improvisation centrale ;
- le surclassement de l'improvisation ;
- la transformation forcée de familles ou cadres en fiches pratiques ;
- la perte des sous-pistes ;
- la confusion entre cadre, genre, forme, procédé, exemple et pratique ;
- la confusion entre source originale et plateforme d'accès ;
- la production d'une taxonomie culturellement brutale.

La base doit être :

```text
conservatoire
relationnelle
prudente
exploitable
rejouable
auditable
```

---

## 2. Doctrine non réductrice

Règles doctrinales à préserver :

```text
classer ≠ réduire
documenter ≠ valider définitivement
conserver ≠ créer une fiche
scinder ≠ perdre le parent
fusionner ≠ effacer les variantes
RUN possible ≠ fiche pratique prête
```

Le système doit automatiser autant la prudence que la production.

Il doit savoir produire :

- une fiche pratique ;
- une fiche-cadre ;
- une fiche-famille ;
- un mécanisme-passerelle ;
- un contrôle de périmètre ;
- une réserve ;
- un alias/doublon à vérifier ;
- une décision provisoire avec prudence ;
- un blocage de publication sans blocage du traitement.

---

## 3. Hiérarchie des autorités

### 3.1 Règles méthodologiques

```text
PROTOCOLE_BASE_IMPROVISATION_v0.2.3
→ SPEC_AUTOMATISATION_DICO_IMPRO_v0.2.3-auto si non contradictoire
→ décisions de pilotage consolidées
→ décisions conversationnelles non matérialisées
```

### 3.2 État des données

```text
journal matérialisé validé
→ archives RUN / contrôles matérialisés
→ décisions conversationnelles non matérialisées
```

### 3.3 Corrections aux directives périmées

1. Le journal actif temporaire post-005 remplace le journal MINI_RUN_004 pour le pilotage courant dès lors qu'il est matérialisé, présent localement et validé par garde-fous.
2. Les archives RUN restent non-actives : elles documentent une exécution, elles ne deviennent pas sources documentaires.
3. Le PDF ancien `Improvisation musicale mondiale.pdf` ne doit pas être utilisé par défaut. Statut recommandé : `legacy_optional_reference`, jamais source décisive automatique.
4. La couche d'exécution s'appelle `v0.2.3-auto`. Elle ne crée pas une v0.2.4 et ne modifie pas la taxonomie.

---

## 4. Architecture générale

Architecture cible :

```text
Fichiers locaux en lecture seule
        ↓
Manifest / état projet
        ↓
Orchestrateur Python déterministe
        ↓
Agents spécialisés sous contrat
        ↓
Validation Pydantic + règles déterministes
        ↓
Décisions provisoires / DELTAS / alertes
        ↓
Exports JSON canonique + XLSX auditable + CSV léger
        ↓
JournalPatch proposé, jamais écriture directe
```

Principe central :

```text
L'orchestrateur gouverne le flux.
Les agents produisent des analyses structurées.
Les validateurs acceptent, corrigent, rétrogradent ou bloquent la publication.
```

Les agents ne doivent jamais devenir l'autorité d'état du projet.

---

## 5. Couches du système

### 5.1 Couche fichiers / manifest

Rôle :

- déclarer les fichiers locaux ;
- déclarer leur statut ;
- empêcher les inférences par dossier ou nom seul ;
- distinguer source active, journal, archive, sortie, référence optionnelle ;
- empêcher l'utilisation du PDF ancien par défaut.

Objets :

```text
DataManifest
ManifestFile
FileRole
FileStatus
```

### 5.2 Couche état projet

Rôle :

- lire la base 001–300 ;
- lire le triage conservatoire ;
- lire le journal actif temporaire ;
- lire les archives uniquement comme traces non-actives ;
- construire un état projet sans lancer de traitement.

Objet cible :

```text
ProjectState
```

Champs minimaux :

```text
batch_id
protocol_version
automation_layer
active_journal_id
known_entries
known_processed_ids
known_reserve_ids
known_non_active_archives
warnings
```

### 5.3 Couche contrats de données

Tout agent et tout module doit produire un objet structuré validable.

Objets minimum :

```text
EntryState
RoutingDecision
ConservationRecord
SourceRecord
SourceAuditReport
ClassificationInput
ClassificationResult
ValidationReport
Run002Request
Run002Result
DeltaRecord
FinalProvisionalDecision
JournalPatch
BatchReport
AuditQueueRecord
```

Le texte libre est secondaire. Il peut exister comme justification, jamais comme vérité technique.

### 5.4 Couche Agents SDK / Responses API

Rôle :

- appeler des agents spécialisés ;
- forcer une sortie JSON conforme ;
- permettre handoff et reprise ;
- produire des traces ;
- séparer les responsabilités.

Le SDK sert à organiser des appels intelligents. Il ne remplace pas le protocole.

### 5.5 Couche validation déterministe

Rôle :

- valider le JSON ;
- appliquer les règles v0.2.3 ;
- rétrograder les indices non justifiés ;
- générer RUN_002 ciblé si nécessaire ;
- bloquer publication si nécessaire ;
- produire audit trail.

### 5.6 Couche production

Rôle :

- écrire les artefacts de sortie ;
- produire `master.json` par batch ;
- produire XLSX lisible ;
- produire CSV léger ;
- produire rapport d'alertes ;
- produire `JournalPatch` séparé.

---

## 6. Agents spécialisés

### 6.1 RoutingAgent

Mission : déterminer le type d'unité avant tout RUN.

Entrées :

```text
EntryState
triage conservatoire
journal state
règles v0.2.3
```

Sortie :

```text
RoutingDecision
```

Interdictions :

- ne pas créer une fiche pratique par défaut ;
- ne pas lancer un RUN ;
- ne pas scinder définitivement ;
- ne pas fusionner définitivement.

### 6.2 ConservationAgent

Mission : protéger sous-pistes, variantes, relations parent/enfant et risques de perte.

Sortie :

```text
ConservationRecord
```

Interdictions :

- ne pas valider musicalement ;
- ne pas transformer une sous-piste en fiche validée.

### 6.3 SourceDiscoveryAgent

Mission : proposer des sources uniquement si une unité est mûre pour RUN documentaire.

Sortie :

```text
SourceRecord[]
```

Interdictions :

- ne pas traiter une plateforme comme source originale ;
- ne pas réutiliser indistinctement une source globale pour plusieurs entrées ;
- ne pas utiliser le PDF ancien par défaut.

### 6.4 SourceAuditAgent

Mission : qualifier les sources.

Sortie :

```text
SourceAuditReport
```

Doit distinguer :

```text
source originale
plateforme d'accès
source décisive
source de renfort
source de contexte
source insuffisante
```

### 6.5 ClassificationAgent

Mission : proposer D/S/I/C/E et justification.

Sortie :

```text
ClassificationResult
```

Interdictions :

- ne pas attribuer `I-A` sans preuve explicite ;
- ne pas attribuer `S-A` sans base documentaire suffisante ;
- ne pas forcer `C-A` si le périmètre est instable.

### 6.6 ValidationAgent / Validation déterministe

Mission : appliquer les règles automatiques.

Sortie :

```text
ValidationReport
Run002Request si nécessaire
```

Ce module peut être partiellement ou totalement déterministe. Les règles bloquantes ne doivent pas dépendre d'un jugement libre de modèle.

### 6.7 SynthesisAgent

Mission : construire la décision finale provisoire, pas publier une vérité définitive.

Sortie :

```text
FinalProvisionalDecision
```

### 6.8 DeltaAgent

Mission : tracer les différences RUN_001/RUN_002.

Sortie :

```text
DeltaRecord[]
```

### 6.9 JournalPatchAgent

Mission : proposer un patch de journal contrôlé.

Sortie :

```text
JournalPatch
```

Interdiction absolue : écriture directe dans le journal actif.

### 6.10 BatchReporter

Mission : produire la vue consolidée d'un lot.

Sortie :

```text
BatchReport
```

---

## 7. Contrats d'exécution

### 7.1 AgentContract

Champs :

```text
agent_name
agent_version
mission
allowed_inputs
required_output_schema
forbidden_actions
quality_gates
handoff_targets
```

### 7.2 AgentTask

Champs :

```text
task_id
batch_id
id_entree_original
task_type
input_payload
allowed_files
forbidden_files
expected_schema
```

### 7.3 AgentResult

Champs :

```text
result_id
task_id
agent_name
schema_name
payload
warnings
audit_notes
raw_model_trace_ref
validation_status
```

### 7.4 BatchState

Champs :

```text
batch_id
created_at
status
steps_completed
entries_scope
artifacts
errors_recoverable
errors_blocking
replay_command
```

---

## 8. Workflow cible complet

```text
LOAD_MANIFEST
LOAD_PROJECT_STATE
CHECK_GUARDS
BUILD_BATCH_SCOPE
BUILD_AGENT_TASKS
ROUTING
CONSERVATION
SOURCE_DISCOVERY si autorisé
SOURCE_AUDIT
CLASSIFICATION
DETERMINISTIC_VALIDATION
RUN_002_REQUEST si nécessaire
RUN_002_TARGETED si autorisé
DELTA_BUILD
FINAL_PROVISIONAL_DECISION
AUDIT_QUEUE_BUILD
JOURNAL_PATCH_BUILD
EXPORT_JSON
EXPORT_XLSX
EXPORT_CSV
BATCH_REPORT
```

Important : `BUILD_BATCH_SCOPE` n'est pas une identification manuelle de candidats. C'est une fonction de système qui prendra ses règles depuis le manifest, le journal et la stratégie de lot validée.

---

## 9. Qualité et validation

### Niveau 1 — Syntaxique

- JSON conforme au schéma ;
- champs obligatoires présents ;
- IDs valides ;
- valeurs contrôlées ;
- dates / références présentes ;
- sortie agent parseable.

### Niveau 2 — Protocolaire

- `type_unite_RUN` avant RUN ;
- `RUN possible ≠ fiche pratique prête` ;
- `S-A` interdit sans source décisive et vérification ;
- `I-A` interdit sans preuve explicite d'improvisation centrale ;
- `C-A` interdit si périmètre instable ;
- plateforme d'accès interdite comme source originale ;
- DELTA obligatoire si RUN_002 modifie S/I/C/décision ;
- journal patch séparé.

### Niveau 3 — Sémantique

- confusion cadre / genre / forme / procédé ;
- surclassement de l'improvisation ;
- fiche famille transformée en fiche pratique ;
- scission sans conservation parent ;
- fusion qui efface variantes ;
- source globale utilisée trop largement ;
- fausse symétrie entre pratiques culturellement différentes.

Le niveau 3 est le cœur intellectuel du système. Il doit être testé par golden set, pas seulement par tests unitaires simples.

---

## 10. RUN_001 / RUN_002

### 10.1 RUN_001

Un RUN_001 est une passe documentaire structurée sur une unité classable.

Il ne doit pas être lancé sur :

- fiche famille non stabilisée ;
- contrôle de périmètre ;
- alias/doublon non résolu ;
- mécanisme-passerelle non cadré ;
- entrée déjà traitée comme nouvelle.

### 10.2 RUN_002 ciblé

Un RUN_002 ne relance pas tout.

Il répond à une faiblesse ciblée :

```text
champ: S / I / C / source / périmètre / décision
faiblesse
question_ciblee
action attendue
```

### 10.3 DELTA

Tout changement entre RUN_001 et RUN_002 doit générer un `DeltaRecord`.

---

## 11. Audit humain, intégration provisoire, publication consolidée

### 11.1 Intégration provisoire

Le pipeline peut intégrer une décision provisoire dans les sorties de travail.

Elle est :

```text
structurée
traçable
auditable
non définitive
```

### 11.2 Audit humain

L'audit humain est possible, mais non bloquant par défaut.

Il sert à :

- revoir les alertes ;
- corriger une règle ;
- rejouer un lot ;
- valider une version publiée ;
- traiter une controverse documentaire.

### 11.3 Publication consolidée

La publication consolidée est une étape séparée.

Elle peut être bloquée par :

- source décisive absente ;
- source originale non identifiée ;
- `S-A` ou `I-A` insuffisamment justifié ;
- périmètre instable ;
- RUN_002 requis mais absent ;
- DELTA manquant ;
- audit sources incomplet ;
- contradiction forte ;
- journalisation incohérente.

Le traitement automatisé peut continuer même si la publication est bloquée.

---

## 12. Stratégie de tests

### 12.1 Tests unitaires

- modèles Pydantic ;
- validateurs ;
- JournalPatch ;
- manifest ;
- lecture journal ;
- garde-fous.

### 12.2 Golden set de prudence

Le prototype doit tester des cas calibrés, non pour les retraiter, mais pour vérifier que le système retrouve les prudences déjà apprises.

Cas de calibration :

```text
026 / 030 : ne pas retraiter comme nouveaux ; statut fiche-cadre / prudence
032 : réserve, pas RUN fait
005 / 006 / 049 / 096 : fiches familles et sous-pistes
007 / 013 : contrôle de périmètre
012 / 048 : mécanismes / passerelles
125 : alias/doublon / passerelle possible
```

### 12.3 Tests d'interdiction

Le système doit échouer si :

- un agent écrit directement dans le journal ;
- le PDF ancien est utilisé par défaut ;
- une archive RUN devient source documentaire ;
- une fiche famille devient fiche pratique sans stabilisation ;
- `S-A` / `I-A` sont attribués sans preuve ;
- un RUN_002 n'a pas de faiblesse ciblée.

---

## 13. Rôle de Codex

Codex est un accélérateur d'implémentation, pas l'architecte intellectuel du projet.

À lui confier :

```text
- implémenter les schémas Pydantic validés ;
- écrire les tests ;
- créer l'adaptateur Agents SDK ;
- générer les exports ;
- refactorer ;
- corriger les erreurs pytest ;
- documenter les commandes.
```

À ne pas lui confier sans cadrage :

```text
- décider ce qu'est une fiche ;
- décider quand scinder/fusionner ;
- décider quand un cas culturellement complexe est stable ;
- changer les règles v0.2.3 ;
- utiliser automatiquement le PDF ancien ;
- choisir les candidats à traiter hors stratégie validée.
```

---

## 14. Plan d'implémentation recommandé

### Phase A — Stabilisation conception

Livrables :

```text
PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md
CONTRATS_JSON_v0.2.3-auto.md
STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md
```

### Phase B — Contrats

Implémenter ou finaliser :

```text
AgentContract
AgentTask
AgentResult
BatchState
ProjectState
AuditQueueRecord
BatchReport
```

### Phase C — Adaptateur Agents SDK

Créer :

```text
agents/base.py
agents/openai_adapter.py
agents/fake_adapter.py
agents/registry.py
```

Le fake adapter est obligatoire pour tester sans appel API.

### Phase D — Orchestration dry-run

Créer une commande :

```text
dico-impro plan-batch --dry-run
```

Elle ne produit aucun RUN. Elle vérifie seulement que le système sait préparer les tâches.

### Phase E — Golden set

Créer un banc de test sur les prudences calibrées.

### Phase F — Production limitée

Seulement après validation : batch expérimental contrôlé, sortie JSON/XLSX, pas d'écriture journal directe.

---

## 15. Décision provisoire sur le code déjà présent

À garder comme socle, sous réserve d'audit :

```text
manifest.py
models.py
validators.py
journal.py
journal_reader.py
cli.py
tests existants
```

À considérer comme exploratoire et à réaligner sur ce plan :

```text
orchestrator.py
docs/ARCHITECTURE_SDK_v0.2.3-auto.md
```

Aucun de ces fichiers ne doit devenir l'autorité de conception tant que les contrats ne sont pas validés.

---

## 16. Prochaine décision à prendre

Avant de coder davantage, valider ou corriger :

1. la liste des agents ;
2. les objets contractuels minimum ;
3. la hiérarchie des autorités ;
4. le statut du PDF ancien ;
5. la séparation traitement automatisé / publication consolidée ;
6. le rôle exact de Codex.

Ensuite seulement : implémentation des contrats `AgentContract`, `AgentTask`, `AgentResult`, `BatchState`.
