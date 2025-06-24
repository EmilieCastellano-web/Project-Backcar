import logging
from mission.models import Client, Vehicule, Intervention, Mission, MissionIntervention
from my_airtable_api.utils.extract_data import ValidationError
from django.db import transaction

def create_client(data, erreurs):
    """Crée un client à partir des données fournies.
    Args:
        data (dict): Les données du client à créer
        erreurs (dict): Un dictionnaire pour stocker les erreurs de validation
    Returns:
        Client: L'objet client créé
    Raises:
        ValidationError: Si des erreurs de validation sont détectées dans les données
    """
    
    try:
        # Vérification client déjà existant
        if 'email' in data:
            client = Client.objects.filter(email=data['email']).first()
            if client:
                erreurs['client']['email'] = "Un client avec cet email existe déjà"
                raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
            
        client = Client.objects.create(**data)
        logging.info(f"Client created: {client.nom} {client.prenom}")
        return client
    except Exception as e:
        logging.error(f"Error creating client: {e}")
        raise

def create_vehicule(data, client, erreurs):
    try:
        vehicule = Vehicule.objects.filter(numero_serie=data.get('numero_serie')).first()
        if vehicule:
            erreurs['vehicule']['numero_serie'] = "Un véhicule avec ce numéro de série existe déjà"
            raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
            
        data.pop('client', None)  # retire 'client' si déjà présent
        data['client'] = client
        vehicule = Vehicule.objects.create(**data)
        logging.info(f"Vehicle created for client {client.nom} {client.prenom}: {vehicule}")
        return vehicule
    except Exception as e:
        logging.error(f"Error creating vehicle: {e}")
        raise

def create_interventions(data_list, erreurs):
    interventions = []
    for data in data_list:
        interventions.append(Intervention.objects.create(**data))
    return interventions

def create_mission(data, client, vehicule, mission_intervention_data, erreurs):
    data = data.copy()  # pour ne pas modifier l'original
    data.pop('client', None)
    data.pop('vehicule', None)

    mission = Mission.objects.filter(vehicule=vehicule, client=client).first()
    if mission:
        erreurs['mission']['id'] = "Une mission pour ce véhicule et ce client existe déjà"
        raise ValidationError("Une mission pour ce véhicule et ce client existe déjà", details=erreurs)
    
    mission = Mission.objects.create(
        **data,
        client=client,
        vehicule=vehicule
    )
    logging.info(f"Mission created for vehicle {vehicule.marque} {vehicule.modele} and client {client.nom} {client.prenom}: {mission}")
    # 2. Ajout de la mission dans chaque relation
    for mi in mission_intervention_data:
        mi['mission'] = mission

    # 3. Création des enregistrements dans la table pivot
    create_mission_interventions(mission_intervention_data, erreurs)
    return mission

def create_mission_interventions(mission_interventions, erreurs):
    try:
        for mi_data in mission_interventions:
            MissionIntervention.objects.create(**mi_data)
        logging.info("Mission interventions created successfully.")
    except Exception as e:
        logging.error(f"Error creating mission interventions: {e}")
        raise

def update_client(data):
    """Met à jour les informations d'un client.

    Args:
        data (dict): Les données du client à mettre à jour.

    Raises:
        ValidationError: Si le client n'existe pas.

    Returns:
        Client: L'objet client mis à jour.
    """
    try:
        client = Client.objects.get(id=data['id'])
        for key, value in data.items():
            if value is not None and key != 'id':
                setattr(client, key, value)
        client.save()
        logging.info(f"Client mis à jour : {client}")
        return client
    except Client.DoesNotExist:
        logging.error(f"Client introuvable : id={data.get('id')}")
        raise ValidationError("Client introuvable.")

def update_vehicule(data):
    """Met à jour les informations d'un véhicule.
    Args:
        data (dict): Les données du véhicule à mettre à jour.
    Raises:
        ValidationError: Si le véhicule n'existe pas.
    Returns:
        Vehicule: L'objet véhicule mis à jour.
    """
    try:
        vehicule = Vehicule.objects.get(id=data['id'])
        for key, value in data.items():
            if value is not None and key != 'id':
                setattr(vehicule, key, value)
        vehicule.save()
        logging.info(f"Véhicule mis à jour : {vehicule}")
        return vehicule
    except Vehicule.DoesNotExist:
        logging.error(f"Véhicule introuvable : id={data.get('id')}")
        raise ValidationError("Véhicule introuvable.")
            
