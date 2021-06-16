from answers.models import Answer, AnswerSession, AssessmentTopicAnswer
from assessments.models import (Assessment, AssessmentTopic, Attachment,
                                Question)
from rest_framework import serializers

from admin.lib.serializers import NestedRelatedField, PolymorphicSerializer

from users.models import User
from assessments.models import Assessment, AssessmentTopic, AssessmentTopicAccess, Attachment, Question, QuestionInput, QuestionNumberLine, QuestionSelect, QuestionSort, SelectOption, SortOption, Hint
from answers.models import AnswerSession, AssessmentTopicAnswer, Answer, AnswerInput, AnswerNumberLine, AnswerSelect, AnswerSort

from assessments.serializers import (SelectOptionSerializer, SortOptionSerializer, HintSerializer, AttachmentSerializer, AssessmentTopicSerializer)


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
        return Assessment.objects.filter(assessmenttopic__assessmenttopicaccess__student=instance).distinct().count()

    def get_language_name(self, instance):
        return instance.language.name_en

    def get_language_code(self, instance):
        return instance.language.code

    def get_country_name(self, instance):
        return instance.country.name_en

    def get_country_code(self, instance):
        return instance.country.code


class UserAssessmentTreeSerializer(serializers.ModelSerializer):

    topics = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('title', 'topics')
    
    
    def get_topics(self, instance):
        student_pk = self.context['student_pk']

        topic_access_list = list(AssessmentTopicAccess.objects.filter(topic__assessment=instance, student=student_pk).values())
        topics = []

        for access in topic_access_list:
            topic = []
            topic.append(AssessmentTopic.objects.get(id=access['topic_id']).name)
            topic.append(access['start_date'])
            topic.append(access['end_date'])
            topics.append(topic)
        
        return topics



class AssessmentTableSerializer(serializers.ModelSerializer):
    """
    Assessment serializer for table.
    """

    # Total number of topics for this assessment
    topics_count = serializers.SerializerMethodField()
    # Total number of students linked to this assessment
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


class AssessmentTopicTableSerializer(serializers.ModelSerializer):
    """
    Assessment topics table serializer.
    """

    # Total of students linked to this topic
    students_count = serializers.SerializerMethodField()
    # Total of students linked to this topic and who completed it
    students_completed_count = serializers.SerializerMethodField()
    # Total of questions in this topic
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

    total_answers_count = serializers.SerializerMethodField()
    correct_answers_count = serializers.SerializerMethodField()
    correct_answers_percentage = serializers.SerializerMethodField()
    hint = NestedRelatedField(model=Hint, serializer_class=HintSerializer, many=False)
    attachments = NestedRelatedField(model=Attachment, serializer_class=AttachmentSerializer, many=True)

    class Meta:
        model = Question
        fields = ('title', 'order', 'question_type', 'total_answers_count', 'correct_answers_count', 'correct_answers_percentage', 'hint', 'attachments')
    
    
    def get_total_answers_count(self, instance):
        return Answer.objects.filter(question=instance).count()
    
    def get_correct_answers_count(self, instance):
        return Answer.objects.filter(question=instance, valid=True).count()
    
    def get_correct_answers_percentage(self, instance):
        correct_answers_percentage = None

        if self.get_total_answers_count(instance):
            correct_answers_percentage = round(
                (100 * self.get_correct_answers_count(instance) / self.get_total_answers_count(instance)), 2)
        
        return correct_answers_percentage


class QuestionInputTableSerializer(AbstractQuestionDetailsTableSerializer):

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionInput
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + ('valid_answer',)   

class QuestionNumberLineTableSerializer(AbstractQuestionDetailsTableSerializer):

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionNumberLine
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + ('expected_value', 'start', 'end', 'step', 'show_ticks', 'show_value')

class QuestionSelectTableSerializer(AbstractQuestionDetailsTableSerializer):

    options = NestedRelatedField(model=SelectOption, serializer_class=SelectOptionSerializer, many=True)
    most_selected_incorrect_option = serializers.SerializerMethodField()
    
    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionSelect
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + ('options', 'most_selected_incorrect_option')
    
    def get_most_selected_incorrect_option(self, instance):
        select_options_list = SelectOption.objects.filter(question_select=instance, valid=False)
        most_incorrect_select_arr = []
        count = 0
        
        for option in select_options_list:
            answer_select = AnswerSelect.objects.filter(question=instance, selected_options=option)
            if answer_select:
                if count < answer_select.count():
                    count = answer_select.count()
                    most_incorrect_select_arr = []
                    most_incorrect_select_arr.append(option)
                
                elif count == answer_select.count():
                    count = answer_select.count()
                    most_incorrect_select = option
                    most_incorrect_select_arr.append(option)

        
        select_options_serializer = SelectOptionSerializer(most_incorrect_select_arr, many=True)
        return select_options_serializer.data


