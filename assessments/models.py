from django.core.validators import MinValueValidator
from django.db import models
from model_utils.managers import InheritanceManager
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
        PRESEL = 'PRESEL', 'PreSel'
        POSTSEL = 'POSTSEL', 'PostSel'

    title = models.CharField(
        max_length=256
    )

    grade = models.CharField(
        max_length=32
    )

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

    icon = models.FileField(
        upload_to='assessments_icons',
        null=True
    )

    def __str__(self):
        return f'{self.title}' \
            f' ({self.subject} grade {self.grade}, {self.country} - {self.language})'


class AssessmentTopic(models.Model):
    """
    Assessment topic model.
    """

    class TopicFeedback(models.IntegerChoices):
        """
        Feedback options enumeration.
        """
        NEVER = 0, 'Never'
        ALWAYS = 1, 'Always'
        SECOND = 2, 'Second attempt on'

    name = models.CharField(
        max_length=256
    )

    description = models.CharField(
        max_length=2048,
        blank=True,
        null=True
    )

    assessment = models.ForeignKey(
        'Assessment',
        on_delete=models.CASCADE,
    )

    # Define when a feedback should be shown to the user
    # when they answer a question
    show_feedback = models.IntegerField(
        choices=TopicFeedback.choices,
        default=TopicFeedback.SECOND
    )

    # Define if the questions inside this topic can be
    # skipped or not
    allow_skip = models.BooleanField(
        default=False
    )

    # Define if the topic is evaluated or not. If it isn't,
    # it will be excluded from datasets concerning, for example,
    # valid answers percentages computation.
    evaluated = models.BooleanField(
        default=True
    )

    # Define the average number of valid answers a student
    # will have to submit before being shown a praise message.
    # A certain degree of randomness is included in the Frontend so it is
    # not too repetitive and predictable
    praise = models.IntegerField(
        default=0
    )

    # Define the maximum number of invalid or skipped answers
    # an user can submit for a topic. Once exceeded, the active topic answer
    # will be closed and the user redirected to homepage.
    max_wrong_answers = models.IntegerField(
        default=0
    )

    icon = models.FileField(
        upload_to='topics_icons',
        null=True
    )

    def __str__(self):
        return f'{self.name} ({self.assessment.id})'


class AssessmentTopicAccess(models.Model):
    """
    Assessment topic access model.
    """

    start_date = models.DateField(
        null=True,
        blank=True
    )

    end_date = models.DateField(
        null=True,
        blank=True
    )

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
        constraints = [
            models.constraints.UniqueConstraint(
                fields=['student', 'topic'],
                name='unique_access_per_student_and_topic'
            )
        ]

    def __str__(self):
        return f'{self.student} has access to {self.topic} from {self.start_date} to {self.end_date}'


class Question(models.Model):
    """
    Question model.
    """

    objects = InheritanceManager()

    class QuestionType(models.TextChoices):
        """
        Question type enumeration.
        """
        INPUT = 'INPUT', 'Input'
        SELECT = 'SELECT', 'Select'
        SORT = 'SORT', 'Sort'
        NUMBER_LINE = 'NUMBER_LINE', 'Number line'

    title = models.CharField(
        max_length=256,
        null=True,
        blank=True
    )

    order = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
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

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=['order', 'assessment_topic'],
                name='unique_order'
            )
        ]


class Hint(models.Model):
    """
    Hint model.
    """

    text = models.CharField(
        max_length=512,
        null=True,
        blank=True
    )

    question = models.OneToOneField(
        'Question',
        on_delete=models.CASCADE,
        related_name='hint'
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

    options = []

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

    show_ticks = models.BooleanField(
        default=False
    )

    show_value = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f'{self.title} ({self.question_type})'


class SelectOption(models.Model):
    """
    Select option model.
    """

    value = models.CharField(
        max_length=256,
        null=True,
        blank=True
    )

    valid = models.BooleanField()

    question_select = models.ForeignKey(
        'QuestionSelect',
        on_delete=models.CASCADE,
        related_name='options'
    )

    def __str__(self):
        return f'[{self.question_select.id}] {self.value} ({self.valid})'


class SortOption(models.Model):
    """
    Sort option model.
    """

    value = models.CharField(
        max_length=256,
        null=True,
        blank=True
    )

    category = models.CharField(
        max_length=256
    )

    question_sort = models.ForeignKey(
        'QuestionSort',
        on_delete=models.CASCADE,
        related_name='options'
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

    file = models.FileField(
        upload_to='attachments',
        null=True
    )

    topic = models.ForeignKey(
        'AssessmentTopic',
        related_name='attachments',
        on_delete=models.CASCADE,
        null=True,
        blank=True
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
        return f'[{self.attachment_type}] {self.file}'

    """
        If we want to delete attachments, we cannot filter and call .delete() on the query result.
        instead we need to get all attachments and delete them one by one in a for loop to trigger this delete
        But if we don't overwrite the delete in this fashion, we will have zombie files, as only the reference is deleted
    """
    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)
