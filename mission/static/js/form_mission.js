document.addEventListener('DOMContentLoaded', () => {
    const isCreatePage = document.getElementById('new_mission_form');
    const isUpdatePage = document.getElementById('update_mission_form');
    const isFormPage = isCreatePage || isUpdatePage;

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
    let selectedIds = [];

    // Récupère les interventions déjà en base (update)
    let selectedIdsActuelles = hiddenInputActuelles
        ? hiddenInputActuelles.value.split(',').filter(id => id)
        : [];
    selectedIds.push(...selectedIdsActuelles);

    // Suppression des interventions actuelles (update)
    document.querySelectorAll('.remove-intervention').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.getAttribute('data-id');
            selectedIds = selectedIds.filter(i => i !== id);
            selectedIdsActuelles = selectedIdsActuelles.filter(i => i !== id);

            hiddenInput.value = selectedIds.filter(i => !selectedIdsActuelles.includes(i)).join(',');
            hiddenInputActuelles.value = selectedIdsActuelles.join(',');

            const li = button.parentElement;
            interventionsActuellesList.removeChild(li);
        });
    });

    // Restauration depuis sessionStorage si le formulaire a échoué
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
            hiddenInput.value = selectedIds.filter(i => !selectedIdsActuelles.includes(i)).join(',');
        }
        sessionStorage.removeItem('form_submitted');
    }

    // Sélection d'une intervention
    select.addEventListener('change', () => {
        const val = select.value;
        const text = select.options[select.selectedIndex]?.text;
        if (val && !selectedIds.includes(val)) {
            selectedIds.push(val);
            addInterventionToList(val, text);
            hiddenInput.value = selectedIds.filter(i => !selectedIdsActuelles.includes(i)).join(',');
            sessionStorage.setItem('interventions', hiddenInput.value);
        }
        select.value = '';
    });

    // Sauvegarde lors de la soumission
    const form = document.querySelector('form');
    form?.addEventListener('submit', () => {
        sessionStorage.setItem('form_submitted', 'true');
    });

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
        btn.style.cursor = 'pointer';

        btn.addEventListener('click', () => {
            selectedIds = selectedIds.filter(i => i !== id);
            li.remove();
            hiddenInput.value = selectedIds.filter(i => !selectedIdsActuelles.includes(i)).join(',');
            sessionStorage.setItem('interventions', hiddenInput.value);
        });

        li.appendChild(btn);
        list.appendChild(li);
    }
});
