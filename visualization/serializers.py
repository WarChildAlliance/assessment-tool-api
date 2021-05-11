from rest_framework import serializers

from users.models import User
from assessments.models import Assessment, AssessmentTopic, AssessmentTopicAccess, Question
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

    # Languages and countries formatted information
    language_name = serializers.SerializerMethodField()
    language_code = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    country_code = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('title', 'language_name', 'language_code',
            'country_name', 'country_code', 'topics_count',
            'students_count')

    def get_topics_count(self, instance):
        return len(AssessmentTopic.objects.filter(assessment=instance))

    def get_students_count(self, instance):
        return len(User.objects.filter(assessmenttopicaccess__topic__assessment=instance))

    def get_language_name(self, instance):
        return instance.language.name_en

    def get_language_code(self, instance):
        return instance.language.code

    def get_country_name(self, instance):
        return instance.country.name_en

    def get_country_code(self, instance):
        return instance.country.code


class AssessmentTopicTableSerializer(serializers.ModelSerializer):
    """
    Assessment topics table serializer.
    """

    # Total of students who have this topic
    students_count = serializers.SerializerMethodField()
    # Total of students who have this topic and completed it
    students_completed_count = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopic
        fields = ('name', 'order',
                  'students_count', 'students_completed_count')

    def get_students_count(self, instance):
        return len(User.objects.filter(assessmenttopicaccess__topic=instance).distinct())

    def get_students_completed_count(self, instance):
        return len(User.objects.filter(
            assessmenttopicaccess__topic=instance,
            assessmenttopicaccess__assessment_topic_answers__complete=True,
        ).distinct())


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
        fields = ('completed_topics_count', 'answered_questions_count',
                  'correct_answers_percentage', 'end_date', 'start_date')

    # TODO make this works with the session instance
    def get_completed_topics_count(self, instance):
        return len(AssessmentTopicAnswer.objects.filter(
            session__student=instance.student,
            session=instance,
            complete=True
        ))

    def get_answered_questions_count(self, instance):
        return len(Answer.objects.filter(
            topic_answer__session__student=instance.student,
            topic_answer__session=instance
        ))

    def get_correct_answers_percentage(self, instance):

        total_answers = self.get_answered_questions_count(instance)

        total_valid_answers = len(Answer.objects.filter(
            topic_answer__session__student=instance.student,
            topic_answer__session=instance,
            valid=True
        ))

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
    # Total of topics completed per assessment
    uncompleted_topics_count = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('title', 'language', 'country', 'completed_topics_count',
                  'uncompleted_topics_count', 'accessible_topics_count')

    def get_completed_topics_count(self, instance):  # For sessions and not
        student_pk = self.context['student_pk']
        session_pk = self.context['session_pk']

        if (session_pk):
            return len(AssessmentTopicAnswer.objects.filter(
                session__student=student_pk,
                session=session_pk,
                topic_access__topic__assessment=instance,
                complete=True
            ))

        return len(AssessmentTopicAnswer.objects.filter(
            session__student=student_pk,
            topic_access__topic__assessment=instance,
            complete=True
        ))

    def get_uncompleted_topics_count(self, instance):  # Only for sessions
        student_pk = self.context['student_pk']
        session_pk = self.context['session_pk']

        if (session_pk):
            return len(AssessmentTopicAnswer.objects.filter(
                session__student=student_pk,
                session=session_pk,
                topic_access__topic__assessment=instance,
                complete=False
            ))

        return None

    def get_accessible_topics_count(self, instance):  # Only not sessions
        student_pk = self.context['student_pk']
        session_pk = self.context['session_pk']

        if (session_pk):
            return None

        return len(AssessmentTopicAccess.objects.filter(student=student_pk, topic__assessment=instance))


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
    # Percentage of correct answers on total
    topic_name = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopicAnswer
        fields = ('topic_name', 'complete', 'start_date', 'end_date',
                  'total_questions_count', 'answered_questions_count', 'correct_answers_percentage')

    def get_topic_name(self, instance):
        return AssessmentTopic.objects.get(assessmenttopicaccess__assessment_topic_answers=instance).name

    def get_total_questions_count(self, instance):
        return len(Question.objects.filter(assessment_topic__assessmenttopicaccess__assessment_topic_answers=instance))

    def get_answered_questions_count(self, instance):
        student_pk = self.context['student_pk']
        session_pk = self.context['session_pk']

        if (session_pk):
            answered_questions = len(Answer.objects.filter(
                topic_answer=instance,
                topic_answer__session=session_pk
            ).distinct())
        else:
            answered_questions = len(Answer.objects.filter(
                topic_answer=instance).distinct())

        return answered_questions

    def get_correct_answers_percentage(self, instance):
        student_pk = self.context['student_pk']
        session_pk = self.context['session_pk']

        total_answers = self.get_answered_questions_count(instance)
        total_valid_answers = None

        if (session_pk):
            total_valid_answers = len(Answer.objects.filter(
                topic_answer=instance,
                topic_answer__session=session_pk,
                valid=True).distinct()
            )
        else:
            total_valid_answers = len(Answer.objects.filter(
                topic_answer=instance,
                valid=True).distinct()
            )

        correct_answers_percentage = None

        if total_answers:
            correct_answers_percentage = 100 * total_valid_answers / total_answers

        return correct_answers_percentage


class QuestionAnswerTableSerializer(serializers.ModelSerializer):
    """
    Question answer serializer
    """

    # Total number of questions
    question_type = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ('id', 'duration', 'valid', 'question_type')

    def get_question_type(self, instance):
        return instance.question.get_question_type_display()
