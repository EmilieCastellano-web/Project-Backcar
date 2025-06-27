from django.shortcuts import render
from django.shortcuts import render
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict

from ..models import Client, Vehicule, MissionIntervention, Priorite
from my_airtable_api.utils.error_manage import render_with_error_handling
from my_airtable_api.utils.crud import get_all_mission_intervention_by_id, get_mission_by_id, get_all_interventions

@login_required
def list_view(request):
    """Affiche la liste des missions, véhicules et clients avec filtrage.

    Args:
        request (HttpRequest): La requête HTTP contenant les paramètres de filtrage.

    Returns:
        HttpResponse: La réponse HTTP contenant le rendu du template avec les données filtrées.
    """
    # Récupération des paramètres de filtrage
    filter_client = request.GET.get('client-filtrage', '')
    filter_vehicule = request.GET.get('vehicule-filtrage', '')
    filter_priorite = request.GET.get('priorite-filtrage', '')
    filter_date_debut = request.GET.get('date_debut', '')
    filter_date_fin = request.GET.get('date_fin', '')
    
    # Construction de la requête avec filtres
    missions_interventions_query = MissionIntervention.objects.select_related(
        'mission', 'mission__vehicule', 'mission__client', 'intervention'
    )
    
    # Q -> permet d’écrire des filtres avec des conditions "OU" (|) et "NON" (~), ou de combiner plusieurs conditions.
    # Application des filtres
    if filter_client:
        missions_interventions_query = missions_interventions_query.filter(
            Q(mission__client__nom__icontains=filter_client) | 
            Q(mission__client__prenom__icontains=filter_client)
        )
    
    if filter_vehicule:
        missions_interventions_query = missions_interventions_query.filter(
            Q(mission__vehicule__marque__icontains=filter_vehicule) |
            Q(mission__vehicule__modele__icontains=filter_vehicule) |
            Q(mission__vehicule__immatriculation__icontains=filter_vehicule)
        )
    
    if filter_priorite:
        missions_interventions_query = missions_interventions_query.filter(
            mission__priorite=filter_priorite
        )
    
    if filter_date_debut:
        try:
            date_debut = datetime.strptime(filter_date_debut, '%Y-%m-%d').date()
            missions_interventions_query = missions_interventions_query.filter(
                mission__date_demande__date__gte=date_debut
            )
        except ValueError:
            pass  # Ignorer les dates mal formatées
    
    if filter_date_fin:
        try:
            date_fin = datetime.strptime(filter_date_fin, '%Y-%m-%d').date()
            missions_interventions_query = missions_interventions_query.filter(
                mission__date_demande__date__lte=date_fin
            )
        except ValueError:
            pass  # Ignorer les dates mal formatées
    
    missions_interventions = missions_interventions_query.all().order_by('mission__date_demande')
    
    missions_group = {}
    for mi in missions_interventions:
        mission = mi.mission
        mission_id = mission.id
        if mission_id not in missions_group:
            missions_group[mission_id] = {
                'id': mission.id,
                'date_demande': mission.date_demande,
                'remarque': mission.remarque,
                'priorite': mission.priorite.replace('_', ' ').title(),
                'taux': mi.taux.title(),
                'vehicule': f"{mission.vehicule.marque} {mission.vehicule.modele} {mission.vehicule.immatriculation}",
                'client': f"{mission.client.nom} {mission.client.prenom}",
                'cout_total': mi.cout_total,
                'duree_supplementaire': mi.duree_supplementaire,
                'interventions': []
            }
        missions_group[mission_id]['interventions'].append({
            'libelle': mi.intervention.libelle,
            'prix_unitaire': mi.intervention.prix_unitaire,
        })
        
        
    missions = list(missions_group.values())
    
    
    # Récupération de la table Véhicule avec les relations nécessaires
    vehicules = Vehicule.objects.all().order_by('marque', 'modele')
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
    clients = Client.objects.all().order_by('nom', 'prenom')
    clients_group = {}
    for client in clients:
        clients_group[client.id] = {
            'id': client.id,
            'nom': client.nom,
            'prenom': client.prenom,
            'email': client.email,
            'societe': client.societe,
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
    
    # Préparation des données pour les filtres
    all_clients = Client.objects.all().order_by('nom', 'prenom')
    all_vehicules = Vehicule.objects.all().order_by('marque', 'modele')
    priorites_choices = [(choix.name, choix.value) for choix in Priorite]
    
    return render(request, 'list-view.html', {
        'missions': missions,
        'vehicules': vehicules,
        'clients': clients,
        # Données pour les filtres
        'all_clients': all_clients,
        'all_vehicules': all_vehicules,
        'priorites_choices': priorites_choices,
        # Valeurs actuelles des filtres
        'filter_client': filter_client,
        'filter_vehicule': filter_vehicule,
        'filter_priorite': filter_priorite,
        'filter_date_debut': filter_date_debut,
        'filter_date_fin': filter_date_fin,
        })
    
@login_required
def show_mission_view(request, mission_id):
    """Affiche les détails d'une mission spécifique.

    Args:
        request (HttpRequest): La requête HTTP
        mission_id (int): L'ID de la mission à afficher

    Returns:
        HttpResponse: La réponse HTTP contenant le rendu du template avec les détails de la mission
    """
    mission = get_mission_by_id(mission_id)
    if not mission:
        logging.error(f"Mission with id {mission_id} does not exist.")
        return render_with_error_handling(request, 'error.html', {
            'error': f"Mission with id {mission_id} does not exist.",
            'template_error': True,
            'error_type': 'template_render_error'
        })

    client =  model_to_dict(mission.client)
    vehicule = model_to_dict(mission.vehicule)
    mission_intervention =  get_all_mission_intervention_by_id(mission_id)
    mission_intervention = [model_to_dict(intervention) for intervention in mission_intervention]
    mission = model_to_dict(mission)

    logging.info(f"Mission data retrieved for id {mission_id}: {mission}")
    return render(request, 'show_mission.html', {
        'mission': mission,
        'client': client,
        'vehicule': vehicule,
        'mission_intervention': mission_intervention
    })
    
@login_required
def list_interventions_view(request):
    """Affiche la liste des interventions.

    Args:
        request (HttpRequest): La requête HTTP

    Returns:
        HttpResponse: La réponse HTTP contenant le rendu du template avec la liste des interventions
    """
    interventions = get_all_interventions()
    return render(request, 'list_interventions.html', {
        'interventions': interventions
    })