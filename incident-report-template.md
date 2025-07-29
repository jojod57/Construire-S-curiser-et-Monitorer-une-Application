# Rapport d’incident et post‑mortem

## Informations générales

- **Date et heure de l’incident** : <!-- ex : 29 juillet 2025, 10:15 CET -->
- **Services impactés** : <!-- ex : API TODO -->
- **Gravité** : <!-- faible / modérée / forte -->

## Résumé

Décrivez en quelques phrases ce qui s’est passé, comment l’incident a été
identifié et quel a été l’impact pour les utilisateurs.

## Timeline

| Heure (CET) | Événement |
|-------------|-----------|
| 10:15 | Déclenchement de l’erreur 500 lors de l’appel à `/error` |
| ... | ... |

## Détection et diagnostic

Expliquez comment la panne a été détectée (alertes Prometheus, logs,
consultation du dashboard Grafana) et quelles métriques ont aidé à
comprendre le problème.

## Cause racine

Précisez quelle modification ou quel bug a provoqué l’incident.  Dans ce TP,
il s’agit de la division par zéro volontaire dans `app.py`.  Détaillez
également les facteurs contributifs (ex. : absence de tests pour ce
comportement, manque de gestion d’erreurs, etc.).

## Actions correctives et rétablissement

Décrivez les étapes entreprises pour restaurer le service (rollback,
correction du code, redéploiement…).  Indiquez les validations effectuées
après la correction.

## Leçons apprises et actions de prévention

- Qu’avez‑vous appris de cet incident ?
- Quelles améliorations mettre en œuvre pour éviter la récidive ?
- Y a‑t‑il des processus ou des outils à adapter ?

Ce modèle s’inspire des bonnes pratiques SRE en matière de post‑mortem : il
se concentre sur la compréhension et l’amélioration continue plutôt que sur la
recherche de responsabilités individuelles【286532960693871†L46-L60】.
