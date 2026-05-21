# Architecture SDK v0.2.3-auto

> Statut : **superseded / document exploratoire**.
>
> Ce document a été créé avant consolidation de l'architecture. Il est conservé comme trace, mais ne doit plus servir de référence principale.
>
> Références actives :
>
> 1. `docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md`
> 2. `docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md`
> 3. `docs/CONTRATS_JSON_v0.2.3-auto.md`
> 4. `docs/STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md`
> 5. `docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md`
> 6. `docs/FEUILLE_ROUTE_IMPLEMENTATION_SDK_v0.2.3-auto.md`
> 7. `docs/MISSIONS_CODEX_v0.2.3-auto.md`
> 8. `docs/AUDIT_CONCEPTION_AVANT_CODEX_v0.2.3-auto.md`

## Objectif historique

Construire le système de production automatisée de la base `dico impro`, pas avancer manuellement sur l'identification des candidats.

Le pipeline doit produire des objets contrôlés, auditables et rejouables :

- décisions de routage ;
- audits de sources ;
- validations automatiques ;
- deltas RUN_001/RUN_002 ;
- décisions finales provisoires ;
- patches de journal proposés, jamais écrits directement ;
- exports JSON/CSV/XLSX.

## Principe central conservé

L'agent ne pilote pas l'état du projet.

Le pilotage est assuré par un orchestrateur déterministe Python. Les agents produisent uniquement des sorties structurées validées par schéma.

```text
Entrées locales -> Orchestrateur Python -> Agents spécialisés -> Validation Pydantic -> Exports contrôlés
```

## Note

Le contenu détaillé initial de ce document a été remplacé par les documents consolidés listés plus haut afin d'éviter les contradictions pendant les missions Codex.
