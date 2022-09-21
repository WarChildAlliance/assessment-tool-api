from rest_framework import serializers
import datetime
from django.utils import timezone
from admin.lib.serializers import NestedRelatedField, PolymorphicSerializer
from users.models import User, Group
from assessments.models import AreaOption, Assessment, AssessmentTopic, AssessmentTopicAccess, Attachment, Question, QuestionDragAndDrop, QuestionInput, QuestionNumberLine, QuestionSelect, QuestionSort, SelectOption, SortOption, Hint
from answers.models import AnswerDragAndDrop, AnswerSession, AssessmentTopicAnswer, Answer, AnswerInput, AnswerNumberLine, AnswerSelect, AnswerSort, DragAndDropAreaEntry

from answers.serializers import DragAndDropAreaEntrySerializer
from assessments.serializers import (AreaOptionSerializer, SelectOptionSerializer, SortOptionSerializer,
                                     HintSerializer, AttachmentSerializer, AssessmentTopicSerializer)
from users.serializers import GroupSerializer


class UserTableSerializer(serializers.ModelSerializer):
    """
    Users table serializer.
    """

    # Last session
    last_session = serializers.SerializerMethodField()
    # Full name
    full_name = serializers.SerializerMethodField()
    # Number of topics completed by the student
    completed_topics_count = serializers.SerializerMethodField()
    # Number of assessments that the student is linked to
    assessments_count = serializers.SerializerMethodField()

    # Languages and countries formatted information
    language_name = serializers.SerializerMethodField()
    language_code = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    country_code = serializers.SerializerMethodField()

    # Group that the student is linked to
    group = serializers.SerializerMethodField()

    # Students can only be deleted after more than 1 year of inactivity
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'first_name', 'last_name', 'last_session', 'completed_topics_count', 'active_status_updated_on',
                  'assessments_count', 'language_name', 'language_code', 'country_name', 'country_code', 'group', 'is_active', 'can_delete')

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

    def get_group(self, instance):
        group = Group.objects.filter(student_group=instance).values_list('name', flat=True)
        return group

    def get_can_delete(self, instance):
        if instance.is_active == False and instance.active_status_updated_on:
            if abs((instance.active_status_updated_on - instance.date_joined).total_seconds()) < 1:
                return True

            return (timezone.now() - instance.active_status_updated_on).days > 365

        return False


class StudentLinkedAssessmentsSerializer(serializers.ModelSerializer):

    topic_access = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'topic_access')

    def get_topic_access(self, instance):

        student_pk = self.context['student_pk']

        topic_list = AssessmentTopic.objects.filter(assessment=instance)
        topic_access_list = []

        for topic in topic_list:
            topic_access = list(AssessmentTopicAccess.objects.filter(
                topic=topic, student=student_pk).values())

            if topic_access:
                access_dict = {
                    'topic_id': topic.id,
                    'topic_name': topic.name,
                    'topic_access_id': topic_access[0]['id'],
                    'start_date': topic_access[0]['start_date'],
                    'end_date': topic_access[0]['end_date']
                }

                topic_access_list.append(access_dict)

        return topic_access_list


class AssessmentTableSerializer(serializers.ModelSerializer):
    """
    Assessment serializer for table.
    """

    # Total number of topics for this assessment
    topics_count = serializers.SerializerMethodField()
    # Total number of students who have an active access to this assessment
    topics = serializers.SerializerMethodField()
    students_count = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    # Languages and countries formatted information
    language_name = serializers.SerializerMethodField()
    language_code = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    country_code = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'language_name', 'language_code',
                  'country_name', 'country_code', 'topics_count', 'topics',
                  'students_count', 'grade', 'subject', 'private', 'can_edit',
                  'icon', 'archived', 'downloadable')

    def get_topics_count(self, instance):
        return AssessmentTopic.objects.filter(assessment=instance).count()
    
    def get_topics(self, instance):
        topics = AssessmentTopic.objects.filter(assessment=instance).values_list('id', 'name', 'description', 'icon', 'archived', 'order')

        topics_with_question_count = []

        for topic in topics:
            question_count = Question.objects.filter(assessment_topic=topic[0]).count()
            topics_with_question_count.append({"id": topic[0], "title": topic[1], "description": topic[2], "questionsCount": question_count,"icon": topic[3], "archived": topic[4], "order": topic[5]})
        
        return topics_with_question_count

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
    
    def get_can_edit(self, instance):
        if not ('supervisor' in self.context):
            return None
        
        supervisor = self.context['supervisor']
        if instance.created_by == supervisor:
            return True
        else:
            return False


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
    # Assesment id
    assessment_id = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopic
        fields = ('id', 'assessment_id', 'name', 'students_count', 'students_completed_count', 'order',
                  'overall_students_completed_count', 'questions_count', 'archived', 'subtopic')

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

    def get_assessment_id(self, instance):
        return Assessment.objects.filter(id=instance.assessment.id).values_list('id', flat=True)[0]

