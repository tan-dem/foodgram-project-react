import csv

from django.core.management import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):
    """Custom command to load data from CSV file into database ."""

    help = "Loads data from ingredients.csv"

    def handle(self, *args, **options):
        with open("data/ingredients.csv") as isfile:
            reader = csv.reader(isfile)
            try:
                for row in reader:
                    name, measurement_unit = row
                    Ingredient.objects.get_or_create(
                        name=name, measurement_unit=measurement_unit
                    )
            except Exception as error:
                raise CommandError(f"Data not loaded: {error}.")
