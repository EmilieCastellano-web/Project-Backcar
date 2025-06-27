from my_airtable_api.utils.extract_data import ValidationError, extract_data_client, extract_data_vehicule, extract_data_intervention, extract_data_mission, extract_data_mission_intervention
from my_airtable_api.utils.crud import create_taches, get_all_mission_intervention_by_id, create_client, create_vehicule, get_client_by_id, get_vehicule_by_id, get_mission_by_id, update_taches
from my_airtable_api.utils.error_manage import handle_template_errors, render_with_error_handling
from mission.models import Client, Vehicule, Intervention, Priorite, Taux
from mission.form import InterventionForm

import logging
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


@handle_template_errors()
@login_required
def get_mission_form_view(request):
    """Fonction pour afficher le formulaire de création d'une nouvelle mission.
    Args:
        request (HttpRequest): La requête HTTP pour afficher le formulaire.
    Returns:
        HttpResponse: La réponse HTTP contenant le rendu du template du formulaire de création de mission.
    """
    
    return render_with_error_handling(request, 'new_mission.html', {
        'clients': Client.objects.all(),
        'vehicules': Vehicule.objects.all(),
        'interventions': Intervention.objects.all(),
        'priorites': [(choix.name, choix.value) for choix in Priorite],
        'taux': [(choix.name, choix.value) for choix in Taux]
    })

def post_mission_form_view(request):
    """Fonction pour traiter les données du formulaire de création d'une nouvelle mission.

    Args:
        request (HttpRequest): La requête HTTP contenant les données du formulaire.

    Returns:
        HttpResponse: La réponse HTTP redirigeant vers la liste des missions ou affichant une erreur.
    """
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
            # logging.info(f"Client data extracted: {client_data}")
            if client_data.get('id'): 
                client = get_client_by_id(client_data['id'])  # objet existant
            else:
                client = create_client(client_data, erreurs)  # sinon on le crée

            # logging.info(f"Client data extracted: {client}")
            
            vehicule_data = extract_data_vehicule(request, client, erreurs)
            if vehicule_data.get('id'):
                vehicule = get_vehicule_by_id(vehicule_data['id'])
                if vehicule.client.id != client.id:
                    erreurs['vehicule']['client'] = "Le véhicule appartient à un autre client"
                    raise ValidationError("Erreur(s) dans le formulaire", details=erreurs)
            else:
                vehicule = create_vehicule(vehicule_data, client, erreurs)
            # logging.info(f"Vehicule data extracted: {vehicule}")
            
            interventions = extract_data_intervention(request, erreurs)
            # logging.info(f"Interventions data extracted: {interventions}")
            mission_data = extract_data_mission(request, vehicule, client, erreurs, mission_id=None)
            # logging.info(f"Mission data extracted: {mission_data}")
            mission_interventions = extract_data_mission_intervention(request, mission_data, interventions, erreurs)
            # logging.info(f"Mission Intervention data extracted: {mission_interventions}")
            # Récuperation des données 
            #  INFO:Client data extracted: Lilo Lila
            # INFO:Vehicule data extracted: Audi A5
            # INFO:Interventions data extracted: {'interventions': [<Intervention: Intervention ob ject (2)>, <Intervention: Intervention object (3)>]}
            # INFO:Mission data extracted: {'id': None, 'remarque': '', 'priorite': 'BASSE', 'vehicule': <Vehicule: Audi A5>, 'client': <Client: Lilo Lila>}
            # INFO:Mission Intervention data extracted: [{'mission': {'id': None, 'remarque': '', 'priorite': 'BASSE', 'vehicule': <Vehicule: Audi A5>, 'client': <Client: Lilo Lila>}, 
            # 'intervention': <Intervention: Intervention object (2)>, 'duree_supplementaire': 0.0, 'taux': 'T2', 'cout_total': 250.0},
            # {'mission': {'id': None, 'remarque': '', 'priorite': 'BASSE', 'vehicule': <Vehicule: Audi A5>, 'client': <Client: Lilo Lila>}, 
            # 'intervention': <Intervention: Intervention object (3)>, 'duree_supplementaire': 0.0, 'taux': 'T2', 'cout_total': 800.0}]                mission = create_taches(mission_interventions, client, vehicule)
            create_taches(mission_interventions, client, vehicule)
            messages.success(request, f'Mission créée avec succès pour le client {client.prenom} {client.nom}!')
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
            'taux': [(choix.name, choix.value) for choix in Taux] 
            })
    
    except Exception as e:
        logging.error(f"Error creating mission: {e}")
        # Variable pour gérer l'affichage du template d'erreur
        return render(request, 'error.html', {
            'error': str(e),
            'template_error': True,
            'error_type': 'template_render_error'
        })

@login_required
def get_update_mission_view(request, mission_id):
    """Fonction pour afficher le formulaire de mise à jour d'une mission existante.

    Args:
        request (HttpRequest): La requête HTTP pour afficher le formulaire de mise à jour.
        mission_id (int): L'identifiant de la mission à mettre à jour.

    Returns:
        HttpResponse: La réponse HTTP contenant le rendu du template de mise à jour de mission.
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
            'error':  f"Mission with id {mission_id} does not exist.",
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
            'cout_total': mi.cout_total        } for mi in mission_intervention_list
    ]
    
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

@login_required
def post_update_mission_view(request, mission_id):
    """Traite les données du formulaire de mise à jour d'une mission existante.

    Args:
        request (HttpRequest): La requête HTTP contenant les données du formulaire.
        mission_id (int): L'identifiant de la mission à mettre à jour.
    Returns:
        HttpResponse: La réponse HTTP redirigeant vers la liste des missions ou affichant une erreur.
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
        update_taches(data, erreurs)

        messages.success(request, f'Mission mise à jour avec succès!')
        return redirect('list_view')
    #TODO : quand update mission sans intervention enregistre n bdd sans intervention dans mission_intervention;
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
        
