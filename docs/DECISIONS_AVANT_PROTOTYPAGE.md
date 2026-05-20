# Décisions avant prototypage — v0.2.3-auto

## Décisions figées

1. Protocole méthodologique : `v0.2.3`.
2. Couche d’exécution automatisée : `v0.2.3-auto`.
3. Orchestrateur Python déterministe au centre.
4. Agents spécialisés appelés sous contrat, jamais maîtres du flux.
5. JSON canonique comme vérité technique.
6. XLSX comme forme lisible et auditable.
7. Journal actif en lecture seule.
8. Mise à jour uniquement par `JournalPatch`.
9. Validation automatique en trois niveaux : syntaxique, protocolaire, sémantique.
10. RUN_002 uniquement ciblé.
11. Audit humain non bloquant.
12. Prototype comme banc de test de prudence, pas mini-production.

## Journal attendu

```text
JOURNAL_PILOTAGE_ACTIF_TEMP_v0.2.3_POST005_RUN002_026030_NON_SOURCE_DOC.xlsx
```

Statut : journal actif temporaire de pilotage, non source documentaire musicale.

Compteurs post-005 attendus :

```text
ID contrôlés : 69
RUN_001 faits : 20
RUN_002 faits : 13
Stables : 10
Acceptées avec prudence : 10
Fiches-cadres : 7
A_NE_PAS_RETRAITER_NOUVEAU : 20
```

Règle : si ce journal est absent localement, aucun batch ne doit être exécuté.

## Cas de garde-fou connus

- 026 et 030 ne doivent pas être retraités comme nouvelles entrées.
- 032 reste réserve P2, non traitée, sans RUN fait.
- Les archives de RUN ne doivent pas être utilisées comme sources documentaires actives.
- Pas de migration implicite vers v0.3.
