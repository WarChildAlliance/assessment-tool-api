from rest_framework import serializers

from users.models import User, Language, Country
from assessments.models import Assessment, AssessmentTopic, Question
from answers.models import AnswerSession, AssessmentTopicAnswer, Answer


class UserTableSerializer(serializers.ModelSerializer):
    """
    Users table serializer.
    """

    # Student's full name
    full_name = serializers.SerializerMethodField()
    # Last session
    last_session = serializers.SerializerMethodField()
    # Number of topics completed by the student
    completed_topics_count = serializers.SerializerMethodField()
    # Number of assessments that the student is linked to
    assessments_count = serializers.SerializerMethodField()

    # Languages and countries formatted information
    language_name = serializers.SerializerMethodField()
    language_code = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    country_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'last_session', 'completed_topics_count',
                  'assessments_count', 'language_name', 'language_code', 'country_name', 'country_code')

    def get_full_name(self, instance):
        return (instance.first_name + ' ' + instance.last_name)

    def get_last_session(self, instance):

        last_session = AnswerSession.objects.filter(student=instance).last()
        if not last_session:
            return
        else:
            return last_session.start_date

    def get_completed_topics_count(self, instance):
        return len(AssessmentTopicAnswer.objects.filter(topic_access__student=instance, complete=True))

    def get_assessments_count(self, instance):
        return len(Assessment.objects.filter(assessmenttopic__assessmenttopicaccess__student=instance))

    def get_language_name(self, instance):
        return instance.language.name_en
        
    def get_language_code(self, instance):
        return instance.language.code

    def get_country_name(self, instance):
        return instance.country.name_en
    
    def get_country_code(self, instance):
        return instance.country.code


class AssessmentTableSerializer(serializers.ModelSerializer):
    """
    Assessment serializer for table.
    """
    topics_count = serializers.SerializerMethodField()
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('title', 'language', 'topics_count',
                  'students_count')

    def get_topics_count(self, instance):
        return len(AssessmentTopic.objects.filter(assessment=instance))

    def get_students_count(self, instance):
        return len(User.objects.filter(assessmenttopicaccess__topic__assessment=instance))


class AssessmentTopicTableSerializer(serializers.ModelSerializer):
    """
    Assessment topics table serializer.
    """

    # Total of students who have this topic
    students_count = serializers.SerializerMethodField()
    # Total of students who have this topic and completed it
    #students_completed_count = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopic
        fields = ('name', 'order',
                  'students_count')

    def get_students_count(self, instance):
        return len(User.objects.filter(assessmenttopicaccess__topic=instance))
    
    def students_completed_count(self, instance):
        return 2



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


class AssessmentAnswerTableSerializer(serializers.ModelSerializer):
    """
    Assessment answers serializer 
    """

    # Total of topics completed per assessment
    completed_topics_count = serializers.SerializerMethodField()
    # Total of topics accessible by the student
    accessible_topics_count = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('completed_topics_count', 'accessible_topics_count', 'title', 'language', 'country')

    def get_completed_topics_count(self, instance):
        student_pk = self.context['request']
        print('2')
        print(student_pk)
        return 2
    
    def get_accessible_topics_count(self, instance):
        return 13


class TopicAnswerTableSerializer(serializers.ModelSerializer):
    """
    Topic answer serializer
    """

    # Total number of questions
    total_question_count = serializers.SerializerMethodField()
    # Total of questions answered
    answered_questions_count = serializers.SerializerMethodField()
    # Percentage of correct answers on total
    correct_answers_percentage = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopicAnswer
        fields = ('complete', 'start_date', 'end_date', 'total_question_count', 'answered_questions_count', 'correct_answers_percentage')

    def get_total_question_count(self, instance):
        return len(Question.objects.filter(assessment_topic__topic_access__topic_answer=instance))
    
    def get_answered_questions_count(self, instance):
        return len(Answer.objects.filter(topic_answer=instance))

    def get_correct_answers_percentage(self, instance):

        total_answers = self.get_answered_questions_count(instance)
        total_valid_answers = len(Answer.objects.filter(topic_answer=instance, valid=True))
        correct_answers_percentage = 100 * total_valid_answers / total_answers

        return correct_answers_percentage


class QuestionAnswerTableSerializer(serializers.ModelSerializer):

    #Stuff

    class Meta:
        model = Answer
        fields = ('valid')
