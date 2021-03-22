from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class User(AbstractUser):
    """
    User model.
    """
    class UserRole(models.TextChoices):
        """
        User roles enumeration.
        """
        STUDENT = 'STUDENT', 'Student'
        SUPERVISOR = 'SUPERVISOR', 'Supervisor'

    role = models.CharField(
        max_length=32,
        choices=UserRole.choices,
        default=UserRole.SUPERVISOR
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
        return self.role and self.role == self.UserRole.STUDENT

    def is_supervisor(self):
        """
        Checks user type
        """
        return self.groups and self.role == self.UserRole.SUPERVISOR

    def __str__(self):
        return f'{self.get_full_name()} ({self.username})'
