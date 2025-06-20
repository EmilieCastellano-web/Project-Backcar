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
    console.log('Is form page:', isFormPage);
    console.log('JE suis dans le fichier form_mission.js');
    
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
            // Indiquer qu'une soumission est en cours
            sessionStorage.setItem('form_submitted', 'true');
            
        });
    } else {
        sessionStorage.removeItem('interventions');
        sessionStorage.removeItem('form_submitted');
    }
});


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

function savedInterventionsToSession(hiddenInput) {
    console.log('Saving interventions to session storage:', hiddenInput.value);
    sessionStorage.setItem('interventions', hiddenInput.value);
    console.log('Interventions saved:', sessionStorage.getItem('interventions'));
}

function restoreFormInterventions() {
    const savedInterventions = sessionStorage.getItem('interventions');
    const hiddenInput = document.getElementById('interventions-hidden');
    const select = document.getElementById('intervention-select');
    const list = document.getElementById('intervention-list');
    let selectedIds = [];

    if (savedInterventions) {
        selectedIds = savedInterventions.split(',').filter(id => id);
        hiddenInput.value = selectedIds.join(',');

        // Affiche les interventions sauvegardées
        selectedIds.forEach(id => {
            const option = select.querySelector(`option[value="${id}"]`);
            if (option) {
                const li = document.createElement('li');
                li.textContent = option.text;

                const btn = document.createElement('button');
                btn.textContent = '×';
                btn.style.marginLeft = '10px';
                btn.type = 'button';
                btn.onclick = () => {
                    list.removeChild(li);
                    selectedIds = selectedIds.filter(savedId => savedId !== id);
                    hiddenInput.value = selectedIds.join(',');
                    savedInterventionsToSession(hiddenInput);
                };

                li.appendChild(btn);
                list.appendChild(li);
            }
        });
    }
}

