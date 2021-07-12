from rest_framework import serializers
import datetime
from admin.lib.serializers import NestedRelatedField, PolymorphicSerializer

from answers.models import AnswerSession, AssessmentTopicAnswer, Answer, AnswerInput, AnswerNumberLine, AnswerSelect, AnswerSort

from assessments.models import Assessment, AssessmentTopic, AssessmentTopicAccess, Attachment, Question, QuestionInput, QuestionNumberLine, QuestionSelect, QuestionSort, SelectOption, SortOption, Hint
from assessments.serializers import SelectOptionSerializer, SortOptionSerializer, HintSerializer, AttachmentSerializer

from users.models import User


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
        fields = ('id', 'username', 'full_name', 'last_session', 'completed_topics_count',
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
        return AssessmentTopic.objects.filter(
            assessmenttopicaccess__student=instance,
            assessmenttopicaccess__assessment_topic_answers__complete=True
        ).distinct().count()

    def get_assessments_count(self, instance):
        return Assessment.objects.filter(
            assessmenttopic__assessmenttopicaccess__student=instance,
            assessmenttopic__assessmenttopicaccess__start_date__lte=datetime.date.today(),
            assessmenttopic__assessmenttopicaccess__end_date__gte=datetime.date.today()
        ).distinct().count()

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

    # Total number of topics for this assessment
    topics_count = serializers.SerializerMethodField()
    # Total number of students who have an active access to this assessment
    students_count = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()

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
        return User.objects.filter(
            assessmenttopicaccess__topic__assessment=instance,
            assessmenttopicaccess__start_date__lte=datetime.date.today(),
            assessmenttopicaccess__end_date__gte=datetime.date.today()
        ).distinct().count()

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


class AssessmentTopicTableSerializer(serializers.ModelSerializer):
    """
    Assessment topics table serializer.
    """

    # Total of students with active access to this topic
    students_count = serializers.SerializerMethodField()
    # Total of students with active access to this topic and who completed it
    students_completed_count = serializers.SerializerMethodField()
    # Total of students who completed this topic
    overall_students_completed_count = serializers.SerializerMethodField()
    # Total of questions in this topic
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopic
        fields = ('id', 'name', 'students_count', 'students_completed_count',
        'overall_students_completed_count', 'questions_count')

    def get_students_count(self, instance):
        return User.objects.filter(
            assessmenttopicaccess__topic=instance,
            assessmenttopicaccess__start_date__lte=datetime.date.today(),
            assessmenttopicaccess__end_date__gte=datetime.date.today()
        ).distinct().count()

    def get_students_completed_count(self, instance):
        return User.objects.filter(
            assessmenttopicaccess__topic=instance,
            assessmenttopicaccess__start_date__lte=datetime.date.today(),
            assessmenttopicaccess__end_date__gte=datetime.date.today(),
            assessmenttopicaccess__assessment_topic_answers__complete=True,
        ).distinct().count()

    def get_overall_students_completed_count(self, instance):
        return User.objects.filter(assessmenttopicaccess__topic=instance).distinct().count()

    def get_questions_count(self, instance):
        return Question.objects.filter(assessment_topic=instance).count()


class QuestionTableSerializer(serializers.ModelSerializer):
    """
    Questions table serializer.
    """

    has_attachment = serializers.SerializerMethodField()
    question_type = serializers.SerializerMethodField()
    # Overall percentage of correct answers on this question
    correct_answers_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'title', 'order', 'question_type',
                  'has_attachment', 'correct_answers_percentage')

    def get_has_attachment(self, instance):
        if(Attachment.objects.filter(question=instance)):
            return True
        return False

    def get_question_type(self, instance):
        return instance.get_question_type_display()
        
    def get_correct_answers_percentage(self, instance):
        
        total_answers = Answer.objects.filter(
            question=instance
        ).count()

        total_valid_answers = Answer.objects.filter(
            question=instance,
            valid=True
        ).count()

        correct_answers_percentage = None

        if total_answers:
            correct_answers_percentage = round(
                (100 * total_valid_answers / total_answers), 2)

        return correct_answers_percentage

class QuestionDetailsTableSerializer(PolymorphicSerializer):

    class Meta:
        model = Question
        fields = '__all__'
    
    def get_serializer_map(self):
        return {
            'QuestionInput': QuestionInputTableSerializer,
            'QuestionNumberLine': QuestionNumberLineTableSerializer,
            'QuestionSelect': QuestionSelectTableSerializer,
            'QuestionSort': QuestionSortTableSerializer
        }


