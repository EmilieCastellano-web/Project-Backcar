from django.core.management.base import BaseCommand

# Importe ta fonction principale
from mission.script.populate_db import main

class Command(BaseCommand):
    help = "Remplit la base de données avec des données de test."

    def handle(self, *args, **options):
        main()
