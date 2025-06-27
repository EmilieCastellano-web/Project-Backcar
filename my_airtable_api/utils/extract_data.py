from datetime import datetime
import logging
from mission.models import  Taux, Vehicule, Client

class ValidationError(Exception):
    def __init__(self, message, field=None, details=None):
        self.message = message
        self.field = field
        self.details = details or {}
        super().__init__(message)     

def extract_data_client(request, erreurs):
    """Extrait les données d'un client à partir d'une requête HTTP POST.

    Args:
        request (HttpRequest): La requête HTTP contenant les données POST du formulaire
        erreurs (dict): Un dictionnaire pour stocker les erreurs de validation

    Raises:
        ValidationError: Si des erreurs de validation sont détectées dans les données
        ValidationError: Si des erreurs de validation sont détectées dans les données

    Returns:
        dict: Un dictionnaire contenant les données du client
    """
    mode = ""
    if '/new/' in request.path:
        mode = "create"
    elif '/edit/' in request.path:
        mode = "update"
    
    if mode == "update":
        client_id = request.POST.get('client_id')
        
    
    if mode == "update" and not client_id:
        erreurs['client']['id'] = "L'identifiant du client est requis pour une mise à jour"
        raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
    
    if mode == "create":    
        client_id = request.POST.get('client')
        if client_id:
            return {'id': client_id}

    client = {
        'id': client_id if client_id else None,
        'nom': request.POST.get('nom', "").strip(),
        'prenom': request.POST.get('prenom', "").strip(),
        'email': request.POST.get('email', "").strip(),
        'societe': request.POST.get('societe', "").strip(),
        'telephone': request.POST.get('telephone', "").strip(),
        'adresse': request.POST.get('adresse', "").strip(),
        'code_postal': request.POST.get('code_postal', "").strip(),
        'ville': request.POST.get('ville', "").strip()
    }
    erreurs.setdefault('client', {})

    if not client['nom']:
        erreurs['client']['nom'] = "Le nom est requis"
    if not client['email'] or "@" not in client['email']:
        erreurs['client']['email'] = "L'adresse email est invalide"
    if not client['telephone'] or len(client['telephone']) != 10:
        erreurs['client']['telephone'] = "Le numéro de téléphone doit comporter 10 chiffres"
    if not client['code_postal'] or len(client['code_postal']) != 5:
        erreurs['client']['code_postal'] = "Le code postal doit comporter 5 chiffres"
    if not client['ville']:
        erreurs['client']['ville'] = "La ville est requise"

    if erreurs['client']: 
        raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
    
    return client
    
def extract_data_vehicule(request, client, erreurs):
    """Extrait les données d'un véhicule à partir d'une requête HTTP POST.

    Args:
        request (HttpRequest): La requête HTTP contenant les données POST du formulaire
        client (dict): Les données du client associé au véhicule
        erreurs (dict): Un dictionnaire pour stocker les erreurs de validation

    Raises:
        ValidationError: Si des erreurs de validation sont détectées dans les données
        ValidationError: Si des erreurs de validation sont détectées dans les données

    Returns:
        dict: Un dictionnaire contenant les données du véhicule
    """
    # compare_km = MinValueValidator(0)
    
    mode = ""
    if '/new/' in request.path:
        mode = "create"
    elif '/edit/' in request.path:
        mode = "update"
    
    vehicule_id = request.POST.get('vehicule_id')
    
    if not vehicule_id:
            date_str = request.POST.get('mise_circulation', "")
            if date_str:
                mise_circulation = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                mise_circulation = None
    
    if mode == "update" and not vehicule_id:
        erreurs['vehicule']['id'] = "L'identifiant du véhicule est requis pour une mise à jour"
        raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
    
    if mode == "create":
        if vehicule_id:
            return {'id': vehicule_id}

        vehicule =  {
            'id': vehicule_id if vehicule_id else None,
            'marque': request.POST.get('marque'),
            'modele': request.POST.get('modele'),
            'immatriculation': request.POST.get('immatriculation'),
            'numero_serie': request.POST.get('numero_serie'),
            'mise_circulation': mise_circulation if mise_circulation else None,
            'kilometrage': request.POST.get('kilometrage', 0),
            'remarque': request.POST.get('remarque_vehicule', ""),
            'vo': request.POST.get('vo') == 'on',
            'boite_vitesse': request.POST.get('boite_vitesse'),
            'carburant': request.POST.get('carburant'),
            'client': client 
        }
        erreurs.setdefault('vehicule', {})
        
        if not vehicule['marque']:
            erreurs['vehicule']['marque'] = "La marque est requise"
        if not vehicule['modele']:
            erreurs['vehicule']['modele'] = "Le modèle est requis"
        if not vehicule['immatriculation'] or len(vehicule['immatriculation']) != 7 or not vehicule['immatriculation'].isalnum():
            erreurs['vehicule']['immatriculation'] = "L'immatriculation doit comporter 9 caractères alphanumériques"
        if not vehicule['numero_serie'] or len(vehicule['numero_serie']) != 17:
            erreurs['vehicule']['numero_serie'] = "Le numéro de série doit comporter 17 caractères"
            
        if not vehicule['boite_vitesse']:
            erreurs['vehicule']['boite_vitesse'] = "La boîte de vitesse est requise"
        if not vehicule['carburant']:
            erreurs['vehicule']['carburant'] = "Le type de carburant est requis"
        if erreurs['vehicule']:
            raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
        
        
    if mode == "update":
        
        vehicule = {
            'id': vehicule_id,
            'kilometrage': request.POST.get('kilometrage', ""),
            'remarque': request.POST.get('remarque_vehicule', ""),
            'vo': request.POST.get('vo') == 'on',
        }
    
    return vehicule
    
