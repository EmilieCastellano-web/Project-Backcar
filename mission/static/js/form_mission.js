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
 * 
 * Ce mécanisme permet de préserver les données d'intervention lors des rechargements de page
 * ou des soumissions de formulaire incorrectes.
 */
document.addEventListener('DOMContentLoaded', function() {
    const isFormPage = document.getElementById('new_mission_form') != null;
    const updateFormPage = document.getElementById('update_mission_form') != null;
    if (updateFormPage) {
        initInterventionForm();
        manageInterventionUpdateForm();

    }
    if (isFormPage) {
        const wasFormSubmitted = sessionStorage.getItem('form_submitted') === 'true';
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

/*
* Fonction pour initialiser le formulaire d'intervention.
* Elle gère la sélection d'interventions, l'affichage des interventions sélectionnées,
* et la sauvegarde de l'état dans un input caché.
* Elle permet également de supprimer des interventions sélectionnées.
*/
function initInterventionForm() {
    const select = document.getElementById('intervention-select');
    const list = document.getElementById('intervention-list');
    const hiddenInput = document.getElementById('interventions-hidden');

    let selectedIds = [];

    select.addEventListener('change', () => {
        const val = select.value;
        const text = select.options[select.selectedIndex].text;

        if (val && !selectedIds.includes(val)) {
            selectedIds.push(val);

            // Crée un élément <li> affiché
            const li = document.createElement('li');
            li.textContent = text;

            // Ajouter un bouton pour supprimer
            const btn = document.createElement('button');
            btn.textContent = '×';
            btn.style.marginLeft = '10px';
            btn.type = 'button';
            btn.onclick = () => {
            list.removeChild(li);
            selectedIds = selectedIds.filter(id => id !== val);
            hiddenInput.value = selectedIds.join(',');
            };

            li.appendChild(btn);
            list.appendChild(li);

            // Met à jour l'input caché
            hiddenInput.value = selectedIds.join(',');
            savedInterventionsToSession(hiddenInput);
            
        }
        // Remet le select à vide
        select.value = "";
        });
}

/** * Fonction pour sauvegarder les interventions sélectionnées dans le stockage de session.
 * 
 * @param {HTMLInputElement} hiddenInput - L'input caché contenant les IDs des interventions sélectionnées.
 */
function savedInterventionsToSession(hiddenInput) {
    sessionStorage.setItem('interventions', hiddenInput.value);
}

function manageInterventionUpdateForm() {
    const list = document.getElementById('intervention_actuelle');
    const hiddenInput = document.getElementById('interventions-actuelle-hidden');
    list.querySelectorAll('li').forEach(li => {
        const id = li.querySelector('.remove-intervention').getAttribute('data-id');
        // Ajouter l'ID de l'intervention à l'input caché
        if (hiddenInput.value) {
            hiddenInput.value += ',' + id;
        } else {
            hiddenInput.value = id;
        }
    });


    // Ajouter un écouteur d'événement pour les boutons de suppression
    list.addEventListener('click', function(event) {
        if (event.target.classList.contains('remove-intervention')) {
            const li = event.target.parentElement;
            const id = event.target.getAttribute('data-id');

            // Supprimer l'élément <li>
            list.removeChild(li);

            // Mettre à jour l'input caché
            let currentInterventions = hiddenInput.value.split(',').filter(i => i !== id);
            hiddenInput.value = currentInterventions.join(',');
        }
    });
}

