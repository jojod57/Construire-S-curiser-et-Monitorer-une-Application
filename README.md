# TD DevSecOps/SRE : Construire, Sécuriser et Monitorer une Application TODO

Ce répertoire contient tout le matériel nécessaire pour réaliser un TD de 4 heures sur les principes du Site Reliability Engineering (SRE) et du DevSecOps. Le but est de mettre en place un pipeline CI/CD complet, d’automatiser le déploiement d’une application Web simple, d’intégrer des scans de sécurité et un monitoring continu via Prometheus et Grafana, puis de pratiquer la gestion d’incidents.

## 1. Pré-requis techniques

Avant de commencer, assurez-vous de disposer des outils suivants :

- un **compte GitHub** pour héberger votre projet et exécuter les workflows GitHub Actions ;
- **Docker** et **Docker Compose** installés sur votre machine (Docker Desktop sous Windows/Mac ou Docker Engine sous Linux/WSL) ;
- **Git** installé et un terminal fonctionnel ;
- un navigateur Web pour consulter Grafana et Prometheus.

## 2. Présentation de l’application de base

L’application fournie se trouve dans `app.py`. C’est une API REST minimale écrite avec Flask qui gère une liste de tâches (TODO) en mémoire :

- `GET /` : renvoie un simple message de santé ("OK") ;
- `GET /tasks` : renvoie toutes les tâches ;
- `POST /tasks` : crée une nouvelle tâche (JSON avec `title` obligatoire et `description` optionnelle) ;
- `PUT /tasks/<id>` : marque une tâche comme terminée ;
- `DELETE /tasks/<id>` : supprime une tâche.

Les métriques HTTP sont exposées sur `GET /metrics` grâce à `prometheus_flask_exporter`. Un endpoint supplémentaire `/health` a été ajouté pour les vérifications de santé. Un endpoint `/error` provoque volontairement une erreur (division par zéro) et peut être utilisé pour simuler une panne dans la partie gestion d’incidents.

Pour lancer l’application localement (pour le développement) :

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

L’API sera accessible sur `http://localhost:5000`.

## 3. Construction et exécution avec Docker

Un `Dockerfile` est fourni pour empaqueter l’application. Pour construire et exécuter l’image :

```bash
# À la racine du projet
docker build -t todo-app .
docker run --rm -p 5000:5000 todo-app
```

Vous pouvez alors utiliser `curl` pour créer et lister des tâches :

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"title":"Apprendre Flask"}' http://localhost:5000/tasks
curl http://localhost:5000/tasks
```

## 4. Pipeline CI/CD automatisé avec GitHub Actions

Le répertoire `.github/workflows/ci.yml` contient un pipeline prêt à l’emploi.
Ce workflow se déclenche à chaque `push` ou `pull_request` sur la branche `main` :

1. **Build et push de l’image** : l’image Docker est construite puis envoyée vers Docker Hub. **Important :** créez les secrets `DOCKERHUB_USERNAME` et `DOCKERHUB_TOKEN` dans les paramètres de votre dépôt GitHub. Ces secrets doivent correspondre à votre identifiant Docker Hub et à un token (ou Personal Access Token) capable de push.
2. **Scan de vulnérabilités avec Trivy** : la tâche `Run Trivy` analyse l’image nouvellement créée et génère un rapport SARIF. Ce rapport est automatiquement publié dans l’onglet Security du dépôt.
3. **Conformité Infrastructure as Code avec Checkov** : la dernière étape exécute Checkov sur l’ensemble du dépôt (Dockerfile, docker-compose, fichiers YAML) et génère un deuxième rapport SARIF. Celui-ci est également envoyé à GitHub Security.

Vous pouvez adapter le tag de l’image ou ajouter des étapes (tests unitaires, linter…) selon vos besoins.

## 5. Déploiement et monitoring avec Docker Compose

Le fichier `docker-compose.yml` permet de lancer simultanément :

- `app` : votre API TODO ;
- `prometheus` : serveur Prometheus configuré pour collecter les métriques de l’application toutes les 15 secondes ;
- `grafana` : instance Grafana pour visualiser les métriques.

Démarrez l’ensemble des services en arrière-plan :

```bash
sudo docker compose up -d --build
```

Les services seront accessibles aux adresses suivantes :

- API TODO : http://localhost:5000
- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000 (identifiant : `admin`, mot de passe : `admin`)

Dans Grafana, ajoutez une **data source** Prometheus avec l’URL `http://prometheus:9090`. Créez ensuite un dashboard affichant par exemple :

- le nombre de requêtes par seconde : `rate(flask_http_request_duration_seconds_count[1m])` ;
- la latence moyenne : `avg(flask_http_request_duration_seconds_sum / flask_http_request_duration_seconds_count)` ;
- la répartition des codes HTTP 2xx, 4xx, 5xx.

Ces requêtes s’appuient sur les métriques exposées automatiquement par `prometheus_flask_exporter`.

## 6. Simulation et gestion d’incidents

1. Lancez la stack avec `sudo docker compose up -d --build`. Vérifiez dans Grafana que les métriques remontent et que les courbes évoluent lorsque vous envoyez des requêtes à votre API.
2. Simulez une panne en visitant `http://localhost:5000/error` dans votre navigateur ou avec `curl`. Cette route provoque une erreur 500 (division par zéro) et doit entraîner une montée du taux d’erreurs dans Prometheus.
3. Rédigez un **rapport d’incident** en vous basant sur le modèle `incident-report-template.md`. Le rapport doit inclure :
   - Le contexte (date, heure, service impacté) ;
   - La détection et le diagnostic (comment l’alerte a été remarquée, quelles métriques ont servi) ;
   - La cause racine (le bug dans l’application) ;
   - Les actions correctives et le rétablissement ;
   - Les leçons apprises et les actions préventives.

   Pour rédiger un post-mortem, inspirez-vous des bonnes pratiques décrites dans la documentation SRE et l’article d’incident.io : l’objectif est d’apprendre collectivement et de renforcer la résilience du service sans blâmer les individus.

## 7. Livrables attendus

Pour valider le TD, vous devez fournir :

- un dépôt GitHub public ou privé contenant ce projet complété ;
- le workflow GitHub Actions opérationnel (fichier `.github/workflows/ci.yml`) ;
- un `docker-compose.yml` fonctionnel incluant votre application, Prometheus et Grafana ;
- une capture d’écran ou export JSON de votre dashboard Grafana montrant les métriques de l’application ;
- un rapport d’incident/post-mortem (`incident-report.md`).

## 8. Barème indicatif

- **Automatisation du déploiement** : 30 % – pipeline GitHub Actions qui construit l’image et la pousse vers Docker Hub.
- **Scans de sécurité** : 20 % – utilisation de Trivy et Checkov avec publication des rapports.
- **Monitoring et observabilité** : 25 % – instrumentation de l’application, configuration de Prometheus et Grafana, création de dashboards.
- **Qualité du rapport d’incident** : 25 % – clarté du post-mortem, analyse des causes et actions de prévention.

Bonne chance ! Ce TD est l’occasion de mettre en pratique des notions essentielles de SRE et de DevSecOps tout en manipulant des outils modernes (Docker, GitHub Actions, Prometheus, Grafana, Trivy, Checkov). N’hésitez pas à aller plus loin : ajouter des tests unitaires, intégrer un linter, mettre en place des alertes Prometheus, etc.


