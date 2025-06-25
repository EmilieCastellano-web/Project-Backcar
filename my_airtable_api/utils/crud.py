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
        data.pop('id', None)  # retire 'id' si déjà présent
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
    """Crée un véhicule à partir des données fournies.
    Args:
        data (dict): Les données du véhicule à créer
        client (Client): L'objet client auquel le véhicule est associé
        erreurs (dict): Un dictionnaire pour stocker les erreurs de validation
    Returns:
        Vehicule: L'objet véhicule créé
    Raises:
        ValidationError: Si des erreurs de validation sont détectées dans les données
    """    
    try:
        data.pop('id', None)  # retire 'id' si déjà présent
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

def create_taches(mission_interventions, client, vehicule):
    """Fonction principale de la création. Crée les tâches (mission, client, véhicule) à partir des données fournies.
    Args:
        data (dict): Les données de la mission, du client et du véhicule.
    Returns:
        Mission: L'objet mission créé.
    Raises:
        ValidationError: Si des erreurs de validation sont détectées dans les données.
    """
    try:
        with transaction.atomic():
            # Création de la mission à partir du premier élément (toutes les interventions ont la même mission)
            mission_data = mission_interventions[0]['mission']
            mission_data['client'] = client
            mission_data['vehicule'] = vehicule

            interventions = [mi['intervention'] for mi in mission_interventions]

            mission = create_mission(mission_data, interventions, erreurs={})

            # Création des liaisons mission-intervention
            mission_intervention_list = []
            for mi in mission_interventions:
                mi_data = {
                    'mission': mission,
                    'intervention': mi['intervention'],
                    'duree_supplementaire': mi['duree_supplementaire'],
                    'taux': mi['taux'],
                    'cout_total': mi['cout_total']
                }
                mission_intervention_list.append(mi_data)

            create_mission_interventions(mission_intervention_list, erreurs={})

        return mission
    except Exception as e: 
        logging.error(f"Error in create_taches: {e}")
        raise ValidationError("Erreur lors de la création des tâches")

def create_mission(mission_data, interventions, erreurs):
    """Crée une mission à partir des données fournies.
    
    Args:
        mission_data (dict): Les données de la mission à créer.
        interventions (list): Liste des interventions associées à la mission.
        erreurs (dict): Un dictionnaire pour stocker les erreurs de validation.
        
    Returns:
        Mission: L'objet mission créé.
        
    Raises:
        ValidationError: Si des erreurs de validation sont détectées dans les données.
    """
    try:
        logging.info(f"Type mission_data client: {type(mission_data.get('client'))}")

        fields = ['remarque', 'priorite', 'client', 'vehicule']
        mission = Mission.objects.create(**{f: mission_data[f] for f in fields})

        logging.info(f"Mission created: {mission}")
        
        return mission
    except Exception as e:
        logging.error(f"Error creating mission: {e}")
        raise ValidationError("Erreur lors de la création de la mission", details=erreurs)
    
def create_mission_interventions(mission_interventions, erreurs):
    """Crée les interventions liées à une mission.
    Args:
        mission_interventions (list): Liste des données des interventions à créer.
        erreurs (dict): Un dictionnaire pour stocker les erreurs de validation.
    Raises:
        ValidationError: Si des erreurs de validation sont détectées dans les données.
    Returns:
        None
    """
    try:
        for mi_data in mission_interventions:
            MissionIntervention.objects.create(**mi_data)
        logging.info("Mission interventions created successfully.")
    except Exception as e:
        logging.error(f"Error creating mission interventions: {e}")
        raise ValidationError("Erreur lors de la création des interventions", details=erreurs)

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
    logging.info(f"update_mission_interventions - Mission ID: {mission.id}")
    logging.info(f"update_mission_interventions - Interventions reçues: {len(interventions_data)}")
    
    # Récupérer les interventions actuelles avant suppression pour logs
    current_interventions = MissionIntervention.objects.filter(mission=mission)
    logging.info(f"update_mission_interventions - Interventions actuelles avant suppression: {[mi.intervention.id for mi in current_interventions]}")
    
    MissionIntervention.objects.filter(mission=mission).delete()  # reset
    logging.info("update_mission_interventions - Toutes les interventions actuelles supprimées")
    
    updated = []

    for mi in interventions_data:
        logging.info(f"update_mission_interventions - Création intervention: {mi['intervention'].id} - {mi['intervention'].libelle}")
        mi_obj = MissionIntervention.objects.create(
            mission=mission,
            intervention=mi['intervention'],
            duree_supplementaire=mi.get('duree_supplementaire', 0.0),
            taux=mi['taux'],
            cout_total=mi['cout_total']
        )
        updated.append(mi_obj)

    logging.info(f"{len(updated)} interventions liées à la mission recréées.")
    logging.info(f"update_mission_interventions - Nouvelles interventions: {[mi.intervention.id for mi in updated]}")
    return updated
        
