from django.core.management.base import BaseCommand
from django.db import transaction

from users.roles import roles


class RollBackException(BaseException):
    """
    Exception class on roll back
    """


class Command(BaseCommand):
    """
    Loads the groups and permissions defined in roles.py
    """

    help = 'Load user groups defined in roles.py'

    def add_arguments(self, parser):
        """
        Adds arguments to the command
        """
        parser.add_argument(
            '--dry_run',
            action='store_true',
            default=False,
            help=u'Does a dry-run, no data will be altered.',
        )

    def handle(self, *args, **options):
        """
        Executes the command
        """
        dry_run = options['dry_run']
        try:
            with transaction.atomic():
                for role in roles:
                    role.save_permissions()
                if dry_run:
                    raise RollBackException('Dry run, rolling back')
                print(f'{len(roles)} roles were saved successfully!')
        except RollBackException:
            print('Dry run, changes were rolled back.')
