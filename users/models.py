from django.db import models
from django.contrib.auth.models import AbstractUser, Group


class User(AbstractUser):
    """
    User model
    """
    
    groups = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        default=Group.objects.get(name="Supervisor").id
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


class UserGroup(models.Model):
    """
    User group
    """

    name = models.CharField(
        max_length=256
    )

    managers = models.ManyToManyField(
        User,
        related_name="groups_manager",
        limit_choices_to={'groups__name': 'Supervisor'}
    )

    members = models.ManyToManyField(
        User,
        related_name="groups_member",
        limit_choices_to={'groups__name': 'Supervisor'}
    )

    students = models.ManyToManyField(
        User,
        related_name="groups_student",
        limit_choices_to={'groups__name': 'Student'}
    )
