# REGISTRE_DECISIONS_CONSOLIDEES_v0.2.3-auto

Statut : registre de décisions consolidées avant implémentation SDK  
Objet : éviter que les décisions méthodologiques soient dispersées dans la conversation, les fichiers de pilotage ou les docs d'architecture.

---

## 0. Fonction du registre

Ce registre ne remplace pas le protocole v0.2.3.

Il sert à documenter les décisions d'architecture et de pilotage prises pour la couche `v0.2.3-auto`.

Il doit permettre de répondre à :

```text
quelle décision a été prise ?
pourquoi ?
quelle est sa portée ?
qu'est-ce qu'elle interdit ?
est-ce stable ou encore à confirmer ?
```

---

## 1. Décisions stables

### D-001 — La couche d'automatisation s'appelle v0.2.3-auto

Décision :

```text
La couche technique d'exécution est nommée v0.2.3-auto.
Le protocole méthodologique reste v0.2.3.
```

Raison :

```text
On ajoute une couche d'automatisation sans modifier la doctrine ni créer une version méthodologique nouvelle.
```

Interdit :

```text
renommer la phase en v0.2.4 sans modification méthodologique validée
changer les règles D/S/I/C/E sous prétexte d'automatisation
```

Statut : stable.

---

### D-002 — L'orchestrateur déterministe gouverne le flux

Décision :

```text
Le pipeline Python gouverne les étapes, l'état, les fichiers, les reprises, les validations et les exports.
Les agents produisent des objets structurés mais ne gouvernent pas le projet.
```

Raison :

```text
Le projet nécessite reproductibilité, traçabilité, prudence et garde-fous.
Un agent autonome risquerait de confondre analyse, décision et état projet.
```

Interdit :

```text
laisser un agent choisir seul le workflow
laisser un agent modifier le journal
laisser un agent décider la publication consolidée
laisser un agent changer la stratégie de lot
```

Statut : stable.

---

### D-003 — JSON est la vérité technique, XLSX est une vue auditable

Décision :

```text
Les objets JSON validés portent la vérité technique du pipeline.
Les XLSX/CSV sont des sorties lisibles ou opératoires.
```

Raison :

```text
Le JSON est plus strict, plus validable, plus rejouable.
Le XLSX reste nécessaire pour audit humain et manipulation lisible.
```

Interdit :

```text
faire d'un XLSX généré la seule source de vérité
accepter une décision non structurée parce qu'elle est lisible dans un tableau
```

Statut : stable.

---

### D-004 — Le journal actif est lu en lecture seule

Décision :

```text
Le journal actif temporaire de pilotage peut être lu pour l'état projet.
Le pipeline ne doit jamais l'écrire directement.
Toute proposition passe par JournalPatch.
```

Raison :

```text
Le journal est un garde-fou anti-retraitement et un état de pilotage.
Une écriture directe rendrait les erreurs difficiles à auditer.
```

Interdit :

```text
écriture directe dans le journal actif
modification silencieuse du journal
patch implicite non exporté séparément
```

Statut : stable.

---

### D-005 — Le journal post-005 est le journal de pilotage courant

Décision :

```text
Le journal matérialisé post-005 / RUN_002 026-030 est la référence active temporaire de pilotage dans l'état actuel.
L'ancien journal MINI_RUN_004 est conservé mais remplacé pour le pilotage courant.
```

Raison :

```text
Il intègre l'état de clôture post-005 et évite de retraiter 026/030 comme nouveaux.
```

Interdit :

```text
revenir au journal MINI_RUN_004 comme référence active sans décision explicite
traiter 026 ou 030 comme nouvelles entrées
marquer 032 comme RUN fait sans matérialisation correspondante
```

Statut : stable sous réserve de matérialisation locale et garde-fous verts.

---

### D-006 — Les archives RUN ne sont pas des sources actives

Décision :

```text
Les archives RUN documentent une exécution.
Elles ne remplacent ni le protocole, ni la base, ni le triage, ni le journal, ni les sources documentaires.
```

Raison :

```text
Une archive contient le résultat d'un traitement, pas une autorité documentaire primaire.
```

Interdit :

```text
utiliser une archive RUN comme source décisive
confondre archive de décision et source documentaire
réactiver automatiquement des fichiers RUN comme sources projet
```

Statut : stable.

---

### D-007 — Le PDF ancien n'est pas utilisé par défaut

Décision :

```text
Le fichier Improvisation musicale mondiale.pdf est rétrogradé en référence legacy optionnelle.
Il n'est pas utilisé par défaut et ne peut pas servir de source décisive automatique.
```

Raison :

```text
Le fichier est ancien, potentiellement obsolète, et peut introduire des biais ou erreurs de cadrage.
```

Interdit :

```text
inclure le PDF ancien dans les sources par défaut
le traiter comme source décisive
bloquer le bootstrap parce qu'il est absent
```

Statut : stable.

---

