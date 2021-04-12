from rest_framework import serializers

from .models import (Answer, AnswerInput, AnswerNumberLine, AnswerSelect,
                     AnswerSession, AnswerSort, AssessmentTopicAnswer)


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


class AnswerSerializer(serializers.ModelSerializer):
    """
    Answer serializer.
    """

    class Meta:
        model = Answer
        fields = ('topic_answer', 'question', 'duration',
                  'valid')


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

    class Meta:
        model = AnswerSelect
        fields = ('topic_answer', 'question', 'duration',
                  'valid', 'selected_options')


class AnswerSortSerializer(serializers.ModelSerializer):
    """
    Answer sort serializer.
    """

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