class QuestionTableSerializer(serializers.ModelSerializer):
    """
    Questions table serializer.
    """

    has_attachment = serializers.SerializerMethodField()
    question_type = serializers.SerializerMethodField()
    # Overall percentage of correct answers on this question on first students' try
    correct_answers_percentage_first = serializers.SerializerMethodField()
    # Overall percentage of correct answers on this question on last students' try
    correct_answers_percentage_last = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'title', 'order', 'question_type',
                  'has_attachment', 'correct_answers_percentage_first',
                  'correct_answers_percentage_last', 'difficulty')

    def get_has_attachment(self, instance):
        if(Attachment.objects.filter(question=instance)):
            return True
        return False

    def get_question_type(self, instance):
        return instance.get_question_type_display()

    def get_correct_answers_percentage_first(self, instance):

        accessible_students = self.context.get("accessible_students")

        total_answers = 0
        total_correct_answers = 0

        for student in accessible_students:

            earliest_topic_answers = AssessmentTopicAnswer.objects.filter(
                topic_access__student=student,
                topic_access__topic=instance.assessment_topic,
                complete=True
            )

            if earliest_topic_answers:

                earliest_topic_answer = earliest_topic_answers.earliest("start_date")
                answers_list = Answer.objects.filter(
                    question=instance,
                    topic_answer=earliest_topic_answer
                )
                total_answers += answers_list.count()
                total_correct_answers += answers_list.filter(
                    valid=True
                ).count()

        correct_answers_percentage = None

        if total_answers:
            correct_answers_percentage = round(
                (100 * total_correct_answers / total_answers), 2)

        return correct_answers_percentage

    def get_correct_answers_percentage_last(self, instance):

        accessible_students = self.context.get("accessible_students")

        total_answers = 0
        total_correct_answers = 0

        for student in accessible_students:

            latest_topic_answers = AssessmentTopicAnswer.objects.filter(
                topic_access__student=student,
                topic_access__topic=instance.assessment_topic,
                complete=True
            )

            if latest_topic_answers:

                latest_topic_answer = latest_topic_answers.latest("start_date")
                answers_list = Answer.objects.filter(
                    question=instance,
                    topic_answer=latest_topic_answer
                )

                total_answers += answers_list.count()
                total_correct_answers += answers_list.filter(
                    valid=True
                ).count()

        correct_answers_percentage = None

        if total_answers:
            correct_answers_percentage = round(
                (100 * total_correct_answers / total_answers), 2)

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
            'QuestionSort': QuestionSortTableSerializer,
            'QuestionDragAndDrop': QuestionDragAndDropTableSerializer
        }


class AbstractQuestionDetailsTableSerializer(serializers.ModelSerializer):

    hint = NestedRelatedField(
        model=Hint, serializer_class=HintSerializer, many=False)
    attachments = NestedRelatedField(
        model=Attachment, serializer_class=AttachmentSerializer, many=True)

    class Meta:
        model = Question
        fields = ('id', 'title', 'order',
                  'question_type', 'hint', 'attachments')


class QuestionInputTableSerializer(AbstractQuestionDetailsTableSerializer):

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionInput
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + \
            ('valid_answer',)


class QuestionNumberLineTableSerializer(AbstractQuestionDetailsTableSerializer):

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionNumberLine
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + \
            ('expected_value', 'start', 'end', 'step', 'show_ticks', 'show_value',)


class QuestionSelectTableSerializer(AbstractQuestionDetailsTableSerializer):

    options = NestedRelatedField(
        model=SelectOption, serializer_class=SelectOptionSerializer, many=True)

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionSelect
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + \
            ('options', 'multiple', )


class QuestionSortTableSerializer(AbstractQuestionDetailsTableSerializer):

    options = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True)

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionSort
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + \
            ('category_A', 'category_B', 'options',)

