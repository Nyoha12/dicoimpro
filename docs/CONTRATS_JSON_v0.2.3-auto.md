# CONTRATS_JSON_v0.2.3-auto

Statut : document de conception des objets structurés  
Portée : définir les sorties techniques attendues du système SDK avant implémentation.  
Principe : le JSON validé est la vérité technique ; les fichiers XLSX/CSV sont des vues lisibles ou opératoires.

---

## 0. Principes généraux

Tous les objets produits par le système doivent être :

```text
structurés
validables
versionnés
traçables
rejouables
auditablement prudents
```

Le texte libre peut exister, mais il ne porte jamais seul une décision.

Chaque objet doit contenir au minimum :

```text
object_type
schema_version
batch_id
created_by
```

Lorsque l'objet concerne une entrée :

```text
id_entree_original
titre_original_exact
```

Lorsqu'un objet exprime une décision :

```text
justification_courte
confidence_level ou niveau_prudence
alertes
```

Lorsqu'un objet s'appuie sur une source :

```text
source_refs
audit_source_status
```

---

## 1. Conventions communes

### 1.1 Identifiants

```text
id_entree_original : chaîne normalisée sur 3 chiffres si possible, ex. "026"
batch_id : ex. "BATCH_2026_05_21_DRYRUN_001"
task_id : ex. "TASK_BATCH_001_026_ROUTING"
result_id : ex. "RESULT_TASK_BATCH_001_026_ROUTING"
delta_id : ex. "DELTA_026_001"
source_id : ex. "SRC_026_001"
```

### 1.2 Niveaux de prudence

Valeurs proposées :

```text
faible
moyen
élevé
bloquant
```

Usage :

- `faible` : alerte informative ;
- `moyen` : prudence requise mais traitement possible ;
- `élevé` : audit recommandé ou RUN_002 ciblé ;
- `bloquant` : publication consolidée interdite.

### 1.3 Statuts de validation

Valeurs proposées :

```text
schema_valid
schema_invalid
validé_sans_correction
validé_avec_corrections
run_002_auto_requis
non_publiable_en_l_etat
audit_humain_requis
```

### 1.4 Règle générale d'extension

Un champ nouveau peut être ajouté uniquement s'il ne remplace pas un champ existant et s'il ne change pas le sens d'une valeur contrôlée.

---

## 2. EntryState

Objet : représenter une entrée avant traitement, avec son état projet connu.

### Champs

```yaml
object_type: EntryState
schema_version: v0.2.3-auto
batch_id: string
id_entree_original: string
titre_original_exact: string
source_base_ref: string | null
triage_ref: string | null
journal_ref: string | null
statut_journal_connu: string | null
dernier_RUN_connu: string | null
a_ne_pas_retraiter_nouveau: boolean
est_archive_non_active: boolean
notes_etat: list[string]
alertes_initiales: list[string]
```

### Règles

- Si `a_ne_pas_retraiter_nouveau = true`, le système ne doit pas créer une tâche de traitement comme nouvelle entrée.
- `statut_journal_connu` n'est pas une validation documentaire ; c'est un état de pilotage.
- Une archive RUN ne peut pas rendre `est_archive_non_active = false`.

---

## 3. RoutingDecision

Objet : décider le type d'unité avant RUN.

### Champs

```yaml
object_type: RoutingDecision
schema_version: v0.2.3-auto
batch_id: string
id_entree_original: string
titre_original_exact: string
statut_unite_classable: enum
type_unite_RUN: enum
decision_pre_RUN: enum
run_autorise: boolean
run_interdit_raison: list[string]
question_documentaire_prioritaire: string | null
risque_perte_donnees: string | null
alerte_doublon: boolean
alerte_scission: boolean
alerte_passerelle: boolean
conservation_parent_requise: boolean
sous_pistes_a_conserver: list[string]
justification_courte: string
niveau_prudence: enum
```

### Valeurs contrôlées

`statut_unite_classable` :

```text
classable_comme_fiche_unique
fiche_famille_a_deplier
agregat_a_scinder
mecanisme_passerelle
doublon_ou_alias
a_verifier
```

`type_unite_RUN` :

