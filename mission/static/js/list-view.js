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