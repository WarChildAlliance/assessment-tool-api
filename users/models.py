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

    language = models.ForeignKey(
        'Language',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    country = models.ForeignKey(
        'Country',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        'User',
        limit_choices_to={'role': UserRole.SUPERVISOR},
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        related_name='student_group',
        null=True,
        blank=True
    )

    # Define the last time AbstractUser.is_active was updated.
    active_status_updated_on = models.DateTimeField(
        null=True,
        blank=True
    )

    see_intro = models.BooleanField(
        default=True
    )
    
    grade = models.CharField(
        max_length=32,
        null=True,
        blank=True
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


class Group(models.Model):
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name='Group name'
    )

    supervisor = models.ForeignKey(
        'User',
        limit_choices_to={'role': User.UserRole.SUPERVISOR},
        on_delete=models.CASCADE,
        related_name='group_supervisor'
    )

    def __str__(self):
        return f'{self.name}'


class Language(models.Model):
    """
    Language model.
    """

    class LanguageDirection(models.TextChoices):
        """
        Language direction enumeration.
        """
        LTR = 'LTR', 'Left to right'
        RTL = 'RTL', 'Right to left'

    code = models.CharField(
        max_length=3,
        primary_key=True
    )

    name_en = models.CharField(
        max_length=100,
        verbose_name='English name'
    )

    name_local = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Local name'
    )

    direction = models.CharField(
        max_length=3,
        choices=LanguageDirection.choices,
        default=LanguageDirection.LTR
    )

    def __str__(self):
        return self.name_en


class Country(models.Model):
    """
    Country model.
    """

    code = models.CharField(
        max_length=3,
        primary_key=True
    )

    name_en = models.CharField(
        max_length=100,
        verbose_name='English name'
    )

    name_local = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Local name'
    )

    language = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name_en
