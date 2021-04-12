from enum import Enum

from rest_framework import serializers

from .models import (Assessment, AssessmentTopic, Attachment, Hint, Question,
                     QuestionInput, QuestionNumberLine, QuestionSelect,
                     QuestionSort, SelectOption, SortOption)


class PolymorphicSerializer(serializers.ModelSerializer):
    """
    Serializer to handle multiple subclasses of another class
    - For serialized dict representations, a 'type' key with the class name as
      the value is expected: ex. {'type': 'Decimal', ... }
    - This type information is used in tandem with get_serializer_map(...) to
      manage serializers for multiple subclasses
    """

    def get_serializer_map(self):
        """
        Return a dict to map class names to their respective serializer classes
        To be implemented by all PolymorphicSerializer subclasses
        """
        raise NotImplementedError

    def to_representation(self, obj):
        """
        Translate object to internal data representation
        Override to allow polymorphism
        """
        if hasattr(obj, 'get_type'):
            type_str = obj.get_type()
            if isinstance(type_str, Enum):
                type_str = type_str.value
        else:
            type_str = obj.__class__.__name__

        try:
            serializer = self.get_serializer_map()[type_str]
        except KeyError:
            raise ValueError(
                'Serializer for "{}" does not exist'.format(type_str), )

        data = serializer(obj, context=self.context).to_representation(obj)
        data['type'] = type_str
        return data

    def to_internal_value(self, data):
        """
        Validate data and initialize primitive types
        Override to allow polymorphism
        """
        try:
            type_str = data['type']
        except KeyError:
            raise serializers.ValidationError({
                'type': 'This field is required',
            })

        try:
            serializer = self.get_serializer_map()[type_str]
        except KeyError:
            raise serializers.ValidationError({
                'type': 'Serializer for "{}" does not exist'.format(type_str),
            })

        validated_data = serializer(
            context=self.context).to_internal_value(data)
        validated_data['type'] = type_str
        return validated_data

    def create(self, validated_data):
        """
        Translate validated data representation to object
        Override to allow polymorphism
        """
        serializer = self.get_serializer_map()[validated_data['type']]
        validated_data.pop('type')
        return serializer(context=self.context).create(validated_data)

    def update(self, instance, validated_data):
        serializer = self.get_serializer_map()[validated_data['type']]
        validated_data.pop('type')
        return serializer(context=self.context).update(instance, validated_data)


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


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Attachment serializer.
    """

    class Meta:
        model = Attachment
        fields = ('id', 'attachment_type', 'link')


class HintSerializer(serializers.ModelSerializer):
    """
    Hint serializer.
    """
    attachments = AttachmentSerializer(many=True)

    class Meta:
        model = Hint
        fields = ('text', 'attachments')


class SelectOptionSerializer(serializers.ModelSerializer):
    """
    Select option serializer.
    """
    attachments = AttachmentSerializer(many=True)

    class Meta:
        model = SelectOption
        fields = ('id', 'value', 'valid', 'attachments')


class SortOptionSerializer(serializers.ModelSerializer):
    """
    Sort option serializer.
    """
    attachments = AttachmentSerializer(many=True)

    class Meta:
        model = SortOption
        fields = ('id', 'value', 'category', 'attachments')


class QuestionSerializer(PolymorphicSerializer):
    """
    Question serializer.
    """

    def get_serializer_map(self):
        return {
            'QuestionInput': QuestionInputSerializer,
            'QuestionNumberLine': QuestionNumberLineSerializer,
            'QuestionSelect': QuestionSelectSerializer,
            'QuestionSort': QuestionSortSerializer
        }


class QuestionInputSerializer(serializers.ModelSerializer):
    """
    Question input serializer.
    """
    attachments = AttachmentSerializer(many=True)
    hint = HintSerializer()

    class Meta:
        model = QuestionInput
        fields = ('id', 'title', 'assessment_topic', 'hint',
                  'question_type', 'valid_answer', 'attachments')


class QuestionSelectSerializer(serializers.ModelSerializer):
    """
    Question select serializer.
    """
    options = SelectOptionSerializer(many=True)
    attachments = AttachmentSerializer(many=True)
    hint = HintSerializer()

    class Meta:
        model = QuestionSelect
        fields = ('id', 'title', 'assessment_topic', 'options',
                  'question_type', 'multiple', 'attachments', 'hint')


class QuestionSortSerializer(serializers.ModelSerializer):
    """
    Question sort serializer.
    """
    options = SortOptionSerializer(many=True)
    attachments = AttachmentSerializer(many=True)
    hint = HintSerializer()

    class Meta:
        model = QuestionSort
        fields = ('id', 'title', 'assessment_topic', 'options', 'hint',
                  'question_type', 'category_A', 'category_B', 'attachments')


class QuestionNumberLineSerializer(serializers.ModelSerializer):
    """
    Question number line serializer.
    """
    attachments = AttachmentSerializer(many=True)
    hint = HintSerializer()

    class Meta:
        model = QuestionNumberLine
        fields = ('id', 'title', 'assessment_topic', 'hint',
                  'question_type', 'expected_value', 'start',
                  'end', 'step', 'show_value', 'show_ticks', 'attachments')