def update_taches(data):
    """Fonction principale de l'update. Met à jour les tâches (mission, client, véhicule) à partir des données fournies.
    Args:
        data (dict): Les données de la mission, du client et du véhicule.
    Returns:
        Mission: L'objet mission mis à jour.
    Raises:
        ValidationError: Si des erreurs de validation sont détectées dans les données.
    """
    try:
        with transaction.atomic():
            client = update_client(data['client'])
            vehicule = update_vehicule(data['vehicule'])

            mission_data = data['mission']
            mission_data['client'] = client
            mission_data['vehicule'] = vehicule
            mission = update_mission(mission_data)

            update_mission_interventions(data['mission_interventions'], mission)

            return mission
    except Exception as e:
        logging.error(f"Erreur dans update_taches : {e}")
        raise
    
def update_mission(data):
    """Met à jour les informations d'une mission.
    Args:
        data (dict): Les données de la mission à mettre à jour.
    Raises:
        ValidationError: Si la mission n'existe pas.
    Returns:
        Mission: L'objet mission mis à jour.
    """
    try:
        mission = Mission.objects.get(id=data['id'])
        mission.remarque = data.get('remarque', '')
        mission.priorite = data.get('priorite')
        mission.vehicule = data.get('vehicule')
        mission.client = data.get('client')
        mission.save()
        logging.info(f"Mission mise à jour : {mission}")
        return mission
    except Mission.DoesNotExist:
        logging.error(f"Mission introuvable : id={data.get('id')}")
        raise ValidationError("Mission introuvable.")
    
def update_mission_interventions(interventions_data, mission):
    """Met à jour les interventions liées à une mission.
    Args:
        interventions_data (list): Liste des données des interventions à mettre à jour.
        mission (Mission): L'objet mission auquel les interventions sont liées.
    Returns:
        list: Liste des objets MissionIntervention mis à jour.
    Raises:
        ValidationError: Si des erreurs de validation sont détectées dans les données.
    """
    MissionIntervention.objects.filter(mission=mission).delete()  # reset
    updated = []

    for mi in interventions_data:
        mi_obj = MissionIntervention.objects.create(
            mission=mission,
            intervention=mi['intervention'],
            duree_supplementaire=mi.get('duree_supplementaire', 0.0),
            taux=mi['taux'],
            cout_total=mi['cout_total']
        )
        updated.append(mi_obj)

    logging.info(f"{len(updated)} interventions liées à la mission recréées.")
    return updated
        
def intervention_get_by_id(intervention_id):
    try:
        intervention = Intervention.objects.get(id=intervention_id)
        return intervention
    except Intervention.DoesNotExist:
        logging.error(f"Intervention with id {intervention_id} does not exist.")
        raise ValidationError(f"Intervention with id {intervention_id} does not exist.")
    
def get_client_by_id(client_id):
    try:
        client = Client.objects.get(id=client_id)
        return client
    except Client.DoesNotExist:
        logging.error(f"Client with id {client_id} does not exist.")
        return None
    
def get_vehicule_by_id(vehicule_id):
    try:
        vehicule = Vehicule.objects.get(id=vehicule_id)
        return vehicule
    except Vehicule.DoesNotExist:
        logging.error(f"Vehicle with id {vehicule_id} does not exist.")
        return None
    
def get_all_mission_intervention_by_id(mission_id):
    try:
        missions_interventions = MissionIntervention.objects.filter(mission_id=mission_id).select_related('mission', 'intervention')
        logging.info(f"Mission intervention found: {missions_interventions}")
        return missions_interventions
    except MissionIntervention.DoesNotExist:
        logging.error(f"Mission intervention with id {mission_id} does not exist.")
        return None
    
def get_mission_by_id(mission_id):
    try:
        mission = Mission.objects.get(id=mission_id)
        logging.info(f"Mission found: {mission}")
        return mission
    except Mission.DoesNotExist:
        logging.error(f"Mission with id {mission_id} does not exist.")
        return None