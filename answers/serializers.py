from assessments.models import (AssessmentTopicAccess, Question, QuestionInput,
                                SelectOption, SortOption)
from assessments.serializers import (AssessmentTopicAccessSerializer,
                                     SelectOptionSerializer,
                                     SortOptionSerializer)
from rest_framework import serializers
from rest_framework.utils import model_meta
from users.models import User
from users.serializers import UserSerializer

from admin.lib.serializers import NestedRelatedField, PolymorphicSerializer

from .models import (Answer, AnswerInput, AnswerNumberLine, AnswerSelect,
                     AnswerSession, AnswerSort, AssessmentTopicAnswer)


class AssessmentTopicAnswerSerializer(serializers.ModelSerializer):
    """
    Assessment topic answer serializer.
    """

    class Meta:
        model = AssessmentTopicAnswer
        fields = '__all__'


class AnswerSessionSerializer(serializers.ModelSerializer):
    """
    Answer session serializer.
    """

    class Meta:
        model = AnswerSession
        fields = '__all__'


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


    def to_representation(self, obj):
        sub_obj = Answer.objects.get_subclass(id=obj.id)
        return super().to_representation(sub_obj)


class AbstractAnswerSerializer(serializers.ModelSerializer):
    """
    Abstract serializer for Answer models.
    """

    class Meta:
        model = Answer
        fields = ('topic_answer', 'question', 'duration', 'valid')
        extra_kwargs = {'topic_answer': {'required': False}}

    def create(self, validated_data):
        """
        Create answer, checking that topic_answer exists
        """

        if 'topic_answer' not in validated_data or validated_data['topic_answer'] is None:
            raise serializers.ValidationError({
                'topic_answer': 'This field is required',
            })

        answer = super().create(validated_data)
        return answer


class AnswerInputSerializer(AbstractAnswerSerializer):
    """
    Answer input serializer.
    """

    class Meta(AbstractAnswerSerializer.Meta):
        model = AnswerInput
        fields = AbstractAnswerSerializer.Meta.fields + ('value',)


class AnswerSelectSerializer(AbstractAnswerSerializer):
    """
    Answer select serializer.
    """
    selected_options = NestedRelatedField(
        model=SelectOption, serializer_class=SelectOptionSerializer, many=True)

    class Meta(AbstractAnswerSerializer.Meta):
        model = AnswerSelect
        fields = AbstractAnswerSerializer.Meta.fields + ('selected_options',)


class AnswerSortSerializer(AbstractAnswerSerializer):
    """
    Answer sort serializer.
    """
    category_A = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True)
    category_B = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True)

    class Meta(AbstractAnswerSerializer.Meta):
        model = AnswerSort
        fields = AbstractAnswerSerializer.Meta.fields + \
            ('category_A', 'category_B',)


class AnswerNumberLineSerializer(AbstractAnswerSerializer):
    """
    Answer number line serializer.
    """

    class Meta(AbstractAnswerSerializer.Meta):
        model = AnswerNumberLine
        fields = AbstractAnswerSerializer.Meta.fields + ('value',)


class AssessmentTopicAnswerFullSerializer(serializers.ModelSerializer):
    """
    Assessment topic answer serializer.
    """

    topic_access = NestedRelatedField(
        model=AssessmentTopicAccess, serializer_class=AssessmentTopicAccessSerializer)
    answers = AnswerSerializer(many=True)

    class Meta:
        model = AssessmentTopicAnswer
        fields = '__all__'
        extra_kwargs = {'session': {'required': False}}

    def create(self, validated_data):
        """
        Create assessment topic answer with answers.
        """
        if 'answers' in validated_data:
            validated_data.pop('answers')
            answers = self.initial_data['answers']

        topic_answer = super().create(validated_data)

        if answers is not None:
            for answer in answers:
                answer_serializer = AnswerSerializer(
                    data={**answer, 'topic_answer': topic_answer.id})
                answer_serializer.is_valid(raise_exception=True)
                answer_serializer.save()

        return topic_answer


class AnswerSessionFullSerializer(serializers.ModelSerializer):
    """
    Answer session full serializer (with topic and answers).
    """
    assessment_topic_answers = AssessmentTopicAnswerFullSerializer(many=True)
    student = NestedRelatedField(
        model=User, serializer_class=UserSerializer)

    class Meta:
        model = AnswerSession
        fields = '__all__'

    def create(self, validated_data):
        """
        Create session with assessment topic answers.
        """
        if 'assessment_topic_answers' in validated_data:
            validated_data.pop('assessment_topic_answers')
            assessment_topic_answers = self.initial_data['assessment_topic_answers']

        session = super().create(validated_data)

        if assessment_topic_answers is not None:
            for topic_answer in assessment_topic_answers:
                topic_answer_serializer = AssessmentTopicAnswerFullSerializer(
                    data={**topic_answer, 'session': session.id})
                topic_answer_serializer.is_valid(raise_exception=True)
                topic_answer_serializer.save()

        return session

