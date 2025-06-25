from django import forms
from django.utils import timezone
from mission.models import Intervention

class InterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        # Exclure les champs de date qui seront gérés automatiquement
        exclude = ['date_creation', 'date_modification']
        
    def save(self, commit=True):
        """Enregistre l'intervention.

        Args:
            commit (bool, optional): Indique si les modifications doivent être enregistrées dans la base de données. Defaults to True.

        Returns:
            Intervention: L'objet Intervention enregistré.
        """
        instance = super().save(commit=False)
        
        # Si c'est une modification (l'objet existe déjà), mettre à jour la date de modification
        if instance.pk:
            instance.date_modification = timezone.now().date()
        
        if commit:
            instance.save()
        return instance