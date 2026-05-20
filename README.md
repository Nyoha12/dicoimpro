# dicoimpro

Pipeline d’automatisation v0.2.3-auto pour le projet **dico impro**.

Objectif : transformer le workflow conversationnel calibré en chaîne de production automatisée, reproductible et auditable, sans lancer de RUN manuel entrée par entrée.

## Principes

- Protocole méthodologique : `v0.2.3`.
- Couche d’exécution automatisée : `v0.2.3-auto`.
- Le JSON est la vérité technique.
- Le XLSX est la forme lisible et auditable.
- Le journal actif est lu en lecture seule.
- Toute mise à jour passe par un `JournalPatch`.
- Les archives de RUN ne sont pas des sources documentaires actives.
- Le pipeline traite les cas complexes sans validation humaine obligatoire, mais produit une file d’audit non bloquante.

## Dossiers

```text
docs/       Spécifications, décisions et règles méthodologiques.
schemas/    Schémas JSON contractuels.
src/        Code Python du pipeline.
tests/      Tests unitaires et futur golden set.
data/       Données locales non versionnées, à placer manuellement.
```

## Données locales

Les fichiers `.xlsx` et `.pdf` du projet ne sont pas versionnés par Git classique. Ils doivent être placés localement dans `data/` selon `data_manifest.yaml`.

Journal de pilotage attendu :

```text
JOURNAL_PILOTAGE_ACTIF_TEMP_v0.2.3_POST005_RUN002_026030_NON_SOURCE_DOC.xlsx
```

Statut : journal actif temporaire de pilotage, non source documentaire musicale.
