# Revue architecture post-015 — dicoimpro v0.2.3-auto

Statut : revue documentaire post-Codex 015.  
Objet : consolider l'état courant, les garde-fous, les risques et les conditions
obligatoires avant tout futur travail sur un appel OpenAI réel ou sur des prompts réels.

Cette revue ne change aucun comportement de production. Elle ne crée aucun prompt, ne charge
aucun prompt, ne rend aucun prompt et n'active aucun accès modèle ou réseau.

---

## 1. Etat d'implémentation courant

Etat attendu au moment de cette revue :

```text
Codex 001 à Codex 015 sont fusionnés dans main.
pytest passe.
Etat courant de main : 232 tests passing.
Le dry-run CLI manuel post-015 a été validé par l'utilisateur.
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

Les seuls chemins autorisés après Codex 015 sont :

```text
1. fake CLI dry-run ;
2. mock OpenAI planning via client injecté uniquement ;
3. validation metadata-only de PromptPackage.
```

Ces chemins restent locaux, déterministes, sans OpenAI réel, sans réseau, sans prompt réel,
sans source discovery et sans écriture dans le journal actif.

## 4. Chemins actuellement interdits

Sont explicitement interdits dans l'état post-015 :

```text
- appel OpenAI réel ;
- appel réseau ;
- rendu ou chargement de prompt ;
- prompts.py ;
- SourceDiscoveryAgent ;
- RUN ;
- sélection de candidats ;
- écriture dans le journal actif ;
- accès data/local_files ;
- usage par défaut de l'ancien PDF ;
- export XLSX/CSV dans la couche d'automatisation ;
- application de JournalPatch.
```

Ces interdictions s'appliquent aussi aux tests, scripts, fixtures et chemins CLI, sauf
autorisation explicite dans une mission future dédiée.

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

## 6. Verdict Go/No-Go

```text
GO    - documentation et fixtures metadata désactivées ;
GO    - tests supplémentaires mock-only ;
NO-GO - OpenAI réel ;
NO-GO - prompts réels ;
NO-GO - source discovery ;
NO-GO - RUN.
```

Ce verdict ne donne aucune autorisation implicite pour activer un chemin modèle, prompt,
source ou journal.

## 7. Risques restants

```text
- les docs peuvent dériver de l'implémentation ;
- le chemin mock OpenAI ne doit pas être exposé dans le CLI ;
- PromptPackage doit rester désactivé jusqu'à un futur protocole d'activation explicite ;
- la politique sans accès aux données réelles n'est pas encore représentée par une sandbox runtime.
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
1. Ajouter des fixtures PromptPackage metadata-only, désactivées.
2. Ajouter un contrôle de synchronisation documentation/tests.
3. Ajouter éventuellement un script de smoke test CLI dry-run, fake-only.
```

Ces étapes restent documentaires ou mock-only. Elles ne doivent pas introduire de prompt
réel, de rendu/chargement de prompt, d'appel OpenAI réel, d'appel réseau, de lecture de
données réelles, de RUN, d'application de JournalPatch, de source discovery, de sélection
de candidats ou d'export XLSX/CSV.
