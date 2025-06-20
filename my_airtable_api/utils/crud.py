import logging
from mission.models import Client, Vehicule, Intervention, Mission, MissionIntervention
from my_airtable_api.utils.extract_data import ValidationError

def create_client(data, erreurs):
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
        logging.info(f"Recherche du véhicule avec id={vehicule_id}")
        vehicule = Vehicule.objects.get(id=vehicule_id)
        logging.info(f"Vehicle found: {vehicule}")
        return vehicule
    except Vehicule.DoesNotExist:
        logging.error(f"Vehicle with id {vehicule_id} does not exist.")
        return None