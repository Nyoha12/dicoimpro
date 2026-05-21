# STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto

Statut : document de conception des tests  
Objet : définir comment tester un système qui doit produire de la prudence structurée, pas seulement du code fonctionnel.

---

## 0. Principe

Le système ne doit pas seulement passer des tests techniques.

Il doit prouver qu'il respecte les contraintes intellectuelles du projet :

```text
ne pas réduire
ne pas surclasser
ne pas confondre source et accès
ne pas transformer une famille en fiche pratique
ne pas effacer les sous-pistes
ne pas publier quand la prudence exige un blocage
ne pas retraiter comme nouveau ce qui est déjà journalisé
```

Les tests doivent donc vérifier deux choses :

```text
1. le pipeline fonctionne ;
2. le pipeline reste prudent.
```

---

## 1. Niveaux de tests

### 1.1 Tests unitaires déterministes

Objet : vérifier les fonctions sans appel modèle.

Exemples :

- normalisation d'ID ;
- lecture du manifest ;
- lecture journal en lecture seule ;
- validation `S-A`, `I-A`, `C-A` ;
- `JournalPatch` sans écriture directe ;
- garde-fous post-005.

Statut : déjà amorcé dans le dépôt.

### 1.2 Tests de contrats JSON

Objet : vérifier que tous les objets structurés sont strictement validables.

Objets concernés :

```text
EntryState
RoutingDecision
ConservationRecord
SourceRecord
SourceAuditReport
ClassificationResult
ValidationReport
Run002Request
DeltaRecord
FinalProvisionalDecision
JournalPatch
AuditQueueRecord
AgentContract
AgentTask
AgentResult
BatchState
BatchReport
```

Critère : aucun objet invalide ne doit passer silencieusement.

### 1.3 Tests de règles protocolaires

Objet : vérifier les interdictions non négociables.

Cas minimaux :

```text
S-A sans source décisive -> rétrogradation ou blocage
S-A sans vérification indépendante -> rétrogradation sauf exception explicite
I-A sans preuve explicite d'improvisation centrale -> rétrogradation
C-A avec périmètre instable -> rétrogradation
RUN_002 sans cible -> invalide
JournalPatch avec écriture directe -> invalide
source plateforme utilisée comme source originale -> invalide
PDF ancien utilisé par défaut -> invalide
archive RUN utilisée comme source documentaire -> invalide
```

### 1.4 Tests d'orchestration

Objet : vérifier que le pipeline suit l'ordre prévu sans appeler de vrai modèle.

Mode obligatoire : fake/local adapter.

Doit tester :

```text
LOAD_MANIFEST
LOAD_PROJECT_STATE
CHECK_GUARDS
BUILD_BATCH_SCOPE
BUILD_AGENT_TASKS
ROUTING
CONSERVATION
SOURCE_AUDIT
CLASSIFICATION
DETERMINISTIC_VALIDATION
FINAL_PROVISIONAL_DECISION
JOURNAL_PATCH_BUILD
EXPORTS
```

Critère : l'orchestrateur peut planifier et simuler un lot sans RUN réel.

### 1.5 Tests golden set de prudence

Objet : vérifier que le système retrouve les prudences calibrées dans les mini-runs précédents.

Important : ces cas ne servent pas à retraiter les entrées. Ils servent à tester le comportement du système.

---

## 2. Golden set minimal

### 2.1 Garde-fous post-005

Cas :

```text
026
030
032
```

Attendus :

```text
026 : ne doit pas être traité comme nouveau
030 : ne doit pas être traité comme nouveau
032 : ne doit pas apparaître comme RUN_001/RUN_002 fait
```

Objectif : empêcher une régression d'état projet.

### 2.2 Fiches familles / sous-pistes

Cas de calibration :

```text
005
006
049
096
```

Attendus généraux :

```text
ne pas produire fiche pratique directe par défaut
conserver parent / sous-pistes
signaler risque de perte de données
produire ConservationRecord
```

Objectif : empêcher la réduction de familles ou agrégats complexes.

### 2.3 Contrôles de périmètre

Cas de calibration :

```text
007
013
```

Attendus généraux :

```text
type_unite_RUN = controle_perimetre ou décision équivalente
pas de fiche finale directe
question documentaire prioritaire obligatoire
publication consolidée impossible à ce stade
```

Objectif : empêcher une fiche sur périmètre instable.

### 2.4 Mécanismes / passerelles

Cas de calibration :

```text
012
048
```

Attendus généraux :

```text
alerte_passerelle = true si pertinent
ne pas forcer fiche pratique
conserver liens vers familles / pratiques apparentées
```

Objectif : ne pas convertir un mécanisme transversal en entrée isolée trop étroite.

### 2.5 Alias / doublons / ambiguïtés

Cas de calibration :

```text
125
```

Attendus généraux :

```text
alerte_doublon ou alerte_passerelle si pertinent
RUN documentaire direct interdit avant résolution
JournalPatch possible uniquement après décision contrôlée
```

Objectif : éviter doublons, fusions abusives et retraitements incohérents.

---

## 3. Structure d'un GoldenSetCase

Objet cible :

