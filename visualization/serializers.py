from rest_framework import serializers

from users.models import User
from assessments.models import Assessment, AssessmentTopic, Attachment, Question
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
            return None
        else:
            return last_session.start_date.strftime("%d %B %Y")

    def get_completed_topics_count(self, instance):
        return AssessmentTopic.objects.filter(
            assessmenttopicaccess__student=instance,
            assessmenttopicaccess__assessment_topic_answers__complete=True
        ).distinct().count()

    def get_assessments_count(self, instance):
        return Assessment.objects.filter(assessmenttopic__assessmenttopicaccess__student=instance).distinct().count()

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
    subject = serializers.SerializerMethodField()
    private = serializers.SerializerMethodField()

    # Languages and countries formatted information
    language_name = serializers.SerializerMethodField()
    language_code = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    country_code = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'language_name', 'language_code',
                  'country_name', 'country_code', 'topics_count',
                  'students_count', 'grade', 'subject', 'private')

    def get_topics_count(self, instance):
        return AssessmentTopic.objects.filter(assessment=instance).count()

    def get_students_count(self, instance):
        return User.objects.filter(assessmenttopicaccess__topic__assessment=instance).count()

    def get_language_name(self, instance):
        return instance.language.name_en

    def get_language_code(self, instance):
        return instance.language.code

    def get_country_name(self, instance):
        return instance.country.name_en

    def get_country_code(self, instance):
        return instance.country.code

    def get_subject(self, instance):
        return instance.get_subject_display()

    def get_private(self, instance):
        if (instance.private):
            return 'Yes'
        return 'No'


class AssessmentTopicTableSerializer(serializers.ModelSerializer):
    """
    Assessment topics table serializer.
    """

    # Total of students who have this topic
    students_count = serializers.SerializerMethodField()
    # Total of students who have this topic and completed it
    students_completed_count = serializers.SerializerMethodField()
    # Total of questions in this topic and completed it
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopic
        fields = ('id', 'name', 'students_count',
                  'students_completed_count', 'questions_count')

    def get_students_count(self, instance):
        return User.objects.filter(assessmenttopicaccess__topic=instance).distinct().count()

    def get_students_completed_count(self, instance):
        return User.objects.filter(
            assessmenttopicaccess__topic=instance,
            assessmenttopicaccess__assessment_topic_answers__complete=True,
        ).distinct().count()

    def get_questions_count(self, instance):
        return Question.objects.filter(assessment_topic=instance).count()



class QuestionTableSerializer(serializers.ModelSerializer):
    """
    Questions table serializer.
    """

    has_attachment = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'title', 'order', 'question_type',
                  'assessment_topic', 'has_attachment')

    def get_has_attachment(self, instance):
        if(Attachment.objects.filter(question=instance)):
            return 'Yes'
        return 'No'


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

    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()

    class Meta:
        model = AnswerSession
        fields = ('id', 'completed_topics_count', 'answered_questions_count',
                  'correct_answers_percentage', 'start_date', 'end_date')

    def get_completed_topics_count(self, instance):
        return AssessmentTopic.objects.filter(
            assessmenttopicaccess__assessment_topic_answers__session=instance,
            assessmenttopicaccess__assessment_topic_answers__complete=True
        ).distinct().count()
        

    def get_answered_questions_count(self, instance):
        return Answer.objects.filter(
            topic_answer__session=instance
        ).count()

    def get_correct_answers_percentage(self, instance):

        total_answers = self.get_answered_questions_count(instance)

        total_valid_answers = Answer.objects.filter(
            topic_answer__session=instance,
            valid=True
        ).count()

        correct_answers_percentage = None

        if total_answers:
            correct_answers_percentage = round(
                (100 * total_valid_answers / total_answers), 2)

        return correct_answers_percentage

    def get_start_date(self, instance):
        if (instance.start_date):
            return instance.start_date.strftime("%d %B %Y - %H:%M:%S")
        return None

    def get_end_date(self, instance):
        if (instance.end_date):
            return instance.end_date.strftime("%d %B %Y - %H:%M:%S")
        return None


