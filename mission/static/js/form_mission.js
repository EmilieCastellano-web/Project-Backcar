/**
 * Gestionnaire d'événement qui s'exécute lorsque le DOM est entièrement chargé.
 * 
 * Cette fonction:
 * 1. Vérifie si nous sommes sur une page contenant le formulaire de mission
 * 2. Si oui:
 *    - Vérifie si le formulaire a été précédemment soumis via le stockage de session
 *    - Initialise le formulaire d'intervention
 *    - Réinitialise le flag de soumission du formulaire
 *    - Restaure les interventions précédemment saisies si le formulaire a été soumis
 *    - Configure un écouteur d'événement sur la soumission du formulaire pour sauvegarder l'état
 * 3. Si non:
 *    - Nettoie le stockage de session en supprimant les données d'intervention et le flag de soumission
 * 4. Si nous sommes sur une page de mise à jour de mission, initialise le formulaire d'intervention.
 * Cette approche permet de gérer les interventions de manière dynamique et de conserver l'état du formulaire.
 *
 * Ce mécanisme permet de préserver les données d'intervention lors des rechargements de page
 * ou des soumissions de formulaire incorrectes.
 */
document.addEventListener('DOMContentLoaded', function() {
    const isFormPage = document.getElementById('new_mission_form') != null;
    const updateFormPage = document.getElementById('update_mission_form') != null;
    
    if (updateFormPage) {
        initInterventionForm();
    }
    
    if (isFormPage) {
        const wasFormSubmitted = getFromSessionStorage('form_submitted') === 'true';
        initInterventionForm();
        sessionStorage.removeItem('form_submitted');
        
        if (wasFormSubmitted) {
            restoreFormInterventions();
        } else {
            sessionStorage.removeItem('interventions');
        }
        
        // Ajouter un gestionnaire d'événements pour la soumission du formulaire
        document.getElementById('new_mission_form').addEventListener('submit', function() {
            sessionStorage.setItem('form_submitted', 'true');
        });
    } else {
        sessionStorage.removeItem('interventions');
        sessionStorage.removeItem('form_submitted');
    }
});

/** * Fonction pour récupérer une valeur depuis le stockage de session.
 * @param {string} key - La clé de l'élément à récupérer.
 * @returns {string|null} - La valeur associée à la clé, ou null si l'élément n'existe pas ou si une erreur se produit.
 */
function getFromSessionStorage(key) {
    try {
        return sessionStorage.getItem(key);
    } catch (e) {
        console.warn('SessionStorage inaccessible', e);
        return null;
    }
}


/*
* Fonction pour initialiser le formulaire d'intervention.
* Elle gère la sélection d'interventions, l'affichage des interventions sélectionnées,
* et la sauvegarde de l'état dans un input caché.
* Elle permet également de supprimer des interventions sélectionnées.
*/
function initInterventionForm() {
    const select = document.getElementById('intervention-select');
    const list = document.getElementById('interventions-list');
    let selectedIds = [];
    const hiddenInput = document.getElementById('interventions-hidden');
    const interventionsActuellesList = document.getElementById('interventions-actuelles-list');
    let selectedIdsActuelles = [];
    const hiddenInputActuelles = document.getElementById('interventions-actuelles-hidden');

    if (hiddenInputActuelles) {
        selectedIdsActuelles = hiddenInputActuelles.value.split(',').filter(id => id);
        console.log('Liste des IDs actuels :', hiddenInputActuelles.value);
    }
    
    selectedIds.push(...selectedIdsActuelles);

    document.querySelectorAll('.remove-intervention').forEach(button => {
        button.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            // Supprime l'ID de la liste des interventions sélectionnées
            selectedIds = selectedIds.filter(selectedId => selectedId !== id);
            selectedIdsActuelles = selectedIdsActuelles.filter(actId => actId !== id);
            // Met à jour les inputs cachés
            hiddenInput.value = selectedIds.filter(id => !selectedIdsActuelles.includes(id)).join(',');
            hiddenInputActuelles.value = selectedIdsActuelles.join(',');

            const li = this.parentElement;
            interventionsActuellesList.removeChild(li);
            // console.log('Interventions sélectionnées mises à jour :', hiddenInput.value);
        });
    });

    // Liste déroulante pour sélectionner une intervention
    select.addEventListener('change', () => {
        const val = select.value;
        const text = select.options[select.selectedIndex].text;

        if (val && !selectedIds.includes(val) && !selectedIdsActuelles.includes(val)) {
            selectedIds.push(val);

            const li = document.createElement('li');
            li.textContent = text;
            li.style.padding = '5px';
            li.style.margin = '2px 0';
            li.style.backgroundColor = '#f0f0f0';
            li.style.borderRadius = '3px';

            // Ajouter un bouton pour supprimer
            const btn = document.createElement('button');
            btn.textContent = '×';
            btn.style.marginLeft = '10px';
            btn.style.backgroundColor = '#ff4444';
            btn.style.color = 'white';
            btn.style.border = 'none';
            btn.style.borderRadius = '3px';
            btn.style.cursor = 'pointer';
            btn.type = 'button';
            btn.onclick = () => {
                list.removeChild(li);
                hiddenInput.value = selectedIds.filter(id => !selectedIdsActuelles.includes(id)).join(',');
                saveInterventionsToSession(hiddenInput);
            };

            li.appendChild(btn); 
            list.appendChild(li);

            hiddenInput.value = selectedIds.filter(id => !selectedIdsActuelles.includes(id)).join(',');
            saveInterventionsToSession(hiddenInput);
            // console.log('Interventions sélectionnées mises à jour (après ajout) :', hiddenInput.value);
        }
        // Remet le select à vide
        select.value = "";
    });


    
}

/**
 * Fonction pour sauvegarder les interventions sélectionnées dans le stockage de session.
 * 
 * @param {HTMLInputElement} hiddenInput - L'input caché contenant les IDs des interventions sélectionnées.
 */
function saveInterventionsToSession(hiddenInput) {
    sessionStorage.setItem('interventions', hiddenInput.value);
}


/**
 * Fonction pour restaurer les interventions depuis le stockage de session
 */
function restoreFormInterventions() {
    const savedInterventions = sessionStorage.getItem('interventions');
    if (savedInterventions) {
        const hiddenInput = document.getElementById('interventions-hidden');
        if (hiddenInput) {
            hiddenInput.value = savedInterventions;
            console.log('Interventions restaurées:', savedInterventions);
        }
    }
}