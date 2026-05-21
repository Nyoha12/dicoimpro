# PROMPT_CODEX_001_CONTRATS_PYDANTIC

Statut : prompt prêt à copier-coller dans Codex  
Mission : implémentation strictement bornée des contrats Pydantic SDK v0.2.3-auto.

---

## Prompt

```text
Tu travailles dans le repo dicoimpro.

Objectif : implémenter les contrats Pydantic de base pour la couche SDK v0.2.3-auto.

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

À faire :
1. Créer un package src/dico_impro/contracts/.
2. Implémenter les modèles Pydantic stricts suivants :
   - GoldenSetCase
   - AgentContract
   - AgentTask
   - AgentResult
   - BatchState
   - BatchReport
   - EntryState
   - AuditQueueRecord
3. Ajouter les modules :
   - src/dico_impro/contracts/__init__.py
   - src/dico_impro/contracts/common.py
   - src/dico_impro/contracts/agents.py
   - src/dico_impro/contracts/batch.py
   - src/dico_impro/contracts/project_state.py
4. Réutiliser les modèles existants dans src/dico_impro/models.py quand c'est pertinent, sans casser les tests existants.
5. Ne modifie pas models.py sauf nécessité minimale ; préfère créer contracts/ et préserver la compatibilité existante.
6. Utilise ConfigDict(extra="forbid") pour les contrats, sauf justification explicite dans le résumé final.
7. Chaque objet produit doit contenir au minimum, quand applicable :
   - object_type
   - schema_version
   - batch_id
   - created_by
8. Pour les objets concernant une entrée, inclure :
   - id_entree_original
   - titre_original_exact si disponible ou requis par le contrat
9. Utilise des valeurs machine ASCII dans les nouveaux enums/contrats :
   - accepte_avec_prudence, pas accepté_avec_prudence
   - a_revoir, pas à_revoir
   - publication_bloquee, pas publication_bloquée
   Si un label humain accentué est nécessaire, ajoute un champ label ou description séparé.
10. Ajouter les tests unitaires pour objets valides et invalides :
   - tests/test_contracts_agents.py
   - tests/test_contracts_batch.py
   - tests/test_contracts_project_state.py
11. Vérifier que les objets invalides sont rejetés :
   - champ obligatoire manquant
   - extra field interdit
   - enum invalide
   - object_type incohérent
   - batch_id manquant quand requis
12. Vérifier que les objets minimaux valides sont acceptés.
13. Lancer pytest.

Interdictions absolues :
- ne lance aucun RUN ;
- n'identifie aucun candidat ;
- ne traite aucune entrée réelle ;
- ne modifie pas le journal actif ;
- ne modifie aucun fichier dans data/local_files ;
- n'utilise pas le PDF ancien ;
- n'ajoute aucun appel OpenAI ;
- n'ajoute aucun appel réseau ;
- ne crée pas AgentRegistry ;
- ne crée pas FakeAdapter ;
- ne crée pas OpenAIAdapter ;
- ne crée pas d'orchestration dry-run ;
- ne crée pas SourceDiscoveryAgent ;
- ne transforme pas Validation, DeltaBuilder, JournalPatchBuilder ou BatchReporter en agents ;
- ne supprime aucun test existant ;
- n'affaiblis pas les règles existantes pour faire passer pytest.

Critères de réussite :
- pytest passe ;
- les tests existants restent verts ;
- les nouveaux tests couvrent cas valides et invalides ;
- aucun fichier source local n'est modifié ;
- aucun appel réseau n'est ajouté ;
- les contrats restent stricts ;
- les valeurs machine sont ASCII.

À la fin, résume précisément :
1. fichiers modifiés ;
2. fichiers ajoutés ;
3. tests ajoutés ;
4. commandes exécutées ;
5. résultat pytest ;
6. choix techniques importants ;
7. points non tranchés ;
8. garantie que data/local_files, le journal actif et les appels OpenAI n'ont pas été touchés.
```

---

## Vérification humaine après retour Codex

Après la mission, vérifier :

```text
pytest
aucun appel réseau
aucun fichier data/local_files modifié
aucun journal modifié
pas de SourceDiscoveryAgent
pas d'orchestration prématurée
pas de changement doctrinal
valeurs machine ASCII dans les nouveaux contrats
```

Si Codex modifie `models.py`, vérifier que la modification est minimale et compatible avec les tests existants.
