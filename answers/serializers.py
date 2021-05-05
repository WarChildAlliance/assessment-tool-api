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

class AnswerSessionTableSerializer(serializers.ModelSerializer):
    """
    Answer sessions serializer
    """

    # Total of topics completed
    completed_topics_count = serializers.SerializerMethodField()
    # Total of questions answered
    answered_questions_count = serializers.SerializerMethodField()
    # Percentage of correct answers on total
    correct_answers_percentage = serializers.SerializerMethodField()

    class Meta:
        model = AnswerSession
        fields = ('completed_topics_count', 'answered_questions_count', 'correct_answers_percentage', 'end_date', 'start_date')

    def get_completed_topics_count(self, instance):
        return len(AssessmentTopicAnswer.objects.filter(session__student=instance.student, complete=True))

    def get_answered_questions_count(self, instance):
        return len(Answer.objects.filter(topic_answer__topic_access__student=instance.student))

    def get_correct_answers_percentage(self, instance):

        total_answers = self.get_answered_questions_count(instance)
        total_valid_answers = len(Answer.objects.filter(topic_answer__topic_access__student=instance.student, valid=True))
        correct_answers_percentage = 100 * total_valid_answers / total_answers

        return correct_answers_percentage

class AssessmentTopicAnswerTableSerializer(serializers.ModelSerializer):
    """
    Answer sessions serializer
    """

    # TODO : finish this
    # Assessment name
    assessment_name = serializers.SerializerMethodField()
    # Total of topics completed per assessment
    completed_topics_count = serializers.SerializerMethodField()
    # Total of questions answered per assessment
    answered_questions_count = serializers.SerializerMethodField()
    # Percentage of correct answers on total per assessment 
    correct_answers_percentage = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopicAnswer
        fields = ('completed_topics_count', 'answered_questions_count', 'correct_answers_percentage', 'assessment_name')

    def get_completed_topics_count(self, instance):
        return len(AssessmentTopicAnswer.objects.filter(complete=True))

    def get_answered_questions_count(self, instance):
        return len(Answer.objects.filter(topic_answer__topic_access__student=instance.student))

    def get_correct_answers_percentage(self, instance):

        total_answers = self.get_answered_questions_count(instance)
        total_valid_answers = len(Answer.objects.filter(topic_answer__topic_access__student=instance.student, valid=True))
        correct_answers_percentage = 100 * total_valid_answers / total_answers

        return correct_answers_percentage

    def get_assessment_name(self, instance):
        return 'Im tired'
