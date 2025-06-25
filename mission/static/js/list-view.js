/**
 * Fonction permettant de changer la liste affichée
 * en fonction de la sélection de l'utilisateur.    
 *  @param {Event} event - L'événement de changement de sélection.
 *  @returns {void}
 */
const select  = document.getElementById("choix-list");
let divList = [document.getElementById("missions-list"), document.getElementById("vehicule-list"), document.getElementById("clients-list")];
select.addEventListener("change", function(event) {
    const selectedValue = event.target.value;

    divList.forEach(div => {
        div.style.display = "none";
    });

    switch (selectedValue) {
        case "missions":
            divList[0].style.display = "block";
            break;
        case "vehicules":
            divList[1].style.display = "block";
            break;
        case "clients":
            divList[2].style.display = "block";
            break;
    }
});


// Script pour gérer l'affichage du bouton de réinitialisation des filtres
document.addEventListener('DOMContentLoaded', () => {
    // Fonction pour vérifier si des filtres sont appliqués
    function checkFiltersAndToggleResetButton() {
        // Récupérer tous les éléments de filtrage
        const clientFilter = document.getElementById('client-filtrage');
        const vehiculeFilter = document.getElementById('vehicule-filtrage');
        const prioriteFilter = document.getElementById('priorite-filtrage');
        const dateDebutFilter = document.getElementById('date_debut');
        const dateFinFilter = document.getElementById('date_fin');
        const resetButton = document.getElementById('reset-button-filter'); // Bouton "Réinitialiser"

        // Vérifier si au moins un filtre a une valeur
        let hasActiveFilters = false;
        
        if (clientFilter && clientFilter.value.trim() !== '') {
            hasActiveFilters = true;
        }
        
        if (vehiculeFilter && vehiculeFilter.value.trim() !== '') {
            hasActiveFilters = true;
        }
        
        if (prioriteFilter && prioriteFilter.value !== '') {
            hasActiveFilters = true;
        }
        
        if (dateDebutFilter && dateDebutFilter.value !== '') {
            hasActiveFilters = true;
        }
        
        if (dateFinFilter && dateFinFilter.value !== '') {
            hasActiveFilters = true;
        }
        
        // Afficher ou masquer le bouton de réinitialisation
        if (resetButton) {
            if (hasActiveFilters) {
                resetButton.style.display = 'inline-block';
                resetButton.style.visibility = 'visible';
                resetButton.style.opacity = '1';
            } else {
                resetButton.style.display = 'none';
                resetButton.style.visibility = 'hidden';
                resetButton.style.opacity = '0';
            }
        }
        
        console.log('Filtres actifs détectés:', hasActiveFilters);
    }
    
    // Vérifier au chargement de la page
    checkFiltersAndToggleResetButton();
    
    // Ajouter des événements sur tous les champs de filtrage pour vérifier en temps réel
    const filterInputs = [
        'client-filtrage',
        'vehicule-filtrage', 
        'priorite-filtrage',
        'date_debut',
        'date_fin'
    ];
    
    filterInputs.forEach(filterId => {
        const filterElement = document.getElementById(filterId);
        if (filterElement) {
            // Événements pour les inputs texte et date
            if (filterElement.type === 'text' || filterElement.type === 'date') {
                filterElement.addEventListener('input', checkFiltersAndToggleResetButton);
                filterElement.addEventListener('keyup', checkFiltersAndToggleResetButton);
                filterElement.addEventListener('paste', () => {
                    setTimeout(checkFiltersAndToggleResetButton, 100); // Délai pour laisser le temps au paste
                });
            }
            // Événement pour les selects
            else if (filterElement.tagName === 'SELECT') {
                filterElement.addEventListener('change', checkFiltersAndToggleResetButton);
            }
        }
    });
    
    // Optionnel : Ajouter des styles CSS pour une transition fluide du bouton
    const resetButton = document.getElementById('reset-button-filter');
    if (resetButton) {
        resetButton.style.transition = 'opacity 0.3s ease, visibility 0.3s ease';
    }
});
