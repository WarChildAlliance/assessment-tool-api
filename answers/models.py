from django.db import models
from django.utils import timezone
from model_utils.managers import InheritanceManager
from users.models import User


class AnswerSession(models.Model):
    """
    Answer session model.
    """

    start_date = models.DateTimeField(
        default=timezone.now
    )

    end_date = models.DateTimeField(
        blank=True,
        null=True
    )

    student = models.ForeignKey(
        'users.User',
        limit_choices_to={'role': User.UserRole.STUDENT},
        on_delete=models.CASCADE
    )

    @property
    def duration(self):
        return self.end_date - self.start_date

    def __str__(self):
        return f'{self.student} on {self.start_date}'


class AssessmentTopicAnswer(models.Model):
    """
    Assessment topic answer model.
    """

    topic_access = models.ForeignKey(
        'assessments.AssessmentTopicAccess',
        on_delete=models.CASCADE,
        related_name='assessment_topic_answers'
    )

    complete = models.BooleanField(
        default=False
    )

    start_date = models.DateTimeField(
        default=timezone.now
    )

    end_date = models.DateTimeField(
        blank=True,
        null=True
    )

    session = models.ForeignKey(
        'AnswerSession',
        on_delete=models.CASCADE,
        related_name='assessment_topic_answers'
    )

    @property
    def duration(self):
        return self.end_date - self.start_date

    @property
    def student(self):
        return self.session.student


class Answer(models.Model):
    """
    Answer answer model.
    """

    objects = InheritanceManager()

    topic_answer = models.ForeignKey(
        'AssessmentTopicAnswer',
        on_delete=models.CASCADE,
        related_name='answers'
    )

    question = models.ForeignKey(
        'assessments.Question',
        on_delete=models.CASCADE
    )

    duration = models.DurationField()

    valid = models.BooleanField()

    @property
    def date(self):
        """
        Answer date
        """
        return self.topic_answer.date

    @property
    def student(self):
        """
        Answer student
        """
        return self.topic_answer.student

    def __str__(self):
        return f'Answer by {self.student} for {self.question}'


class AnswerInput(Answer):
    """
    Answer input model (inherits Answer).
    """

    value = models.CharField(
        max_length=512
    )


class AnswerSelect(Answer):
    """
    Answer select model (inherits Answer).
    """

    selected_options = models.ManyToManyField(
        'assessments.SelectOption'
    )


class AnswerSort(Answer):
    """
    Answer sort model (inherits Answer).
    """

    category_A = models.ManyToManyField(
        'assessments.SortOption',
        related_name='answer_category_A'
    )

    category_B = models.ManyToManyField(
        'assessments.SortOption',
        related_name='answer_category_B'
    )


class AnswerNumberLine(Answer):
    """
    Answer number line model (inherits Answer).
    """

    value = models.IntegerField()