from answers.models import Answer
from rest_framework import serializers
from admin.lib.serializers import NestedRelatedField, PolymorphicSerializer
from assessments.models import Question, Assessment
from answers.models import AssessmentTopicAnswer


class CompleteStudentAnswersSerializer(serializers.ModelSerializer):

    student_id = serializers.SerializerMethodField()
    topic_name = serializers.SerializerMethodField()
    assessment_title = serializers.SerializerMethodField()
    question_id = serializers.SerializerMethodField()
    attempt = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ('student_id','topic_name', 'assessment_title', 'question_id','attempt','valid', 'start_datetime', 'end_datetime')

    def get_student_id(self, instance):
        return instance.topic_answer.topic_access.student.id
    
    def get_topic_name(self, instance):
        return instance.topic_answer.topic_access.topic.name
    
    def get_assessment_title(self, instance):
        topic = instance.topic_answer.topic_access.topic
        return Assessment.objects.filter(assessmenttopic=topic).distinct().values()[0]['title']
    
    def get_question_id(self, instance):
        return instance.question.id
    
    def get_attempt(self, instance):
        attempts = AssessmentTopicAnswer.objects.filter(topic_access=instance.topic_answer.topic_access).order_by('start_date')
        for index, attempt in enumerate(attempts):
            if attempt == instance.topic_answer:
                attempt_id = index + 1
        return attempt_id
