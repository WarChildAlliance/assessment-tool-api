from django.db import models
from users.models import User
from assessments.models import AssessmentTopic

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

    def __str__(self):
        return f'Profile of {self.student.first_name} {self.student.last_name}'


class TopicCompetency(models.Model):

    topic = models.ForeignKey(
        'assessments.AssessmentTopic',
        on_delete=models.CASCADE,
    )

    profile = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
    )

    competency = models.IntegerField(
        default=0
    )

    def __str__(self):
        return f'Competency of {self.profile} on {self.topic} equals {self.competency}'
