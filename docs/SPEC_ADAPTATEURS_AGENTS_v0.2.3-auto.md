# SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto

Statut : document de conception technique avant implémentation  
Objet : définir comment brancher des agents SDK sans leur donner le contrôle intellectuel ou méthodologique du projet.

---

## 0. Principe central

L'adaptateur agent est une frontière.

Il sert à envoyer une tâche bornée à un modèle et à récupérer un objet structuré.

Il ne sert pas à :

```text
choisir les règles du projet
modifier le journal
décider la publication consolidée
inventer de nouvelles catégories
réinterpréter les sources actives
changer la stratégie de lot
```

Le système doit pouvoir fonctionner en mode test sans appel modèle grâce à un fake adapter.

---

## 1. Architecture d'adaptation

```text
Orchestrateur déterministe
        ↓
AgentRegistry
        ↓
AgentContract
        ↓
AgentTask
        ↓
AgentAdapter
        ↓
Raw model response ou fake response
        ↓
AgentResult
        ↓
Validation Pydantic
        ↓
QualityGate
        ↓
Artefacts batch
```

L'orchestrateur ne reçoit jamais directement du texte libre comme décision.

Toute réponse doit être convertie en `AgentResult`, puis validée.

---

## 2. Interfaces conceptuelles

### 2.1 AgentAdapter

Responsabilité : exécuter une tâche agent et retourner un `AgentResult`.

Méthodes conceptuelles :

```text
run_task(task: AgentTask, contract: AgentContract) -> AgentResult
validate_capabilities(contract: AgentContract) -> AdapterCapabilityReport
```

Interdictions :

```text
écrire un fichier source
écrire le journal actif
modifier le manifest
changer le batch state sans passer par l'orchestrateur
```

### 2.2 FakeAgentAdapter

Responsabilité : simuler les réponses agent localement.

Utilisation obligatoire pour :

```text
tests unitaires
tests d'orchestration
tests de reprise
tests erreurs
tests golden set
```

Comportements à simuler :

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

### 2.3 OpenAIAgentAdapter

Responsabilité : appeler le SDK / Responses API dans une enveloppe contrôlée.

Il doit :

```text
construire le prompt système de l'agent depuis AgentContract
injecter uniquement les entrées autorisées
exiger une sortie JSON compatible expected_schema
récupérer la trace brute dans une référence séparée
ne jamais accepter une décision non validée
```

Il ne doit pas :

```text
laisser le modèle choisir le schéma
laisser le modèle choisir la suite du workflow
laisser le modèle accéder à des fichiers interdits
réutiliser le PDF ancien sans activation explicite
```

---

## 3. AgentRegistry

Objet : registre des agents disponibles.

Champs conceptuels :

```text
agent_name
agent_version
contract_ref
adapter_type
enabled
default_temperature
max_retries
expected_schema
```

Règles :

- un agent absent du registry ne peut pas être appelé ;
- un agent disabled ne peut pas être appelé ;
- un agent sans contrat validé ne peut pas être appelé ;
- un agent dont la sortie attendue n'existe pas dans les contrats JSON est invalide.

---

## 4. Prompt système par agent

Chaque agent reçoit un prompt système minimal et strict.

Structure recommandée :

```text
1. mission de l'agent
2. limites de décision
3. entrées autorisées
4. fichiers interdits
5. objet JSON attendu
6. règles de prudence
7. interdictions explicites
8. consigne : ne pas produire de texte hors JSON
```

Le prompt ne doit pas réexpliquer tout le projet si cela augmente le risque de dérive. Il doit fournir le contexte nécessaire et les interdictions pertinentes.

---

## 5. Handoffs

Un handoff n'est pas une conversation libre entre agents.

C'est un passage structuré d'un objet validé à une autre tâche.

Exemple :

```text
RoutingDecision validé
        ↓
ConservationAgent si risque_perte_donnees ou fiche_famille
        ↓
SourceDiscoveryAgent si RUN documentaire autorisé
        ↓
SourceAuditAgent
        ↓
ClassificationAgent
        ↓
Validation déterministe
```

Règles :

- un agent ne déclenche pas directement le suivant ;
- l'orchestrateur décide du handoff ;
- chaque handoff est inscrit dans `BatchState` ;
- un handoff peut être refusé par QualityGate.

---

## 6. Gestion des erreurs

### 6.1 Erreurs récupérables

```text
sortie JSON non parseable
champ manquant
valeur enum invalide
timeout modèle
réponse incomplète
source proposée insuffisante
```

Action : retry limité, puis erreur récupérable dans `BatchState`.