class AbstractQuestionDetailsTableSerializer(serializers.ModelSerializer):

    hint = NestedRelatedField(model=Hint, serializer_class=HintSerializer, many=False)
    attachments = NestedRelatedField(model=Attachment, serializer_class=AttachmentSerializer, many=True)

    class Meta:
        model = Question
        fields = ('title', 'order', 'question_type', 'hint', 'attachments')


class QuestionInputTableSerializer(AbstractQuestionDetailsTableSerializer):

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionInput
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + ('valid_answer',)   

class QuestionNumberLineTableSerializer(AbstractQuestionDetailsTableSerializer):

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionNumberLine
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + ('expected_value', 'start', 'end', 'step', 'show_ticks', 'show_value',)

class QuestionSelectTableSerializer(AbstractQuestionDetailsTableSerializer):

    options = NestedRelatedField(model=SelectOption, serializer_class=SelectOptionSerializer, many=True)
    
    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionSelect
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + ('options',)


class QuestionSortTableSerializer(AbstractQuestionDetailsTableSerializer):

    options = NestedRelatedField(model=SortOption, serializer_class=SortOptionSerializer, many=True)

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionSort
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + ('category_A', 'category_B', 'options',)
        
class AnswerSessionTableSerializer(serializers.ModelSerializer):
    """
    Answer sessions serializer
    """

    # Total of completed topics for this session
    completed_topics_count = serializers.SerializerMethodField()
    # Total of answered questions for this session
    answered_questions_count = serializers.SerializerMethodField()
    # Total of correctly answered questions for this session
    correctly_answered_questions_count = serializers.SerializerMethodField()
    # Overall percentage of correct answers for this session
    correct_answers_percentage = serializers.SerializerMethodField()

    class Meta:
        model = AnswerSession
        fields = ('id', 'completed_topics_count', 'answered_questions_count', 'correctly_answered_questions_count',
                  'correct_answers_percentage', 'start_date', 'end_date')

    def get_completed_topics_count(self, instance):
        return AssessmentTopic.objects.filter(
            assessmenttopicaccess__assessment_topic_answers__session=instance,
            assessmenttopicaccess__assessment_topic_answers__complete=True
        ).distinct().count()
        
    def get_answered_questions_count(self, instance):
        return Answer.objects.filter(
            question__assessment_topic__evaluated=True,
            topic_answer__session=instance
        ).count()

    def get_correctly_answered_questions_count(self, instance):
        return Answer.objects.filter(
            topic_answer__session=instance,
            valid=True
        ).count()

    def get_correct_answers_percentage(self, instance):

        total_answers = self.get_answered_questions_count(instance)

        total_valid_answers = Answer.objects.filter(
            question__assessment_topic__evaluated=True,
            topic_answer__session=instance,
            valid=True
        ).count()

        correct_answers_percentage = None

        if total_answers:
            correct_answers_percentage = round(
                (100 * total_valid_answers / total_answers), 2)

        return correct_answers_percentage

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
    # Overall percentage of correct answers for the first topic answer
    earliest_topic_answers_correct_answers_percentage = serializers.SerializerMethodField()
    # Overall percentage of correct answers for the last topic answer
    latest_topic_answers_correct_answers_percentage = serializers.SerializerMethodField()
    # Last session datetime
    last_session = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'subject', 'completed_topics_count', 'accessible_topics_count',
            'earliest_topic_answers_correct_answers_percentage', 'latest_topic_answers_correct_answers_percentage', 'last_session')

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
            assessment=instance
        ).distinct().count()

    def get_subject(self, instance):
        return instance.get_subject_display()

    def get_earliest_topic_answers_correct_answers_percentage(self, instance):
        student_pk = self.context['student_pk']
        session_pk = self.context['session_pk']

        if (session_pk):
            return None

        total_correct_answers = 0
        total_answers = 0

        for topic in AssessmentTopic.objects.filter(assessment=instance, evaluated=True):

            earliest_topic_answer = AssessmentTopicAnswer.objects.filter(
                topic_access__topic=topic,
                session__student=student_pk,
                complete=True
            )

            if not (earliest_topic_answer.exists()):
                continue

            earliest_topic_answer = earliest_topic_answer.earliest('start_date')

            total_correct_answers = total_correct_answers + Answer.objects.filter(
                topic_answer=earliest_topic_answer,
                valid=True
            ).count()

            total_answers = total_answers + Answer.objects.filter(
                topic_answer=earliest_topic_answer
            ).count()

        correct_answers_percentage = None

        if (total_answers):
            correct_answers_percentage = round((total_correct_answers / total_answers) * 100, 2)

        return correct_answers_percentage

    def get_latest_topic_answers_correct_answers_percentage(self, instance):
        student_pk = self.context['student_pk']
        session_pk = self.context['session_pk']

        if (session_pk):
            return None

        total_correct_answers = 0
        total_answers = 0

        for topic in AssessmentTopic.objects.filter(assessment=instance, evaluated=True):

            latest_topic_answer = AssessmentTopicAnswer.objects.filter(
                topic_access__topic=topic,
                session__student=student_pk,
                complete=True
            )

            if not (latest_topic_answer.exists()):
                continue

            latest_topic_answer = latest_topic_answer.latest('start_date')

            total_correct_answers = total_correct_answers + Answer.objects.filter(
                topic_answer=latest_topic_answer,
                valid=True
            ).count()

            total_answers = total_answers + Answer.objects.filter(
                topic_answer=latest_topic_answer
            ).count()

        correct_answers_percentage = None

        if (total_answers):
            correct_answers_percentage = round((total_correct_answers / total_answers) * 100, 2)

        return correct_answers_percentage

    def get_last_session(self, instance):
        student_pk = self.context['student_pk']
        session_pk = self.context['session_pk']

        if (session_pk):
            return None

        last_session = AnswerSession.objects.filter(
            assessment_topic_answers__topic_access__topic__assessment=instance,
            student=student_pk,
        ).latest('start_date')

        return last_session.start_date