def intervention_get_by_id(intervention_id):
    """Récupère une intervention par son ID.
    Args:
        intervention_id (int): L'ID de l'intervention à récupérer.
    Returns:
        Intervention: L'objet Intervention correspondant à l'ID.
    Raises:
        ValidationError: Si l'intervention n'existe pas.
    """
    try:
        intervention = Intervention.objects.get(id=intervention_id)
        return intervention
    except Intervention.DoesNotExist:
        logging.error(f"Intervention with id {intervention_id} does not exist.")
        raise ValidationError(f"Intervention with id {intervention_id} does not exist.")
    
def get_client_by_id(client_id):
    """Récupère un client par son ID.

    Args:
        client_id (int): L'ID du client à récupérer.

    Returns:
        Client: L'objet Client correspondant à l'ID.
    """
    try:
        client = Client.objects.get(id=client_id)
        return client
    except Client.DoesNotExist:
        logging.error(f"Client with id {client_id} does not exist.")
        return None
    
def get_vehicule_by_id(vehicule_id):
    """Récupère un véhicule par son ID.

    Args:
        vehicule_id (int): L'ID du véhicule à récupérer.

    Returns:
        Vehicule: L'objet Vehicule correspondant à l'ID.
    """
    try:
        vehicule = Vehicule.objects.get(id=vehicule_id)
        return vehicule
    except Vehicule.DoesNotExist:
        logging.error(f"Vehicle with id {vehicule_id} does not exist.")
        return None
    
def get_all_mission_intervention_by_id(mission_id):
    """Récupère toutes les interventions liées à une mission par son ID.
    Args:
        mission_id (int): L'ID de la mission pour laquelle récupérer les interventions.
    Returns:
        QuerySet: Un queryset contenant toutes les interventions liées à la mission.
    Raises:
        MissionIntervention.DoesNotExist: Si aucune intervention n'est trouvée pour la mission.
    """
    try:
        missions_interventions = MissionIntervention.objects.filter(mission_id=mission_id).select_related('mission', 'intervention')
        logging.info(f"Mission intervention found: {missions_interventions}")
        return missions_interventions
    except MissionIntervention.DoesNotExist:
        logging.error(f"Mission intervention with id {mission_id} does not exist.")
        return None
    
def get_all_interventions():
    """Récupère toutes les interventions.
    
    Returns:
        QuerySet: Un queryset contenant toutes les interventions.
    """
    try:
        interventions = Intervention.objects.all()
        logging.info(f"All interventions retrieved: {interventions.count()} found.")
        return interventions
    except Exception as e:
        logging.error(f"Error retrieving all interventions: {e}")
        raise ValidationError("Erreur lors de la récupération des interventions.")    

def get_mission_by_id(mission_id):
    """Récupère une mission par son ID.
    Args:
        mission_id (int): L'ID de la mission à récupérer.
    Returns:
        Mission: L'objet Mission correspondant à l'ID.
    Raises:
        Mission.DoesNotExist: Si la mission n'existe pas.
    """
    try:
        mission = Mission.objects.get(id=mission_id)
        logging.info(f"Mission found: {mission}")
        return mission
    except Mission.DoesNotExist:
        logging.error(f"Mission with id {mission_id} does not exist.")
        return None
    
def delete_mission(mission_id):
    """Supprime une mission et toutes ses relations associées.
    
    Args:
        mission_id (int): L'ID de la mission à supprimer.
        
    Returns:
        dict: Un dictionnaire contenant les informations sur la suppression.
        
    Raises:
        ValidationError: Si la mission n'existe pas ou si une erreur survient lors de la suppression.
    """
    try:
        with transaction.atomic():
            # Récupération de la mission
            mission = Mission.objects.get(id=mission_id)
            
            # Récupération des informations avant suppression pour le retour
            mission_info = {
                'id': mission.id,
                'date_demande': mission.date_demande,
                'remarque': mission.remarque,
                'priorite': mission.priorite,
                'client': f"{mission.client.prenom} {mission.client.nom}",
                'vehicule': f"{mission.vehicule.marque} {mission.vehicule.modele}"
            }
            
            # Comptage des MissionIntervention liées (pour information)
            nb_interventions = MissionIntervention.objects.filter(mission=mission).count()
            
            # Suppression de la mission
            # Les MissionIntervention seront supprimées automatiquement grâce à CASCADE
            mission.delete()
            
            logging.info(f"Mission supprimée avec succès : {mission_info}")
            logging.info(f"Nombre d'interventions liées supprimées : {nb_interventions}")
            
            return {
                'success': True,
                'mission_info': mission_info,
                'nb_interventions_supprimees': nb_interventions,
                'message': f"Mission {mission_id} supprimée avec succès"
            }
            
    except Mission.DoesNotExist:
        logging.error(f"Mission avec l'ID {mission_id} introuvable")
        raise ValidationError(f"Mission avec l'ID {mission_id} introuvable")
    except Exception as e:
        logging.error(f"Erreur lors de la suppression de la mission {mission_id}: {e}")
        raise ValidationError(f"Erreur lors de la suppression de la mission : {str(e)}")
