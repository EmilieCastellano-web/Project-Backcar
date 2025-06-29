from django.db import models
from django.core import validators
from django.db.models import DecimalField
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from enum import Enum

class Priorite(Enum):
    NON_PRIORITAIRE = "Non prioritaire"
    BASSE = "Basse"
    MOYENNE = "Moyenne"
    HAUTE = "Haute"
    URGENTE = "Urgente"
    
class Categorie(Enum):
    MECA_BCR = "Méca BCR"
    MECA_CBC = "Méca CBC"
    CARROSSERIE = "Carrosserie"
    CUSTOM = "Personnalisée"
    
class Taux(Enum):
    HORAIRE = "Horaire"
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    
class PositiveDecimalField(DecimalField):
    description = _("Positive Decimal Field")

    def __init__(self, verbose_name=None, name=None, max_digits=6, decimal_places=2, **kwargs):
        kwargs['max_digits'] = max_digits
        kwargs['decimal_places'] = decimal_places
        super().__init__(verbose_name, name, **kwargs)

    @cached_property
    def validators(self):
        validators_ = super().validators
        validators_.append(validators.MinValueValidator(0.0))
        return validators_

class Client(models.Model):
    class Meta:
        ordering = ["id"]
        verbose_name = "client"
        verbose_name_plural = "clients"
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email')
            ]
        
    nom = models.CharField(verbose_name="nom", null=False, blank=False, max_length=50)
    prenom = models.CharField(verbose_name="prénom", null=False, blank=False, max_length=50)
    societe = models.CharField(verbose_name="société", null= True, max_length=50)
    telephone = models.CharField(verbose_name="téléphone", null=False, blank=False, max_length=10)
    email = models.EmailField(verbose_name="email", null=False, blank=False)
    adresse = models.CharField(verbose_name="adresse", null=False, max_length=200)
    code_postal = models.CharField(verbose_name="code postal", null=False, blank=False, max_length=5)
    ville = models.CharField(verbose_name="ville", null=False, blank=False, max_length=100)
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Vehicule(models.Model):
    class Meta:
        ordering = ["id"]
        verbose_name = "véhicule"
        verbose_name_plural = "véhicules"
        
    marque = models.CharField(verbose_name="marque", null=False, max_length=50)
    modele = models.CharField(verbose_name="modèle", null=False, max_length=50)
    immatriculation = models.CharField(verbose_name="immatriculation", null=False, max_length=9)
    numero_serie = models.CharField(verbose_name="numéro de série", null=False, unique=True, max_length=17)
    mise_circulation = models.DateField(verbose_name="date de mise en circulation", null=True)
    kilometrage = models.PositiveIntegerField(verbose_name="kilométrage", null=False, default=0)
    remarque = models.TextField(verbose_name="Remarque", null=True)
    client = models.ForeignKey(verbose_name="client", to=Client, null=False, on_delete=models.CASCADE)
    vo = models.BooleanField(verbose_name="vo", null=False)
    boite_vitesse = models.CharField(verbose_name="boite de vitesse", null=False)
    carburant = models.CharField(verbose_name="carburant", null=False)
    
    def __str__(self):
        return f"{self.marque} {self.modele}"
    
class Intervention(models.Model):
    libelle = models.CharField(verbose_name="libellé", null=False, max_length=100)
    duree_intervention = PositiveDecimalField(verbose_name="durée", null=False, default=0.00, max_digits=6, decimal_places=2)
    prix_unitaire = PositiveDecimalField(verbose_name="prix unitaire", blank=True, default=0.00, max_digits=6, decimal_places=2)
    forfait = PositiveDecimalField(verbose_name="forfait", default=0.00, blank=True, max_digits=6, decimal_places=2)
    is_forfait = models.BooleanField(verbose_name="is_forfait", default=False)
    date_creation = models.DateField(verbose_name="date de création", default=timezone.now, null=False)
    date_modification = models.DateField(verbose_name="date de modification", null=True)
    description = models.TextField(verbose_name="description", null=True)
    categorie = models.CharField(null=False, choices=[(choix.name, choix.value) for choix in Categorie])
    
    def save(self, *args, **kwargs):
        # Mise à jour automatique de la date de modification si l'objet existe déjà
        if self.pk:
            self.date_modification = timezone.now().date()
        
        self.is_forfait = bool(self.forfait > 0)
        super().save(*args, **kwargs)
    
class Mission(models.Model):
    class Meta:
        ordering = ["-date_demande"]
        unique_together = ["vehicule", "client"]
        
    date_demande = models.DateTimeField(verbose_name="date de demande ", default=timezone.now, null=False) 
    remarque = models.TextField(verbose_name="remarque", null=True)
    priorite = models.CharField(verbose_name="priorité", choices = [(choix.name, choix.value) for choix in Priorite])
    vehicule = models.ForeignKey(verbose_name="véhicule", to=Vehicule, on_delete=models.CASCADE, null=False)
    client = models.ForeignKey(verbose_name="client", to=Client, on_delete=models.PROTECT, null=False)
    interventions = models.ManyToManyField(verbose_name="interventions", to="Intervention", through="MissionIntervention", related_name="missions", blank=True)
    
    
class MissionIntervention(models.Model):
    class Meta:
        verbose_name = "mission_intervention"
        verbose_name_plural = "missions_interventions"
        unique_together = ["mission", "intervention"]
        
    mission = models.ForeignKey(verbose_name="mission", to=Mission, on_delete=models.CASCADE, null=False)
    intervention = models.ForeignKey(verbose_name="intervention", to=Intervention, on_delete=models.CASCADE, null=False)
    duree_supplementaire = PositiveDecimalField(verbose_name="durée supplémentaire", null=True, default=0.00, max_digits=6, decimal_places=2)
    taux = models.CharField(verbose_name="taux horaire", null=False, choices=[(choix.name, choix.value) for choix in Taux])
    cout_total = PositiveDecimalField(verbose_name="total", null=False, default=0.00, max_digits=6, decimal_places=2)