def extract_data_intervention(request, erreurs):
    """Extrait les données d'une intervention à partir d'une requête HTTP POST.

    Args:
        request (HttpRequest): La requête HTTP contenant les données POST du formulaire
        erreurs (dict): Un dictionnaire pour stocker les erreurs de validation

    Raises:
        ValidationError: Si des erreurs de validation sont détectées dans les données

    Returns:
        dict: Un dictionnaire contenant les données de l'intervention
    """
    from .crud import intervention_get_by_id
    import logging

    # Récupération de toutes les interventions (actuelles + nouvelles)
    intervention_ids = request.POST.get('interventions', '') 
    logging.info(f"extract_data_intervention - IDs reçus: '{intervention_ids}'")
    
    interventions = []
    
    if intervention_ids.strip():  # Vérifier que ce n'est pas vide
        for i in intervention_ids.split(','):
            intervention_id = i.strip()  # Nettoyer les espaces
            if intervention_id:  # Vérifier que l'ID n'est pas vide
                try:
                    intervention = intervention_get_by_id(intervention_id)  
                    interventions.append(intervention)
                    logging.info(f"Intervention trouvée: {intervention.id} - {intervention.libelle}")
                except Exception as e:
                    logging.error(f"Erreur lors de la récupération de l'intervention {intervention_id}: {e}")
                    erreurs['intervention'][intervention_id] = f"L'intervention avec l'ID {intervention_id} n'existe pas"
                    raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
    if not interventions:
        erreurs['intervention']['interventions'] = "Aucune intervention sélectionnée"
        raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
    logging.info(f"extract_data_intervention - Total interventions extraites: {len(interventions)}")
    return {'interventions': interventions}

def extract_data_mission(request, vehicule, client, erreurs, mission_id):
    """Extrait les données d'une mission à partir d'une requête HTTP POST.

    Args:
        request (HttpRequest): La requête HTTP contenant les données POST du formulaire
        vehicule (dict): Les données du véhicule associé à la mission
        client (dict): Les données du client associé à la mission
        erreurs (dict): Un dictionnaire pour stocker les erreurs de validation
        mission_id (int): L'ID de la mission à mettre à jour (le cas échéant)

    Raises:
        ValidationError: Si des erreurs de validation sont détectées dans les données

    Returns:
        dict: Un dictionnaire contenant les données de la mission
    """
    if isinstance(client, dict):
        client_obj = Client.objects.get(id=client['id'])
    else:
        client_obj = client

    if isinstance(vehicule, dict):
        vehicule_obj = Vehicule.objects.get(id=vehicule['id'])
    else:
        vehicule_obj = vehicule


    mission = {
        'id': mission_id if mission_id else None,
        'remarque': request.POST.get('remarque_mission'),
        'priorite': request.POST.get('priorite'),
        'vehicule': vehicule_obj,
        'client': client_obj
    }
    erreurs.setdefault('mission', {})
    # Validation des données de la mission
    if not mission['priorite']:
        erreurs['mission']['priorite'] = "La priorité est requise"
    if not mission['vehicule']:
        erreurs['mission']['vehicule'] = "Le véhicule est requis"
    if not mission['client']:
        erreurs['mission']['client'] = "Le client est requis"
    if erreurs['mission']:
        raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
    
    return mission

def extract_data_mission_intervention(request, mission, interventions, erreurs):
    """Extrait les données des interventions de mission à partir d'une requête HTTP POST.

    Args:
        request (HttpRequest): La requête HTTP contenant les données POST du formulaire
        mission (dict): Les données de la mission associée
        interventions (list): La liste des interventions sélectionnées pour la mission
        erreurs (dict): Un dictionnaire pour stocker les erreurs de validation

    Raises:
        ValidationError: Si des erreurs de validation sont détectées dans les données

    Returns:
        list: Une liste de dictionnaires contenant les données des interventions de mission
    """
    mission_interventions = []
    cout_total = 0.0    
    taux = request.POST.get(f'taux', '')
    duree_supp = float(request.POST.get('duree_supplementaire', 0.0) or 0.0)
    duree_supp_total = duree_supp + mission.get('duree_supplementaire', 0.0)
    logging.info(f"extract_data_mission_intervention - Taux: {taux}, Durée supplémentaire: {duree_supp}, Durée totale: {duree_supp_total}")

    match taux:
        case 'HORAIRE':
            taux_calcul = 1.0
        case 'T1':
            taux_calcul = 1.5
        case 'T2':
            taux_calcul = 2.0
        case 'T3':
            taux_calcul = 2.5 
    
    for intervention in interventions['interventions']:
        try:
            if intervention.is_forfait:
                cout = float(intervention.forfait)
            else:
                cout = float(intervention.prix_unitaire) * taux_calcul
            if duree_supp > 0:   
                cout *= duree_supp or 1.0
                
            cout_total += cout
            mission_intervention = {
                'mission': mission,
                'intervention': intervention,
                'duree_supplementaire': duree_supp_total, 
                'taux': taux,
                'cout_total': cout
            }
            erreurs.setdefault('mission_intervention', {})
            logging.info (f"MISSION INTERVENTION: {mission_intervention}")

            if mission_intervention['cout_total'] < 0:
                erreurs['mission_intervention']['cout_total'] = "Le coût total ne peut pas être négatif"
            if not taux or taux not in [choix.name for choix in Taux]:
                erreurs['mission_intervention']['taux'] = "Le taux horaire est requis et doit être valide"
            if erreurs['mission_intervention']:
                raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)

            mission_interventions.append(mission_intervention)
        
        except ValueError as e:
            logging.error(f"Invalid data for intervention {intervention.id}: {e}")
            raise

    return mission_interventions
