# AUDIT_CONCEPTION_AVANT_CODEX_v0.2.3-auto

Statut : audit de cohérence avant délégation Codex  
Objet : identifier ce qui est solide, ce qui doit être corrigé, ce qui doit être reporté, et décider si Codex 001 peut être lancé.

---

## 0. Verdict synthétique

```text
GO conception : oui
GO Codex 001 : oui, après corrections mineures déjà identifiées
GO Codex 002+ : non, attendre validation de Codex 001
GO appel OpenAI réel : non
GO traitement candidats : non
GO RUN : non
```

Raison : la conception est suffisamment stabilisée pour implémenter les contrats Pydantic, mais pas encore pour créer une orchestration réelle ou appeler le SDK.

---

## 1. Points solides

### 1.1 Doctrine projet correctement recentrée

Le système vise une base prudente, relationnelle et auditable sur des pratiques humaines complexes, pas une génération rapide de fiches.

Points solides :

```text
classer ≠ réduire
documenter ≠ valider définitivement
conserver ≠ créer une fiche
scinder ≠ perdre le parent
fusionner ≠ effacer les variantes
RUN possible ≠ fiche pratique prête
```

### 1.2 Architecture générale saine

Décision solide :

```text
orchestrateur déterministe Python
+ agents spécialisés sous contrat
+ validation Pydantic
+ règles déterministes
+ exports séparés
+ JournalPatch sans écriture directe
```

### 1.3 Codex correctement borné

Codex est cadré comme exécutant technique.

Première mission sûre :

```text
Mission Codex 001 — Contrats Pydantic SDK
```

Elle ne traite aucune entrée, ne lance aucun RUN, ne modifie aucune source et n'appelle pas OpenAI.

---

## 2. Corrections à appliquer avant ou pendant Codex 001

### C-001 — Statut du PDF ancien

Problème repéré : le manifest décrivait encore le PDF ancien comme `documentary_reference_active`.

Correction décidée :

```yaml
status: legacy_optional_reference
role: deprecated_context_reference
layer: legacy_reference
may_be_used_as_documentary_source: false
requires_explicit_activation: true
required_for_bootstrap: false
```

Règle : ce fichier ne doit pas bloquer le bootstrap, ne doit pas être utilisé par défaut et ne doit jamais servir de source décisive automatique.

Statut : corrigé dans le manifest.

---

### C-002 — Agents à rétrograder en modules déterministes

Problème repéré : la liste d'agents peut encourager une société d'agents trop autonome.

Correction recommandée :

Agents probables :

```text
RoutingAgent
ConservationAgent
SourceAuditAgent
ClassificationAgent
SynthesisAgent prudent
```

Modules déterministes :

```text
Validation
DeltaBuilder
JournalPatchBuilder
BatchReporter
Exporters
```

À suspendre :

```text
SourceDiscoveryAgent
```

Remplacement recommandé :

```text
SourceCandidateProvider
```

Raison : la découverte documentaire automatique est volatile et risquée. Elle ne doit pas apparaître trop tôt dans l'architecture exécutée.

Statut : à répercuter dans les docs avant Codex 002, non bloquant pour Codex 001.

---

### C-003 — Valeurs machine ASCII

Problème repéré : certains enums de `models.py` contiennent des accents ou caractères fragiles pour JSON/CSV/XLSX multi-outils.

Exemples fragiles :

```text
accepté_avec_prudence
à_revoir
publication_bloquée
```

Décision recommandée :

```text
valeurs machine ASCII : accepte_avec_prudence, a_revoir, publication_bloquee
labels humains séparés si nécessaire
```

Statut : à traiter dans `contracts/` pendant Codex 001. Ne pas forcément casser immédiatement `models.py`, qui peut rester compatibilité provisoire.

---

### C-004 — Hiérarchie interne des documents

Problème repéré : plusieurs documents se recouvrent.

Hiérarchie recommandée :

```text
1. REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md
2. PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md
3. CONTRATS_JSON_v0.2.3-auto.md
4. STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md
5. SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md
6. FEUILLE_ROUTE_IMPLEMENTATION_SDK_v0.2.3-auto.md
7. MISSIONS_CODEX_v0.2.3-auto.md
8. CHECKLIST_VALIDATION_AVANT_CODEX_v0.2.3-auto.md
```

À faire : marquer `docs/ARCHITECTURE_SDK_v0.2.3-auto.md` comme superseded ou le supprimer plus tard.

Statut : non bloquant pour Codex 001.

---

### C-005 — Manifest local vs manifest canonique

Problème repéré : le manifest actuel colle aux noms locaux réels, y compris `(1)` et nom court du journal.

C'était utile pour débloquer localement, mais fragile à long terme.

Architecture future recommandée :

```text
data_manifest.example.yaml  -> noms canoniques / rôles / statuts
data_manifest.local.yaml    -> chemins réels locaux, ignoré par Git
```

Statut : dette technique acceptée. Ne pas traiter avant Codex 001.

---

## 3. Points à ne pas corriger maintenant

### N-001 — Publication consolidée

Il manque une grille détaillée de publication, mais elle n'est pas nécessaire pour Codex 001.

À traiter avant production réelle :

```text
publiable
publiable_avec_note
interne_seulement
publication_differee
publication_bloquee
```

### N-002 — Source discovery automatique

Ne pas implémenter maintenant.

Le système peut d'abord fonctionner avec :

```text
sources fournies
fixtures de tests
source audit sur objets déjà présents
```

### N-003 — Application réelle JournalPatch

Ne pas implémenter maintenant.

Le système doit d'abord produire des `JournalPatch` séparés et validés.

---

## 4. Risques si on lance Codex trop tôt

```text
création de trop d'agents
validation confiée à un modèle plutôt qu'à des règles
valeurs enum incohérentes
réintroduction du PDF ancien comme source
scope de batch implicite
confusion dry-run / traitement réel
```

Mesure : commencer seulement par Codex 001.

---

## 5. Prompt Codex 001 ajusté après audit

Ajouter à la mission Codex 001 :

```text
Important : dans les nouveaux contrats, utilise des valeurs machine ASCII pour les enums.
Exemple : accepte_avec_prudence, a_revoir, publication_bloquee.
Si un label humain accentué est nécessaire, ajoute un champ label ou description séparé.
Ne modifie pas models.py sauf nécessité minimale ; préfère créer contracts/ et préserver la compatibilité existante.
Ne crée pas SourceDiscoveryAgent, AgentRegistry, FakeAdapter ou orchestration dans cette mission.
```

---

## 6. Décision Go / No-Go

### GO Codex 001

Oui, sous conditions :

```text
mission limitée aux contrats Pydantic
pas de réseau
pas de traitement d'entrée
pas de journal
pas de RUN
pas de modification data/local_files
pas d'affaiblissement des tests existants
```

### NO-GO Codex 002+

Oui, tant que Codex 001 n'est pas relu et vert.

---

## 7. Prochaine action recommandée

Deux options acceptables :

```text
Option A : lancer Codex 001 avec le prompt ajusté.
Option B : implémenter manuellement Codex 001 dans une PR/commit contrôlé.
```

Option recommandée : Codex 001, parce que la mission est maintenant assez bornée et testable.
