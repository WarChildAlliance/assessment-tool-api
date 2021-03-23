import csv
import os

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from admin.settings.base import BASE_DIR
from users.models import Country, Language


class Command(BaseCommand):
    """
    Command to load languages and countries in the database.
    """
    help = 'Loads languages and countries in the database'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        languages_data = BASE_DIR / 'users/management/commands/languages.csv'
        countries_data = BASE_DIR / 'users/management/commands/countries.csv'

        with open(languages_data) as languages:
            csv_reader = csv.reader(languages, delimiter=',')
            next(csv_reader)
            with transaction.atomic():
                for row in csv_reader:
                    code = row[0].strip() if row[0].strip() != '' else None
                    name_en = row[1].strip() if row[1].strip() != '' else None
                    name_local = row[2].strip() if row[2].strip() != '' else None
                    obj, created = Language.objects.update_or_create(
                        code=code,
                        defaults={'name_en': name_en, 'name_local': name_local}
                    )
                    self.stdout.write(f'{obj} added.')
            self.stdout.write('Languages saved!\n\n')

        with open(countries_data) as countries:
            csv_reader = csv.reader(countries, delimiter=',')
            next(csv_reader)
            with transaction.atomic():
                for row in csv_reader:
                    code = row[0].strip() if row[0].strip() != '' else None
                    name_en = row[1].strip() if row[1].strip() != '' else None
                    name_local = row[2].strip() if row[2].strip() != '' else None
                    language = None
                    if row[3].strip() != '':
                        try:
                            language = Language.objects.get(code=row[3].strip())
                        except ObjectDoesNotExist:
                            self.stdout.write(f'Could not find language {row[3].strip()},' \
                                ' no language was set.')
                    obj, created = Country.objects.update_or_create(
                        code=code,
                        defaults={'name_en': name_en, 'name_local': name_local,
                            'language': language}
                    )
                    self.stdout.write(f'{obj} added.')
            self.stdout.write('Countries saved!\n\n')
