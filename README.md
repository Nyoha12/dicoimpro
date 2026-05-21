# dicoimpro

Pipeline d’automatisation `v0.2.3-auto` pour le projet **dico impro**.

Objectif : transformer le workflow conversationnel calibré en chaîne de production automatisée, reproductible et auditable, sans lancer de RUN manuel entrée par entrée.

## Principes

- Protocole méthodologique : `v0.2.3`.
- Couche d’exécution automatisée : `v0.2.3-auto`.
- Le JSON validé est la vérité technique.
- Le XLSX/CSV sont des vues lisibles ou opératoires.
- Le journal actif est lu en lecture seule.
- Toute mise à jour passe par un `JournalPatch` séparé.
- Les archives de RUN ne sont pas des sources documentaires actives.
- Le vieux PDF `Improvisation musicale mondiale.pdf` est une référence legacy optionnelle : il n’est pas requis, pas utilisé par défaut et jamais source décisive automatique.
- Le pipeline doit traiter les cas complexes sans réduire les pratiques humaines à des catégories trop brutales.

## Documentation active

Lire d’abord :

```text
docs/README.md
```

Ce fichier donne la hiérarchie documentaire active.

Documents clés :

```text
docs/REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto.md
docs/PLAN_ARCHITECTURE_SDK_DICO_IMPRO_v0.2.3-auto.md
docs/CONTRATS_JSON_v0.2.3-auto.md
docs/STRATEGIE_TESTS_PRUDENCE_v0.2.3-auto.md
docs/SPEC_ADAPTATEURS_AGENTS_v0.2.3-auto.md
docs/AUDIT_CONCEPTION_AVANT_CODEX_v0.2.3-auto.md
docs/PROMPT_CODEX_001_CONTRATS_PYDANTIC.md
```

`docs/ARCHITECTURE_SDK_v0.2.3-auto.md` est conservé comme trace exploratoire et ne doit pas être utilisé comme référence principale.

## Dossiers

```text
docs/              Spécifications, décisions et règles méthodologiques.
src/               Code Python du pipeline.
tests/             Tests unitaires et futur golden set.
data/local_files/  Données locales non versionnées, à placer manuellement.
data/outputs/      Sorties générées.
data/logs/         Logs générés.
```

## Données locales

Les fichiers `.xlsx`, `.md` et éventuels `.pdf` de travail ne sont pas versionnés par Git classique. Ils doivent être placés localement dans :

```text
data/local_files/
```

Leur rôle exact est défini par :

```text
data_manifest.yaml
```

Ne pas inférer le statut d’un fichier depuis son nom ou son dossier. Le manifest est l’autorité technique pour les rôles fichier.

Journal de pilotage actuellement attendu localement :

```text
JOURN_PILOT_ACTIF_TEMP_v0.2.3_POST005_RUN002_026030_NON_SOURCE.xlsx
```

Nom canonique associé :

```text
JOURNAL_PILOTAGE_ACTIF_TEMP_v0.2.3_POST005_RUN002_026030_NON_SOURCE_DOC.xlsx
```

Statut : journal actif temporaire de pilotage, non source documentaire musicale, lecture seule.

## Commandes locales utiles

Après installation editable :

```text
pip install -e ".[dev]"
```

Contrôler le manifest :

```text
dico-impro check-manifest
```

Contrôler les garde-fous post-005 :

```text
dico-impro check-journal-post005
```

Lancer les tests :

```text
pytest
```

## Prochaine étape technique

Mission autorisée :

```text
Codex 001 — Contrats Pydantic SDK
```

Prompt prêt à copier-coller :

```text
docs/PROMPT_CODEX_001_CONTRATS_PYDANTIC.md
```

Interdictions maintenues :

```text
pas de RUN
pas d’identification de candidats
pas d’écriture directe journal
pas d’appel OpenAI réel
pas de modification data/local_files
```
