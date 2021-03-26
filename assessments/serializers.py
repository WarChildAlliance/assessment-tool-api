from rest_framework import serializers

from .models import (Assessment, AssessmentTopic, Attachment, Question,
                     QuestionInput, QuestionSelect, QuestionSort,
                     QuestionNumberLine, SelectOption, SortOption)


class AssessmentSerializer(serializers.ModelSerializer):
    """
    Assessment serializer.
    """

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'grade', 'subject',
                  'language', 'country', 'private')


class AssessmentTopicSerializer(serializers.ModelSerializer):
    """
    Assessment topic serializer.
    """

    class Meta:
        model = AssessmentTopic
        fields = ('id', 'name', 'order',
                  'assessment')


class QuestionSerializer(serializers.ModelSerializer):
    """
    Question serializer.
    """

    class Meta:
        model = Question
        fields = ('id', 'title', 'assessment_topic',
                  'type', 'hint')


class QuestionInputSerializer(serializers.ModelSerializer):
    """
    Question input serializer.
    """

    class Meta:
        model = QuestionInput
        fields = ('id', 'title', 'assessment_topic',
                  'type', 'hint', 'valid_answer')


class QuestionSelectSerializer(serializers.ModelSerializer):
    """
    Question select serializer.
    """

    class Meta:
        model = QuestionSelect
        fields = ('id', 'title', 'assessment_topic',
                  'type', 'hint', 'multiple')


class QuestionSortSerializer(serializers.ModelSerializer):
    """
    Question sort serializer.
    """

    class Meta:
        model = QuestionSort
        fields = ('id', 'title', 'assessment_topic',
                  'type', 'hint', 'category_A', 'category_B')


class QuestionNumberLineSerializer(serializers.ModelSerializer):
    """
    Question number line serializer.
    """

    class Meta:
        QuestionNumberLine
        model = QuestionSort
        fields = ('id', 'title', 'assessment_topic',
                  'type', 'hint', 'expected_value', 'start',
                  'end', 'step', 'show_value', 'show ticks')


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Attachment serializer.
    """

    class Meta:
        model = Attachment
        fields = ('id', 'type', 'link', 'question_id',
                  'select_option_id', 'sort_option_id')


class SelectOptionSerializer(serializers.ModelSerializer):
    """
    Select option serializer.
    """

    class Meta:
        model = SelectOption
        fields = ('id', 'value', 'valid', 'question_select')


class SortOptionSerializer(serializers.ModelSerializer):
    """
    Sort option serializer.
    """

    class Meta:
        model = SortOption
        fields = ('id', 'value', 'category', 'question_sort')
