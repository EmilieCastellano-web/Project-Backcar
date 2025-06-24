from django.shortcuts import render
from .models import Client, Vehicule, Intervention, MissionIntervention, Priorite, Taux
from django.shortcuts import render, redirect
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')
from django.db import transaction
from django.db.models import Q
from datetime import datetime
from my_airtable_api.utils.error_manage import handle_template_errors, render_with_error_handling

from my_airtable_api.utils.crud import create_taches, create_client, create_vehicule, get_client_by_id, get_vehicule_by_id, get_all_mission_intervention_by_id, get_mission_by_id, update_taches
from my_airtable_api.utils.extract_data import ValidationError, extract_data_client, extract_data_vehicule, extract_data_intervention, extract_data_mission, extract_data_mission_intervention


def list_view(request):
    """"Affiche la liste des missions, véhicules et clients avec filtrage.
    Cette vue récupère les données des missions, véhicules et clients depuis la base de données
    et les organise pour les afficher dans un template. Supporte le filtrage par client, véhicule, priorité et date.
    Returns:
        HttpResponse: La réponse HTTP contenant le rendu du template avec les données des missions, véhicules et clients.
    """
    # Récupération des paramètres de filtrage
    filter_client = request.GET.get('client', '')
    filter_vehicule = request.GET.get('vehicule', '')
    filter_priorite = request.GET.get('priorite', '')
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
    
    missions_interventions = missions_interventions_query.all()
    
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
            'vehicules': []        }
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
    
@handle_template_errors()
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
    if request.method == 'POST':
        erreurs = {
            'client': {},
            'vehicule': {},
            'mission': {}, 
            'intervention': {}
        }
        try:
            with transaction.atomic():
                # 1. Extraction des données
                client_data = extract_data_client(request, erreurs)
                if client_data.get('id'): 
                    client = get_client_by_id(client_data['id'])  # objet existant
                else:
                    client = create_client(client_data, erreurs)  # sinon on le crée

                logging.info(f"Client data extracted: {client}")
                
                vehicule_data = extract_data_vehicule(request, client, erreurs)
                if vehicule_data.get('id'):
                    vehicule = get_vehicule_by_id(vehicule_data['id'])
                    if vehicule.client.id != client.id:
                        erreurs['vehicule']['client'] = "Le véhicule appartient à un autre client"
                        raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
                else:
                    vehicule = create_vehicule(vehicule_data, client, erreurs)
                logging.info(f"Vehicule data extracted: {vehicule}")
                
                interventions = extract_data_intervention(request, erreurs)
                logging.info(f"Interventions data extracted: {interventions}")
                mission_data = extract_data_mission(request, vehicule, client, erreurs, mission_id=None)
                logging.info(f"Mission data extracted: {mission_data}")
                mission_interventions = extract_data_mission_intervention(request, mission_data, interventions, erreurs)
                logging.info(f"Mission Intervention data extracted: {mission_interventions}")
                # Récuperation des données 
                #  INFO:Client data extracted: Lilo Lila
                # INFO:Vehicule data extracted: Audi A5
                # INFO:Interventions data extracted: {'interventions': [<Intervention: Intervention object (2)>, <Intervention: Intervention object (3)>]}
                # INFO:Mission data extracted: {'id': None, 'remarque': '', 'priorite': 'BASSE', 'vehicule': <Vehicule: Audi A5>, 'client': <Client: Lilo Lila>}
                # INFO:Mission Intervention data extracted: [{'mission': {'id': None, 'remarque': '', 'priorite': 'BASSE', 'vehicule': <Vehicule: Audi A5>, 'client': <Client: Lilo Lila>}, 
                # 'intervention': <Intervention: Intervention object (2)>, 'duree_supplementaire': 0.0, 'taux': 'T2', 'cout_total': 250.0},
                # {'mission': {'id': None, 'remarque': '', 'priorite': 'BASSE', 'vehicule': <Vehicule: Audi A5>, 'client': <Client: Lilo Lila>}, 
                # 'intervention': <Intervention: Intervention object (3)>, 'duree_supplementaire': 0.0, 'taux': 'T2', 'cout_total': 800.0}]
                mission = create_taches(mission_interventions, client, vehicule)

                logging.info(f"Mission created: {mission}")
                return redirect('list_view')
        
        except ValidationError as ve:
            logging.error(f"Validation error: {ve.message}")
            return render_with_error_handling(request, 'new_mission.html', {
                'erreurs': erreurs,
                'valeurs': request.POST.dict(),
                'clients': Client.objects.all(),
                'vehicules': Vehicule.objects.all(),
                'interventions': Intervention.objects.all(),
                'priorites': [(choix.name, choix.value) for choix in Priorite],
                'taux': [(choix.name, choix.value) for choix in Taux]                })
        
        except Exception as e:
            logging.error(f"Error creating mission: {e}")
            # Variable pour gérer l'affichage du template d'erreur
            return render(request, 'error.html', {
                'error': str(e),
                'template_error': True,
                'error_type': 'template_render_error'
            })
    else:
        return render_with_error_handling(request, 'new_mission.html', {
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
        return render_with_error_handling(request, 'error.html', {
            'error': str(e),
            'template_error': True,
            'error_type': 'template_render_error'
        })

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
                return render_with_error_handling(request, 'update_mission.html', {
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
                return render(request, 'error.html', {
                    'error': str(e),
                    'template_error': True,
                    'error_type': 'template_render_error'
                })

    # GET : affichage du formulaire
    return render_with_error_handling(request, 'update_mission.html', {
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

def delete_mission_view(request, mission_id):
    """Vue pour supprimer une mission avec ses relations.
    
    Args:
        request: La requête HTTP
        mission_id: L'ID de la mission à supprimer
        
    Returns:
        HttpResponse: Redirection vers la liste des missions ou rendu d'erreur
    """
    if request.method != 'POST':
        # Seules les requêtes POST sont autorisées pour la suppression
        return redirect('list_view')
    
    # Debug pour vérifier les données de la requête
    logging.info(f"Requête de suppression pour mission {mission_id}")
    logging.info(f"CSRF Token présent: {'csrfmiddlewaretoken' in request.POST}")
    logging.info(f"Headers: {dict(request.headers)}")
    
    try:
        from my_airtable_api.utils.crud import delete_mission
        from django.contrib import messages
        
        result = delete_mission(mission_id)
        
        if result['success']:
            logging.info(f"Mission {mission_id} supprimée avec succès par l'utilisateur")
            # Créer un message de succès pour l'afficher dans la liste
            messages.success(request, f"Mission {mission_id} supprimée avec succès. "
                           f"{result['nb_interventions_supprimees']} intervention(s) associée(s) supprimée(s).")
            
            return redirect('list_view')
        else:
            logging.error(f"Échec de la suppression de la mission {mission_id}: {result.get('message', 'Erreur inconnue')}")
            return render_with_error_handling(request, 'error.html', {
                'error': f"Impossible de supprimer la mission: {result.get('message', 'Erreur inconnue')}"
            })
            
    except ValidationError as ve:
        logging.error(f"Erreur de validation lors de la suppression de la mission {mission_id}: {ve}")
        return render_with_error_handling(request, 'error.html', {
            'error': str(ve),
            'template_error': True,
            'error_type': 'template_render_error'
        })
        
    except Exception as e:
        logging.error(f"Erreur inattendue lors de la suppression de la mission {mission_id}: {e}")
        return render_with_error_handling(request, 'error.html', {
            'error': str(e),
            'template_error': True,
            'error_type': 'template_render_error'
        })