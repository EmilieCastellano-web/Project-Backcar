from datetime import datetime
import logging
from mission.models import Intervention, Taux

class ValidationError(Exception):
    def __init__(self, message, field=None, details=None):
        self.message = message
        self.field = field
        self.details = details or {}
        super().__init__(message)     

def extract_data_client(request, erreurs): 
    client_id = request.POST.get('client')
    
    if client_id:
        return {'id': client_id}

    client = {
        'nom': request.POST.get('nom', "").strip(),
        'prenom': request.POST.get('prenom', "").strip(),
        'email': request.POST.get('email', "").strip(),
        'societe': request.POST.get('societe', "").strip(),
        'telephone': request.POST.get('telephone', "").strip(),
        'adresse': request.POST.get('adresse', "").strip(),
        'code_postal': request.POST.get('code_postal', "").strip(),
        'ville': request.POST.get('ville', "").strip()
    }
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
    vehicule_id = request.POST.get('vehicule')
    if vehicule_id:
        return {'id': vehicule_id}
    else:
        date_str = request.POST.get('mise_circulation', "")
        if date_str:
            mise_circulation = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            mise_circulation = None
        vehicule =  {
            'marque': request.POST.get('marque'),
            'modele': request.POST.get('modele'),
            'immatriculation': request.POST.get('immatriculation'),
            'numero_serie': request.POST.get('numero_serie'),
            'mise_circulation': mise_circulation,
            'kilometrage': request.POST.get('kilometrage', ""),
            'remarque': request.POST.get('remarque_vehicule', ""),
            'vo': request.POST.get('vo') == 'on',
            'boite_vitesse': request.POST.get('boite_vitesse'),
            'carburant': request.POST.get('carburant'),
            'client': client 
        }
        
        if not vehicule['marque']:
            erreurs['vehicule']['marque'] = "La marque est requise"
        if not vehicule['modele']:
            erreurs['vehicule']['modele'] = "Le modèle est requis"
        if not vehicule['immatriculation'] or len(vehicule['immatriculation']) != 7 or not vehicule['immatriculation'].isalnum():
            erreurs['vehicule']['immatriculation'] = "L'immatriculation doit comporter 9 caractères alphanumériques"
        if not vehicule['numero_serie'] or len(vehicule['numero_serie']) != 17:
            erreurs['vehicule']['numero_serie'] = "Le numéro de série doit comporter 17 caractères"
        if not vehicule['kilometrage'].isdigit() or int(vehicule['kilometrage']) < 0:
            erreurs['vehicule']['kilometrage'] = "Le kilométrage doit être un nombre positif"
        if not vehicule['boite_vitesse']:
            erreurs['vehicule']['boite_vitesse'] = "La boîte de vitesse est requise"
        if not vehicule['carburant']:
            erreurs['vehicule']['carburant'] = "Le type de carburant est requis"
        if erreurs['vehicule']:
            raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
        
    return vehicule
    
def extract_data_intervention(request, erreurs):
    from .crud import intervention_get_by_id

    interventions_list = []  # initialisation avant la boucle
    interventions_ids = request.POST.get('interventions', '')
    # logging.info(f"Interventions IDs: {interventions_ids}")
    if not interventions_ids:
        erreurs['intervention']['length'] = "Aucune intervention n'a été ajoutée"
        raise ValidationError("Aucune intervention n'a été ajoutée", details=erreurs)
    
    for i in interventions_ids.split(','):
        try:
            intervention = intervention_get_by_id(i)
            interventions_list.append(intervention)
            logging.info(f"Intervention added: {intervention.libelle}")
        except Intervention.DoesNotExist:
            erreurs['intervention']['id'] = f"L'intervention avec l'ID {i} n'existe pas"
            raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
        
    return interventions_list

def extract_data_mission(request, vehicule):
    
    mission = {
        'remarque': request.POST.get('remarque_mission'),
        'priorite': request.POST.get('priorite'),
        'vehicule': vehicule,
        'client': vehicule.client
    }
    return mission

def extract_data_mission_intervention(request, mission, interventions, erreurs):
    mission_interventions = []
    cout_total = 0.0  
    for intervention in interventions:
        try:
            duree_supp = float(request.POST.get(f'duree_supplementaire_{intervention.id}', 0.0))
            taux = request.POST.get(f'taux', '')
            if intervention.is_forfait:
                cout = float(intervention.forfait)
            else:
                if duree_supp == 0.0:
                    cout = float(intervention.prix_unitaire)
                else:
                    cout = float(intervention.prix_unitaire) * duree_supp
            cout_total += cout
            
            mission_intervention = {
                'mission': mission,
                'intervention': intervention,
                'duree_supplementaire': duree_supp,
                'taux': taux,
                'cout_total': cout_total
            }
            if mission_intervention['cout_total'] < 0:
                erreurs['mission']['cout_total'] = "Le coût total ne peut pas être négatif"
            if not taux or taux not in [choix.name for choix in Taux]:
                erreurs['mission']['taux'] = "Le taux horaire est requis et doit être valide"
            if erreurs['mission']:
                raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
            
            mission_interventions.append(mission_intervention)
        
        except ValueError as e:
            logging.error(f"Invalid data for intervention {intervention.id}: {e}")
            raise

    return mission_interventions
