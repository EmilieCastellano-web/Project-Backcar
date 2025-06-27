/**
 * Fonction de confirmation de suppression d'intervention
 *  Cette fonction affiche un message de confirmation détaillé avant de supprimer une intervention.
 *  Elle demande à l'utilisateur de taper "SUPPRIMER" pour confirmer la suppression.
 *   Si l'utilisateur confirme, une seconde confirmation est demandée avant de procéder à la suppression.
 *   Si l'utilisateur annule ou ne tape pas "SUPPRIMER", la suppression est
 *  annulée.
 * @param {*} interventionId 
 * @param {*} libelle 
 * @param {*} dureeIntervention 
 * @param {*} prixUnitaire 
 * @param {*} categorie 
 * @returns 
 */
function confirmDeleteIntervention(interventionId, libelle, dureeIntervention, prixUnitaire, categorie) {
    const confirmationMessage = `CONFIRMATION DE SUPPRESSION D'INTERVENTION

Êtes-vous absolument certain(e) de vouloir supprimer cette intervention ?

Détails de l'intervention :
• ID Intervention : ${interventionId}
• Libellé : ${libelle}
• Durée : ${dureeIntervention}h
• Prix unitaire : ${prixUnitaire}€
• Catégorie : ${categorie}

ATTENTION : Cette action est IRREVERSIBLE !

Cette intervention sera supprimée définitivement et ne pourra plus être utilisée dans les missions.

Tapez "SUPPRIMER" dans le champ ci-dessous pour confirmer :`;

    const userInput = prompt(confirmationMessage);
    
    if (userInput === null) {
        return false; // Utilisateur a annulé
    }
    
    if (userInput.toUpperCase() !== "SUPPRIMER") {
        alert("Suppression annulée.\n\nVous devez taper exactement 'SUPPRIMER' pour confirmer.");
        return false;
    }
    
    const secondConfirmation = confirm(`DERNIÈRE CONFIRMATION

Vous avez tapé "SUPPRIMER" correctement.

Cliquez sur OK pour supprimer DÉFINITIVEMENT l'intervention "${libelle}".

Cette action ne peut pas être annulée !`);
    
    if (!secondConfirmation) {
        return false;
    }
    
    return true;
}

// Fonction pour confirmer la suppression avec un formulaire simple
function confirmDeleteInterventionForm(libelle) {
    return confirm(`Êtes-vous sûr de vouloir supprimer l'intervention "${libelle}" ?`);
}

// Initialisation des événements de suppression
document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-intervention-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const interventionId = this.dataset.interventionId;
            const libelle = this.dataset.libelle;
            const duree = this.dataset.duree;
            const prix = this.dataset.prix;
            const categorie = this.dataset.categorie;
            
            if (confirmDeleteIntervention(interventionId, libelle, duree, prix, categorie)) {
                const form = this.closest('form');
                if (form) {
                    // Désactiver le bouton pendant la soumission pour éviter les clics multiples
                    this.disabled = true;
                    this.innerHTML = 'Suppression en cours...';
                    form.submit();
                } else {
                    console.warn('Formulaire non trouvé, utilisation du fallback URL - non sécurisé');
                    window.location.href = this.href;
                }
            }
        });
    });
    
    // Gestionnaire pour les boutons de suppression simples
    const simpleDeleteButtons = document.querySelectorAll('.simple-delete-intervention-btn');
    simpleDeleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const libelle = this.dataset.libelle;
            const interventionId = this.dataset.interventionId;
            
            if (!confirmDeleteInterventionForm(interventionId, libelle)) {
                e.preventDefault();
            }
        });
    });
});

// Fonction pour disable l'input de forfait si is_forfait est false
function toggleForfaitInput(isForfait) {
    const forfaitInput = document.getElementById('id_forfait');
    const prixInput = document.getElementById('id_prix_unitaire');
    if (forfaitInput) {
        if (isForfait) {
            forfaitInput.disabled = false;
            prixInput.disabled = true;
            prixInput.value = ''; // Réinitialiser la valeur si activé
        } else {
            forfaitInput.disabled = true;
            forfaitInput.value = ''; // Réinitialiser la valeur si désactivé
            prixInput.disabled = false; // Activer le champ prix unitaire
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Gestion des cases à cocher pour les interventions forfaitaires
    const forfaitCheckInput = document.getElementById('id_is_forfait');
    if (forfaitCheckInput) {
        forfaitCheckInput.addEventListener('change', function() {
            const isForfait = this.checked;
            toggleForfaitInput(isForfait);
        });

        // Initialisation de l'état de l'input forfait
        toggleForfaitInput(forfaitCheckInput.checked);
    }
});