```text
fiche_pratique
fiche_cadre
fiche_famille
mecanisme_passerelle
controle_perimetre
alias_doublon
```

`decision_pre_RUN` :

```text
pret_RUN_001_fiche_pratique
pret_RUN_001_fiche_cadre
mecanisme_passerelle
controle_perimetre_avant_RUN
rester_fiche_famille
verifier_alias_doublon
```

### Règles bloquantes

- `run_autorise = true` interdit si `type_unite_RUN` absent.
- `fiche_famille` ne doit pas devenir `pret_RUN_001_fiche_pratique` sans justification de scission.
- `alias_doublon` ne doit pas produire RUN documentaire direct.
- `controle_perimetre` ne doit pas produire une fiche finale.

---

## 4. ConservationRecord

Objet : protéger les nuances, sous-pistes, variantes et relations parent/enfant.

### Champs

```yaml
object_type: ConservationRecord
schema_version: v0.2.3-auto
batch_id: string
id_entree_original: string
titre_original_exact: string
parent_requis: boolean
parent_label: string | null
sous_pistes: list[string]
variantes_a_ne_pas_fusionner: list[string]
risques_perte: list[string]
risque_reduction_culturelle: boolean
recommendation_conservation: enum
justification_courte: string
```

### Valeurs `recommendation_conservation`

```text
conserver_parent
scinder_avec_parent
fusion_interdite
fiche_famille_a_conserver
fiche_cadre_recommandee
aucune_alerte_majeure
```

---

## 5. SourceRecord

Objet : décrire une source candidate avant audit.

### Champs

```yaml
object_type: SourceRecord
schema_version: v0.2.3-auto
batch_id: string
source_id: string
id_entree_original: string | null
titre_source: string
auteur_ou_institution: string | null
type_source: enum
url_ou_reference: string | null
plateforme_acces: string | null
langue: string | null
date_source: string | null
source_candidate_pour: list[string]
notes: string | null
```

### Valeurs `type_source`

```text
article_scientifique
ouvrage
archive_audio_video
notice_institutionnelle
source_primaire
source_secondaire
plateforme_acces
source_contextuelle
source_legacy_optionnelle
inconnue
```

### Règles

- Une plateforme d'accès ne peut pas être source originale.
- Une source `legacy_optionnelle` ne peut pas être décisive par défaut.
- Une source globale ne peut pas être réutilisée comme preuve spécifique sans justification.

---

## 6. SourceAuditReport

Objet : qualifier les sources et leur rôle réel.

### Champs

```yaml
object_type: SourceAuditReport
schema_version: v0.2.3-auto
batch_id: string
id_entree_original: string
sources_auditees: list[SourceAuditItem]
source_decisive_presente: boolean
verification_independante_presente: boolean
source_originale_identifiee: boolean
plateforme_confondue_avec_source: boolean
niveau_source_global: enum
audit_source_status: enum
alertes_source: list[string]
justification_courte: string
```

### SourceAuditItem

```yaml
source_id: string
role_source: enum
source_decisive: oui | non | partiel
verification_independante: boolean
est_plateforme_acces: boolean
est_source_originale: boolean
peut_soutenir_S_A: boolean
peut_soutenir_I_A: boolean
limites: list[string]
```

### Valeurs `role_source`

```text
source_originale
plateforme_acces
source_decisive
source_renfort
source_contexte
source_insuffisante
source_legacy_optionnelle
```

### Valeurs `audit_source_status`

```text
suffisant_pour_prudence
suffisant_pour_S_A
insuffisant_pour_S_A
source_originale_absente
plateforme_confondue
bloquant_publication
```

---

## 7. ClassificationResult

Objet : proposer ou recevoir D/S/I/C/E avec justification.

### Champs

```yaml
object_type: ClassificationResult
schema_version: v0.2.3-auto
batch_id: string
id_entree_original: string
titre_original_exact: string
indices_proposes:
  D: string | null
  S: string | null
  I: string | null
  C: string | null
  E: string | null
preuve_improvisation_centrale_explicitement_documentee: boolean
perimetre_stable: boolean
exception_S_A_justifiee: boolean
justification_D: string | null
justification_S: string | null
justification_I: string | null
justification_C: string | null
justification_E: string | null
source_refs: list[string]
alertes_classification: list[string]
```

