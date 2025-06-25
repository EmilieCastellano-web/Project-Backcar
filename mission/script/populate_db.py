#!/usr/bin/env python
"""
Script de remplissage de la base de données avec des données de test.

Ce script génère des données de test réalistes pour l'application de gestion de missions automobiles.
Il crée des clients, véhicules, interventions et missions avec leurs relations.

Usage:
    python manage.py shell
    >>> exec(open('mission/script/populate_db.py').read())

Ou depuis le terminal:
    python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_airtable_api.settings'); import django; django.setup(); exec(open('mission/script/populate_db.py').read())"
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_airtable_api.settings')
django.setup()

from mission.models import Client, Vehicule, Intervention, Mission, MissionIntervention, Priorite, Categorie, Taux
from django.db import transaction
from django.utils import timezone

def clear_database():
    """Vide toutes les tables pour un nouveau remplissage."""
    print("Suppression des données existantes...")
    MissionIntervention.objects.all().delete()
    Mission.objects.all().delete()
    Intervention.objects.all().delete()
    Vehicule.objects.all().delete()
    Client.objects.all().delete()
    print("Données supprimées avec succès.")


def create_clients():
    """Crée des clients de test."""
    print("Création des clients...")
    
    clients_data = [
        {
            'nom': 'Dupont', 'prenom': 'Jean', 'societe': 'Dupont SARL',
            'telephone': '0123456789', 'email': 'jean.dupont@email.com',
            'adresse': '15 rue de la Paix', 'code_postal': '75001', 'ville': 'Paris'
        },
        {
            'nom': 'Martin', 'prenom': 'Marie', 'societe': None,
            'telephone': '0234567890', 'email': 'marie.martin@email.com',
            'adresse': '28 avenue des Champs', 'code_postal': '69001', 'ville': 'Lyon'
        },
        {
            'nom': 'Leroy', 'prenom': 'Pierre', 'societe': 'Garage Leroy',
            'telephone': '0345678901', 'email': 'pierre.leroy@email.com',
            'adresse': '42 boulevard du Commerce', 'code_postal': '33000', 'ville': 'Bordeaux'
        },
        {
            'nom': 'Durand', 'prenom': 'Sophie', 'societe': None,
            'telephone': '0456789012', 'email': 'sophie.durand@email.com',
            'adresse': '7 place de la République', 'code_postal': '13001', 'ville': 'Marseille'
        },
        {
            'nom': 'Moreau', 'prenom': 'Luc', 'societe': 'Transport Moreau',
            'telephone': '0567890123', 'email': 'luc.moreau@email.com',
            'adresse': '33 rue du Port', 'code_postal': '44000', 'ville': 'Nantes'
        },
        {
            'nom': 'Roux', 'prenom': 'Amélie', 'societe': None,
            'telephone': '0678901234', 'email': 'amelie.roux@email.com',
            'adresse': '19 avenue de la Liberté', 'code_postal': '31000', 'ville': 'Toulouse'
        },
        {
            'nom': 'Garnier', 'prenom': 'Thomas', 'societe': 'Garnier & Co',
            'telephone': '0789012345', 'email': 'thomas.garnier@email.com',
            'adresse': '8 rue de la Gare', 'code_postal': '67000', 'ville': 'Strasbourg'
        },
        {
            'nom': 'Blanc', 'prenom': 'Julie', 'societe': None,
            'telephone': '0890123456', 'email': 'julie.blanc@email.com',
            'adresse': '14 place du Marché', 'code_postal': '59000', 'ville': 'Lille'
        }
    ]
    
    clients = []
    for data in clients_data:
        client = Client.objects.create(**data)
        clients.append(client)
        print(f"  Client créé: {client}")
    
    return clients


def create_vehicules(clients):
    """Crée des véhicules de test associés aux clients."""
    print("Création des véhicules...")
    
    marques_modeles = [
        ('Renault', 'Clio'), ('Peugeot', '308'), ('Citroën', 'C4'),
        ('Volkswagen', 'Golf'), ('BMW', 'Série 3'), ('Mercedes', 'Classe A'),
        ('Audi', 'A4'), ('Ford', 'Focus'), ('Opel', 'Astra'),
        ('Toyota', 'Yaris'), ('Nissan', 'Micra'), ('Hyundai', 'i20')
    ]
    
    carburants = ['Essence', 'Diesel', 'Hybride', 'Électrique']
    boites_vitesse = ['Manuelle', 'Automatique']
    
    vehicules = []
    for i, client in enumerate(clients):
        # Chaque client a 1 à 3 véhicules
        nb_vehicules = random.randint(1, 3)
        
        for j in range(nb_vehicules):
            marque, modele = random.choice(marques_modeles)
            
            # Génération d'une immatriculation française
            lettres = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
            chiffres = f"{random.randint(100, 999)}"
            lettres2 = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
            immatriculation = f"{lettres}-{chiffres}-{lettres2}"
            
            # Génération d'un numéro de série VIN
            numero_serie = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=17))
            
            # Date de mise en circulation (entre 2010 et 2023)
            start_date = datetime(2010, 1, 1)
            end_date = datetime(2023, 12, 31)
            mise_circulation = start_date + timedelta(
                days=random.randint(0, (end_date - start_date).days)
            )
            
            vehicule = Vehicule.objects.create(
                marque=marque,
                modele=modele,
                immatriculation=immatriculation,
                numero_serie=numero_serie,
                mise_circulation=mise_circulation.date(),
                kilometrage=random.randint(5000, 200000),
                remarque=f"Véhicule {j+1} de {client.prenom} {client.nom}" if j > 0 else None,
                client=client,
                vo=random.choice([True, False]),
                boite_vitesse=random.choice(boites_vitesse),
                carburant=random.choice(carburants)
            )
            vehicules.append(vehicule)
            print(f"  Véhicule créé: {vehicule} ({vehicule.immatriculation}) - {client}")
    
    return vehicules


def create_interventions():
    """Crée des interventions de test."""
    print("Création des interventions...")
    
    interventions_data = [
        # Interventions Méca BCR
        {
            'libelle': 'Vidange moteur',
            'duree_intervention': Decimal('1.5'),
            'prix_unitaire': Decimal('80.00'),
            'forfait': Decimal('0.00'),
            'description': 'Vidange complète du moteur avec changement du filtre à huile',
            'categorie': 'MECA_BCR'
        },
        {
            'libelle': 'Changement plaquettes de frein',
            'duree_intervention': Decimal('2.0'),
            'prix_unitaire': Decimal('120.00'),
            'forfait': Decimal('0.00'),
            'description': 'Remplacement des plaquettes de frein avant',
            'categorie': 'MECA_BCR'
        },
        {
            'libelle': 'Contrôle technique',
            'duree_intervention': Decimal('1.0'),
            'prix_unitaire': Decimal('0.00'),
            'forfait': Decimal('75.00'),
            'description': 'Contrôle technique réglementaire',
            'categorie': 'MECA_BCR'
        },
        {
            'libelle': 'Changement courroie de distribution',
            'duree_intervention': Decimal('4.0'),
            'prix_unitaire': Decimal('250.00'),
            'forfait': Decimal('0.00'),
            'description': 'Remplacement de la courroie de distribution et des galets',
            'categorie': 'MECA_BCR'
        },
        
        # Interventions Méca CBC
        {
            'libelle': 'Réparation boîte de vitesses',
            'duree_intervention': Decimal('6.0'),
            'prix_unitaire': Decimal('300.00'),
            'forfait': Decimal('0.00'),
            'description': 'Démontage et réparation de la boîte de vitesses',
            'categorie': 'MECA_CBC'
        },
        {
            'libelle': 'Réfection moteur',
            'duree_intervention': Decimal('12.0'),
            'prix_unitaire': Decimal('400.00'),
            'forfait': Decimal('0.00'),
            'description': 'Réfection complète du moteur',
            'categorie': 'MECA_CBC'
        },
        {
            'libelle': 'Diagnostic électronique',
            'duree_intervention': Decimal('1.5'),
            'prix_unitaire': Decimal('90.00'),
            'forfait': Decimal('0.00'),
            'description': 'Diagnostic complet des systèmes électroniques',
            'categorie': 'MECA_CBC'
        },
        
        # Interventions Carrosserie
        {
            'libelle': 'Réparation impact pare-chocs',
            'duree_intervention': Decimal('3.0'),
            'prix_unitaire': Decimal('150.00'),
            'forfait': Decimal('0.00'),
            'description': 'Réparation et peinture d\'un impact sur pare-chocs',
            'categorie': 'CARROSSERIE'
        },
        {
            'libelle': 'Remplacement rétroviseur',
            'duree_intervention': Decimal('0.5'),
            'prix_unitaire': Decimal('80.00'),
            'forfait': Decimal('0.00'),
            'description': 'Remplacement d\'un rétroviseur extérieur',
            'categorie': 'CARROSSERIE'
        },
        {
            'libelle': 'Débosselage porte',
            'duree_intervention': Decimal('2.5'),
            'prix_unitaire': Decimal('120.00'),
            'forfait': Decimal('0.00'),
            'description': 'Débosselage et remise en forme d\'une porte',
            'categorie': 'CARROSSERIE'
        },
        
        # Interventions Personnalisées
        {
            'libelle': 'Installation kit main libre',
            'duree_intervention': Decimal('1.0'),
            'prix_unitaire': Decimal('0.00'),
            'forfait': Decimal('120.00'),
            'description': 'Installation et configuration d\'un kit main libre',
            'categorie': 'CUSTOM'
        },
        {
            'libelle': 'Pose film de protection',
            'duree_intervention': Decimal('2.0'),
            'prix_unitaire': Decimal('0.00'),
            'forfait': Decimal('200.00'),
            'description': 'Pose de film de protection sur la carrosserie',
            'categorie': 'CUSTOM'
        }
    ]
    
    interventions = []
    for data in interventions_data:
        intervention = Intervention.objects.create(**data)
        interventions.append(intervention)
        print(f"  Intervention créée: {intervention.libelle} ({intervention.categorie})")
    
    return interventions


def create_missions_and_relations(clients, vehicules, interventions):
    """Crée des missions et leurs relations avec les interventions."""
    print("Création des missions...")
    
    missions = []
    priorites = [p.name for p in Priorite]
    taux_choices = [t.name for t in Taux]
    
    # Liste pour éviter les doublons véhicule/client
    couples_utilises = set()
    
    # Création de 15 missions (ou moins si pas assez de couples uniques)
    tentatives = 0
    missions_creees = 0
    max_tentatives = 50  # Pour éviter une boucle infinie
    
    while missions_creees < 15 and tentatives < max_tentatives:
        tentatives += 1
        
        # Sélection aléatoire d'un véhicule (et donc de son client)
        vehicule = random.choice(vehicules)
        client = vehicule.client
        
        # Vérifier si ce couple véhicule/client a déjà été utilisé
        couple = (vehicule.id, client.id)
        if couple in couples_utilises:
            continue  # Passer à la tentative suivante
        
        couples_utilises.add(couple)
        
        # Date de demande entre il y a 3 mois et dans 1 mois
        start_date = timezone.now() - timedelta(days=90)
        end_date = timezone.now() + timedelta(days=30)
        date_demande = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        remarques = [
            "Client très pressé",
            "Véhicule accidenté",
            "Intervention sous garantie",
            "Client fidèle - tarif préférentiel",
            "Urgent - véhicule de service",
            "Contrôle avant vente",
            None,  # Pas de remarque
            None,
            None
        ]
        
        mission = Mission.objects.create(
            date_demande=date_demande,
            remarque=random.choice(remarques),
            priorite=random.choice(priorites),
            vehicule=vehicule,
            client=client
        )
        missions.append(mission)
        missions_creees += 1
        
        # Création des relations MissionIntervention
        # Chaque mission a entre 1 et 4 interventions
        nb_interventions = random.randint(1, 4)
        selected_interventions = random.sample(interventions, nb_interventions)
        
        for intervention in selected_interventions:
            # Calcul du coût total
            taux = random.choice(taux_choices)
            duree_supplementaire = Decimal(str(random.uniform(0, 2)))
            
            # Calcul selon le type d'intervention
            if intervention.is_forfait:
                cout_total = intervention.forfait
            else:
                # Simulation d'un calcul basé sur le taux horaire
                taux_horaire = {
                    'HORAIRE': Decimal('50.00'),
                    'T1': Decimal('60.00'),
                    'T2': Decimal('70.00'),
                    'T3': Decimal('80.00')
                }
                duree_totale = intervention.duree_intervention + duree_supplementaire
                cout_total = intervention.prix_unitaire + (duree_totale * taux_horaire[taux])
            
            MissionIntervention.objects.create(
                mission=mission,
                intervention=intervention,
                duree_supplementaire=duree_supplementaire,
                taux=taux,
                cout_total=cout_total
            )
        
        print(f"  Mission créée: {mission.id} - {client} - {vehicule} ({len(selected_interventions)} intervention(s))")
    
    if missions_creees < 15:
        print(f"  Note: Seulement {missions_creees} missions créées (contrainte unique véhicule/client)")
    
    return missions


def display_statistics():
    """Affiche les statistiques des données créées."""
    print("Statistiques des données créées:")
    print(f"  • Clients: {Client.objects.count()}")
    print(f"  • Véhicules: {Vehicule.objects.count()}")
    print(f"  • Interventions: {Intervention.objects.count()}")
    print(f"  • Missions: {Mission.objects.count()}")
    print(f"  • Relations Mission-Intervention: {MissionIntervention.objects.count()}")
    
    print("Répartition par priorité:")
    for priorite in Priorite:
        count = Mission.objects.filter(priorite=priorite.name).count()
        print(f"  • {priorite.value}: {count}")
    
    print("Répartition par catégorie d'intervention:")
    for categorie in Categorie:
        count = Intervention.objects.filter(categorie=categorie.name).count()
        print(f"  • {categorie.value}: {count}")


def main():
    """Fonction principale pour remplir la base de données."""
    print("Démarrage du script de remplissage de la base de données...\n")
    
    try:
        with transaction.atomic():
            # Suppression des données existantes
            clear_database()
            
            # Création des données
            clients = create_clients()
            vehicules = create_vehicules(clients)
            interventions = create_interventions()
            missions = create_missions_and_relations(clients, vehicules, interventions)
            
            # Affichage des statistiques
            display_statistics()

            print("Base de données remplie avec succès!")
            print("Vous pouvez maintenant:")
            print("  • Démarrer le serveur Django: python manage.py runserver")
            print("  • Accéder à l'admin Django pour voir les données")
            print("  • Tester les vues de votre application")
            
    except Exception as e:
        print(f"\nErreur lors du remplissage de la base de données: {e}")
        raise


if __name__ == "__main__":
    main()