class AssessmentAnswerTableSerializer(serializers.ModelSerializer):
    """
    Assessment answers serializer 
    """

    # Subject of the assessment in a readable format
    subject = serializers.SerializerMethodField()
    # Total of topics completed per assessment
    completed_topics_count = serializers.SerializerMethodField()
    # Total of topics accessible by the student
    accessible_topics_count = serializers.SerializerMethodField()

    # Languages and countries formatted information
    language_name = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'subject', 'language_name', 'country_name',
            'completed_topics_count', 'accessible_topics_count')

    def get_completed_topics_count(self, instance):
        student_pk = self.context['student_pk']
        session_pk = self.context['session_pk']

        if (session_pk):
            return AssessmentTopic.objects.filter(
                assessment=instance,
                assessmenttopicaccess__student=student_pk,
                assessmenttopicaccess__assessment_topic_answers__session=session_pk,
                assessmenttopicaccess__assessment_topic_answers__complete=True
            ).distinct().count()
        
        return AssessmentTopic.objects.filter(
            assessment=instance,
            assessmenttopicaccess__student=student_pk,
            assessmenttopicaccess__assessment_topic_answers__complete=True
        ).distinct().count()

    def get_accessible_topics_count(self, instance):
        student_pk = self.context['student_pk']

        return AssessmentTopic.objects.filter(
            assessmenttopicaccess__student=student_pk,
            assessment=instance).distinct().count()

    def get_subject(self, instance):
        return instance.get_subject_display()

    def get_language_name(self, instance):
        return instance.language.name_en

    def get_country_name(self, instance):
        return instance.country.name_en


class TopicAnswerTableSerializer(serializers.ModelSerializer):
    """
    Topic answer serializer
    """

    # Total number of questions
    total_questions_count = serializers.SerializerMethodField()
    # Total of questions answered
    answered_questions_count = serializers.SerializerMethodField()
    # Percentage of correct answers on total
    correct_answers_percentage = serializers.SerializerMethodField()

    id = serializers.SerializerMethodField()
    topic_name = serializers.SerializerMethodField()

    complete = serializers.SerializerMethodField()

    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopicAnswer
        fields = ('id', 'topic_name', 'complete', 'start_date', 'end_date',
                  'total_questions_count', 'answered_questions_count', 'correct_answers_percentage')

    def get_id(self, instance):
        return AssessmentTopic.objects.get(assessmenttopicaccess__assessment_topic_answers=instance).id

    def get_topic_name(self, instance):
        return AssessmentTopic.objects.get(assessmenttopicaccess__assessment_topic_answers=instance).name

    def get_total_questions_count(self, instance):
        return Question.objects.filter(assessment_topic__assessmenttopicaccess__assessment_topic_answers=instance).count()

    def get_answered_questions_count(self, instance):
        session_pk = self.context['session_pk']

        if (session_pk):
            answered_questions = Answer.objects.filter(
                topic_answer=instance,
                topic_answer__session=session_pk
            ).distinct().count()
        else:
            answered_questions = Answer.objects.filter(
                topic_answer=instance).distinct().count()

        return answered_questions

    def get_correct_answers_percentage(self, instance):
        session_pk = self.context['session_pk']

        total_answers = self.get_answered_questions_count(instance)
        total_valid_answers = None

        if (session_pk):
            total_valid_answers = Answer.objects.filter(
                topic_answer=instance,
                topic_answer__session=session_pk,
                valid=True).distinct().count()
            
        else:
            total_valid_answers = Answer.objects.filter(
                topic_answer=instance,
                valid=True).distinct().count()
            

        correct_answers_percentage = None

        if total_answers:
            correct_answers_percentage = round(
                (100 * total_valid_answers / total_answers), 2)

        return correct_answers_percentage

    def get_complete(self, instance):
        if(instance.complete):
            return 'Yes'
        return 'No'

    def get_start_date(self, instance):
        if (instance.start_date):
            return instance.start_date.strftime("%d %B %Y - %H:%M:%S")
        return None

    def get_end_date(self, instance):
        if (instance.end_date):
            return instance.end_date.strftime("%d %B %Y - %H:%M:%S")
        return None


class QuestionAnswerTableSerializer(serializers.ModelSerializer):
    """
    Question answer serializer
    """

    # Total number of questions
    question_type = serializers.SerializerMethodField()

    valid = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ('id', 'duration', 'valid', 'question_type')

    def get_question_type(self, instance):
        return instance.question.get_question_type_display()

    def get_valid(self, instance):
        if(instance.valid):
            return 'Yes'
        return 'No'
