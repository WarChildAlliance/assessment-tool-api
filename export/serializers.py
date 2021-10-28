from answers.models import Answer
from rest_framework import serializers
from admin.lib.serializers import NestedRelatedField, PolymorphicSerializer
from assessments.models import Question, Assessment, SelectOption, SortOption
from answers.models import AssessmentTopicAnswer, AnswerInput, AnswerNumberLine, AnswerSelect, AnswerSort

class AnswerTableSerializer(PolymorphicSerializer):

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

class CompleteStudentAnswersSerializer(serializers.ModelSerializer):

    student_id = serializers.SerializerMethodField()
    topic_name = serializers.SerializerMethodField()
    assessment_title = serializers.SerializerMethodField()
    question_id = serializers.SerializerMethodField()
    attempt = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ('student_id','assessment_title', 'topic_name', 'question_id','attempt','valid', 'start_datetime', 'end_datetime')

    def get_student_id(self, instance):
        return instance.topic_answer.topic_access.student.username

    def get_assessment_title(self, instance):
        topic = instance.topic_answer.topic_access.topic
        return Assessment.objects.filter(assessmenttopic=topic).distinct().values()[0]['title']
    
    def get_topic_name(self, instance):
        return instance.topic_answer.topic_access.topic.name
    
    def get_question_id(self, instance):
        return instance.question.identifier
    
    def get_attempt(self, instance):
        attempts = AssessmentTopicAnswer.objects.filter(topic_access=instance.topic_answer.topic_access).order_by('start_date')
        for index, attempt in enumerate(attempts):
            if attempt == instance.topic_answer:
                attempt_id = index + 1
        return attempt_id

class AnswerInputSerializer(CompleteStudentAnswersSerializer):
    """
    Answer input serializer.
    """

    class Meta(CompleteStudentAnswersSerializer.Meta):
        model = AnswerInput
        fields = CompleteStudentAnswersSerializer.Meta.fields + ('value',)


class SelectOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SelectOption
        fields = ('identifier',)

class AnswerSelectSerializer(CompleteStudentAnswersSerializer):
    """
    Answer select serializer.
    """

    selected_options = NestedRelatedField(
        model=SelectOption, serializer_class=SelectOptionSerializer, many=True, required=False)

    class Meta(CompleteStudentAnswersSerializer.Meta):
        model = AnswerSelect
        fields = CompleteStudentAnswersSerializer.Meta.fields + ('selected_options',)


class AnswerNumberLineSerializer(CompleteStudentAnswersSerializer):
    """
    Answer number line serializer.
    """

    class Meta(CompleteStudentAnswersSerializer.Meta):
        model = AnswerNumberLine
        fields = CompleteStudentAnswersSerializer.Meta.fields + ('value',)

class SortOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SortOption
        fields = ('value',)

class AnswerSortSerializer(CompleteStudentAnswersSerializer):
    """
    Answer sort line serializer.
    """

    category_A = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True, required=False)
    category_B = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True, required=False)

    class Meta(CompleteStudentAnswersSerializer.Meta):
        model = AnswerSort
        fields = CompleteStudentAnswersSerializer.Meta.fields + \
            ('category_A', 'category_B',)