### 6.2 Erreurs bloquantes

```text
tentative d'écriture journal
utilisation fichier interdit
contradiction protocolaire forte
publication consolidée proposée sans autorisation
source plateforme déclarée source originale malgré garde-fou
```

Action : stop de l'entrée ou du lot selon gravité.

### 6.3 Erreurs de prudence

```text
surclassement probable
perte sous-piste
fiche famille réduite
improvisation centrale non prouvée
périmètre instable
```

Action : alerte, RUN_002 ciblé ou publication différée.

---

## 7. Retry policy

Les retries doivent rester prudents.

Règles :

```text
max_retries par agent défini dans registry
retry autorisé pour erreur syntaxique
retry autorisé pour JSON non parseable
retry interdit pour forcer une décision forte
retry interdit après violation protocolaire grave
```

Un retry doit conserver la trace de l'échec précédent.

---

## 8. Traces et audit

Chaque appel agent doit produire ou référencer :

```text
task_id
agent_name
agent_version
contract_version
input_hash
output_hash
raw_trace_ref
validation_status
warnings
duration_ms si disponible
```

Les traces brutes ne deviennent pas vérité projet. Elles servent à l'audit.

---

## 9. Sécurité documentaire

Avant d'appeler un agent, l'orchestrateur construit `allowed_files` et `forbidden_files`.

Règles minimales :

```text
journal actif : lecture état seulement, jamais source documentaire
archives RUN : traces non-actives, jamais source documentaire
PDF ancien : interdit par défaut
outputs précédents : consultables seulement comme artefacts, pas sources
manifest : autorité technique des rôles fichiers
```

Un agent ne doit recevoir que le contenu strictement nécessaire.

---

## 10. Mode dry-run

Le mode dry-run est obligatoire avant production.

Il doit permettre :

```text
préparer les tâches agent
valider les contrats
simuler les handoffs
produire BatchState
produire BatchReport simulé
ne faire aucun appel modèle réel si fake adapter activé
ne modifier aucun fichier source
```

Commande cible :

```text
dico-impro plan-batch --dry-run
```

Cette commande ne doit pas identifier manuellement les candidats. Elle doit appliquer une stratégie de lot explicitement fournie ou prévalidée.

---

## 11. Mode réel contrôlé

Un appel modèle réel n'est autorisé que si :

```text
contrats Pydantic validés
fake adapter vert
tests golden set verts
manifest ok
journal garde-fous ok
aucune écriture directe journal possible
stratégie de lot explicite
```

Le mode réel doit rester batché et traçable.

---

## 12. Sortie d'un appel agent

Une sortie agent brute suit ce parcours :

```text
raw_response
→ parse JSON
→ AgentResult
→ payload Pydantic
→ validation protocolaire
→ validation sémantique ciblée
→ accepté / corrigé / rejeté / audit
```

Aucune étape ne peut être sautée.

---

## 13. Risques spécifiques au projet

### 13.1 Risque d'autorité excessive du modèle

Symptôme : le modèle décide qu'une entrée est stable parce que le texte semble convaincant.

Réponse système : validation déterministe + source audit + publication status séparé.

### 13.2 Risque de réduction culturelle

Symptôme : une pratique familiale ou contextuelle devient fiche pratique isolée.

Réponse système : ConservationAgent + golden set + alertes.

### 13.3 Risque de source faible

Symptôme : plateforme ou notice générale utilisée comme preuve décisive.

Réponse système : SourceAuditAgent + règles S-A / I-A.

### 13.4 Risque de dérive batch

Symptôme : le système commence à traiter des entrées hors stratégie.

Réponse système : BatchState + entries_scope + interdiction hors scope.

---

## 14. Implémentation recommandée

Modules cibles :

```text
src/dico_impro/agents/contracts.py
src/dico_impro/agents/registry.py
src/dico_impro/agents/adapters/base.py
src/dico_impro/agents/adapters/fake.py
src/dico_impro/agents/adapters/openai.py
src/dico_impro/agents/prompts.py
src/dico_impro/agents/quality_gates.py
```

Tests cibles :

```text
tests/test_agent_contracts.py
tests/test_agent_registry.py
tests/test_fake_adapter.py
tests/test_agent_quality_gates.py
tests/test_orchestration_dry_run.py
```

---

## 15. Décision avant codage

Avant implémentation, valider :

```text
1. liste finale des agents
2. liste finale des contrats
3. stratégie fake adapter
4. erreurs récupérables vs bloquantes
5. statut exact du mode dry-run
6. format minimal des traces
```