class TopicAnswerTableSerializer(serializers.ModelSerializer):
    """
    Topic answer serializer
    """

    # Total number of questions
    total_questions_count = serializers.SerializerMethodField()
    # Total of answered questions
    answered_questions_count = serializers.SerializerMethodField()
    # Overall percentage of correct answers
    correct_answers_percentage = serializers.SerializerMethodField()
    # We have the AssessmentTopicAnswer's id, but need the Topic id, so we have to fetch it
    id = serializers.SerializerMethodField()
    # Name of the topic to which this AssessmentTopicAnswer is linked to
    topic_name = serializers.SerializerMethodField()

    evaluated = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopicAnswer
        fields = ('id', 'topic_name', 'complete', 'start_date', 'end_date', 'evaluated',
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

        if (instance.topic_access.topic.evaluated!=True):
            return None

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

    def get_evaluated(self, instance):
        return instance.topic_access.topic.evaluated

class QuestionAnswerTableSerializer(serializers.ModelSerializer):
    """
    Question answer serializer
    """

    # Total number of questions
    question_type = serializers.SerializerMethodField()
    # Order of the question to which the Answer is linked
    question_order = serializers.SerializerMethodField()
    # Specify is the linked question has an attachment
    has_attachment = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ('id', 'question_order', 'duration', 'valid', 'question_type', 'has_attachment')

    def get_question_type(self, instance):
        return instance.question.get_question_type_display()

    def get_has_attachment(self, instance):
        if(Attachment.objects.filter(question=instance.question)):
            return True
        return False

    def get_question_order(self, instance):
        return instance.question.order

class AnswerTableSerializer(PolymorphicSerializer):

    class Meta:
        model = Answer
        fields = '__all__'
    
    def get_serializer_map(self):
        return {
            'AnswerInput': AnswerInputTableSerializer,
            'AnswerNumberLine': AnswerNumberLineTableSerializer,
            'AnswerSelect': AnswerSelectTableSerializer,
            'AnswerSort': AnswerSortTableSerializer
        }


class AbstractAnswerTableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ('question', 'valid')
    
    

class AnswerInputTableSerializer(AbstractAnswerTableSerializer):

    valid_answer = serializers.SerializerMethodField()
    question = NestedRelatedField(model=QuestionInput, serializer_class=QuestionInputTableSerializer, many=False)

    class Meta(AbstractAnswerTableSerializer.Meta):
        model = AnswerInput
        fields = AbstractAnswerTableSerializer.Meta.fields + ('valid_answer', 'value', 'question', )
    
    def get_valid_answer(self, instance):
        return QuestionInput.objects.get(id=instance.question.id).valid_answer

class AnswerNumberLineTableSerializer(AbstractAnswerTableSerializer):

    question = NestedRelatedField(model=QuestionNumberLine, serializer_class=QuestionNumberLineTableSerializer, many=False)

    class Meta(AbstractAnswerTableSerializer.Meta):
        model = AnswerNumberLine
        fields = AbstractAnswerTableSerializer.Meta.fields + ('value', 'question',)
      

class AnswerSelectTableSerializer(AbstractAnswerTableSerializer):

    question = NestedRelatedField(model=QuestionSelect, serializer_class=QuestionSelectTableSerializer, many=False)

    class Meta(AbstractAnswerTableSerializer.Meta):
        model = AnswerSelect
        fields = AbstractAnswerTableSerializer.Meta.fields + ('selected_options', 'question',)

class AnswerSortTableSerializer(AbstractAnswerTableSerializer):

    category_A = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True)
    category_B = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True)
    
    question = NestedRelatedField(model=QuestionSort, serializer_class=QuestionSortTableSerializer, many=False)

    class Meta(AbstractAnswerTableSerializer):
        model = AnswerSort
        fields = AbstractAnswerTableSerializer.Meta.fields + ('category_A', 'category_B', 'question',)


class ScoreByTopicSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()
    topics = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('full_name', 'topics')

    def get_full_name(self, instance):
        return (instance.first_name + ' ' + instance.last_name)
    
    def get_topics(self, instance):
        assessment_pk = self.context['assessment_pk']

        topics = AssessmentTopic.objects.filter(assessment=assessment_pk)
        topic_score = []

        total_correct_answers = 0
        total_answers = 0

        for topic in topics:

            if topic.evaluated:

                topic_accesses = list(AssessmentTopicAccess.objects.filter(topic=topic, student=instance))

                if topic_accesses:

                    for access in topic_accesses:
                        
                        if AssessmentTopicAnswer.objects.filter(topic_access=access,session__student=instance):

                            if AssessmentTopicAnswer.objects.filter(topic_access=access, session__student=instance, complete=True):
                                
                                earliest_topic_answer = AssessmentTopicAnswer.objects.filter(
                                    topic_access=access,
                                    session__student=instance,
                                    complete=True
                                ).earliest('start_date')

                                total_correct_answers = total_correct_answers + Answer.objects.filter(
                                    topic_answer=earliest_topic_answer,
                                    valid=True
                                ).count()

                                total_answers = total_answers + Answer.objects.filter(
                                    topic_answer=earliest_topic_answer
                                ).count()


                                if (total_answers):
                                    correct_answers_percentage = round((total_correct_answers / total_answers) * 100, 1)
                                    topic_score_dict = {
                                        topic.name: correct_answers_percentage
                                    }
                                    topic_score.append(topic_score_dict)

                            else :
                                topic_score_dict = {
                                    topic.name: 'not_started'
                                }
                                topic_score.append(topic_score_dict)                    
                        
                        else :
                            topic_score_dict = {
                                topic.name: 'not_started'
                            }
                            topic_score.append(topic_score_dict)

                else :
                    topic_score_dict = {
                        topic.name: None
                    }
                    topic_score.append(topic_score_dict)

            else :

                topic_score_dict = {
                    topic.name: 'not_evaluated'
                }
                topic_score.append(topic_score_dict)

            
        return topic_score


class TopicLisForDashboardSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssessmentTopic
        fields = ('id', 'name', 'evaluated')
    

