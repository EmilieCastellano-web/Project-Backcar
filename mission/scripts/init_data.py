from datetime import datetime
from ..models import Client, Vehicule, Mission, Intervention, MissionIntervention
import logging
from decimal import Decimal

################### CLIENT ###################
def insert_client():
    client_data = {
            "nom": "Martin",
            "prenom": "Julien",
            "societe": "Martin Solutions",
            "telephone": "0612345678",
            "email": "julien.martin@martinsolutions.fr",
            "adresse": "15 rue des Fleurs",
            "code_postal": "69007",
            "ville": "Lyon",
        
    }
    try: 
        client = Client(
            nom=client_data.get("nom", ""),
            prenom=client_data.get("prenom", ""),
            societe=client_data.get("societe", ""),
            telephone=client_data.get("telephone", ""),
            email=client_data.get("email", ""),
            adresse=client_data.get("adresse", ""),
            code_postal=client_data.get("code_postal", ""),
            ville=client_data.get("ville", ""),
        )
        client.save()
        logging.info(f"Client enregistré : ", client)
        return client
    except Exception as e:
        logging.warning(f"Erreur lors de l'insertion : ", e)
        return None
    
def delete_client():
    try:
        client = Client.objects.get(id=4)  # Assuming the client ID is known
        client.delete()
        logging.info("Client supprimé avec succès.")
    except Client.DoesNotExist:
        logging.warning("Client non trouvé.")
    except Exception as e:
        logging.warning(f"Erreur lors de la suppression du client : {e}")
        
def update_client():
    client_data = {
        "id": 3,  # Assuming the client ID is known
        "nom": "Dupont",    
        "prenom": "Marie",
        "societe": "Dupont SARL",
        "telephone": "0612345678",
        "email": "marie.durand@gmail.com",
        "adresse": "10 avenue des Champs-Élysées",  
        "code_postal": "75008",
        "ville": "Paris",
    }
    try:
        client = Client.objects.get(id=client_data.get("id", None))
        client.nom = client_data.get("nom", client.nom)
        client.prenom = client_data.get("prenom", client.prenom)
        client.societe = client_data.get("societe", client.societe)
        client.telephone = client_data.get("telephone", client.telephone)
        client.email = client_data.get("email", client.email)
        client.adresse = client_data.get("adresse", client.adresse)
        client.code_postal = client_data.get("code_postal", client.code_postal)
        client.ville = client_data.get("ville", client.ville)
        client.save()
        logging.info(f"Client mis à jour : ", client)
        return client
    except Client.DoesNotExist:
        logging.warning("Client non trouvé pour la mise à jour.")
        return None
    
#################### VEHICULE ###################
def insert_vehicule():
    vehicule_data = {
        "client": 4,
        "marque": "BMW",
        "modele": "X5",
        "immatriculation": "XY-456-ZT",
        "numero_serie": "WBAVL11080VR12345",
        "mise_circulation": "2018-09-10",
        "kilometrage": 54000,
        "remarque": "Révision récente",
        "boite_vitesse": "Automatique",
        "carburant": "Diesel",
    }
    try:
        car = Vehicule(
            client = Client.objects.get(id=vehicule_data.get("client", None)),
            marque=vehicule_data.get("marque", ""),
            modele=vehicule_data.get("modele", ""),
            immatriculation=vehicule_data.get("immatriculation", ""),
            numero_serie=vehicule_data.get("numero_serie", ""),
            mise_circulation=vehicule_data.get("mise_circulation", None),
            kilometrage=vehicule_data.get("kilometrage", None),
            remarque=vehicule_data.get("remarque", ""),
            boite_vitesse = vehicule_data.get("boite_vitesse", ""),
            carburant = vehicule_data.get("carburant", ""),
            vo = vehicule_data.get("vo", False),
        )
        car.save()
        logging.info(f"Véhicule enregistré :", car)
        return car

    except Exception as e:
        logging.warning(f" Erreur lors de l'insertion :", e)
        return None
    
def update_vehicule():
    vehicule_data = {
        "id": 6,  
        "marque": "Audi",
        "modele": "A4",
        "immatriculation": "EF-456-GH",
        "numero_serie": "WAUZZZ8KXFA123456",
        "mise_circulation": "2019-03-10",
        "kilometrage": 50000,
        "remarque": "",
        "boite_vitesse": "Automatique",
        "carburant": "Diesel",
        "vo": True,
    }
    try:
        vehicule = Vehicule.objects.get(id=vehicule_data.get("id", None))
        vehicule.marque = vehicule_data.get("marque", vehicule.marque)
        vehicule.modele = vehicule_data.get("modele", vehicule.modele)
        vehicule.immatriculation = vehicule_data.get("immatriculation", vehicule.immatriculation)
        vehicule.numero_serie = vehicule_data.get("numero_serie", vehicule.numero_serie)
        vehicule.mise_circulation = vehicule_data.get("mise_circulation", vehicule.mise_circulation)
        vehicule.kilometrage = vehicule_data.get("kilometrage", vehicule.kilometrage)
        vehicule.remarque = vehicule_data.get("remarque", vehicule.remarque)
        vehicule.boite_vitesse = vehicule_data.get("boite_vitesse", vehicule.boite_vitesse)
        vehicule.carburant = vehicule_data.get("carburant", vehicule.carburant)
        vehicule.vo = vehicule_data.get("vo", False)
        
        vehicule.save()
        logging.info(f"Véhicule mis à jour :", vehicule)
        return vehicule
    except Vehicule.DoesNotExist:
        logging.warning("Véhicule non trouvé pour la mise à jour.")
        
        
