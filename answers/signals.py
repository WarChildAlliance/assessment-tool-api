from assessments.models import Question, SelectOption, SortOption
from django.conf import settings
from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver

from .models import AnswerInput, AnswerNumberLine, AnswerSelect, AnswerSort


@receiver(pre_save, sender=AnswerInput)
def check_answer_input_validity(sender, instance=None, **kwargs):
    """
    Check answer validity for question input.
    """
    question_answer = Question.objects.get_subclass(
        id=instance.question_id).valid_answer
    if question_answer == instance.value:
        instance.valid = True
    else:
        instance.valid = False


@receiver(pre_save, sender=AnswerNumberLine)
def check_answer_number_line_validity(sender, instance=None, **kwargs):
    """
    Check answer validity for question input.
    """
"""     question_answer = Question.objects.get_subclass(
        id=instance.question_id).expected_value
    if question_answer == instance.value:
        instance.valid = True
    else:
        instance.valid = False """


@receiver(m2m_changed, sender=AnswerSelect.selected_options.through)
def check_answer_select_validity(sender, instance=None, action=None, pk_set=None, **kwargs):
    """
    Check answer validity for question input.
    Triggered when many-to-many relationship on selected_options is changed.
    """
    if action == 'post_add':
        invalid_answer = SelectOption.objects.filter(id__in=pk_set, valid=False).exists()
        if invalid_answer:
            instance.valid = False
        else:
            instance.valid = True
        instance.save()


@receiver(m2m_changed, sender=AnswerSort.category_A.through)
@receiver(m2m_changed, sender=AnswerSort.category_B.through)
def check_answer_sort_validity(sender, instance=None, action=None, pk_set=None, **kwargs):
    """
    Check answer validity for question input.
    Triggered when many-to-many relationship on category_A or category_B is changed.
    """
    if action == 'post_add':
        if 'category_A' in sender.__name__:
            category_name = Question.objects.get_subclass(
                id=instance.question_id).category_A
        else:
            category_name = Question.objects.get_subclass(
                id=instance.question_id).category_B

        count_selected = SortOption.objects.filter(
            id__in=pk_set, category=category_name).count()
        count_expected = SortOption.objects.filter(
            category=category_name).count()

        if count_selected != count_expected:
            instance.valid = False
        else:
            instance.valid = True
        instance.save()