class QuestionDragAndDropTableSerializer(AbstractQuestionDetailsTableSerializer):

    drop_areas = NestedRelatedField(
        model=AreaOption, serializer_class=AreaOptionSerializer, many=True)

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionDragAndDrop
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + \
            ('drop_areas',)

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
    # Last session datetime
    last_session = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'subject', 'completed_topics_count',
                  'accessible_topics_count', 'last_session')

    def get_completed_topics_count(self, instance):
        student_pk = self.context['student_pk']

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

    def get_last_session(self, instance):
        student_pk = self.context['student_pk']

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
    questions_count = serializers.SerializerMethodField()
    # Total of answered questions
    student_tries_count = serializers.SerializerMethodField()
    # Overall percentage of correct answers on first try
    correct_answers_percentage_first_try = serializers.SerializerMethodField()
    # Overall percentage of correct answers on last try
    correct_answers_percentage_last_try = serializers.SerializerMethodField()
    # Last submission
    last_submission = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopic
        fields = ('id', 'name', 'questions_count', 'student_tries_count',
                  'correct_answers_percentage_first_try',
                  'correct_answers_percentage_last_try',
                  'last_submission')

    def get_questions_count(self, instance):
        return Question.objects.filter(assessment_topic=instance).count()

    def get_student_tries_count(self, instance):
        student_pk = self.context['student_pk']

        return AssessmentTopicAnswer.objects.filter(
            topic_access__topic=instance,
            session__student=student_pk
        ).distinct().count()

    def get_correct_answers_percentage_first_try(self, instance):
        student_pk = self.context['student_pk']

        first_topic_answer = AssessmentTopicAnswer.objects.filter(
            topic_access__topic=instance,
            session__student=student_pk,
            complete=True
        )

        if not first_topic_answer.exists():
            return None

        if (instance.evaluated != True):
            return None

        first_topic_answer = first_topic_answer.earliest('end_date')

        total_answers = Answer.objects.filter(
            topic_answer=first_topic_answer
        ).distinct().count()

        total_valid_answers = Answer.objects.filter(
            topic_answer=first_topic_answer,
            valid=True
        ).distinct().count()

        correct_answers_percentage = None

        if total_answers:
            correct_answers_percentage = round(
                (100 * total_valid_answers / total_answers), 2)

        return correct_answers_percentage

    def get_correct_answers_percentage_last_try(self, instance):

        student_pk = self.context['student_pk']

        last_topic_answer = AssessmentTopicAnswer.objects.filter(
            topic_access__topic=instance,
            session__student=student_pk,
            complete=True
        )

        if not last_topic_answer.exists():
            return None

        if (instance.evaluated != True):
            return None

        last_topic_answer = last_topic_answer.latest('end_date')

        total_answers = Answer.objects.filter(
            topic_answer=last_topic_answer
        ).distinct().count()

        total_valid_answers = Answer.objects.filter(
            topic_answer=last_topic_answer,
            valid=True
        ).distinct().count()

        correct_answers_percentage = None

        if total_answers:
            correct_answers_percentage = round(
                (100 * total_valid_answers / total_answers), 2)

        return correct_answers_percentage

    def get_last_submission(self, instance):
        student_pk = self.context['student_pk']

        last_topic_answer = AssessmentTopicAnswer.objects.filter(
            topic_access__topic=instance,
            session__student=student_pk
        )

        if not last_topic_answer.exists():
            return None

        return last_topic_answer.latest('end_date').end_date


class QuestionAnswerTableSerializer(serializers.ModelSerializer):
    """
    Question answer serializer
    """

    # Average duration that the student takes to answer the question
    average_duration = serializers.SerializerMethodField()
    # Overall percentage of correct answers on first try
    correctly_answered_first_try = serializers.SerializerMethodField()
    # Overall percentage of correct answers on last try
    correctly_answered_last_try = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'title', 'order',
                  'question_type', 'average_duration',
                  'correctly_answered_first_try',
                  'correctly_answered_last_try')

    def get_average_duration(self, instance):
        student_pk = self.context['student_pk']

        all_answers = Answer.objects.filter(
            question=instance,
            topic_answer__complete=True,
            topic_answer__session__student=student_pk
        ).distinct()

        if not all_answers:
            return None

        total_durations = 0

        for answer in all_answers:
            if answer.start_datetime and answer.end_datetime:
                total_durations =+ (answer.end_datetime - answer.start_datetime)

        return (total_durations / all_answers.count())

    def get_correctly_answered_first_try(self, instance):
        student_pk = self.context['student_pk']

        first_topic_answer = AssessmentTopicAnswer.objects.filter(
            topic_access__topic__question=instance,
            session__student=student_pk,
            complete=True
        )

        if not first_topic_answer:
            return None

        first_topic_answer = first_topic_answer.earliest('end_date')

        return Answer.objects.get(
            topic_answer=first_topic_answer,
            question=instance
        ).valid

    def get_correctly_answered_last_try(self, instance):
        student_pk = self.context['student_pk']

        last_topic_answer = AssessmentTopicAnswer.objects.filter(
            topic_access__topic__question=instance,
            session__student=student_pk,
            complete=True
        )

        if not last_topic_answer:
            return None

        last_topic_answer = last_topic_answer.latest('end_date')

        return Answer.objects.get(
            topic_answer=last_topic_answer,
            question=instance
        ).valid


