from django.core.validators import MinValueValidator
from django.db import models
from model_utils.managers import InheritanceManager
from users.models import User
from django.utils import timezone

class AssessmentSubject(models.TextChoices):
    """
    Subject enumeration.
    """
    MATH = 'MATH', 'Math'
    LITERACY = 'LITERACY', 'Literacy'
    TUTORIAL = 'TUTORIAL', 'Tutorial'


class Assessment(models.Model):
    """
    Assessment model.
    """

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
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    country = models.ForeignKey(
        'users.Country',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
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

    archived = models.BooleanField(
        default=False
    )

    downloadable = models.BooleanField(
        default=True
    )

    icon = models.FileField(
        upload_to='assessments_icons',
        null=True,
        blank=True
    )

    sel_question = models.BooleanField(
        default=True
    )

    topic = models.ForeignKey(
        'Topic',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.title}' \
            f' ({self.subject} grade {self.grade}, {self.country} - {self.language})'

    """
        If we want to delete attachments, we cannot filter and call .delete() on the query result.
        instead we need to get all attachments and delete them one by one in a for loop to trigger this delete
        But if we don't overwrite the delete in this fashion, we will have zombie files, as only the reference is deleted
    """
    def delete(self, *args, **kwargs):
        self.icon.delete()
        super().delete(*args, **kwargs)

        


class QuestionSet(models.Model):
    """
    Set of questions model.
    """

    class QuestionSetFeedback(models.IntegerChoices):
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

    # Define if the question set is evaluated or not. If it isn't,
    # it will be excluded from datasets concerning, for example,
    # valid answers percentages computation.
    evaluated = models.BooleanField(
        default=True
    )

    icon = models.FileField(
        upload_to='question_sets_icons',
        null=True,
        blank=True
    )

    # Is nullable because the database needs something to populate existing rows.
    order = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True
    )

    learning_objective = models.ForeignKey(
        'LearningObjective',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.name} ({self.assessment.id})'

    """
        If we want to delete attachments, we cannot filter and call .delete() on the query result.
        instead we need to get all attachments and delete them one by one in a for loop to trigger this delete
        But if we don't overwrite the delete in this fashion, we will have zombie files, as only the reference is deleted
    """
    def delete(self, *args, **kwargs):
        self.icon.delete()
        super().delete(*args, **kwargs)


