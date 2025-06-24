from django.shortcuts import render
from .models import Client, Vehicule, Intervention, MissionIntervention, Priorite, Taux
from django.shortcuts import render, redirect
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')
from django.db import transaction

from my_airtable_api.utils.crud import create_client, create_vehicule, create_mission, get_client_by_id, get_vehicule_by_id, get_all_mission_intervention_by_id, get_mission_by_id, update_taches
from my_airtable_api.utils.extract_data import ValidationError, extract_data_client, extract_data_vehicule, extract_data_intervention, extract_data_mission, extract_data_mission_intervention


def list_view(request):
    """"Affiche la liste des missions, véhicules et clients.
    Cette vue récupère les données des missions, véhicules et clients depuis la base de données
    et les organise pour les afficher dans un template.
    Returns:
        HttpResponse: La réponse HTTP contenant le rendu du template avec les données des missions, véhicules et clients.
    """
    missions_interventions = MissionIntervention.objects.select_related(
        'mission', 'mission__vehicule', 'mission__client', 'intervention'
    ).all()
    
    missions_group = {}
    for mi in missions_interventions:
        mission = mi.mission
        mission_id = mission.id
        if mission_id not in missions_group:
            missions_group[mission_id] = {
                'id': mission.id,
                'id_mission_intervention': mi.id,
                'date_demande': mission.date_demande,
                'remarque': mission.remarque,
                'priorite': mission.priorite.replace('_', ' ').title(),
                'taux': mi.taux.title(),
                'vehicule': f"{mission.vehicule.marque} {mission.vehicule.modele} {mission.vehicule.immatriculation}",
                'client': f"{mission.client.nom} {mission.client.prenom}",
                'cout_total': mi.cout_total,
                'interventions': []
            }
        missions_group[mission_id]['interventions'].append({
            'libelle': mi.intervention.libelle,
            'prix_unitaire': mi.intervention.prix_unitaire,
        })
        missions_group[mission_id]['cout_total'] += mi.cout_total
        
        
    missions = list(missions_group.values())
    
    
    # Récupération de la table Véhicule avec les relations nécessaires
    vehicules = Vehicule.objects.all()
    vehicules_group = {}
    for vehicule in vehicules:
        vehicules_group[vehicule.id] = {
            'id': vehicule.id,
            'marque': vehicule.marque,
            'modele': vehicule.modele,
            'immatriculation': vehicule.immatriculation,
            'numero_serie': vehicule.numero_serie,
            'mise_circulation': vehicule.mise_circulation,
            'kilometrage': vehicule.kilometrage,
            'remarque': vehicule.remarque,
            'client': f"{vehicule.client.nom} {vehicule.client.prenom}",
            'vo': vehicule.vo,
            'boite_vitesse': vehicule.boite_vitesse,
            'carburant': vehicule.carburant
        }
        for mi in missions_interventions:
            if mi.mission.vehicule.id == vehicule.id:
                vehicules_group[vehicule.id]['missions'] = vehicules_group[vehicule.id].get('missions', [])
                vehicules_group[vehicule.id]['missions'].append({
                    'id': mi.mission.id,
                    'date_demande': mi.mission.date_demande,
                    'priorite': mi.mission.priorite,
                    'cout_total': mi.cout_total,
                    'interventions': [
                        {
                            'libelle': mi.intervention.libelle
                        }
                    ]
                })
    vehicules = list(vehicules_group.values())  
    # Récupération de la table Client
    clients = Client.objects.all()
    clients_group = {}
    for client in clients:
        clients_group[client.id] = {
            'id': client.id,
            'nom': client.nom,
            'prenom': client.prenom,
            'email': client.email,
            'telephone': client.telephone,
            'adresse': client.adresse,
            'code_postal': client.code_postal,
            'ville': client.ville,
            'vehicules': []
        }
        for vehicule in vehicules:
            if vehicule['client'] == f"{client.nom} {client.prenom}":
                clients_group[client.id]['vehicules'].append(vehicule)
    clients = list(clients_group.values())
    return render(request, 'list-view.html', {
        'missions': missions,
        'vehicules': vehicules,
        'clients': clients
        }) 
    