### Règles

- `I-A` exige `preuve_improvisation_centrale_explicitement_documentee = true`.
- `S-A` exige source décisive et vérification indépendante, sauf exception explicitement justifiée.
- `C-A` exige `perimetre_stable = true`.
- Le modèle peut proposer un indice fort, mais la validation déterministe peut le rétrograder.

---

## 8. ValidationReport

Objet : appliquer les règles automatiques v0.2.3-auto.

### Champs

```yaml
object_type: ValidationReport
schema_version: v0.2.3-auto
batch_id: string
id_entree_original: string
validation_status: enum
indices_avant_validation: Indices
indices_apres_validation: Indices
corrections_automatiques: list[CorrectionAutomatique]
run_002_requis: boolean
run_002_cible: list[Run002Cible]
audit_queue_requis: boolean
audit_gravite: string | null
publication_bloquee: boolean
justification_courte: string
```

### CorrectionAutomatique

```yaml
champ: string
avant: string | null
apres: string | null
raison: string
regle: string
```

### Règles minimales

```text
V-S-001 : S-A interdit sans source décisive
V-S-002 : S-A interdit sans vérification indépendante sauf exception
V-I-001 : I-A interdit sans preuve explicite d'improvisation centrale
V-C-001 : C-A interdit si périmètre instable
V-D-001 : D non A peut bloquer publication
V-PUB-001 : C-B2 / C-C / C-D / C-X peuvent bloquer publication
```

---

## 9. Run002Request

Objet : demander un RUN_002 ciblé.

### Champs

```yaml
object_type: Run002Request
schema_version: v0.2.3-auto
batch_id: string
id_entree_original: string
requested_by: string
cibles: list[Run002Cible]
raison_generale: string
run_002_autorise: boolean
conditions_avant_run: list[string]
```

### Règles

- Un RUN_002 sans cible est invalide.
- Une cible doit nommer le champ ou la faiblesse.
- Un RUN_002 ne relance pas toute la fiche par défaut.

---

## 10. DeltaRecord

Objet : tracer une modification significative entre états.

### Champs

```yaml
object_type: DeltaRecord
schema_version: v0.2.3-auto
batch_id: string
delta_id: string
id_entree_original: string
champ_modifie: string
valeur_avant: string | null
valeur_apres: string | null
raison_delta: string
impact_decision: string
source_ou_regle_declencheuse: string | null
```

### Règles

Un delta est obligatoire si RUN_002 change :

```text
S
I
C
decision_finale_provisoire
type_unite_RUN
publication_status
```

---

## 11. FinalProvisionalDecision

Objet : décision de travail après validation, non publication consolidée.

### Champs

```yaml
object_type: FinalProvisionalDecision
schema_version: v0.2.3-auto
batch_id: string
id_entree_original: string
titre_original_exact: string
statut_traitement: enum
decision_finale_provisoire: enum
type_unite_RUN: enum
indices_finaux: Indices
publication_status: enum
audit_status: enum
note_prudence: string | null
deltas_associes: list[string]
alertes_associees: list[string]
justification_courte: string
```

### Valeurs `publication_status`

```text
publiable
publiable_avec_note
publication_bloquée
non_publiable_comme_fiche_pratique
publication_differee
```

---

## 12. JournalPatch

Objet : proposer une mise à jour contrôlée du journal, sans l'écrire.

### Champs

```yaml
object_type: JournalPatch
schema_version: v0.2.3-auto
batch_id: string
patch_id: string
active_journal_cible: string
mode: append_or_update_controlled
entries: list[JournalPatchEntry]
controle_patch: JournalPatchControl
```

### JournalPatchEntry

```yaml
id_entree_original: string
titre_original_exact: string
operation: append | update
statut_traitement: string
dernier_controle: string | null
dernier_RUN: string | null
decision_finale_provisoire: string
type_unite_RUN: string
lien_archive_RUN: string | null
remarque: string | null
a_ne_pas_retraiter_nouveau: boolean
```

### JournalPatchControl

```yaml
nb_entries: integer
contains_direct_journal_write: false
requires_human_review_before_publication: boolean
schema_valid: boolean
```

