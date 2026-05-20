# Règles de validation — v0.2.3-auto

## Niveaux

1. Validation syntaxique : schéma JSON, champs obligatoires, IDs, enums, dates.
2. Validation protocolaire : règles v0.2.3 non négociables.
3. Validation sémantique : prudence, non-réduction, cohérence musicale et documentaire.

## Règles prioritaires

- `V-S-001` : si `S = S-A` et aucune `source_decisive = oui`, rétrograder `S-B` ou `type_a_verifier`.
- `V-S-002` : si `S = S-A` et `verification_independante != oui`, rétrograder `S-B`, sauf exception justifiée.
- `V-I-001` : si `I = I-A` et absence de preuve explicite d’improvisation centrale, rétrograder `I-B` ou `I-C`.
- `V-C-001` : si `C = C-A` et périmètre instable, rétrograder `C-B1` ou `C-B2`.
- `V-FAM-001` : une fiche famille ne peut pas être traitée comme fiche pratique unique.
- `V-CADRE-001` : une fiche-cadre ne doit pas être convertie automatiquement en fiche pratique.
- `V-SOURCE-001` : une plateforme d’accès ne peut pas être source décisive.
- `V-SCIND-001` : une scission candidate exige conservation du parent.
- `V-FUSION-001` : une fusion candidate ne doit pas effacer variantes, alias ou angles différents.
- `V-DELTA-001` : tout changement entre RUN_001 et RUN_002 sur `S`, `I`, `C` ou décision impose un `DeltaRecord`.
- `V-PUB-001` : si `D < D-A` ou `C in [C-B2, C-C, C-D, C-X]`, publication bloquée ou différée.

## Principe

Le pipeline ne bloque pas sur les cas difficiles : il les traite, les trace, applique les prudences, et bloque seulement leur publication consolidée si nécessaire.