def mission_form_view(request):
    """Affiche le formulaire de création d'une nouvelle mission.
    Cette vue gère l'affichage du formulaire pour créer une nouvelle mission.
    Si la requête est de type POST, elle traite les données du formulaire.
    Args:
        request: La requête HTTP contenant les données du formulaire
    Returns:
        HttpResponse: La réponse HTTP contenant le rendu du template du formulaire de mission
    Raises:
        ValidationError: Si des erreurs de validation sont détectées dans les données du formulaire
    """
    #TODDO MODIFIER FONCTION UN APPELLE AU CRUD 
    if request.method == 'POST':
        erreurs = {
            'client': {},
            'vehicule': {},
            'mission': {},
            'intervention': {}
        }
        try:
            with transaction.atomic():
                client_data = extract_data_client(request, erreurs)
                # Récupération ou création du client
                if client_data.get('id'):
                    client = get_client_by_id(client_data['id'])
                else:
                    client = create_client(client_data, erreurs)
                    
                # Récupération ou création du véhicule
                vehicule_data = extract_data_vehicule(request, client_data, erreurs)
                if vehicule_data.get('id'):
                    vehicule = get_vehicule_by_id(vehicule_data['id'])
                    if vehicule.client != client:
                        erreurs['vehicule']['client'] = "Le véhicule appartien à un autre client"
                        raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
                else:
                    vehicule = create_vehicule(vehicule_data, client, erreurs)
                
                interventions = extract_data_intervention(request, erreurs)
                
                mission_data = extract_data_mission(request, vehicule)
                mission_intervention_data = extract_data_mission_intervention(request, mission_data, interventions, erreurs)
                mission = create_mission(mission_data, client, vehicule, mission_intervention_data, erreurs)
                
                logging.info(f"Mission created: {mission}")
                return redirect('list_view')
        
        except ValidationError as ve:
            logging.error(f"Validation error: {ve.message}")
            # logging.info(f"VALEURS: {request.POST.dict()}")
            return render(request, 'new_mission.html', {
                'erreurs': erreurs,
                'valeurs': request.POST.dict(),
                'clients': Client.objects.all(),
                'vehicules': Vehicule.objects.all(),
                'interventions': Intervention.objects.all(),
                'priorites': [(choix.name, choix.value) for choix in Priorite],
                'taux': [(choix.name, choix.value) for choix in Taux]
                })
        
        except Exception as e:
            logging.error(f"Error creating mission: {e}")
            return render(request, 'error.html', {'error': str(e)})
    else:
        return render(request, 'new_mission.html', {
            'clients': Client.objects.all(),
            'vehicules': Vehicule.objects.all(),
            'interventions': Intervention.objects.all(),
            'priorites': [(choix.name, choix.value) for choix in Priorite],
            'taux': [(choix.name, choix.value) for choix in Taux]
        })

def update_mission_view(request, mission_id):
    """Affiche le formulaire de mise à jour d'une mission existante.
    Cette vue gère l'affichage du formulaire pour mettre à jour une mission existante.
    Si la requête est de type POST, elle traite les données du formulaire.
    Args:
        request: La requête HTTP contenant les données du formulaire
        id: L'identifiant de la mission à mettre à jour
    Returns:
        HttpResponse: La réponse HTTP contenant le rendu du template du formulaire de mise à jour de la mission
    Raises:
        ValidationError: Si des erreurs de validation sont détectées dans les données du formulaire
    """
    erreurs = {
        'client': {},
        'vehicule': {},
        'mission': {},
        'intervention': {},
        'mission_intervention': {}
    }
    mission_intervention_list = get_all_mission_intervention_by_id(mission_id)
    mission = get_mission_by_id(mission_id)
    if not mission:
        logging.error(f"Mission with id {mission_id} does not exist.")
        return render(request, 'error.html', {'error': 'Mission not found'})

    mission_intervention_display = [
        {
            'id': mi.id,
            'id_intervention': mi.intervention.id,
            'libelle': mi.intervention.libelle,
            'prix_unitaire': mi.intervention.prix_unitaire,
            'taux': mi.taux,
            'priorite': mi.mission.priorite,
            'cout_total': mi.cout_total
        } for mi in mission_intervention_list
    ]
    if request.method == 'POST':
            try:
                # 1. Extraction des données
                client = extract_data_client(request, erreurs)
                vehicule = extract_data_vehicule(request, client, erreurs)
                interventions = extract_data_intervention(request, erreurs)
                mission_data = extract_data_mission(request, vehicule, client, erreurs, mission_id)
                mission_interventions = extract_data_mission_intervention(request, mission_data, interventions, erreurs)

                # 2. Construction du paquet global
                data = {
                    'client': client,
                    'vehicule': vehicule,
                    'mission': mission_data,
                    'mission_interventions': mission_interventions
                }

                # 3. Mise à jour dans la BDD
                update_taches(data)

                return redirect('list_view')
            
            except ValidationError as ve:
                logging.warning(f"Validation error: {ve}")
                return render(request, 'update_mission.html', {
                    'erreurs': erreurs,
                    'valeurs': request.POST.dict(),
                    'mission': mission,
                    'mission_intervention': {
                        'mission': mission,
                        'mission_intervention_list': mission_intervention_list,
                        'vehicule': mission.vehicule,
                        'client': mission.client,
                    },
                    'mission_intervention_list': mission_intervention_display,
                    'interventions': Intervention.objects.all(),
                    'priorites': [(choix.name, choix.value) for choix in Priorite],
                    'taux': [(choix.name, choix.value) for choix in Taux],
                })
            except Exception as e:
                logging.error(f"Error updating GLOBAL: {e}")
                return render(request, 'error.html', {'error': str(e)})

    # GET : affichage du formulaire
    return render(request, 'update_mission.html', {
        'mission': mission,
        'mission_intervention': {
            'mission': mission,
            'mission_intervention_list': mission_intervention_list,
            'vehicule': mission.vehicule,
            'client': mission.client,
        },
        'mission_intervention_list': mission_intervention_display,
        'interventions': Intervention.objects.all(),
        'priorites': [(choix.name, choix.value) for choix in Priorite],
        'taux': [(choix.name, choix.value) for choix in Taux],
        'erreurs': erreurs,
    })