### D-008 — Codex est un exécutant borné, pas un architecte doctrinal

Décision :

```text
Codex peut implémenter des missions courtes, testables et réversibles.
Il ne décide pas les règles méthodologiques.
```

Raison :

```text
Codex peut accélérer le code mais risque d'improviser si la mission n'est pas strictement bornée.
```

Interdit :

```text
lui demander de décider les catégories
lui demander de choisir les candidats
lui demander de lancer des RUN
lui laisser affaiblir les tests pour passer pytest
```

Statut : stable.

---

### D-009 — Fake adapter obligatoire avant OpenAI réel

Décision :

```text
L'adaptateur local/fake doit exister avant tout appel réel à l'Agents SDK ou Responses API.
```

Raison :

```text
Il faut tester orchestration, contrats, erreurs, reprises et exports sans coût, sans réseau, sans dérive modèle.
```

Interdit :

```text
brancher OpenAI avant contrats et fake adapter
faire dépendre pytest d'un appel réseau
utiliser un modèle pour masquer des règles non implémentées
```

Statut : stable.

---

### D-010 — Le golden set sert à tester la prudence, pas à retraiter

Décision :

```text
Les cas calibrés servent aux tests anti-régression.
Ils ne constituent pas une relance de traitement.
```

Raison :

```text
On veut vérifier que le système garde les prudences apprises sans rouvrir les RUN clos.
```

Interdit :

```text
relancer les cas golden set comme production
modifier leurs attendus pour faciliter le passage des tests
transformer un test de prudence en fiche finale
```

Statut : stable.

---

## 2. Décisions provisoires à confirmer

### P-001 — Liste finale des agents

Proposition actuelle :

```text
RoutingAgent
ConservationAgent
SourceDiscoveryAgent
SourceAuditAgent
ClassificationAgent
ValidationAgent ou validation déterministe
SynthesisAgent
DeltaAgent
JournalPatchAgent
BatchReporter
```

Points à confirmer :

```text
SourceDiscoveryAgent doit-il exister comme agent séparé ou rester outil documentaire ?
ValidationAgent doit-il être un agent ou seulement un module déterministe ?
SynthesisAgent doit-il produire la fiche ou seulement la décision finale provisoire ?
```

Statut : à arbitrer avant implémentation Agents SDK réelle.

---

### P-002 — Granularité des contrats Pydantic

Proposition actuelle :

```text
un package contracts/ séparé
modèles communs factorisés
models.py existant réaligné progressivement
```

Points à confirmer :

```text
conserver models.py comme compatibilité ?
migrer tous les contrats vers contracts/ ?
quelle tolérance extra=forbid / extra=allow selon objets ?
```

Statut : à arbitrer pendant Phase B.

---

### P-003 — Stratégie de lot

Proposition actuelle :

```text
aucune sélection automatique implicite
scope fourni explicitement pour dry-run
stratégie de lot documentée avant production
```

Points à confirmer :

```text
format du fichier scope
qui autorise un scope réel
quelles règles de lot pour cas simples / complexes
```

Statut : à arbitrer avant Phase D.

---

### P-004 — Niveau exact de publication consolidée

Proposition actuelle :

```text
traitement automatisé possible
publication consolidée séparée
blocage publication non bloquant pour la suite du traitement
```

Points à confirmer :

```text
quels statuts autorisent publication publique
quelle forme de note prudence est requise
quelles décisions exigent audit humain avant publication
```

Statut : à arbitrer avant tout export public.

---

## 3. Décisions explicitement rejetées

### R-001 — Agent unique qui produit directement des fiches

Rejeté.

Raison :

```text
Risque maximal de confusion entre routage, sources, classification, synthèse et publication.
```

---

### R-002 — Traitement automatique des candidats maintenant

Rejeté pour la phase actuelle.

Raison :

```text
La phase actuelle est architecture SDK et système de production, pas identification opérationnelle.
```

---

### R-003 — Utilisation du PDF ancien comme source documentaire active

Rejeté.

Raison :

```text
Ancienneté, risque d'obsolescence, risque de biais, non nécessaire au bootstrap.
```

---

### R-004 — Écriture directe du journal par pipeline

Rejeté.

Raison :

```text
Perte d'auditabilité et risque de corruption de l'état projet.
```

---

## 4. Points de vigilance

```text
ne pas confondre architecture et traitement
ne pas multiplier les scripts avant validation des contrats
ne pas faire de Codex un décideur
ne pas accepter une sortie modèle non structurée
ne pas réduire une pratique culturelle pour satisfaire un schéma
ne pas transformer les tests en doctrine parallèle
```

---

## 5. Prochaine décision attendue

Avant première mission Codex :

```text
valider que Mission Codex 001 peut commencer
ou corriger d'abord les contrats JSON / liste d'agents
```

Décision recommandée : commencer par Mission Codex 001 seulement si ce registre ne soulève pas d'objection majeure.
