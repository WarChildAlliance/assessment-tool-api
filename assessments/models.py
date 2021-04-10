from django.db import models
from users.models import User


class Assessment(models.Model):
    """
    Assessment model.
    """

    class AssessmentSubject(models.TextChoices):
        """
        Subject enumeration.
        """
        MATH = 'MATH', 'Math'
        LITERACY = 'LITERACY', 'Literacy'

    title = models.CharField(
        max_length=256
    )

    grade = models.IntegerField()

    subject = models.CharField(
        max_length=32,
        choices=AssessmentSubject.choices
    )

    language = models.ForeignKey(
        'users.Language',
        on_delete=models.CASCADE
    )

    country = models.ForeignKey(
        'users.Country',
        on_delete=models.CASCADE
    )

    created_by = models.ForeignKey(
        'users.User',
        limit_choices_to={'role': User.UserRole.SUPERVISOR},
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    private = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f'{self.title}' \
            f' ({self.subject} grade {self.grade}, {self.country} - {self.language})'


class AssessmentTopic(models.Model):
    """
    Assessment topic model.
    """

    name = models.CharField(
        max_length=256
    )

    order = models.IntegerField()

    assessment = models.ForeignKey(
        'Assessment',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.name} ({self.assessment.id})'


class AssessmentTopicAccess(models.Model):
    """
    Assessment topic access model.
    """

    start_date = models.DateField()

    end_date = models.DateField()

    student = models.ForeignKey(
        'users.User',
        limit_choices_to={'role': User.UserRole.STUDENT},
        on_delete=models.CASCADE,
    )

    topic = models.ForeignKey(
        'AssessmentTopic',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name_plural = 'Assessment topics access'

    def __str__(self):
        return f'{self.student} has access to {self.topic} from {self.start_date} to {self.end_date}'


class Question(models.Model):
    """
    Question model.
    """

    class QuestionType(models.TextChoices):
        """
        Question type enumeration.
        """
        INPUT = 'INPUT', 'Input'
        SELECT = 'SELECT', 'Select'
        SORT = 'SORT', 'Sort'
        NUMBER_LINE = 'NUMBER_LINE', 'Number line'

    title = models.CharField(
        max_length=256
    )

    assessment_topic = models.ForeignKey(
        'AssessmentTopic',
        on_delete=models.CASCADE
    )

    question_type = models.CharField(
        max_length=32,
        choices=QuestionType.choices
    )

    def __str__(self):
        return f'{self.title} ({self.question_type})'


class Hint(models.Model):
    """
    Hint model.
    """

    text = models.CharField(
        max_length=512
    )

    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE
    )


class QuestionInput(Question):
    """
    Question input model (inherits Question).
    """

    valid_answer = models.CharField(
        max_length=512
    )

    def __str__(self):
        return f'{self.title} ({self.question_type})'


class QuestionSelect(Question):
    """
    Question select model (inherits Question).
    """

    multiple = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f'{self.title} ({self.question_type})'


class QuestionSort(Question):
    """
    Question sort model (inherits Question).
    """

    category_A = models.CharField(
        max_length=256
    )
    category_B = models.CharField(
        max_length=256
    )

    def __str__(self):
        return f'{self.title} ({self.question_type})'


class QuestionNumberLine(Question):
    """
    Question number line model (inherits Question).
    """

    expected_value = models.IntegerField()
    start = models.IntegerField()
    end = models.IntegerField()
    step = models.IntegerField()
    show_ticks = models.BooleanField()
    show_value = models.BooleanField()

    def __str__(self):
        return f'{self.title} ({self.question_type})'


class SelectOption(models.Model):
    """
    Select option model.
    """

    value = models.CharField(
        max_length=256
    )

    valid = models.BooleanField()

    question_select = models.ForeignKey(
        'QuestionSelect',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'[{self.question_select.id}] {self.value} ({self.valid})'


class SortOption(models.Model):
    """
    Sort option model.
    """

    value = models.CharField(
        max_length=256
    )

    category = models.CharField(
        max_length=256
    )

    question_sort = models.ForeignKey(
        'QuestionSort',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'[{self.question_sort.id}] {self.value} ({self.category})'


class Attachment(models.Model):
    """
    Attachment model.
    """

    class AttachmentType(models.TextChoices):
        AUDIO = 'AUDIO', 'Audio'
        IMAGE = 'IMAGE', 'Image'

    attachment_type = models.CharField(
        max_length=64,
        choices=AttachmentType.choices
    )

    link = models.CharField(
        max_length=2048
    )

    question = models.ForeignKey(
        'Question',
        related_name='attachments',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    hint = models.ForeignKey(
        'Hint',
        related_name='attachments',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    select_option = models.ForeignKey(
        'SelectOption',
        related_name='attachments',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    sort_option = models.ForeignKey(
        'SortOption',
        related_name='attachments',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return f'[{self.attachment_type}] {self.link}'
