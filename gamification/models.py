from django.db import models
from django.db.models.deletion import CASCADE, SET_DEFAULT, SET_NULL
from django.db.models.fields import IntegerField, related
from django.db.models.lookups import In
from users.models import User
from assessments.models import QuestionSet


class Avatar(models.Model):

    image = models.FileField(
        upload_to='avatars',
        null=True
    )

    effort_cost = models.IntegerField()

    def __str__(self):
        return f'Avatar which costs {self.effort_cost}'

    class Meta:
        ordering = ['effort_cost']

    """
        If we want to delete avatars, we cannot filter and call .delete() on the query result.
        instead we need to get all avatars and delete them one by one in a for loop to trigger this delete
        But if we don't overwrite the delete in this fashion, we will have zombie files, as only the reference is deleted
    """
    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args, **kwargs)


class Profile(models.Model):
    """
    Profile model.
    """

    student = models.ForeignKey(
        'users.User',
        limit_choices_to={'role': User.UserRole.STUDENT},
        on_delete=models.CASCADE,
    )

    effort = models.IntegerField(
        default=0
    )

    current_avatar = models.ForeignKey(Avatar,
        on_delete=SET_NULL,
        null=True,
        related_name='selected_on_profile'
    )

    unlocked_avatars = models.ManyToManyField(Avatar,
        related_name='unlocked_on_profile'
    )

    def __str__(self):
        return f'Profile of {self.student.first_name} {self.student.last_name}'


class QuestionSetCompetency(models.Model):

    question_set = models.ForeignKey(
        'assessments.QuestionSet',
        on_delete=models.CASCADE,
    )

    profile = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
    )

    competency = models.IntegerField(
        default=0
    )

    class Meta:
        verbose_name_plural = 'QuestionSet competencies'

    def __str__(self):
        return f'Competency of {self.profile} on {self.question_set} equals {self.competency}'