@login_required
def delete_mission_view(request, mission_id):
    """Vue pour supprimer une mission avec ses relations.

    Args:
        request (HttpRequest): La requête HTTP
        mission_id (int): L'ID de la mission à supprimer

    Returns:
        HttpResponse: Redirection vers la liste des missions ou rendu d'erreur
    """
    if request.method != 'POST':
        # Seules les requêtes POST sont autorisées pour la suppression
        return redirect('list_view')
    
    # Debug pour vérifier les données de la requête
    logging.info(f"Requête de suppression pour mission {mission_id}")
    
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

@login_required
def create_intervention_view(request):
    """Vue pour créer une nouvelle intervention.

    Args:
        request (HttpRequest): La requête HTTP contenant les données du formulaire.

    Returns:
        HttpResponse: La réponse HTTP contenant le rendu du template du formulaire d'intervention.
    """
    if request.method == 'POST':
        form = InterventionForm(request.POST)
        if form.is_valid():
            intervention = form.save()
            messages.success(request, f'Intervention "{intervention.libelle}" créée avec succès!')
            return redirect('list_interventions_view')
    else:
        form = InterventionForm()
    
    return render(request, 'intervention_form.html', {
        'form': form,
        'title': 'Créer une intervention',
        'action': 'Créer'
    })

@login_required
def update_intervention_view(request, intervention_id):
    """Vue pour modifier une intervention existante.

    Args:
        request (HttpRequest): La requête HTTP contenant les données du formulaire.
        intervention_id (int): L'ID de l'intervention à modifier.

    Returns:
        HttpResponse: La réponse HTTP contenant le rendu du template du formulaire de modification de l'intervention.
    """
    intervention = get_object_or_404(Intervention, id=intervention_id)
    
    if request.method == 'POST':
        form = InterventionForm(request.POST, instance=intervention)
        if form.is_valid():
            intervention = form.save()
            messages.success(request, f'Intervention "{intervention.libelle}" modifiée avec succès!')
            return redirect('list_interventions_view')
    else:
        form = InterventionForm(instance=intervention)
    
    return render(request, 'intervention_form.html', {
        'form': form,
        'title': 'Modifier une intervention',
        'action': 'Modifier',
        'intervention': intervention
    })

@login_required
def delete_intervention_view(request, intervention_id):
    """Vue pour supprimer une intervention avec vérifications sécurisées.

    Args:
        request (HttpRequest): La requête HTTP
        intervention_id (int): L'ID de l'intervention à supprimer

    Returns:
        HttpResponse: Redirection vers la liste des interventions ou rendu d'erreur
    """
    # Sécurité : seules les requêtes POST sont autorisées
    if request.method != 'POST':
        logging.warning(f"Tentative de suppression d'intervention {intervention_id} avec méthode {request.method} par utilisateur {request.user.username}")
        messages.error(request, "Méthode non autorisée pour la suppression.")
        return redirect('list_interventions_view')
    
    try:
        # Récupération sécurisée de l'intervention
        intervention = get_object_or_404(Intervention, id=intervention_id)
        intervention_name = intervention.libelle
        
        # Vérification des relations - est-ce que l'intervention est utilisée dans des missions ?
        missions_liees = intervention.missions.all()
        if missions_liees.exists():
            nb_missions = missions_liees.count()
            missions_ids = list(missions_liees.values_list('id', flat=True))
            
            logging.warning(f"Tentative de suppression d'intervention {intervention_id} ({intervention_name}) "
                          f"liée à {nb_missions} mission(s) (IDs: {missions_ids}) par utilisateur {request.user.username}")
            
            messages.error(request, 
                f'Impossible de supprimer l\'intervention "{intervention_name}". '
                f'Elle est utilisée dans {nb_missions} mission(s). '
                f'Veuillez d\'abord supprimer ces missions ou retirer l\'intervention de celles-ci.')
            return redirect('list_interventions_view')
        
        # Suppression sécurisée avec transaction atomique
        with transaction.atomic():
            intervention.delete()
            
            # Logging de sécurité pour audit
            logging.info(f"Intervention {intervention_id} ({intervention_name}) supprimée avec succès "
                        f"par utilisateur {request.user.username} depuis IP {request.META.get('REMOTE_ADDR', 'inconnue')}")
            
            messages.success(request, f'Intervention "{intervention_name}" supprimée avec succès!')
            
        return redirect('list_interventions_view')
        
    except Exception as e:
        # Logging d'erreur pour audit de sécurité
        logging.error(f"Erreur lors de la suppression de l'intervention {intervention_id} "
                     f"par utilisateur {request.user.username}: {str(e)}")
        
        messages.error(request, 
            'Une erreur est survenue lors de la suppression. '
            'Veuillez réessayer ou contacter l\'administrateur.')
        return redirect('list_interventions_view')