class QuestionSortTableSerializer(AbstractQuestionDetailsTableSerializer):

    options = NestedRelatedField(model=SortOption, serializer_class=SortOptionSerializer, many=True)

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionSort
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + ('category_A', 'category_B', 'options')
        
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
    # Overall percentage of correct answers for the first session
    first_session_correct_answers_percentage = serializers.SerializerMethodField()
    # Overall percentage of correct answers for the last session
    last_session_correct_answers_percentage = serializers.SerializerMethodField()
    # Last session datetime
    last_session = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'subject', 'completed_topics_count', 'accessible_topics_count',
            'first_session_correct_answers_percentage', 'last_session_correct_answers_percentage', 'last_session')

    def find_correct_answers_from_session(self, session):

        total_answers = Answer.objects.filter(
                topic_answer__session=session
            ).distinct().count()

        total_valid_answers = Answer.objects.filter(
                topic_answer__session=session,
                valid=True
            ).distinct().count()
            
        correct_answers_percentage = None

        if total_answers:
            correct_answers_percentage = round(
                (100 * total_valid_answers / total_answers), 2)

        return correct_answers_percentage

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

    def get_first_session_correct_answers_percentage(self, instance):
        student_pk = self.context['student_pk']
        session_pk = self.context['session_pk']

        if (session_pk):
            return None

        first_session = AnswerSession.objects.filter(
            assessment_topic_answers__topic_access__topic__assessment=instance,
            student=student_pk,
        ).earliest('start_date')

        correct_answers_percentage = self.find_correct_answers_from_session(first_session)

        return correct_answers_percentage

    def get_last_session_correct_answers_percentage(self, instance):
        student_pk = self.context['student_pk']
        session_pk = self.context['session_pk']

        if (session_pk):
            return None

        last_session = AnswerSession.objects.filter(
            assessment_topic_answers__topic_access__topic__assessment=instance,
            student=student_pk,
        ).latest('start_date')

        correct_answers_percentage = self.find_correct_answers_from_session(last_session)

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

    question_title = serializers.SerializerMethodField()
    question_type = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ('question_type', 'question_title', 'duration', 'valid')
    
    def get_question_title(self, instance):
        return instance.question.title
    
    def get_question_type(self, instance):
        return instance.question.get_question_type_display()
    

class AnswerInputTableSerializer(AbstractAnswerTableSerializer):

    valid_answer = serializers.SerializerMethodField()

    class Meta(AbstractAnswerTableSerializer.Meta):
        model = AnswerInput
        fields = AbstractAnswerTableSerializer.Meta.fields + ('valid_answer', 'value',)
    
    def get_valid_answer(self, instance):
        return QuestionInput.objects.get(id=instance.question.id).valid_answer

class AnswerNumberLineTableSerializer(AbstractAnswerTableSerializer):

    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    expected_value = serializers.SerializerMethodField()

    class Meta(AbstractAnswerTableSerializer.Meta):
        model = AnswerNumberLine
        fields = AbstractAnswerTableSerializer.Meta.fields + ('value', 'start', 'end', 'expected_value',)
      
    def get_start(self, instance):
        return QuestionNumberLine.objects.get(id=instance.question.id).start
    
    def get_end(self, instance):
        return QuestionNumberLine.objects.get(id=instance.question.id).end

    def get_expected_value(self, instance):
        return QuestionNumberLine.objects.get(id=instance.question.id).expected_value

class AnswerSelectTableSerializer(AbstractAnswerTableSerializer):

    all_options = serializers.SerializerMethodField()

    class Meta(AbstractAnswerTableSerializer.Meta):
        model = AnswerSelect
        fields = AbstractAnswerTableSerializer.Meta.fields + ('all_options',)
    
    def get_all_options(self, instance):
        select_options = list(SelectOption.objects.filter(question_select=instance.question).values())
        selected_options = AnswerSelect.objects.filter(id=instance.id).values('selected_options')

        all_options = []
        for select_option in select_options:
            for selected_option in selected_options:
                if selected_option['selected_options'] == select_option['id']:
                    select_option['selected'] = True
                
                else :
                    select_option['selected'] = False
            
            all_options.append(select_option)

        return all_options

class AnswerSortTableSerializer(AbstractAnswerTableSerializer):

    category_A = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True)
    category_B = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True)

    class Meta(AbstractAnswerTableSerializer):
        model = AnswerSort
        fields = AbstractAnswerTableSerializer.Meta.fields + ('category_A', 'category_B',)