class QuestionSetAccess(models.Model):
    """
    Question set access model.
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

    question_set = models.ForeignKey(
        'QuestionSet',
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(
        editable=False,
        null=True
    )

    updated_at = models.DateTimeField(
        null=True
    )

    def save(self, *args, **kwargs):
        ''' On save, update timestamps'''
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Set of questions accesses'
        constraints = [
            models.constraints.UniqueConstraint(
                fields=['student', 'question_set'],
                name='unique_access_per_student_and_question_set'
            )
        ]

    def __str__(self):
        return f'{self.student} has access to {self.question_set} from {self.start_date} to {self.end_date}'


class Question(models.Model):
    """
    Question model.
    """

    objects = InheritanceManager()

    class QuestionType(models.TextChoices):
        """
        Question type enumeration.
        """
        SEL = 'SEL', 'Social and Emotional Learning'
        INPUT = 'INPUT', 'Input'
        SELECT = 'SELECT', 'Select'
        SORT = 'SORT', 'Sort'
        DOMINO = 'DOMINO', 'Domino'
        NUMBER_LINE = 'NUMBER_LINE', 'Number line'
        DRAG_AND_DROP = 'DRAG_AND_DROP', 'Drag and Drop'
        CUSTOMIZED_DRAG_AND_DROP = 'CUSTOMIZED_DRAG_AND_DROP', 'Customized Drag and Drop'
        CALCUL = 'CALCUL', 'Calcul'
        FIND_HOTSPOT = 'FIND_HOTSPOT', 'Find hotspot'

    value = models.CharField(
        max_length=256,
        default='question-value-missing',
        null=False
    )

    title = models.CharField(
        max_length=256,
        null=True,
        blank=True
    )

    order = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    question_set = models.ForeignKey(
        'QuestionSet',
        on_delete=models.CASCADE
    )

    question_type = models.CharField(
        max_length=32,
        choices=QuestionType.choices
    )

    number_range = models.ForeignKey(
        'NumberRange',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        editable=False,
        null=True
    )

    updated_at = models.DateTimeField(
        null=True
    )

    shuffle = models.BooleanField(
        default=False
    )

    def save(self, *args, **kwargs):
        ''' On save, update timestamps'''
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} ({self.question_type})'

    class Meta:
        ordering = ['order']


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


class QuestionSEL(Question):
    """
    Question SEL (Social and Emotional Learning) model (inherits Question).
    """

    class SELType(models.TextChoices):
        MATH = 'MATH', 'Math Self-Efficacy'
        READ = 'READ', 'Read Self-Efficacy'
        GROWTH_MINDSET = 'GROWTH_MINDSET', 'Growth Mindset'

    sel_type = models.CharField(
        max_length=32,
        choices=SELType.choices
    )

    def __str__(self):
        return f'{self.title} ({self.question_type})'

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

    class displayTypes(models.TextChoices):
        GRID = 'GRID', 'Grid'
        HORIZONTAL = 'HORIZONTAL', 'Horizontal'
        VERTICAL = 'VERTICAL', 'Vertical'

    display_type = models.CharField(
        max_length=32,
        choices=displayTypes.choices,
        default=displayTypes.GRID
    )

    show_options_title = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f'{self.title} ({self.question_type})'

class QuestionDomino(Question):
    """
    Question domino model (inherits Question).
    """

    expected_value = models.IntegerField()

    def __str__(self):
        return f'{self.title} ({self.question_type})'

class QuestionCalcul(Question):
    """
    Question calcul model (inherits Question).
    """
    class OperatorType(models.TextChoices):
        ADDITION = 'ADDITION', 'Addition'
        SUBTRACTION = 'SUBTRACTION', 'Subtraction'
        DIVISION = 'DIVISION', 'Division'
        MULTIPLICATION = 'MULTIPLICATION', 'Multiplication'

    first_value = models.IntegerField()

    second_value = models.IntegerField()

    operator = models.CharField(
        max_length=32,
        choices=OperatorType.choices,
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

    start = models.IntegerField(
        null=False
    )

    end = models.IntegerField(
        null=False
    )

    step = models.IntegerField(
        default=1
    )

    def __str__(self):
        return f'{self.title} ({self.question_type})'

class QuestionDragAndDrop(Question):
    """
    Question Drag And Drop (inherits from Question).
    """

    def __str__(self):
        return f'{self.title} ({self.question_type})'

class QuestionFindHotspot(Question):
    """
    Question Find hotspot (inherits from Question).
    """

    def __str__(self):
        return f'{self.title} ({self.question_type})'

class QuestionCustomizedDragAndDrop(Question):
    """
    Question Customized Drag And Drop (inherits from Question).
    """
    class OperatorType(models.TextChoices):
        ADDITION = 'ADDITION', 'Addition'
        SUBTRACTION = 'SUBTRACTION', 'Subtraction'
        DIVISION = 'DIVISION', 'Division'
        MULTIPLICATION = 'MULTIPLICATION', 'Multiplication'

    class ShapesType(models.TextChoices):
        PENCIL = 'PENCIL', 'Pencil'
        FRUIT = 'FRUIT', 'Fruit'
        BALLON = 'BALLON', 'Ballon'
        BUTTON = 'BUTTON', 'Button'
        SOCKS = 'SOCKS', 'Socks'
        PAINT = 'PAINT', 'Paint'
        BUG = 'BUG', 'Bug'

    class StyleTypes(models.TextChoices):
        # Colors
        RED = 'RED', 'Red'
        LIGHT_GREEN = 'LIGHT_GREEN', 'Light Green'
        DARK_GREEN = 'DARK_GREEN', 'Dark Green'
        YELLOW = 'YELLOW', 'Yellow'
        ORANGE = 'ORANGE', 'Orange' # Can also be the fruit orange
        LIGHT_BLUE = 'LIGHT_BLUE', 'Light Blue'
        DARK_BLUE = 'DARK_BLUE', 'Dark Blue'
        PINK = 'PINK', 'Pink'
        PURPLE = 'PURPLE', 'Purple'
        # Bugs
        CATERPILLAR = 'CATERPILLAR', 'Caterpillar'
        ANT = 'ANT', 'Ant'
        BUTTERFLY = 'BUTTERFLY', 'Butterfly'
        CENTIPEDE = 'CENTIPEDE', 'Centipede'
        FLY = 'FLY', 'Fly'
        #Fruits
        APPLE = 'APPLE', 'Apple'
        BANANA = 'BANANA', 'Banana'
        WATERMELON = 'WATERMELON', 'Watermelon'

    first_value = models.IntegerField()

    first_style = models.CharField(
        max_length=32,
        choices=StyleTypes.choices
    )

    second_value = models.IntegerField()

    second_style = models.CharField(
        max_length=32,
        choices=StyleTypes.choices
    )

    operator = models.CharField(
        max_length=32,
        choices=OperatorType.choices,
    )

    shape = models.CharField(
        max_length=32,
        choices=ShapesType.choices,
    )

    def __str__(self):
        return f'{self.title} ({self.question_type})'

class AreaOption(models.Model):
    """
    Area option model (used for QuestionFindHotspot and QuestionDragAndDrop).
    The areas are rectangules. Saves the start point and the measurements of the rectangle.
    """

    name = models.CharField(
        max_length=256
    )

    question_drag_and_drop = models.ForeignKey(
        'QuestionDragAndDrop',
        related_name='drop_areas',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    question_find_hotspot = models.ForeignKey(
        'QuestionFindHotspot',
        related_name='hotspot_areas',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    # Initial point: (x, y)
    x = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    y = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Rectangle measurements (width and height)
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    height = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f'{self.name} ({self.id})'

class DraggableOption(models.Model):
    """
    Draggable option model (used for QuestionDragAndDrop).
    """
    question_drag_and_drop = models.ForeignKey(
        'QuestionDragAndDrop',
        on_delete=models.CASCADE,
        related_name='drag_options',
    )

    area_option = models.ForeignKey(
        'AreaOption',
        on_delete=models.CASCADE,
        related_name='_areas',
        null=True
    )

    def __str__(self):
        return f'{self.id} [question: {self.question_drag_and_drop.id}]'

class SelectOption(models.Model):
    """
    Select option model.
    """

    value = models.CharField(
        max_length=256,
        default='select-option-value-missing',
        null=False
    )

    title = models.CharField(
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
        return f'[{self.question_select.id}] {self.title} ({self.valid})'

class DominoOption(models.Model):
    """
    Domino option model.
    """

    left_side_value = models.IntegerField()

    right_side_value = models.IntegerField()

    valid = models.BooleanField()

    question_domino = models.ForeignKey(
        'QuestionDomino',
        on_delete=models.CASCADE,
        related_name='options'
    )

    def __str__(self):
        return f'[{self.question_domino.id}] {self.left_side_value} | {self.right_side_value} ({self.valid})'

class SortOption(models.Model):
    """
    Sort option model.
    """

    title = models.CharField(
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
        return f'[{self.question_sort.id}] {self.title} ({self.category})'


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

    question_set = models.ForeignKey(
        'QuestionSet',
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

    # Use for QuestionDragAndDrop or QuestonFindHotspot: indicates whether the attachment is the
    # question's background_image or just a normal attachment
    background_image = models.BooleanField(
        default=False,
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

    draggable_option = models.ForeignKey(
        'DraggableOption',
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


class Topic(models.Model):
    """
    Topic model.
    """
    subject = models.CharField(
        max_length=32,
        choices=AssessmentSubject.choices
    )

    name = models.CharField(
        max_length=62,
    )

    def __str__(self):
        return f'{self.name}'


class NumberRange(models.Model):
    """
    Number range model.
    """
    grade = models.CharField(max_length=32)

    min = models.PositiveSmallIntegerField(default=1)

    max = models.PositiveSmallIntegerField()

    @property
    def handle(self):
        return f'{self.min}-{self.max}'

    def __str__(self):
        return f'{self.grade}: {self.handle}'


class LearningObjective(models.Model):
    """
    Learning objective model.
    """
    code = models.CharField(
        max_length=8,
        primary_key=True
    )

    grade = models.CharField(
        max_length=32
    )

    topic = models.ForeignKey(
        'Topic',
        on_delete=models.CASCADE,
    )

    name_eng = models.CharField(
        max_length=255,
        default=''
    )

    name_ara = models.CharField(
        max_length=255,
        default=''
    )
