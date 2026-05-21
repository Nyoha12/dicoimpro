# PROMPT_CODEX_002_AGENT_REGISTRY_FAKE_ADAPTER

Statut : prompt prêt à copier-coller dans Codex  
Mission : implémentation strictement bornée de AgentRegistry + FakeAgentAdapter, sans appel OpenAI et sans orchestration.

---

## Prompt

```text
Tu travailles dans le repo dicoimpro.

Objectif : créer la mécanique agent locale minimale pour v0.2.3-auto : AgentRegistry, AgentAdapter, FakeAgentAdapter et QualityGate local, sans appel OpenAI réel, sans orchestration dry-run, sans sélection de candidats.

Lis d'abord, dans cet ordre :
1. docs/README.md
2. docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md
3. docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md
4. docs/CONTRATS_JSON_v0.2.3-auto.md
5. docs/STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md
6. docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md
7. docs/FEUILLE_ROUTE_IMPLEMENTATION_SDK_v0.2.3-auto.md
8. docs/AUDIT_CONCEPTION_AVANT_CODEX_v0.2.3-auto.md
9. docs/MISSIONS_CODEX_v0.2.3-auto.md

Important : docs/ARCHITECTURE_SDK_v0.2.3-auto.md est superseded. Ne l'utilise pas comme référence principale.

État préalable attendu : Mission Codex 001 est intégrée sur main et pytest passe.

À faire :
1. Créer les modules :
   - src/dico_impro/agents/__init__.py
   - src/dico_impro/agents/registry.py
   - src/dico_impro/agents/adapters/__init__.py
   - src/dico_impro/agents/adapters/base.py
   - src/dico_impro/agents/adapters/fake.py
   - src/dico_impro/agents/quality_gates.py
2. Créer une interface/protocole AgentAdapter avec une méthode run_task(task: AgentTask, contract: AgentContract) -> AgentResult.
3. Créer AgentRegistry.
   - Il enregistre seulement des AgentContract déjà valides.
   - Il doit refuser un agent disabled.
   - Il doit refuser un agent absent.
   - Il doit vérifier la cohérence agent_name / expected_schema au minimum.
4. Créer FakeAgentAdapter.
   - Il consomme AgentTask + AgentContract.
   - Il retourne toujours un AgentResult Pydantic valide pour les scénarios contrôlés.
   - Il ne lit aucun fichier local.
   - Il n'appelle aucun réseau.
5. Simuler au minimum les scénarios :
   - success_valid
   - success_with_warning
   - schema_invalid
   - non_parseable_output
   - protocol_violation
   - source_confusion
   - publication_blocking
   - run_002_required
6. Créer une classification simple des résultats/erreurs dans quality_gates.py :
   - récupérable
   - bloquant
   - prudence
   - ok
7. Ajouter les tests :
   - tests/test_agent_registry.py
   - tests/test_fake_adapter.py
   - tests/test_agent_quality_gates.py
8. Les tests doivent vérifier :
   - registry accepte un contrat valide ;
   - registry refuse un agent absent ;
   - registry refuse un agent disabled ;
   - FakeAgentAdapter produit AgentResult valide ;
   - chaque scénario fake attendu est couvert ;
   - les erreurs sont classées correctement ;
   - aucun objet sans schema_version ou object_type ne passe ;
   - aucune opération fichier/source/journal n'est réalisée.
9. Lancer pytest.

Interdictions absolues :
- ne lance aucun RUN ;
- n'identifie aucun candidat ;
- ne traite aucune entrée réelle ;
- ne modifie pas le journal actif ;
- ne modifie aucun fichier dans data/local_files ;
- n'utilise pas le PDF ancien ;
- n'ajoute aucun appel OpenAI ;
- n'ajoute aucun appel réseau ;
- ne crée pas OpenAIAdapter ;
- ne crée pas src/dico_impro/agents/prompts.py ;
- ne crée pas de CLI dry-run ;
- ne crée pas de package orchestration ;
- ne crée pas de package exports ;
- ne crée pas SourceDiscoveryAgent ;
- ne transforme pas Validation, DeltaBuilder, JournalPatchBuilder ou BatchReporter en agents autonomes ;
- ne supprime aucun test existant ;
- n'affaiblis pas les règles existantes pour faire passer pytest.

Critères de réussite :
- pytest passe ;
- les tests existants restent verts ;
- les nouveaux tests couvrent tous les scénarios fake listés ;
- aucun fichier source local n'est modifié ;
- aucun appel réseau n'est ajouté ;
- aucune orchestration dry-run n'est ajoutée ;
- aucun agent documentaire de découverte automatique n'est ajouté.

À la fin, résume précisément :
1. fichiers modifiés ;
2. fichiers ajoutés ;
3. tests ajoutés ;
4. commandes exécutées ;
5. résultat pytest ;
6. choix techniques importants ;
7. points non tranchés ;
8. garantie que data/local_files, le journal actif, les appels OpenAI/réseau, l'orchestration dry-run et SourceDiscoveryAgent n'ont pas été touchés.
```

---

## Vérification humaine après retour Codex

Après la mission, vérifier :

```text
pytest
git status
git diff --stat
git diff --check
absence d'appel réseau
absence de OpenAIAdapter
absence de prompts.py
absence de package orchestration
absence de package exports
absence de SourceDiscoveryAgent
aucun fichier data/local_files modifié
aucun journal modifié
```

Ne pas utiliser `git add .`. Ajouter uniquement les fichiers explicitement attendus.
