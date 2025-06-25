# Scripts de Remplissage de Base de Données

Ce dossier contient les scripts pour remplir la base de données de l'application de gestion de missions automobiles avec des données de test réalistes.

## Structure du dossier

```text
mission/script/
├── __init__.py
├── populate_db.py          # Script principal de remplissage
└── README.md              # Ce fichier
```

## Utilisation

### Méthode 1: Shell Django (Recommandée)

```bash
python manage.py shell
```

Puis dans le shell Django :

```python
exec(open('mission/script/populate_db.py', encoding='utf-8').read())
```

### Méthode 2: Exécution directe

```bash
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_airtable_api.settings'); import django; django.setup(); exec(open('mission/script/populate_db.py', encoding='utf-8').read())"
```

### Utilisation

### Prérequis

Assurez-vous que votre environnement de base de données est démarré :

```bash
# Si vous utilisez Docker
docker-compose up -d db

# Ou démarrez tous les services
docker-compose up -d
```

## Données créées

Le script crée les données suivantes :

### Clients (8 clients)

- Clients particuliers et professionnels
- Données complètes : nom, prénom, société, contact, adresse

### Véhicules (8-24 véhicules)

- 1 à 3 véhicules par client
- Différentes marques : Renault, Peugeot, BMW, Mercedes, etc.
- Immatriculations françaises réalistes
- Numéros VIN uniques
- Données techniques : carburant, boîte de vitesse, kilométrage

### Interventions (12 interventions types)

Réparties par catégorie :

- **Méca BCR** : Vidange, plaquettes, courroie, contrôle technique
- **Méca CBC** : Réparation boîte, réfection moteur, diagnostic
- **Carrosserie** : Réparation impacts, débosselage, rétroviseurs
- **Personnalisé** : Kit main libre, film de protection

### Missions (15 missions)

- Dates de demande réparties sur 4 mois (3 mois passés + 1 mois futur)
- Priorités variées (Non prioritaire à Urgente)
- 1 à 4 interventions par mission
- Calculs de coût réalistes selon les taux

## Fonctionnalités du script

- **Suppression sécurisée** : Vide la base avant le remplissage
- **Transactions atomiques** : Rollback automatique en cas d'erreur
- **Données réalistes** : Noms, adresses, immatriculations françaises
- **Relations cohérentes** : Respect des contraintes de clés étrangères
- **Statistiques** : Affichage du résumé des données créées
- **Logging détaillé** : Suivi de la création de chaque élément

## Attention

- **Le script supprime toutes les données existantes** avant de créer les nouvelles
- Utilisez uniquement sur des environnements de développement/test
- Assurez-vous d'avoir une sauvegarde si nécessaire

## Cas d'usage

Ce script est idéal pour :

- **Développement** : Tester rapidement l'application avec des données
- **Démonstration** : Présenter l'application avec des données réalistes  
- **Tests** : Valider les fonctionnalités avec un jeu de données complet
- **Formation** : Apprendre à utiliser l'application

## Statistiques générées

Après exécution, vous obtiendrez environ :

- 8 clients
- 12-20 véhicules
- 12 interventions types
- 15 missions
- 25-45 relations mission-intervention

Les données sont générées aléatoirement, les statistiques exactes peuvent varier à chaque exécution.
