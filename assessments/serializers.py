from rest_framework import serializers
from users.models import User
from users.serializers import UserSerializer

from admin.lib.serializers import NestedRelatedField, PolymorphicSerializer

from .models import (Assessment, AssessmentTopic, AssessmentTopicAccess,
                     Attachment, Hint, Question, QuestionInput,
                     QuestionNumberLine, QuestionSelect, QuestionSort,
                     SelectOption, SortOption)


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Attachment serializer.
    """

    class Meta:
        model = Attachment
        fields = ('id', 'attachment_type', 'link')


class AssessmentSerializer(serializers.ModelSerializer):
    """
    Assessment serializer.
    """

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'grade', 'subject',
                  'language', 'country', 'private', 'created_by')
        extra_kwargs = {'created_by': {
            'default': serializers.CurrentUserDefault(),
            'write_only': True
        }}


class AssessmentTopicSerializer(serializers.ModelSerializer):
    """
    Assessment topic serializer.
    """
    attachments = AttachmentSerializer(many=True, required=False)

    class Meta:
        model = AssessmentTopic
        fields = '__all__'

    def to_internal_value(self, data):
        data = data.copy()
        kwargs = self.context['request'].parser_context['kwargs']
        if 'assessment' not in data:
            data['assessment'] = kwargs.get('assessment_pk', None)
        return super().to_internal_value(data)


class HintSerializer(serializers.ModelSerializer):
    """
    Hint serializer.
    """
    attachments = AttachmentSerializer(many=True, required=False)

    class Meta:
        model = Hint
        fields = ('text', 'attachments', 'question')
        extra_kwargs = {'question': {
            'required': False,
            'write_only': True
        }}

    def create(self, validated_data):
        """
        Create hint with attachments.
        """
        if validated_data['question'] is None:
            raise serializers.ValidationError({
                'question': 'This field is required',
            })

        attachments_data = validated_data.pop(
            'attachments') if 'attachments' in validated_data else None

        hint = super().create(validated_data)

        if attachments_data is not None:
            for attachment_data in attachments_data:
                Attachment.objects.create(
                    hint=hint, **attachment_data)

        return hint


class SelectOptionSerializer(serializers.ModelSerializer):
    """
    Select option serializer.
    """
    attachments = AttachmentSerializer(many=True, required=False)

    class Meta:
        model = SelectOption
        fields = ('id', 'value', 'valid', 'attachments', 'question_select')
        extra_kwargs = {'question_select': {
            'required': False,
            'write_only': True
        }}

    def create(self, validated_data):
        """
        Create select option with attachments.
        """
        if validated_data['question_select'] is None:
            raise serializers.ValidationError({
                'question_select': 'This field is required',
            })

        attachments_data = validated_data.pop(
            'attachments') if 'attachments' in validated_data else None

        select_option = super().create(validated_data)

        if attachments_data is not None:
            for attachment_data in attachments_data:
                Attachment.objects.create(
                    select_option=select_option, **attachment_data)

        return select_option


class SortOptionSerializer(serializers.ModelSerializer):
    """
    Sort option serializer.
    """
    attachments = AttachmentSerializer(many=True, required=False)

    class Meta:
        model = SortOption
        fields = ('id', 'value', 'category', 'attachments', 'question_sort')
        extra_kwargs = {'question_sort': {
            'required': False,
            'write_only': True
        }}

    def create(self, validated_data):
        """
        Create select option with attachments.
        """
        if validated_data['question_sort'] is None:
            raise serializers.ValidationError({
                'question_sort': 'This field is required',
            })

        attachments_data = validated_data.pop(
            'attachments') if 'attachments' in validated_data else None

        sort_option = super().create(validated_data)

        if attachments_data is not None:
            for attachment_data in attachments_data:
                Attachment.objects.create(
                    sort_option=sort_option, **attachment_data)

        return sort_option


class QuestionSerializer(PolymorphicSerializer):
    """
    Question serializer.
    """

    class Meta:
        model = Question
        fields = '__all__'

    def get_serializer_map(self):
        return {
            'QuestionInput': QuestionInputSerializer,
            'QuestionNumberLine': QuestionNumberLineSerializer,
            'QuestionSelect': QuestionSelectSerializer,
            'QuestionSort': QuestionSortSerializer
        }

    def to_internal_value(self, data):
        data = data.copy()
        type_dict = {
            Question.QuestionType.INPUT: 'QuestionInput',
            Question.QuestionType.SELECT: 'QuestionSelect',
            Question.QuestionType.SORT: 'QuestionSort',
            Question.QuestionType.NUMBER_LINE: 'QuestionNumberLine'
        }
        if 'question_type' in data and data['question_type'] in type_dict:
            data['type'] = type_dict[data['question_type']]
        elif self.instance:
            data['type'] = type_dict[self.instance.question_type]
        else:
            raise serializers.ValidationError({
                'question_type': 'Unkown question type',
            })

        kwargs = self.context['request'].parser_context['kwargs']
        if 'assessment_topic' not in data:
            data['assessment_topic'] = kwargs.get('topic_pk', None)
        return super().to_internal_value(data)


class AbstractQuestionSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, required=False)
    hint = HintSerializer(required=False, allow_null=True)

    def create(self, validated_data):
        """
        Create question with hint and attachments.
        """
        hint_data = validated_data.pop(
            'hint') if 'hint' in validated_data else None
        attachments_data = validated_data.pop(
            'attachments') if 'attachments' in validated_data else None

        question = super().create(validated_data)

        if hint_data is not None:
            hint_serializer = HintSerializer(
                data={**hint_data, 'question': question.id})
            hint_serializer.is_valid(raise_exception=True)
            hint_serializer.save()

        if attachments_data is not None:
            for attachment_data in attachments_data:
                Attachment.objects.create(**attachment_data, question=question)

        return question

    def update(self, instance, validated_data):
        """
        Update question with hint and attachments.
        """
        instance.title = validated_data.get('title', instance.title)

        new_question_type = validated_data.get('question_type', None)
        if new_question_type is not None and new_question_type != instance.question_type:
            if instance.question_type == Question.QuestionType.INPUT:
                QuestionInput.objects.get(id=instance.id).delete()
            elif instance.question_type == Question.QuestionType.SELECT:
                QuestionSelect.objects.get(id=instance.id).delete()
            elif instance.question_type == Question.QuestionType.SORT:
                QuestionSort.objects.get(id=instance.id).delete()
            elif instance.question_type == Question.QuestionType.NUMBER_LINE:
                QuestionNumberLine.objects.get(id=instance.id).delete()
            instance.question_type = new_question_type

        if 'attachments' in validated_data:
            instance.attachments.clear()
            for attachment_data in validated_data.get('attachments', []):
                Attachment.objects.create(**attachment_data, question=instance)
            validated_data.pop('attachments')

        if 'hint' in validated_data:
            if hasattr(instance, 'hint'):
                instance.hint.delete()
            elif validated_data['hint'] is not None:
                hint_serializer = HintSerializer(
                    instance.hint,
                    data={**validated_data['hint'], 'question': instance.id})
                hint_serializer.is_valid(raise_exception=True)
                hint_serializer.save()
            validated_data.pop('hint')

        return super().update(instance, validated_data)


class QuestionInputSerializer(AbstractQuestionSerializer):
    """
    Question input serializer.
    """

    class Meta:
        model = QuestionInput
        fields = ('id', 'title', 'assessment_topic', 'hint',
                  'question_type', 'valid_answer', 'attachments')


class QuestionSelectSerializer(AbstractQuestionSerializer):
    """
    Question select serializer.
    """
    options = SelectOptionSerializer(many=True)

    class Meta:
        model = QuestionSelect
        fields = ('id', 'title', 'assessment_topic', 'options',
                  'question_type', 'multiple', 'attachments', 'hint')

    def create(self, validated_data):
        """
        Create question select with options.
        """
        options_data = validated_data.pop(
            'options') if 'options' in validated_data else None

        question = super().create(validated_data)

        if options_data is not None:
            for option_data in options_data:
                select_option_serializer = SelectOptionSerializer(
                    data={**option_data, 'question_select': question.id})
                select_option_serializer.is_valid(raise_exception=True)
                select_option_serializer.save()

        return question

    def update(self, instance, validated_data):
        """
        Update question select with options.
        """
        instance_class = instance.__class__.__name__

        if 'options' in validated_data:
            if instance_class == 'QuestionSelect':
                instance.options.clear()
            for option_data in validated_data.get('options', []):
                select_option_serializer = SelectOptionSerializer(
                    data={**option_data, 'question_select': instance.id})
                select_option_serializer.is_valid(raise_exception=True)
                select_option_serializer.save()
            validated_data.pop('options')

        return super().update(instance, validated_data)


class QuestionSortSerializer(AbstractQuestionSerializer):
    """
    Question sort serializer.
    """
    options = SortOptionSerializer(many=True)

    class Meta:
        model = QuestionSort
        fields = ('id', 'title', 'assessment_topic', 'options', 'hint',
                  'question_type', 'category_A', 'category_B', 'attachments')

    def create(self, validated_data):
        """
        Create question select with options.
        """
        options_data = validated_data.pop(
            'options') if 'options' in validated_data else None

        question = super().create(validated_data)

        if options_data is not None:
            for option_data in options_data:
                sort_option_serializer = SortOptionSerializer(
                    data={**option_data, 'question_sort': question.id})
                sort_option_serializer.is_valid(raise_exception=True)
                sort_option_serializer.save()

        return question

    def update(self, instance, validated_data):
        """
        Update question select with options.
        """
        instance_class = instance.__class__.__name__

        if 'options' in validated_data:
            if instance_class == 'QuestionSelect':
                instance.options.clear()
            for option_data in validated_data.get('options', []):
                sort_option_serializer = SortOptionSerializer(
                    data={**option_data, 'question_sort': instance.id})
                sort_option_serializer.is_valid(raise_exception=True)
                sort_option_serializer.save()
            validated_data.pop('options')

        return super().update(instance, validated_data)


class QuestionNumberLineSerializer(AbstractQuestionSerializer):
    """
    Question number line serializer.
    """

    class Meta:
        model = QuestionNumberLine
        fields = ('id', 'title', 'assessment_topic', 'hint',
                  'question_type', 'expected_value', 'start',
                  'end', 'step', 'show_value', 'show_ticks', 'attachments')


class AssessmentTopicAccessListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        to_create = []
        to_update = []
        for item in validated_data:
            try:
                obj = AssessmentTopicAccess.objects.get(
                    student=item['student'], topic=item['topic'])
                obj.start_date = item['start_date']
                obj.end_date = item['end_date']
                to_update.append(obj)
            except AssessmentTopicAccess.DoesNotExist:
                to_create.append(AssessmentTopicAccess(**item))

        created = AssessmentTopicAccess.objects.bulk_create(to_create)
        AssessmentTopicAccess.objects.bulk_update(
            to_update, ['start_date', 'end_date'])
        return (created if created is not None else []) + to_update


class AssessmentTopicAccessSerializer(serializers.ModelSerializer):
    """
    Assessment topic access serializer.
    """
    topic = NestedRelatedField(
        model=AssessmentTopic, serializer_class=AssessmentTopicSerializer)
    student = NestedRelatedField(
        model=User, serializer_class=UserSerializer)

    class Meta:
        model = AssessmentTopicAccess
        fields = '__all__'
        list_serializer_class = AssessmentTopicAccessListSerializer
