# CHECKLIST_VALIDATION_AVANT_CODEX_v0.2.3-auto

Statut : checklist de passage avant délégation à Codex  
Objet : vérifier que la conception est assez stable pour confier une mission d'implémentation bornée.

---

## 0. Principe

Codex ne doit intervenir que si la mission est :

```text
bornée
testable
réversible
sans décision doctrinale
sans accès destructif aux sources
sans appel modèle réel non prévu
```

Cette checklist sert à éviter de transformer Codex en agent qui improvise l'architecture.

---

## 1. Documents de référence présents

Avant Codex, vérifier que ces documents existent dans `docs/` :

```text
PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md
CONTRATS_JSON_v0.2.3-auto.md
STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md
SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md
FEUILLE_ROUTE_IMPLEMENTATION_SDK_v0.2.3-auto.md
MISSIONS_CODEX_v0.2.3-auto.md
```

Critère : chaque mission Codex doit renvoyer explicitement vers ces documents.

---

## 2. Points doctrinaux à verrouiller

### 2.1 Intention du projet

Validé si :

```text
le système vise la production d'une base prudente et auditable
le système ne vise pas seulement l'accélération de fiches
le système respecte la complexité des pratiques humaines
```

### 2.2 Non-réduction

Validé si le système conserve :

```text
fiche pratique
fiche-cadre
fiche-famille
mécanisme-passerelle
contrôle périmètre
alias/doublon
réserve
audit humain
publication différée
```

### 2.3 RUN

Validé si :

```text
RUN possible ≠ fiche pratique prête
type_unite_RUN obligatoire avant RUN
RUN_002 toujours ciblé
DELTA obligatoire si modification significative
```

### 2.4 Sources

Validé si :

```text
source originale ≠ plateforme d'accès
S-A exige source décisive + vérification indépendante
I-A exige preuve explicite d'improvisation centrale
PDF ancien non utilisé par défaut
archives RUN non sources documentaires
```

---

## 3. Points techniques à verrouiller

### 3.1 Orchestrateur

Validé si :

```text
l'orchestrateur Python gouverne le flux
les agents ne décident pas le workflow
les agents ne modifient pas l'état projet
les agents produisent seulement des objets structurés
```

### 3.2 Contrats

Validé si :

```text
chaque sortie agent a un object_type
chaque sortie agent a une schema_version
chaque sortie agent est validable par Pydantic
les textes libres ne portent pas seuls les décisions
```

### 3.3 Journal

Validé si :

```text
journal actif lu en lecture seule
JournalPatch séparé
aucune écriture directe journal
ancien journal MINI_RUN_004 ignoré pour pilotage courant
post-005 validé par garde-fous
```

### 3.4 Tests

Validé si :

```text
tests existants verts
fake adapter prévu avant OpenAI réel
golden set de prudence prévu
aucun test ne dépend d'un appel réseau
aucun test ne modifie data/local_files
```

---

## 4. Stop conditions avant Codex

Ne pas lancer Codex si :

```text
une règle méthodologique est encore floue
la mission demande de choisir des candidats
la mission demande de traiter une entrée réelle
la mission demande un RUN
la mission demande d'écrire dans le journal
la mission suppose l'utilisation du PDF ancien
la mission peut modifier data/local_files
la mission nécessite un appel OpenAI réel
```

---

## 5. Première mission autorisée

La première mission autorisée est :

```text
Mission Codex 001 — Contrats Pydantic SDK
```

Raison :

```text
elle ne traite aucune entrée
elle ne lance aucun RUN
elle ne lit aucune nouvelle source documentaire
elle ne modifie pas le journal
elle ne nécessite aucun appel modèle
elle transforme seulement les contrats validés en modèles testables
```

---

## 6. Prompt court de lancement Codex 001

Version courte :

```text
Implémente Mission Codex 001 depuis docs/MISSIONS_CODEX_v0.2.3-auto.md.
Respecte strictement les documents d'architecture dans docs/.
N'ajoute aucun appel OpenAI, ne traite aucune entrée, ne modifie pas data/local_files, ne modifie pas le journal.
Ajoute les tests Pydantic nécessaires et termine par pytest.
```

Version longue : utiliser le prompt complet de `docs/MISSIONS_CODEX_v0.2.3-auto.md`.

---

## 7. Vérification après Codex 001

Après retour Codex, vérifier :

```text
1. fichiers modifiés uniquement dans src/dico_impro/contracts/ et tests associés, sauf justification ;
2. aucun fichier data/local_files modifié ;
3. aucun appel OpenAI ajouté ;
4. aucun changement de règles dans validators.py sans demande ;
5. aucun test supprimé ;
6. pytest vert ;
7. modèles invalides bien rejetés ;
8. modèles valides acceptés ;
9. rapport Codex clair sur limites et choix.
```

---

## 8. Décision Go / No-Go

### GO Codex 001 si :

```text
documents de conception présents
mission bornée
aucun point doctrinal bloquant
tests actuels verts localement
utilisateur accepte délégation Codex
```

### NO-GO si :

```text
besoin de corriger la doctrine
désaccord sur les contrats
incertitude sur le rôle d'un agent
risque de traitement réel prématuré
risque d'appel modèle prématuré
```

---

## 9. Note de prudence

Même après Codex 001, l'autorité reste :

```text
protocole v0.2.3
plan architecture SDK
contrats JSON
stratégie de tests
feuille de route
```

Le code n'est accepté que s'il matérialise ces documents sans les contredire.
