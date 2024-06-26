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

    def __str__(self):
        return f'{self.student} on {self.start_date}'


class QuestionSetAnswer(models.Model):
    """
    Question set answer model.
    """

    question_set_access = models.ForeignKey(
        'assessments.QuestionSetAccess',
        on_delete=models.SET_NULL,
        related_name='question_set_answers',
        null=True,
        blank=True
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
        related_name='question_set_answers'
    )

    @property
    def student(self):
        return self.session.student


class Answer(models.Model):
    """
    Answer answer model.
    """

    objects = InheritanceManager()

    question_set_answer = models.ForeignKey(
        'QuestionSetAnswer',
        on_delete=models.CASCADE,
        related_name='answers'
    )

    question = models.ForeignKey(
        'assessments.Question',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    valid = models.BooleanField()

    start_datetime = models.DateTimeField(
        blank=True,
        null=True
    )

    end_datetime = models.DateTimeField(
        blank=True,
        null=True
    )

    @property
    def date(self):
        """
        Answer date
        """
        return self.question_set_answer.date

    @property
    def student(self):
        """
        Answer student
        """
        return self.question_set_answer.student

    def __str__(self):
        return f'Answer by {self.student} for {self.question}'


class AnswerInput(Answer):
    """
    Answer input model (inherits Answer).
    """

    value = models.CharField(
        max_length=512,
        null=True,
        blank=True
    )


class AnswerSelect(Answer):
    """
    Answer select model (inherits Answer).
    """

    selected_option = models.ForeignKey(
        'assessments.SelectOption',
        related_name='selected_option',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )


class AnswerDomino(Answer):
    """
    Answer domino model (inherits Answer).
    """

    selected_domino = models.ForeignKey(
        'assessments.DominoOption',
        related_name='selected_domino',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

class AnswerSort(Answer):
    """
    Answer sort model (inherits Answer).
    """

    category_A = models.ManyToManyField(
        'assessments.SortOption',
        related_name='answer_category_A',
        blank=True
    )

    category_B = models.ManyToManyField(
        'assessments.SortOption',
        related_name='answer_category_B',
        blank=True
    )


class AnswerNumberLine(Answer):
    """
    Answer number line model (inherits Answer).
    """

    value = models.IntegerField(
        null=True,
        blank=True
    )

class AnswerFindHotspot(Answer):
    """
    Answer find hotspot model (inherits Answer).
    """

    selected_options = models.ManyToManyField(
        'assessments.AreaOption',
        blank=True
    )


class AnswerDragAndDrop(Answer):
    """
    Answer drag and drop model (inherits Answer).
    The concrete answers for each area are stored in DragAndDropAreaEntry.
    """
    pass


class DragAndDropAreaEntry(models.Model):
    """
    Drag and drop area entry model.
    Designates an answer for one of the AreaOptions of the QuestionDragAndDrop.
    """

    selected_draggable_option = models.ForeignKey(
        'assessments.DraggableOption',
        related_name='selected_draggable_option',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    area = models.ForeignKey(
        'assessments.AreaOption',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    answer = models.ForeignKey(
        AnswerDragAndDrop,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

class AnswerSEL(Answer):
    """
    Answer SEL model (inherits Answer).
    """

    class SELStatements(models.TextChoices):
        NOT_REALLY = 'NOT_REALLY', 'Not really like me'
        A_LITTLE = 'A_LITTLE', 'A little like me'
        A_LOT = 'A_LOT', 'A lot like me'

    statement = models.CharField(
        max_length=32,
        choices=SELStatements.choices
    )

class AnswerCalcul(Answer):
    """
    Answer Calcul model (inherits Answer).
    """

    value = models.IntegerField()

class AnswerCustomizedDragAndDrop(Answer):
    """
    Answer Customized Drag And Drop model (inherits Answer).
    """

    left_value = models.IntegerField()

    right_value = models.IntegerField()

    final_value = models.IntegerField()