class AssessmentListForDashboardSerializer(serializers.ModelSerializer):

    topics = serializers.SerializerMethodField()
    evaluated = serializers.SerializerMethodField()
    topics_average = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'evaluated', 'topics', 'topics_average')
    

    def get_topics(self, instance):

        topics = []

        for topic in AssessmentTopic.objects.filter(assessment=instance):

            if topic.evaluated:
                topics.append(topic.name)

        return topics
    
    def get_evaluated(self, instance):

        evaluated = False

        for topic in AssessmentTopic.objects.filter(assessment=instance):

            if topic.evaluated == True:
                evaluated = True
        
        return evaluated
    
    def get_topics_average(self, instance):

        supervisor = self.context['supervisor']
        students_average = []
        topic_average = []
        total_correct_answers = 0
        total_answers = 0

        for topic in AssessmentTopic.objects.filter(assessment=instance):

            if topic.evaluated:

                for student in User.objects.filter(created_by=supervisor):

                    topic_accesses = AssessmentTopicAccess.objects.filter(topic=topic, student=student)

                    for topic_access in topic_accesses:

                        if AssessmentTopicAnswer.objects.filter(topic_access=topic_access, session__student=student, complete=True):

                            earliest_topic_answer = AssessmentTopicAnswer.objects.filter(
                                topic_access=topic_access,
                                session__student=student,
                                complete=True
                            ).earliest('start_date')

                            total_correct_answers = total_correct_answers + Answer.objects.filter(
                                topic_answer=earliest_topic_answer,
                                valid=True
                            ).count()

                            total_answers = total_answers + Answer.objects.filter(
                                topic_answer=earliest_topic_answer
                            ).count()


                            if (total_answers):
                                correct_answers_percentage = round((total_correct_answers / total_answers) * 100, 1)
                                students_average.append(correct_answers_percentage)
            
            else:
                topic_average.append(None)
            
            if len(students_average) != 0:            
                topic_average.append(sum(students_average)/len(students_average))

        return topic_average


class QuestionOverviewSerializer(serializers.ModelSerializer):

    correct_answers_count = serializers.SerializerMethodField()
    incorrect_answers_count = serializers.SerializerMethodField()
    total_of_first_try_answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'title', 'order', 'question_type', 'correct_answers_count', 'incorrect_answers_count', 'total_of_first_try_answers')
       
    
    def get_total_of_first_try_answers(self, instance):

        supervisor = self.context['supervisor']
        topic_pk = self.context['topic_pk']
        total_answers = 0
        students = User.objects.filter(created_by=supervisor)

        for access in AssessmentTopicAccess.objects.filter(topic=topic_pk, student__in=students):

            if AssessmentTopicAnswer.objects.filter(topic_access=access, session__student__in=students, complete=True):
                earliest_topic_answer = AssessmentTopicAnswer.objects.filter(
                    topic_access=access,
                    session__student__in=students,
                    complete=True
                ).earliest('start_date')

                total_answers = total_answers + Answer.objects.filter(topic_answer=earliest_topic_answer, question=instance).count()
        
        return total_answers
    
    def get_correct_answers_count(self,  instance):

        supervisor = self.context['supervisor']
        topic_pk = self.context['topic_pk']
        total_correct_answers = 0
        students = User.objects.filter(created_by=supervisor)

        for access in AssessmentTopicAccess.objects.filter(topic=topic_pk, student__in=students):

            if AssessmentTopicAnswer.objects.filter(topic_access=access, session__student__in=students, complete=True):
                earliest_topic_answer = AssessmentTopicAnswer.objects.filter(
                    topic_access=access,
                    session__student__in=students,
                    complete=True
                ).earliest('start_date')

                total_correct_answers = total_correct_answers + Answer.objects.filter(topic_answer=earliest_topic_answer, question=instance, valid=True).count()
        
        return total_correct_answers
    
    def get_incorrect_answers_count(self, instance):

        correct_answers_count = self.get_correct_answers_count(instance) 
        total_answers_count = self.get_total_of_first_try_answers(instance)

        return total_answers_count - correct_answers_count


class UserFullNameSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name')

    def get_full_name(self, instance):
        return (instance.first_name + ' ' + instance.last_name)


class StudentsByTopicAccessSerializer(serializers.ModelSerializer):

    student = NestedRelatedField(model=User, serializer_class=UserFullNameSerializer, many=False)
    topic_first_try = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopicAccess
        fields = ('id','student', 'topic_first_try')
    

    def get_topic_first_try(self, instance):

        if AssessmentTopicAnswer.objects.filter(topic_access=instance, complete=True):
            return AssessmentTopicAnswer.objects.filter(topic_access=instance, complete=True).values().earliest('start_date')
        else:
            return None


class QuestionDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ('id', 'order', 'title')


class StudentAnswersSerializer(serializers.ModelSerializer):

    question = NestedRelatedField(model=Question, serializer_class=QuestionDetailsSerializer, many=False)

    class Meta:
        model = Answer
        fields = ('id', 'valid', 'question')