def delete_vehicule():
    try:
        vehicule = Vehicule.objects.get(id=12)  # Assuming the vehicle ID is known
        vehicule.delete()
        logging.info("Véhicule supprimé avec succès.")
    except Vehicule.DoesNotExist:
        logging.warning("Véhicule non trouvé.")
    except Exception as e:
        logging.warning(f"Erreur lors de la suppression du véhicule : {e}")
        

###################### INTERVENTION ######################
def insert_intervention():
    intervention_data = {
        "libelle": "Remplacement pneus avant",
        "duree_intervention": 2.00,
        "prix_unitaire": 75.00,
        "description": "Montage et équilibrage des pneus avant",
        "categorie": "Pneumatique",
        "forfait": 140.00,
        "is_forfait": True,
    }
    try:
        intervention = Intervention(
            libelle=intervention_data.get("libelle", ""),
            duree_intervention=intervention_data.get("duree_intervention", 0.0),
            prix_unitaire=intervention_data.get("prix_unitaire", 0.0),
            description=intervention_data.get("description", ""),
            categorie=intervention_data.get("categorie", ""),
            forfait=intervention_data.get("forfait", 0.0),
            is_forfait=intervention_data.get("is_forfait", False),
        )
        intervention.save()
        logging.info(f"Intervention enregistrée :", intervention)
        return intervention
    except Exception as e:
        logging.warning(f"Erreur lors de l'insertion :", e)
        return None
    
def delete_intervention():
    try:
        intervention = Intervention.objects.get(id=3)  # Assuming the intervention ID is known
        intervention.delete()
        logging.info("Intervention supprimée avec succès.")
    except Intervention.DoesNotExist:
        logging.warning("Intervention non trouvée.")
    except Exception as e:
        logging.warning(f"Erreur lors de la suppression de l'intervention : {e}")    
    
######################## MISSION ######################        
def insert_mission(): 
    mission = {
        "client": 4,
        "vehicule": 4,
        "remarque": "",
        "priorite": "Urgent",
        "date_demande": "2023-10-01T10:00:00Z",  # Format ISO 8601
    }
    try: 
        mission = Mission(
            client=Client.objects.get(id=mission.get("client", None)),
            vehicule=Vehicule.objects.get(id=mission.get("vehicule", None)),
            remarque=mission.get("remarque", ""),
            priorite=mission.get("priorite", ""),
        )
        mission.save()
        logging.info(f"Mission enregistrée :", mission)
        return mission
    except Exception as e:
        logging.warning(f"Erreur lors de l'insertion :", e)
        return None

def delete_mission():
    try:
        mission = Mission.objects.get(id=3)  
        mission.delete()
        logging.info("Mission supprimée avec succès.")
    except Mission.DoesNotExist:
        logging.warning("Mission non trouvée.")
    except Exception as e:
        logging.warning(f"Erreur lors de la suppression de la mission : {e}")    
    
#################### MISSION INTERVENTION #####################
def insert_mission_intervention():
    mission_intervention_data = {
        "duree_supplementaire": 0.00,
        "taux": "T2",
        "zone": "Test durée",
        "interventions": [5, 6],  
    }
    try:
        mission = Mission.objects.get(id=7)  
        interventions = mission_intervention_data.get("interventions", [])
        if not interventions:
            logging.warning("Aucune intervention fournie pour la mission.")
            return None
        mission_interventions = []
        for intervention_id in interventions:
            intervention_obj = Intervention.objects.get(id=intervention_id)
            duree_supp = Decimal(str(mission_intervention_data.get("duree_supplementaire", 0.00)))
            cout_total = intervention_obj.prix_unitaire * duree_supp + intervention_obj.forfait

            mission_intervention = MissionIntervention(
                mission=mission,
                intervention=intervention_obj,
                duree_supplementaire=duree_supp,
                taux=mission_intervention_data.get("taux", ""),
                zone=mission_intervention_data.get("zone", ""),
                cout_total= cout_total
            )
            mission_intervention.save()
            mission_interventions.append(mission_intervention)
            logging.info(f"MissionIntervention enregistrée : {mission_intervention}")
        return mission_interventions
    except Exception as e:
        logging.warning(f"Erreur lors de l'insertion de mission_interventions : {e}")
    return None

def delete_mission_intervention():
    try:
        mission_intervention = MissionIntervention.objects.get(id=1) 
        mission_intervention.delete()
        logging.info("MissionIntervention supprimée avec succès.")
    except MissionIntervention.DoesNotExist:
        logging.warning("MissionIntervention non trouvée.")
    except Exception as e:
        logging.warning(f"Erreur lors de la suppression de la mission_intervention : {e}")

################### SUPPRESSION DES DONNÉES ###################
def delete_data():
    try:
        # Vehicule.objects.all().delete()
        # Client.objects.all().delete()
        # Intervention.objects.all().delete()
        # Mission.objects.all().delete()
        MissionIntervention.objects.all().delete()
        logging.info("Toutes les données ont été supprimées.")
    except Exception as e:
        logging.warning(f"Erreur lors de la suppression : {e}")
    return None

            


