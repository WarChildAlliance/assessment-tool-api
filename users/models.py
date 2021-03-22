from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class User(AbstractUser):
    """
    User model
    """

    groups = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        default=1
    )

    first_name = models.CharField(
        max_length=150
    )

    last_name = models.CharField(
        max_length=150
    )

    language = models.CharField(
        max_length=3
    )

    country = models.CharField(
        max_length=3
    )

    def is_student(self):
        """
        Checks user type
        """
        return self.groups and self.groups.name == 'Student'

    def is_supervisor(self):
        """
        Checks user type
        """
        return self.groups and self.groups.name == 'Supervisor'

    def __str__(self):
        return f'{self.get_full_name()} ({self.username})'
