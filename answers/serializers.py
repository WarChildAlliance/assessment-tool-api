from assessments.models import Question, QuestionInput, SelectOption, SortOption
from assessments.serializers import (SelectOptionSerializer,
                                     SortOptionSerializer)
from rest_framework import serializers

from admin.lib.serializers import NestedRelatedField, PolymorphicSerializer

from .models import (Answer, AnswerInput, AnswerNumberLine, AnswerSelect,
                     AnswerSession, AnswerSort, AssessmentTopicAnswer)

from rest_framework.utils import model_meta

class AssessmentTopicAnswerSerializer(serializers.ModelSerializer):
    """
    Assessment topic answer serializer.
    """

    class Meta:
        model = AssessmentTopicAnswer
        fields = ('complete', 'duration', 'topic_access', 'session')


class AnswerSessionSerializer(serializers.ModelSerializer):
    """
    Answer session serializer.
    """

    class Meta:
        model = AnswerSession
        fields = ('duration', 'date', 'student')


class AnswerSerializer(PolymorphicSerializer):
    """
    Answer serializer.
    """

    class Meta:
        model = Answer
        fields = '__all__'

    def get_serializer_map(self):
        return {
            'AnswerInput': AnswerInputSerializer,
            'AnswerNumberLine': AnswerNumberLineSerializer,
            'AnswerSelect': AnswerSelectSerializer,
            'AnswerSort': AnswerSortSerializer
        }

    def to_internal_value(self, data):
        data = data.copy()
        question = Question.objects.get_subclass(id=data['question'])
        question_type = type(question).__name__
        if question_type == 'QuestionInput':
            data['type'] = 'AnswerInput'
        elif question_type == 'QuestionNumberLine':
            data['type'] = 'AnswerNumberLine'
        elif question_type == 'QuestionSelect':
            data['type'] = 'AnswerSelect'
        elif question_type == 'QuestionSort':
            data['type'] = 'AnswerSort'
        return super().to_internal_value(data)


class AnswerInputSerializer(serializers.ModelSerializer):
    """
    Answer input serializer.
    """

    class Meta:
        model = AnswerInput
        fields = ('topic_answer', 'question', 'duration',
                  'valid', 'value')


class AnswerSelectSerializer(serializers.ModelSerializer):
    """
    Answer select serializer.
    """
    selected_options = NestedRelatedField(
        model=SelectOption, serializer_class=SelectOptionSerializer, many=True)

    class Meta:
        model = AnswerSelect
        fields = ('topic_answer', 'question', 'duration',
                  'valid', 'selected_options')


class AnswerSortSerializer(serializers.ModelSerializer):
    """
    Answer sort serializer.
    """
    category_A = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True)
    category_B = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True)

    class Meta:
        model = AnswerSort
        fields = ('topic_answer', 'question', 'duration',
                  'valid', 'category_A', 'category_B')


class AnswerNumberLineSerializer(serializers.ModelSerializer):
    """
    Answer number line serializer.
    """

    class Meta:
        model = AnswerNumberLine
        fields = ('topic_answer', 'question', 'duration',
                  'valid', 'value')