class AnswerTableSerializer(PolymorphicSerializer):

    class Meta:
        model = Answer
        fields = '__all__'

    def get_serializer_map(self):
        return {
            'AnswerInput': AnswerInputTableSerializer,
            'AnswerNumberLine': AnswerNumberLineTableSerializer,
            'AnswerSelect': AnswerSelectTableSerializer,
            'AnswerSort': AnswerSortTableSerializer,
            'AnswerDragAndDrop': AnswerDragAndDropTableSerializer
        }


class AbstractAnswerTableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ('question', 'valid')


class AnswerInputTableSerializer(AbstractAnswerTableSerializer):

    valid_answer = serializers.SerializerMethodField()
    question = NestedRelatedField(
        model=QuestionInput, serializer_class=QuestionInputTableSerializer, many=False)

    class Meta(AbstractAnswerTableSerializer.Meta):
        model = AnswerInput
        fields = AbstractAnswerTableSerializer.Meta.fields + \
            ('valid_answer', 'value', 'question', )

    def get_valid_answer(self, instance):
        return QuestionInput.objects.get(id=instance.question.id).valid_answer


class AnswerNumberLineTableSerializer(AbstractAnswerTableSerializer):

    question = NestedRelatedField(
        model=QuestionNumberLine, serializer_class=QuestionNumberLineTableSerializer, many=False)

    class Meta(AbstractAnswerTableSerializer.Meta):
        model = AnswerNumberLine
        fields = AbstractAnswerTableSerializer.Meta.fields + \
            ('value', 'question',)


class AnswerSelectTableSerializer(AbstractAnswerTableSerializer):

    question = NestedRelatedField(
        model=QuestionSelect, serializer_class=QuestionSelectTableSerializer, many=False)

    class Meta(AbstractAnswerTableSerializer.Meta):
        model = AnswerSelect
        fields = AbstractAnswerTableSerializer.Meta.fields + \
            ('selected_options', 'question',)


class AnswerSortTableSerializer(AbstractAnswerTableSerializer):

    category_A = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True)
    category_B = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True)

    question = NestedRelatedField(
        model=QuestionSort, serializer_class=QuestionSortTableSerializer, many=False)

    class Meta(AbstractAnswerTableSerializer):
        model = AnswerSort
        fields = AbstractAnswerTableSerializer.Meta.fields + \
            ('category_A', 'category_B', 'question',)


class AnswerDragAndDropTableSerializer(AbstractAnswerTableSerializer):

    answers_per_area = serializers.SerializerMethodField()

    question = NestedRelatedField(
        model=QuestionDragAndDrop, serializer_class=QuestionDragAndDropTableSerializer, many=False)

    class Meta(AbstractAnswerTableSerializer):
        model = AnswerDragAndDrop
        fields = AbstractAnswerTableSerializer.Meta.fields + \
            ('answers_per_area', 'question',)

    def get_answers_per_area(self, instance):
        answers_per_area = DragAndDropAreaEntry.objects.filter(answer=instance)
        serializer = DragAndDropAreaEntrySerializer(answers_per_area, many=True)
        return serializer.data


class ScoreByTopicSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()
    topics = serializers.SerializerMethodField()
    student_access = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'topics', 'student_access', 'group')

    def get_group(self, instance):
        group = Group.objects.filter(student_group=instance)
        serializer = GroupSerializer(group, many = True)
        return serializer.data

    def get_full_name(self, instance):
        return (instance.first_name + ' ' + instance.last_name)
    
    def get_student_access(self, instance):
        assessment_pk = self.context['assessment_pk']

        topics = AssessmentTopic.objects.filter(assessment=assessment_pk)
        for access in AssessmentTopicAccess.objects.filter(student=instance, topic__in=topics):
            if AssessmentTopicAnswer.objects.filter(topic_access=access, session__student=instance, complete=True):
                return True
        return False
    
    def get_topics(self, instance):
        assessment_pk = self.context['assessment_pk']
        topic_score = []

        for topic in AssessmentTopic.objects.filter(assessment=assessment_pk, archived=False):

            if topic.evaluated:
                total_answers = Question.objects.filter(assessment_topic=topic).count()
                access = AssessmentTopicAccess.objects.filter(topic=topic, student=instance)

                if access:
                    if AssessmentTopicAnswer.objects.filter(topic_access=access.first(), complete=True):
                        earliest_topic_answer = AssessmentTopicAnswer.objects.filter(
                            topic_access=access.first(),
                            complete=True
                        ).earliest('start_date')

                        total_correct_answers = Answer.objects.filter(
                            topic_answer=earliest_topic_answer,
                            valid=True
                        ).count()

                        correct_answers_percentage = 0

                        if (total_answers != 0):
                            correct_answers_percentage = round((total_correct_answers / total_answers) * 100, 1)

                        topic_score_dict = {
                            topic.name: correct_answers_percentage
                        }
                        topic_score.append(topic_score_dict)
                    else:
                        topic_score_dict = {
                            topic.name: 'not_started'
                        }
                        topic_score.append(topic_score_dict)
                
                else:
                    topic_score_dict = {
                        topic.name: None
                    }
                    topic_score.append(topic_score_dict)
            else:
                topic_score_dict = {
                    topic.name: 'not_evaluated'
                }
                topic_score.append(topic_score_dict)
       
        return topic_score


