# CLI dry-run usage — dicoimpro v0.2.3-auto

Statut : mode d'emploi local validé manuellement  
Objet : documenter le premier workflow exécutable sans données réelles, sans RUN, sans OpenAI et sans écriture journal.

---

## 1. Commande

Depuis la racine du repo :

```powershell
dico-impro plan-batch --dry-run --scope <scope.json> --output-dir <output_dir>
```

Exemple validé localement :

```powershell
dico-impro plan-batch --dry-run --scope tmp_manual\scope_manual.json --output-dir tmp_manual\exports
```

---

## 2. Format minimal du scope JSON

Le scope est explicite. Le système ne sélectionne aucun candidat automatiquement.

```json
{
  "batch_id": "BATCH_MANUAL_001",
  "entries": [
    {
      "id_entree_original": "026",
      "titre_original_exact": "Test manual 026"
    },
    {
      "id_entree_original": "031",
      "titre_original_exact": "Test manual 031"
    }
  ]
}
```

Notes :

```text
- batch_id est obligatoire ;
- entries doit contenir au moins une entrée ;
- id_entree_original est obligatoire pour chaque entrée ;
- titre_original_exact est conseillé mais peut être absent selon le contrat ;
- le fichier peut être encodé en UTF-8 avec ou sans BOM.
```

---

## 3. Sortie attendue sur stdout

Exemple de sortie validée :

```json
{
  "ok": true,
  "batch_id": "BATCH_MANUAL_001",
  "output_dir": "tmp_manual\\exports",
  "created_files": [
    "agent_results.json",
    "batch_report.json",
    "batch_state.json",
    "master.json",
    "quality_gates.json"
  ],
  "entries_total": 2,
  "entries_processed": 2,
  "entries_skipped": 0,
  "entries_blocked": 0
}
```

---

## 4. Fichiers JSON produits

Le dossier de sortie contient :

```text
master.json
batch_state.json
batch_report.json
agent_results.json
quality_gates.json
```

Ces fichiers sont des exports de dry-run. Ils ne sont pas encore une publication projet.

---

## 5. Garde-fous actifs

La commande actuelle :

```text
- exige --dry-run ;
- lit uniquement le scope JSON fourni ;
- écrit uniquement dans le dossier --output-dir fourni ;
- utilise AgentRegistry + FakeAgentAdapter ;
- produit BatchState + BatchReport ;
- exporte uniquement des JSON ;
- ne lit pas data/local_files ;
- ne lit pas le journal actif ;
- ne modifie pas le journal actif ;
- ne lance pas de RUN ;
- ne sélectionne pas de candidats ;
- n'appelle pas OpenAI ;
- n'effectue aucun appel réseau ;
- ne produit pas de XLSX/CSV.
```

---

## 6. Nettoyage local

Les tests manuels peuvent utiliser un dossier temporaire local :

```powershell
Remove-Item -Recurse -Force tmp_manual
```

`tmp_manual/` doit rester hors Git.

---

## 7. Statut du jalon

Jalon validé :

```text
scope JSON explicite
→ dico-impro plan-batch --dry-run
→ orchestration in-memory
→ FakeAgentAdapter
→ QualityGate
→ BatchState / BatchReport
→ exports JSON
```

Dernier état connu :

```text
pytest : 105 passed
manual CLI dry-run : OK
```