```yaml
object_type: GoldenSetCase
schema_version: v0.2.3-auto
case_id: string
id_entree_original: string
titre_original_exact: string | null
purpose: string
input_fixture_refs: list[string]
expected_must: list[string]
expected_must_not: list[string]
expected_alerts: list[string]
expected_publication_status: string | null
notes: string | null
```

Exemple conceptuel :

```yaml
case_id: GOLDEN_032_RESERVE
id_entree_original: "032"
purpose: vérifier que 032 reste réserve non RUN fait
expected_must:
  - journal lu
  - entrée reconnue
  - pas de RUN_001/RUN_002 fait
expected_must_not:
  - traiter comme RUN fait
  - produire JournalPatch de traitement terminé
```

---

## 4. Tests négatifs obligatoires

Les tests négatifs doivent prouver que le système refuse les mauvaises sorties.

### 4.1 Source

```text
plateforme_acces comme source_originale -> rejet
source_legacy_optionnelle comme source décisive automatique -> rejet
source globale utilisée pour preuve spécifique sans justification -> alerte ou rejet
```

### 4.2 Classification

```text
I-A sans preuve explicite -> rétrograde I-B
S-A sans source décisive -> rétrograde S-B
C-A sans périmètre stable -> rétrograde C-B1
D-B/C-B2 avec publication libre -> publication bloquée ou audit rouge
```

### 4.3 Journal

```text
JournalPatch nb_entries incohérent -> rejet
JournalPatch contains_direct_journal_write true -> rejet
JournalPatch avec doublon d'ID -> rejet
```

### 4.4 Orchestration

```text
agent sans output_schema -> rejet
agent qui veut écrire journal -> rejet
batch sans batch_id -> rejet
résultat agent non parseable -> erreur récupérable ou bloquante
```

---

## 5. Tests de fake adapter Agents SDK

Avant tout appel modèle réel, créer un adaptateur local qui renvoie des sorties contrôlées.

Objectifs :

```text
tester l'orchestrateur sans coût API
tester les schémas
tester les erreurs
tester les reprises
tester les exports
```

Comportements à simuler :

```text
résultat valide
résultat schema_invalid
résultat non parseable
résultat avec alerte source
résultat avec RUN_002 requis
résultat bloquant publication
```

Le fake adapter doit être obligatoire dans les tests CI/local.

---

## 6. Tests de reprise

Le système doit pouvoir reprendre un batch interrompu.

Cas à tester :

```text
interruption après routing
interruption après source audit
interruption après validation
interruption avant export
interruption avant JournalPatch
```

Attendus :

```text
BatchState conservé
étapes déjà terminées non rejouées sauf demande explicite
artefacts existants reconnus
commande replay générée
aucune écriture journal directe
```

---

## 7. Tests d'export

Chaque batch doit produire des artefacts cohérents.

Exports attendus :

```text
master.json
batch_report.json
journal_patch.json si nécessaire
audit_queue.json si nécessaire
export_lisible.xlsx
export_light.csv
logs
```

Tests :

```text
JSON parseable
schémas valides
nombre d'entrées cohérent
JournalPatch séparé
aucun fichier source modifié
```

---

## 8. Tests anti-réduction culturelle

Ce sont les tests les plus difficiles et les plus importants.

Ils ne doivent pas prétendre résoudre automatiquement toute nuance, mais vérifier que le système ralentit ou bloque quand la nuance est menacée.

Alertes attendues :

```text
risque_reduction_culturelle
risque_perte_donnees
fiche_famille_a_conserver
perimetre_instable
source_insuffisante
contexte_culturel_insuffisant
```

Exemples de comportements à encourager :

```text
fiche-cadre plutôt que fiche pratique
réserve plutôt que surclassement
RUN_002 ciblé plutôt que validation forte
publication différée plutôt que publication fragile
```

---

## 9. Critères de passage avant implémentation SDK réelle

Avant d'appeler réellement l'Agents SDK / Responses API, il faut :

```text
1. contrats JSON validés en Pydantic
2. fake adapter opérationnel
3. tests de règles protocolaires verts
4. tests JournalPatch verts
5. tests post-005 verts
6. au moins un batch dry-run simulé sans appel modèle
7. aucun usage par défaut du PDF ancien
8. aucune écriture directe journal possible
```

---

## 10. Critères de passage avant production par lot

Avant un vrai batch expérimental :

```text
1. golden set minimal vert
2. exports testés
3. reprise testée
4. erreurs récupérables testées
5. audit_queue testée
6. JournalPatch séparé testé
7. rapport batch lisible généré
8. humain capable de relire les décisions
```

---

## 11. Rôle de Codex dans les tests

Codex peut être utilisé pour :

```text
écrire les tests unitaires
écrire les fixtures
générer fake adapter
corriger les échecs pytest
refactorer les modèles
ajouter des tests négatifs
```

Codex ne doit pas être utilisé pour :

```text
inventer le golden set
changer les attendus méthodologiques
décider qu'une pratique est stable
réduire une famille complexe pour faire passer un test
```

---

## 12. Prochaine étape

Implémenter les contrats Pydantic nécessaires aux tests :

```text
GoldenSetCase
AgentContract
AgentTask
AgentResult
BatchState
BatchReport
```

Puis écrire les tests sans appel modèle.