class TopicLisForDashboardSerializer(serializers.ModelSerializer):

    started = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopic
        fields = ('id', 'name', 'evaluated', 'started')
    
    def get_started(self, instance):

        started = False
        
        if AssessmentTopicAnswer.objects.filter(topic_access__topic=instance, complete=True):
            started = True

        return started


class AssessmentListForDashboardSerializer(serializers.ModelSerializer):

    topics = serializers.SerializerMethodField()
    evaluated = serializers.SerializerMethodField()
    started = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'evaluated', 'topics', 'started')
    
    def get_topics(self, instance):

        supervisor = self.context['supervisor']
        students = User.objects.filter(created_by=supervisor)
        topics = []

        #Iterate through topics
        for topic in AssessmentTopic.objects.filter(assessment=instance, evaluated=True):
            accesses = AssessmentTopicAccess.objects.filter(topic=topic, student__in=students)
            total_answers = Question.objects.filter(assessment_topic=topic).count()
            students_average = []

            #Iterate through the supervisors student to get topic accesses
            for access in accesses:
                #For each topic access, check for completed topic answers
                if AssessmentTopicAnswer.objects.filter(topic_access=access, complete=True):
                    #Get the first try
                    earliest_topic_answer = AssessmentTopicAnswer.objects.filter(
                        topic_access=access,
                        complete=True
                    ).earliest('start_date')

                    #Get correct answers for this first try
                    total_correct_answers = Answer.objects.filter(
                        topic_answer=earliest_topic_answer,
                        valid=True
                    ).count()

                    percentage = 0

                    if(total_answers != 0):
                        percentage = round((total_correct_answers / total_answers) * 100, 1)

                    students_average.append(percentage)
            
            if len(students_average) != 0:
                topic_dict = {
                    'id': topic.id,
                    'name': topic.name,
                    'average': round(sum(students_average)/len(students_average), 1)
                }
            else :
                topic_dict = {
                    'id': topic.id,
                    'name': topic.name,
                    'average': None
                }
            topics.append(topic_dict)
    
        return topics


    def get_evaluated(self, instance):

        evaluated = False

        for topic in AssessmentTopic.objects.filter(assessment=instance):

            if topic.evaluated == True:
                evaluated = True

        return evaluated
    
    def get_started(self, instance):
        started = False
        for topic in self.get_topics(instance):
            if topic['average'] != None:
                started = True
        return started


class QuestionOverviewSerializer(serializers.ModelSerializer):

    correct_answers_count = serializers.SerializerMethodField()
    incorrect_answers_count = serializers.SerializerMethodField()
    total_of_first_try_answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'title', 'order', 'question_type', 'correct_answers_count',
                  'incorrect_answers_count', 'total_of_first_try_answers')

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

                total_answers = total_answers + \
                    Answer.objects.filter(
                        topic_answer=earliest_topic_answer, question=instance).count()

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

                total_correct_answers = total_correct_answers + Answer.objects.filter(
                    topic_answer=earliest_topic_answer, question=instance, valid=True).count()

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

    student = NestedRelatedField(
        model=User, serializer_class=UserFullNameSerializer, many=False)
    topic_first_try = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopicAccess
        fields = ('id', 'student', 'topic_first_try')

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

    question = NestedRelatedField(
        model=Question, serializer_class=QuestionDetailsSerializer, many=False)
    color = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ('id', 'valid', 'question', 'color')

    # The color returned is according to the validity of the answer
    def get_color(self, instance):
        if instance.valid == True:
            return '#7EBF9A'
        else:
            return '#F2836B'