### Règles absolues

- `contains_direct_journal_write` doit toujours être `false`.
- Le patch ne modifie jamais le fichier journal actif.
- Le patch peut être exporté comme JSON/XLSX séparé.
- Un humain ou une procédure validée applique ensuite le patch si nécessaire.

---

## 13. AuditQueueRecord

Objet : placer un cas dans une file d'audit humain.

### Champs

```yaml
object_type: AuditQueueRecord
schema_version: v0.2.3-auto
batch_id: string
id_entree_original: string
audit_id: string
audit_gravite: enum
audit_reason: list[string]
blocking_for_publication: boolean
blocking_for_processing: boolean
recommended_action: string
linked_objects: list[string]
```

### Valeurs `audit_gravite`

```text
info
jaune
orange
rouge
```

---

## 14. AgentContract

Objet : définir ce qu'un agent a le droit de faire.

### Champs

```yaml
object_type: AgentContract
schema_version: v0.2.3-auto
agent_name: string
agent_version: string
mission: string
allowed_inputs: list[string]
required_output_schema: string
forbidden_actions: list[string]
quality_gates: list[string]
handoff_targets: list[string]
```

### Règles

- Un agent sans `required_output_schema` est interdit.
- Un agent sans `forbidden_actions` est incomplet.
- Un agent ne peut pas écrire dans le journal.
- Un agent ne peut pas décider seul une publication consolidée.

---

## 15. AgentTask

Objet : unité d'exécution pour un agent.

### Champs

```yaml
object_type: AgentTask
schema_version: v0.2.3-auto
task_id: string
batch_id: string
id_entree_original: string | null
task_type: string
agent_name: string
input_payload: object
allowed_files: list[string]
forbidden_files: list[string]
expected_schema: string
```

### Règles

- `expected_schema` doit correspondre au contrat agent.
- `forbidden_files` doit inclure les archives non actives si l'agent pourrait les confondre avec sources.
- Le PDF ancien est interdit sauf activation explicite.

---

## 16. AgentResult

Objet : résultat d'une tâche agent.

### Champs

```yaml
object_type: AgentResult
schema_version: v0.2.3-auto
result_id: string
task_id: string
batch_id: string
agent_name: string
schema_name: string
payload: object
warnings: list[string]
audit_notes: list[string]
raw_model_trace_ref: string | null
validation_status: string
```

### Règles

- `payload` doit être validé contre `schema_name`.
- Les warnings ne remplacent pas les champs structurés.
- Une sortie non parseable doit devenir erreur récupérable ou bloquante selon l'étape.

---

## 17. BatchState

Objet : état de traitement d'un lot.

### Champs

```yaml
object_type: BatchState
schema_version: v0.2.3-auto
batch_id: string
created_at: string
status: enum
steps_completed: list[string]
entries_scope: list[string]
artifacts: list[string]
errors_recoverable: list[string]
errors_blocking: list[string]
replay_command: string | null
```

### Valeurs `status`

```text
planned
running
completed_with_warnings
completed_clean
failed_recoverable
failed_blocking
cancelled
```

---

## 18. BatchReport

Objet : rapport consolidé d'un lot.

### Champs

```yaml
object_type: BatchReport
schema_version: v0.2.3-auto
batch_id: string
protocol_version: string
automation_layer: string
entries_total: integer
entries_processed: integer
entries_skipped: integer
entries_blocked: integer
run_002_requested: integer
publication_blocked: integer
audit_queue_count: integer
journal_patch_id: string | null
artifacts: list[string]
summary_human: string
warnings: list[string]
```

---

## 19. Ordre minimal de validation d'un résultat

```text
1. JSON parseable
2. object_type reconnu
3. schema_version compatible
4. validation Pydantic
5. validation protocolaire
6. validation sémantique ciblée
7. décision acceptée / corrigée / bloquée
8. export
```

---

## 20. Décision d'implémentation

Avant de coder les agents SDK, implémenter les contrats suivants :

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
```

Les contrats déjà partiellement présents dans `models.py` devront être réalignés avec ce document.

Aucune nouvelle logique d'exécution ne doit être ajoutée avant validation de ces contrats.
