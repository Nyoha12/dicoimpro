# Architecture SDK v0.2.3-auto

## Objectif

Construire le système de production automatisée de la base `dico impro`, pas avancer manuellement sur l'identification des candidats.

Le pipeline doit produire des objets contrôlés, auditables et rejouables :

- décisions de routage ;
- audits de sources ;
- validations automatiques ;
- deltas RUN_001/RUN_002 ;
- décisions finales provisoires ;
- patches de journal proposés, jamais écrits directement ;
- exports JSON/CSV/XLSX.

## Principe central

L'agent ne pilote pas l'état du projet.

Le pilotage est assuré par un orchestrateur déterministe Python. Les agents produisent uniquement des sorties structurées validées par schéma.

```text
Entrées locales -> Orchestrateur Python -> Agents spécialisés -> Validation Pydantic -> Exports contrôlés
```

## Couches

### 1. Couche déterministe

Responsabilités :

- lire le manifest ;
- lire les fichiers locaux en lecture seule ;
- préparer les tâches agent ;
- valider tous les JSON produits ;
- appliquer les règles automatiques ;
- générer les artefacts de sortie ;
- empêcher toute écriture directe dans le journal actif.

Modules déjà amorcés :

- `manifest.py` ;
- `journal_reader.py` ;
- `models.py` ;
- `validators.py` ;
- `journal.py` ;
- `cli.py`.

### 2. Couche Agents SDK

Responsabilités :

- exécuter des agents spécialisés ;
- forcer des sorties JSON structurées ;
- isoler les tâches ;
- tracer les étapes ;
- permettre reprise, audit et réexécution.

Agents prévus :

| Agent | Rôle | Sortie attendue |
|---|---|---|
| `RoutingAgent` | déterminer le type d'unité et le statut pré-RUN | `RoutingDecision` |
| `SourceAuditAgent` | qualifier les sources et plateformes d'accès | `SourceAuditReport` |
| `ClassificationAgent` | proposer D/S/I/C/E avec justification | `ClassificationInput` |
| `ValidationAgent` | expliquer les corrections automatiques | `ValidationReport` |
| `SynthesisAgent` | produire la fiche ou fiche-cadre | `FinalProvisionalDecision` |
| `DeltaAgent` | tracer les changements RUN_001/RUN_002 | `DeltaRecord[]` |
| `JournalPatchAgent` | proposer un patch de journal contrôlé | `JournalPatch` |

### 3. Couche orchestration

Responsabilités :

- définir les étapes d'un lot ;
- exécuter ou simuler un lot ;
- conserver les logs ;
- produire un répertoire de sortie par batch ;
- ne jamais décider sur la base d'un nom de dossier ;
- ne jamais traiter une archive RUN comme source active.

Étapes cibles :

```text
LOAD_MANIFEST
LOAD_PROJECT_STATE
BUILD_AGENT_TASKS
RUN_ROUTING_AGENT
RUN_SOURCE_AUDIT_AGENT
RUN_CLASSIFICATION_AGENT
APPLY_DETERMINISTIC_VALIDATION
BUILD_FINAL_DECISION
BUILD_DELTA_RECORDS
BUILD_JOURNAL_PATCH
WRITE_OUTPUT_ARTIFACTS
```

## Garde-fous non négociables

- Aucun agent ne modifie un fichier source.
- Le journal actif est lu en lecture seule.
- Un `JournalPatch` est une proposition, pas une écriture.
- Les fichiers anciens ou optionnels ne sont pas utilisés par défaut.
- Le PDF ancien n'est pas une source de production par défaut.
- Tout résultat agent doit passer par Pydantic avant d'être accepté.
- Les sorties doivent être rejouables et liées à un batch ID.

## Ce qu'on ne fait pas ici

- Pas de RUN réel tant que l'architecture n'est pas verrouillée.
- Pas d'identification manuelle des candidats.
- Pas de publication consolidée.
- Pas d'écriture dans le journal.
- Pas d'utilisation automatique du PDF ancien.
