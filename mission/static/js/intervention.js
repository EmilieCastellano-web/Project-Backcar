// Fonction de confirmation de suppression d'intervention
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
    
    // Double confirmation
    const secondConfirmation = confirm(`DERNIÈRE CONFIRMATION

Vous avez tapé "SUPPRIMER" correctement.

Cliquez sur OK pour supprimer DÉFINITIVEMENT l'intervention "${libelle}".

Cette action ne peut pas être annulée !`);
    
    if (!secondConfirmation) {
        return false;
    }
    
    // Afficher un message de chargement après validation
    setTimeout(() => {
        const deleteButton = document.querySelector('[type="submit"][style*="background-color: #ff4444"], .btn-danger, .delete-btn');
        if (deleteButton) {
            deleteButton.innerHTML = "Suppression en cours...";
            deleteButton.disabled = true;
        }
    }, 100);
    
    return true;
}

// Fonction pour confirmer la suppression avec un formulaire simple (alternative)
function confirmDeleteInterventionForm(interventionId, libelle) {
    return confirm(`Êtes-vous sûr de vouloir supprimer l'intervention "${libelle}" ?`);
}

// Initialisation des événements de suppression
document.addEventListener('DOMContentLoaded', function() {
    // Gestionnaire pour les boutons de suppression avec confirmation complète
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
                // Soumettre le formulaire de suppression (méthode POST sécurisée)
                const form = this.closest('form');
                if (form) {
                    // Désactiver le bouton pendant la soumission pour éviter les clics multiples
                    this.disabled = true;
                    this.innerHTML = 'Suppression en cours...';
                    form.submit();
                } else {
                    // Fallback pour les anciens liens (ne devrait plus arriver)
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
