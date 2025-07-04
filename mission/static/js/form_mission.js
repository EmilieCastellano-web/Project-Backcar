document.addEventListener('DOMContentLoaded', () => {
    const isCreatePage = document.getElementById('new_mission_form');
    const isUpdatePage = document.getElementById('update_mission_form');
    const isFormPage = isCreatePage || isUpdatePage;
    // Vérification de la présence de la page de formulaire
    if (!isFormPage) {
        sessionStorage.removeItem('interventions');
        sessionStorage.removeItem('form_submitted');
        return;
    }

    const hiddenInput = document.getElementById('interventions-hidden');
    const select = document.getElementById('intervention-select');
    const list = document.getElementById('interventions-list');

    const hiddenInputActuelles = document.getElementById('interventions-actuelles-hidden');
    const interventionsActuellesList = document.getElementById('interventions-actuelles-list');
    let selectedIds = [];    // Récupère les interventions déjà en base (update)
    let selectedIdsActuelles = hiddenInputActuelles
        ? hiddenInputActuelles.value.split(',').filter(id => id)
        : [];
    selectedIds.push(...selectedIdsActuelles);
    document.querySelectorAll('.remove-intervention').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.getAttribute('data-id');

            selectedIds = selectedIds.filter(i => i !== id);
            selectedIdsActuelles = selectedIdsActuelles.filter(i => i !== id);

            // Mise à jour des champs cachés avec TOUTES les interventions
            hiddenInput.value = selectedIds.join(',');
            hiddenInputActuelles.value = selectedIdsActuelles.join(',');
            const li = button.parentElement;
            interventionsActuellesList.removeChild(li);
        });
    });    // Restauration depuis sessionStorage si le formulaire a échoué
    if (sessionStorage.getItem('form_submitted') === 'true') {
        const saved = sessionStorage.getItem('interventions');
        if (saved) {
            saved.split(',').forEach(id => {
                if (!selectedIds.includes(id)) {
                    selectedIds.push(id);
                    const text = select.querySelector(`option[value="${id}"]`)?.textContent;
                    if (text) addInterventionToList(id, text);
                }
            });
            hiddenInput.value = selectedIds.join(',');
        }
        sessionStorage.removeItem('form_submitted');
    }    // Sélection d'une intervention
    select.addEventListener('change', () => {
        const val = select.value;
        const text = select.options[select.selectedIndex]?.text;
        if (val && !selectedIds.includes(val)) {
            selectedIds.push(val);
            addInterventionToList(val, text);
            hiddenInput.value = selectedIds.join(',');
            sessionStorage.setItem('interventions', hiddenInput.value);
        }
        select.value = '';
    });
    // Sauvegarde lors de la soumission
    if (isCreatePage || isUpdatePage) {
        const form = isCreatePage || isUpdatePage;
        form.addEventListener('submit', () => {
            hiddenInput.value = selectedIds.join(',');
            sessionStorage.setItem('interventions', hiddenInput.value);
            sessionStorage.setItem('form_submitted', 'true');
        });
    };
    
    // Fonction utilitaire d’ajout d’un <li>
    function addInterventionToList(id, text) {
        const li = document.createElement('li');
        li.textContent = text;
        li.style.padding = '5px';
        li.style.margin = '2px 0';
        li.style.backgroundColor = '#f0f0f0';
        li.style.borderRadius = '3px';

        const btn = document.createElement('button');
        btn.textContent = '×';
        btn.type = 'button';
        btn.style.marginLeft = '10px';
        btn.style.backgroundColor = '#ff4444';
        btn.style.color = 'white';
        btn.style.border = 'none';
        btn.style.borderRadius = '3px';
        btn.style.cursor = 'pointer';        btn.addEventListener('click', () => {
            selectedIds = selectedIds.filter(i => i !== id);
            li.remove();
            hiddenInput.value = selectedIds.join(',');
            sessionStorage.setItem('interventions', hiddenInput.value);
        });

        li.appendChild(btn);
        list.appendChild(li);
    }
});

// Fonction de confirmation de suppression de mission
function confirmDelete(missionId, clientName, vehiculeName, nbInterventions) {
    const confirmationMessage = `CONFIRMATION DE SUPPRESSION

Êtes-vous absolument certain(e) de vouloir supprimer cette mission ?

Détails de la mission :
• ID Mission : ${missionId}
• Client : ${clientName}
• Véhicule : ${vehiculeName}
• Interventions : ${nbInterventions}

ATTENTION : Cette action est IRREVERSIBLE !

Toutes les données associées seront perdues définitivement.

Tapez "SUPPRIMER" dans le champ ci-dessous pour confirmer :`;

    const userInput = prompt(confirmationMessage);
    
    if (userInput === null) {
        return false; // Utilisateur a annulé
    }
    
    if (userInput.toUpperCase() !== "SUPPRIMER") {
        alert("Suppression annulée.\n\nVous devez taper exactement 'SUPPRIMER' pour confirmer.");
        return false;
    }
    
    // Double confirmation
    const secondConfirmation = confirm(`DERNIÈRE CONFIRMATION

Vous avez tapé "SUPPRIMER" correctement.

Cliquez sur OK pour supprimer DÉFINITIVEMENT la mission ${missionId}.

Cette action ne peut pas être annulée !`);
    
    if (!secondConfirmation) {
        return false;
    }
    
    // Afficher un message de chargement après validation
    setTimeout(() => {
        const deleteButton = document.querySelector('[type="submit"][style*="background-color: #ff4444"]');
        if (deleteButton) {
            deleteButton.innerHTML = "Suppression en cours...";
            deleteButton.disabled = true;
        }
    }, 100);
    
    return true;
}
