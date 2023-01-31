from gamification.models import Profile
from rest_framework import serializers
import datetime
import time
from django.db.models.functions import Round
from django.db.models import Q, Avg, ExpressionWrapper, F, fields, Min, Max, ExpressionWrapper, Count, Sum, Case, When, FloatField, IntegerField
from django.utils import timezone
from admin.lib.serializers import NestedRelatedField, PolymorphicSerializer
from users.models import User, Group
from assessments.models import AreaOption, Assessment, QuestionSet, QuestionSetAccess, Attachment, DominoOption, Question, QuestionCalcul, QuestionDomino, QuestionDragAndDrop, QuestionInput, QuestionNumberLine, QuestionSEL, QuestionSelect, QuestionSort, SelectOption, SortOption, Hint, Topic, LearningObjective, QuestionCustomizedDragAndDrop
from answers.models import AnswerCalcul, AnswerDomino, AnswerDragAndDrop, AnswerSEL, AnswerSession, QuestionSetAnswer, Answer, AnswerInput, AnswerNumberLine, AnswerSelect, AnswerSort, DragAndDropAreaEntry, AnswerCustomizedDragAndDrop
from answers.serializers import DragAndDropAreaEntrySerializer
from assessments.serializers import (AreaOptionSerializer, DominoOptionSerializer, SelectOptionSerializer, SortOptionSerializer,
                                     HintSerializer, AttachmentSerializer, LearningObjectiveSerializer, TopicSerializer, LearningObjectiveSerializer)
from users.serializers import GroupSerializer
from .utils import calculate_student_score, calculate_assessments_score


class AssessmentTableSerializer(serializers.ModelSerializer):
    """
    Assessment serializer for table.
    """

    # Total number of question_sets for this assessment
    question_sets_count = serializers.SerializerMethodField()
    # Total number of students who have an active access to this assessment
    question_sets = serializers.SerializerMethodField()
    topic = NestedRelatedField(
        model=Topic, serializer_class=TopicSerializer, allow_null=True)
    students_count = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    # Languages and countries formatted information
    language_name = serializers.SerializerMethodField()
    language_code = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    country_code = serializers.SerializerMethodField()

    # Number of student invited to the assessment
    invites = serializers.SerializerMethodField()
    # Number of time the assessment has been played by a student
    plays = serializers.SerializerMethodField()
    # Score is the global average score for this assessment amongst all the students
    score = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'language_name', 'language_code', 'invites',
                  'country_name', 'country_code', 'question_sets_count', 'question_sets', 'topic',
                  'plays', 'students_count', 'grade', 'subject', 'private', 'can_edit',
                  'icon', 'archived', 'downloadable', 'sel_question', 'score')

    def __get_question_set_correct_answers_percentage(self, question_set):
        """
        Get the percentage of correct answers for the given question_set
        """
        correct_answers_percentage = 0
        question_set_total_answers = Question.objects.filter(question_set=question_set).exclude(question_type='SEL').count()
        question_set_answers = QuestionSetAnswer.objects.filter(question_set_access__question_set=question_set)
        if not question_set_total_answers or not question_set_answers:
            return None
        question_set_total_correct_answers = Answer.objects.filter(
                question_set_answer__in=question_set_answers,
                valid=True
            ).exclude(question__question_type='SEL').count()
        question_set_total_wrong_answers = 0
        if question_set_total_correct_answers == 0:
            question_set_total_wrong_answers = Answer.objects.filter(
                question_set_answer__in=question_set_answers,
                valid=False
            ).exclude(question__question_type='SEL').count()
        if (question_set_total_answers != 0):
            if question_set_total_correct_answers != 0:
                correct_answers_percentage = round((question_set_total_correct_answers / question_set_total_answers) * 100, 1)
            elif question_set_total_wrong_answers != 0:
                correct_answers_percentage = 0

        return min(correct_answers_percentage, 100.0)

    def __get_question_set_SEL_average(self, question_set):
        choices = ['NOT_REALLY', 'A_LITTLE', 'A_LOT']
        answers = AnswerSEL.objects.filter(question__question_set=question_set).distinct()

        if answers:
            vals = [choices.index(answer.statement) for answer in answers]
            average = round(sum(vals) / len(vals))
            return choices[average]

        return None

    def get_question_sets_count(self, instance):
        return QuestionSet.objects.filter(assessment=instance).count()

    def get_question_sets(self, instance):
        question_sets = QuestionSet.objects.filter(assessment=instance).values_list('id', 'name', 'description', 'icon', 'order', 'learning_objective')

        question_sets_res = []
        for question_set in question_sets:
            learning_objective_data = None
            if question_set[5]:
                learning_objective = LearningObjective.objects.get(code=question_set[5])
                learning_objective_data = LearningObjectiveSerializer(learning_objective).data
            question_count = Question.objects.filter(question_set=question_set[0]).exclude(
                Q(question_type='SEL') & (~Q(question_set__order=1) | Q(question_set__assessment__sel_question=False))
            ).count()
            correct_answers_percentage = self.__get_question_set_correct_answers_percentage(question_set)
            sel_average = self.__get_question_set_SEL_average(question_set)
            question_sets_res.append({"id": question_set[0], "title": question_set[1], "description": question_set[2], "icon": question_set[3], "order": question_set[4], "learning_objective": learning_objective_data,
                    "questionsCount": question_count, "score": correct_answers_percentage, "sel_average": sel_average})

        return question_sets_res

    def get_students_count(self, instance):
        return User.objects.filter(
            questionsetaccess__question_set__assessment=instance,
            questionsetaccess__start_date__lte=datetime.date.today(),
            questionsetaccess__end_date__gte=datetime.date.today()
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

    def get_invites(self, instance):
        question_sets = QuestionSet.objects.filter(assessment=instance)
        return User.objects.filter(questionsetaccess__question_set__in=question_sets).distinct().count()

    def get_plays(self, instance):
        question_sets = QuestionSet.objects.filter(assessment=instance)
        return QuestionSetAnswer.objects.filter(question_set_access__question_set__in=question_sets).distinct('session').count()

    def get_score(self, instance):
        question_sets = QuestionSet.objects.filter(assessment=instance)
        question_sets_answers = []

        for question_set in question_sets:
            if question_set.evaluated:
                correct_answers_percentage = self.__get_question_set_correct_answers_percentage(question_set)
                if correct_answers_percentage is not None:
                    question_sets_answers.append(correct_answers_percentage)

        score = None
        if question_sets_answers:
            score = sum(question_sets_answers) / float(len(question_sets_answers))

        return score

class UserTableSerializer(serializers.ModelSerializer):
    """
    Users table serializer.
    """

    # Last session
    last_session = serializers.SerializerMethodField()
    # Full name
    full_name = serializers.SerializerMethodField()
    # Number of question_sets completed by the student
    completed_question_sets_count = serializers.SerializerMethodField()
    # Number of questions completed by the student
    completed_questions_count = serializers.SerializerMethodField()
    # Number of assessments that the student is linked to
    assessments_count = serializers.SerializerMethodField()
    # If the student has an assessment that is not done yet
    assessment_complete = serializers.SerializerMethodField()
    # All assessments assigned to the student
    assessments = serializers.SerializerMethodField()

    # Languages and countries formatted information
    language_name = serializers.SerializerMethodField()
    language_code = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    country_code = serializers.SerializerMethodField()

    # Group that the student is linked to
    group = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    # Average speed of all questions answered by the student
    speed = serializers.SerializerMethodField()
    # Students can only be deleted after more than 1 year of inactivity
    can_delete = serializers.SerializerMethodField()
    # Global sel data of the student
    sel_overview = serializers.SerializerMethodField()
    # Average score of the student for all the completed assessments
    average_score = serializers.SerializerMethodField()
    # Effort of the student
    honey = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'first_name', 'last_name', 'last_session', 'completed_question_sets_count', 'active_status_updated_on',
                  'assessments_count', 'language_name', 'language_code', 'country_name', 'country_code', 'group', 'is_active', 'can_delete', 'grade', 'assessment_complete',
                  'assessments', 'speed', 'sel_overview', 'average_score', 'completed_questions_count', 'honey')

    def get_full_name(self, instance):
        return (instance.first_name + ' ' + instance.last_name)

    def get_last_session(self, instance):
        last_session = instance.answersession_set.last()
        if not last_session:
            return None
        else:
            return last_session.start_date

    def get_completed_question_sets_count(self, instance):
        return QuestionSet.objects.filter(
            questionsetaccess__student=instance,
            questionsetaccess__question_set_answers__complete=True
        ).distinct().count()

    def get_completed_questions_count(self, instance):
        return Answer.objects.filter(
            question_set_answer__question_set_access__student=instance,
        ).distinct('question').count()

    def get_assessments_count(self, instance):
        return Assessment.objects.filter(
            questionset__questionsetaccess__student=instance,
            questionset__questionsetaccess__start_date__lte=datetime.date.today(),
            questionset__questionsetaccess__end_date__gte=datetime.date.today()
        ).distinct().count()

    def get_assessment_complete(self, instance):
        assessment_instance = Assessment.objects.filter(
            questionset__questionsetaccess__student=instance,
            questionset__questionsetaccess__start_date__lte=datetime.date.today(),
            questionset__questionsetaccess__end_date__gte=datetime.date.today()
        ).distinct().first()

        completed_question_sets = QuestionSet.objects.filter(
            assessment=assessment_instance,
            questionsetaccess__student=instance,
            questionsetaccess__question_set_answers__complete=True,
            questionsetaccess__question_set_answers__session__student=instance
        ).distinct().count()

        total_question_sets = QuestionSet.objects.filter(
            assessment=assessment_instance,
            questionsetaccess__student=instance,
        ).distinct().count()

        return (completed_question_sets == total_question_sets)

    # could be more optimized, 0.30s for some assessments
    def get_assessments(self, instance):
        start_time = time.perf_counter()
        answer_sessions = AnswerSession.objects.filter(student=instance)
        question_set_answers = QuestionSetAnswer.objects.filter(
            session__in=answer_sessions,
            complete=True,
            question_set_access__start_date__lte=datetime.date.today(),
            question_set_access__end_date__gte=datetime.date.today()
        ).prefetch_related(
            'answers__valid',
            'question_set_access__question_set'
        )
        assessments = Assessment.objects.filter(
            questionset__in=question_set_answers.values('question_set_access__question_set')
        )

        student_scores = question_set_answers.annotate(
            student_score=Round(
                Sum('answers__valid', output_field=IntegerField()) / Count('answers', output_field=IntegerField()),
                1
            )
        ).values('question_set_access__question_set', 'student_score')

        assessments_data = AssessmentTableSerializer(assessments, many=True, context={'student_pk': int(instance.id), 'student_scores': student_scores}).data
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"The execution time of get_assessments is: {execution_time}")
        return assessments_data

    def get_language_name(self, instance):
        return instance.language.name_en

    def get_language_code(self, instance):
        return instance.language.code

    def get_country_name(self, instance):
        return instance.country.name_en

    def get_country_code(self, instance):
        return instance.country.code

    def get_grade(self, instance):
        return instance.grade

    def get_group(self, instance):
        return [instance.group.name] if instance.group else []

    def get_speed(self, instance):
        student_speed = None
        student_answers = Answer.objects.filter(
            question_set_answer__session__student=instance
        ).exclude(question__question_type__exact='SEL')

        if student_answers:
            student_speed = student_answers.annotate(
                durations = ExpressionWrapper(F('end_datetime') - F('start_datetime'), output_field=fields.DurationField()),
            ).aggregate(Avg('durations'))['durations__avg'].total_seconds()

        return student_speed

    def get_can_delete(self, instance):
        if instance.is_active == False and instance.active_status_updated_on:
            if abs((instance.active_status_updated_on - instance.date_joined).total_seconds()) < 1:
                return True

            return (timezone.now() - instance.active_status_updated_on).days > 365

        return False

    def get_sel_overview(self, instance):
        sel_data = {}
        choices = ['NOT_REALLY', 'A_LITTLE', 'A_LOT']
        answers = AnswerSEL.objects.filter(question_set_answer__session__student=instance)

        if answers:
            last_sel_answer = answers.latest('end_datetime')
            last_session_pk = last_sel_answer.question_set_answer.session.pk
            last_session_answers = answers.filter(question_set_answer__session=last_session_pk)
            vals = [choices.index(answer.statement) for answer in answers]
            last_session_vals = [choices.index(answer.statement) for answer in last_session_answers]
            average = round(sum(vals) / len(vals))
            last_session_average = round(sum(last_session_vals) / len(last_session_vals))
            progress = 0 if len(vals) == 1 or average == last_session_average else -1 if average > last_session_average else 1
            sel_data['average_statement'] = choices[average]
            sel_data['progress'] = progress

        return sel_data

    # To get a look
    def get_average_score(self, instance):
        question_sets = QuestionSet.objects.filter(
        questionsetaccess__student=instance,
        ).annotate(
        correct_answers=Sum(
            Case(
                When(questionsetaccess__question_set_answers__answers__valid=True, then=1),
                output_field=IntegerField()
            )
        ),
        total_answers=Count('questionsetaccess__question_set_answers__answers')
        ).annotate(
            percentage=ExpressionWrapper(
                F('correct_answers') / F('total_answers'),
                output_field=FloatField()
            ) * 100
        ).values('percentage')

        average = question_sets.filter(percentage__isnull=False).aggregate(Avg('percentage'))

        return average['percentage__avg'] if average['percentage__avg'] else None

    def get_honey(self, instance):
        return instance.profile_set.first().effort


class StudentLinkedAssessmentsSerializer(serializers.ModelSerializer):

    question_set_access = serializers.SerializerMethodField()
    student_score = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'question_set_access', 'student_score')

    def get_question_set_access(self, instance):

        start_time = time.perf_counter()
        student_pk = self.context['student_pk']

        question_set_list = QuestionSet.objects.filter(assessment=instance)
        question_set_access_list = []

        for question_set in question_set_list:
            question_set_access = list(QuestionSetAccess.objects.filter(
                question_set=question_set, student=student_pk).values())

            if question_set_access:
                access_dict = {
                    'question_set_id': question_set.id,
                    'question_set_name': question_set.name,
                    'question_set_access_id': question_set_access[0]['id'],
                    'start_date': question_set_access[0]['start_date'],
                    'end_date': question_set_access[0]['end_date']
                }

                question_set_access_list.append(access_dict)

        end_time = time.perf_counter()
        execution_time = end_time - start_time
#        print(f"The execution time of get_question_set_access is: {execution_time}")
        return question_set_access_list

    def __get_question_set_correct_answers_percentage(self, question_set, student):
        """
        Get the percentage of correct answers for the given question_set and student
        """
        start_time = time.perf_counter()
        correct_answers_percentage = 0
        question_set_total_answers = Question.objects.filter(question_set=question_set).exclude(question_type='SEL').count()
        question_set_answers = QuestionSetAnswer.objects.filter(
            question_set_access__question_set=question_set,
            question_set_access__student=student
        )
        if not question_set_total_answers or not question_set_answers:
            return None
        question_set_total_correct_answers = Answer.objects.filter(
                question_set_answer__in=question_set_answers,
                valid=True
            ).exclude(question__question_type='SEL').count()
        question_set_total_wrong_answers = 0
        if question_set_total_correct_answers == 0:
            question_set_total_wrong_answers = Answer.objects.filter(
                question_set_answer__in=question_set_answers,
                valid=False
            ).exclude(question__question_type='SEL').count()
        if (question_set_total_answers != 0):
            if question_set_total_correct_answers != 0:
                correct_answers_percentage = round((question_set_total_correct_answers / question_set_total_answers) * 100, 1)
            elif question_set_total_wrong_answers != 0:
                correct_answers_percentage = 0

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        #print(f"The execution time of __get_question_set_correct_answers_percentage is: {execution_time}")
        return min(correct_answers_percentage, 100.0)

    # to investigate
    def get_student_score(self, instance):
        start_time = time.perf_counter()
        student_pk = self.context['student_pk']
        student = User.objects.get(pk=student_pk)
        question_sets = QuestionSet.objects.filter(
            assessment=instance,
            questionsetaccess__student=student,
        ).distinct()
        question_set_scores = []
        for question_set in question_sets:
            question_set_score = self.__get_question_set_correct_answers_percentage(question_set, student)
            if question_set_score is not None:
                question_set_scores.append(question_set_score)
        if len(question_set_scores) == 0:
            return None

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"The execution time of get_student_score is: {execution_time}")
        return sum(question_set_scores) / len(question_set_scores)


class QuestionSetTableSerializer(serializers.ModelSerializer):
    """
    Question sets table serializer.
    """

    # Total of students with active access to this question_set
    students_count = serializers.SerializerMethodField()
    # Total of students with active access to this question_set and who completed it
    students_completed_count = serializers.SerializerMethodField()
    # Total of students who completed this question_set
    overall_students_completed_count = serializers.SerializerMethodField()
    # Total of questions in this question_set
    questions_count = serializers.SerializerMethodField()
    # Assesment id
    assessment_id = serializers.SerializerMethodField()
    # QuerySet learning objective
    learning_objective = NestedRelatedField(
        model=LearningObjective, serializer_class=LearningObjectiveSerializer, allow_null=True)

    class Meta:
        model = QuestionSet
        fields = ('id', 'assessment_id', 'name', 'students_count', 'students_completed_count', 'order',
                  'overall_students_completed_count', 'questions_count', 'learning_objective', 'icon',)

    def get_students_count(self, instance):
        return User.objects.filter(
            questionsetaccess__question_set=instance,
            questionsetaccess__start_date__lte=datetime.date.today(),
            questionsetaccess__end_date__gte=datetime.date.today()
        ).distinct().count()

    def get_students_completed_count(self, instance):
        return User.objects.filter(
            questionsetaccess__question_set=instance,
            questionsetaccess__start_date__lte=datetime.date.today(),
            questionsetaccess__end_date__gte=datetime.date.today(),
            questionsetaccess__question_set_answers__complete=True,
        ).distinct().count()

    def get_overall_students_completed_count(self, instance):
        return User.objects.filter(questionsetaccess__question_set=instance).distinct().count()

    def get_questions_count(self, instance):
        return Question.objects.filter(question_set=instance).count()

    def get_assessment_id(self, instance):
        return Assessment.objects.filter(id=instance.assessment.id).values_list('id', flat=True)[0]


class QuestionTableSerializer(serializers.ModelSerializer):
    """
    Questions table serializer.
    """

    has_attachment = serializers.SerializerMethodField()
    question_type = serializers.SerializerMethodField()

    # Parent assessment grade
    grade = serializers.SerializerMethodField()
    # Parent assessment subject
    subject = serializers.SerializerMethodField()
    # Parent assessment topic
    topic = serializers.SerializerMethodField()
    # Lowest, average and highest answer times in milliseconds
    speeds = serializers.SerializerMethodField()
    # Number of time the assessment has been played by a student
    plays = serializers.SerializerMethodField()
    # Number of students invited with QuestionSetAccess to the question topic
    invites = serializers.SerializerMethodField()
    # Score is the global average score for this question amongst all the students
    score = serializers.SerializerMethodField()
    learning_objective = serializers.SerializerMethodField()
    assessment = serializers.SerializerMethodField()
    question_set = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'title', 'order', 'created_at', 'topic', 'question_type', 'plays', 'invites', 'question_set',
                  'has_attachment', 'score', 'grade', 'subject', 'topic', 'learning_objective', 'assessment', 'speeds')

    def __get_all_answers(self, instance):
        return Answer.objects.filter(question=instance)

    def get_assessment(self, instance):
        return instance.question_set.assessment.id

    def get_question_set(self, instance):
        return instance.question_set.id

    def get_has_attachment(self, instance):
        if(Attachment.objects.filter(question=instance)):
            return True
        return False

    def get_question_type(self, instance):
        return instance.get_question_type_display()

    def get_learning_objective(self, instance):
        learning_objective = instance.question_set.learning_objective
        serializer = LearningObjectiveSerializer(learning_objective)
        return serializer.data

    # NO LONGER USED: Overall percentage of correct answers on this question on first students' try
    def __get_correct_answers_percentage_first(self, instance):

        accessible_students = self.context.get("accessible_students")

        total_answers = 0
        total_correct_answers = 0

        for student in accessible_students:

            earliest_question_set_answers = QuestionSetAnswer.objects.filter(
                question_set_access__student=student,
                question_set_access__question_set=instance.question_set,
                complete=True
            )

            if earliest_question_set_answers:

                earliest_question_set_answer = earliest_question_set_answers.earliest("start_date")
                answers_list = Answer.objects.filter(
                    question=instance,
                    question_set_answer=earliest_question_set_answer
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

    # NO LONGER USED:: Overall percentage of correct answers on this question on last students' try
    def __get_correct_answers_percentage_last(self, instance):

        accessible_students = self.context.get("accessible_students")

        total_answers = 0
        total_correct_answers = 0

        for student in accessible_students:

            latest_question_set_answers = QuestionSetAnswer.objects.filter(
                question_set_access__student=student,
                question_set_access__question_set=instance.question_set,
                complete=True
            )

            if latest_question_set_answers:

                latest_question_set_answer = latest_question_set_answers.latest("start_date")
                answers_list = Answer.objects.filter(
                    question=instance,
                    question_set_answer=latest_question_set_answer
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

    def get_grade(self, instance):
        return Assessment.objects.get(id=instance.question_set.assessment.id).grade

    def get_subject(self, instance):
        return Assessment.objects.get(id=instance.question_set.assessment.id).subject

    def get_topic(self, instance):
        topic = Assessment.objects.get(id=instance.question_set.assessment.id).topic
        serializer = TopicSerializer(topic)
        return serializer.data

    def get_speeds(self, instance):
        speeds = {}
        answers = Answer.objects.filter(question=instance)
        if answers:
            durations = answers.annotate(
                durations = ExpressionWrapper(F('end_datetime') - F('start_datetime'), output_field=fields.DurationField()))
            speeds['slowest'] = round(durations.aggregate(Max('durations'))['durations__max'].total_seconds(), 3) * 1000
            speeds['fastest'] = round(durations.aggregate(Min('durations'))['durations__min'].total_seconds(), 3) * 1000
            speeds['average'] = round(durations.aggregate(Avg('durations'))['durations__avg'].total_seconds(), 3) * 1000
        return speeds

    def get_topic(self, instance):
        return instance.question_set.name

    def get_plays(self, instance):
        return self.__get_all_answers(instance).count()

    def get_invites(self, instance):
        return QuestionSetAccess.objects.filter(question_set=instance.question_set).count()

    def get_score(self, instance):
        correct_answers_percentage = 0
        all_answers = self.__get_all_answers(instance)
        if not all_answers:
            return None

        total_answers = all_answers.count()
        total_correct_answers = all_answers.filter(valid=True).exclude(question__question_type='SEL').count()
        total_wrong_answers = 0
        if total_correct_answers == 0:
            total_wrong_answers = all_answers.filter(valid=False ).exclude(question__question_type='SEL').count()

        if total_correct_answers != 0:
            correct_answers_percentage = round((total_correct_answers / total_answers) * 100, 1)
        elif total_wrong_answers != 0:
            correct_answers_percentage = 0

        return min(correct_answers_percentage, 100.0)

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
            'QuestionDragAndDrop': QuestionDragAndDropTableSerializer,
            'QuestionSEL': QuestionSELTableSerializer,
            'QuestionDomino': QuestionDominoTableSerializer,
            'QuestionCalcul': QuestionCalculTableSerializer,
            'QuestionCustomizedDragAndDrop': QuestionCustomizedDragAndDropTableSerializer,
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
            ('expected_value', 'start', 'end', 'step',)

class QuestionCustomizedDragAndDropTableSerializer(AbstractQuestionDetailsTableSerializer):

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionCustomizedDragAndDrop
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + \
            ('first_value', 'first_style', 'second_value', 'second_style', 'operator', 'shape',)

class QuestionCalculTableSerializer(AbstractQuestionDetailsTableSerializer):

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionCalcul
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + \
            ('first_value', 'second_value', 'operator',)

class QuestionSelectTableSerializer(AbstractQuestionDetailsTableSerializer):

    options = NestedRelatedField(
        model=SelectOption, serializer_class=SelectOptionSerializer, many=True)

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionSelect
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + \
            ('options', )

class QuestionSELTableSerializer(AbstractQuestionDetailsTableSerializer):

    median_statement = serializers.SerializerMethodField()
    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionSEL
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + \
            ('sel_type', 'median_statement')

    def get_median_statement(self, instance):
        answers = AnswerSEL.objects.filter(question=instance)
        if answers:
            most_common_answer = answers.annotate(most_common=Count('statement')).order_by('-most_common').first()
            return most_common_answer.statement
        return None


class QuestionDominoTableSerializer(AbstractQuestionDetailsTableSerializer):
    options = NestedRelatedField(
        model=DominoOption, serializer_class=DominoOptionSerializer, many=True)

    class Meta(AbstractQuestionDetailsTableSerializer.Meta):
        model = QuestionDomino
        fields = AbstractQuestionDetailsTableSerializer.Meta.fields + \
            ('expected_value', 'options',)

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
    # Total of question_sets completed per assessment
    completed_question_sets_count = serializers.SerializerMethodField()
    # Total of question_sets accessible by the student
    accessible_question_sets_count = serializers.SerializerMethodField()
    # Last session datetime
    last_session = serializers.SerializerMethodField()
    # Answers of the assessment (can be filtered via query params)
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'subject', 'completed_question_sets_count',
                  'accessible_question_sets_count', 'last_session', 'answers',
                  'icon')

    def get_completed_question_sets_count(self, instance):
        student_pk = self.context['student_pk']

        return QuestionSet.objects.filter(
            assessment=instance,
            questionsetaccess__student=student_pk,
            questionsetaccess__question_set_answers__complete=True
        ).distinct().count()

    def get_accessible_question_sets_count(self, instance):
        student_pk = self.context['student_pk']

        return QuestionSet.objects.filter(
            questionsetaccess__student=student_pk,
            assessment=instance
        ).distinct().count()

    def get_subject(self, instance):
        return instance.get_subject_display()

    def get_last_session(self, instance):
        student_pk = self.context['student_pk']

        last_session = AnswerSession.objects.filter(
            question_set_answers__question_set_access__question_set__assessment=instance,
            student=student_pk,
        ).latest('start_date')

        return last_session.start_date

    def get_answers(self, instance):
        student_pk = self.context['student_pk']
        answers = Answer.objects.filter(
            question_set_answer__question_set_access__question_set__assessment=instance,
            question_set_answer__question_set_access__student=student_pk
        ).distinct()

        answers_data = AnswerTableSerializer(answers, many=True).data

        return answers_data


class QuestionSetAnswerTableSerializer(serializers.ModelSerializer):
    """
    QuestionSet answer serializer
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
        model = QuestionSet
        fields = ('id', 'name', 'questions_count', 'student_tries_count',
                  'correct_answers_percentage_first_try',
                  'correct_answers_percentage_last_try',
                  'last_submission')

    def get_questions_count(self, instance):
        return Question.objects.filter(question_set=instance).count()

    def get_student_tries_count(self, instance):
        student_pk = self.context['student_pk']

        return QuestionSetAnswer.objects.filter(
            question_set_access__question_set=instance,
            session__student=student_pk
        ).distinct().count()

    def get_correct_answers_percentage_first_try(self, instance):
        student_pk = self.context['student_pk']

        first_question_set_answer = QuestionSetAnswer.objects.filter(
            question_set_access__question_set=instance,
            session__student=student_pk,
            complete=True
        )

        if not first_question_set_answer.exists():
            return None

        if (instance.evaluated != True):
            return None

        first_question_set_answer = first_question_set_answer.earliest('end_date')

        total_answers = Answer.objects.filter(
            question_set_answer=first_question_set_answer
        ).exclude(question__question_type='SEL').distinct().count()

        total_valid_answers = Answer.objects.filter(
            question_set_answer=first_question_set_answer,
            valid=True
        ).exclude(question__question_type='SEL').distinct().count()

        correct_answers_percentage = None

        if total_answers:
            correct_answers_percentage = round(
                (100 * total_valid_answers / total_answers), 2)

        return correct_answers_percentage

    def get_correct_answers_percentage_last_try(self, instance):

        student_pk = self.context['student_pk']

        last_question_set_answer = QuestionSetAnswer.objects.filter(
            question_set_access__question_set=instance,
            session__student=student_pk,
            complete=True
        )

        if not last_question_set_answer.exists():
            return None

        if (instance.evaluated != True):
            return None

        last_question_set_answer = last_question_set_answer.latest('end_date')

        total_answers = Answer.objects.filter(
            question_set_answer=last_question_set_answer
        ).exclude(question__question_type='SEL').distinct().count()

        total_valid_answers = Answer.objects.filter(
            question_set_answer=last_question_set_answer,
            valid=True
        ).exclude(question__question_type='SEL').distinct().count()

        correct_answers_percentage = None

        if total_answers:
            correct_answers_percentage = round(
                (100 * total_valid_answers / total_answers), 2)

        return correct_answers_percentage

    def get_last_submission(self, instance):
        student_pk = self.context['student_pk']

        last_question_set_answer = QuestionSetAnswer.objects.filter(
            question_set_access__question_set=instance,
            session__student=student_pk
        )

        if not last_question_set_answer.exists():
            return None

        return last_question_set_answer.latest('end_date').end_date


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
    student_speed = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'title', 'order',
                  'question_type', 'average_duration',
                  'correctly_answered_first_try',
                  'correctly_answered_last_try',
                  'student_speed')

    def get_average_duration(self, instance):
        student_pk = self.context['student_pk']

        all_answers = Answer.objects.filter(
            question=instance,
            question_set_answer__complete=True,
            question_set_answer__session__student=student_pk
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

        first_question_set_answer = QuestionSetAnswer.objects.filter(
            question_set_access__question_set__question=instance,
            session__student=student_pk,
            complete=True
        )

        if not first_question_set_answer:
            return None

        first_question_set_answer = first_question_set_answer.earliest('end_date')

        return Answer.objects.get(
            question_set_answer=first_question_set_answer,
            question=instance
        ).valid

    def get_correctly_answered_last_try(self, instance):
        student_pk = self.context['student_pk']

        last_question_set_answer = QuestionSetAnswer.objects.filter(
            question_set_access__question_set__question=instance,
            session__student=student_pk,
            complete=True
        )

        if not last_question_set_answer:
            return None

        last_question_set_answer = last_question_set_answer.latest('end_date')

        return Answer.objects.get(
            question_set_answer=last_question_set_answer,
            question=instance
        ).valid

    def get_student_speed(self, instance):
        student_pk = self.context['student_pk']
        try:
            answer = Answer.objects.annotate(
                duration = ExpressionWrapper(F('end_datetime') - F('start_datetime'), output_field=fields.DurationField())
            ).get(
                question_set_answer__session__student=student_pk,
                question=instance
            )
            return answer.duration.total_seconds() * 1000
        except:
            return None

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
            'AnswerDragAndDrop': AnswerDragAndDropTableSerializer,
            'AnswerSEL': AnswerSELTableSerializer,
            'AnswerDomino': AnswerDominoTableSerializer,
            'AnswerCalcul': AnswerCalculTableSerializer,
            'AnswerCustomizedDragAndDrop': AnswerCustomizedDragAndDropTableSerializer
        }

    def to_representation(self, obj):
        sub_obj = Answer.objects.get_subclass(id=obj.id)
        return super().to_representation(sub_obj)


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

class AnswerCalculTableSerializer(AbstractAnswerTableSerializer):

    question = NestedRelatedField(
        model=QuestionCalcul, serializer_class=QuestionCalculTableSerializer, many=False)

    class Meta(AbstractAnswerTableSerializer.Meta):
        model = AnswerCalcul
        fields = AbstractAnswerTableSerializer.Meta.fields + \
            ('value', 'question',)

class AnswerCustomizedDragAndDropTableSerializer(AbstractAnswerTableSerializer):

    question = NestedRelatedField(
        model=QuestionCalcul, serializer_class=QuestionCustomizedDragAndDropTableSerializer, many=False)

    class Meta(AbstractAnswerTableSerializer.Meta):
        model = AnswerCustomizedDragAndDrop
        fields = AbstractAnswerTableSerializer.Meta.fields + \
            ('left_value',  'right_value', 'final_value', 'question',)

class AnswerSelectTableSerializer(AbstractAnswerTableSerializer):

    question = NestedRelatedField(
        model=QuestionSelect, serializer_class=QuestionSelectTableSerializer, many=False)

    class Meta(AbstractAnswerTableSerializer.Meta):
        model = AnswerSelect
        fields = AbstractAnswerTableSerializer.Meta.fields + \
            ('selected_option', 'question',)


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
        return list(serializer.data)

class AnswerSELTableSerializer(AbstractAnswerTableSerializer):

    question = NestedRelatedField(
        model=QuestionSEL, serializer_class=QuestionSELTableSerializer, many=False)

    class Meta(AbstractAnswerTableSerializer.Meta):
        model = AnswerSEL
        fields = AbstractAnswerTableSerializer.Meta.fields + \
            ('statement', 'question',)

class AnswerDominoTableSerializer(AbstractAnswerTableSerializer):

    question = NestedRelatedField(
        model=QuestionDomino, serializer_class=QuestionDominoTableSerializer, many=False)

    class Meta(AbstractAnswerTableSerializer.Meta):
        model = AnswerDomino
        fields = AbstractAnswerTableSerializer.Meta.fields + \
            ('selected_domino', 'question',)

class ScoreByQuestionSetSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()
    question_sets = serializers.SerializerMethodField()
    student_access = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'question_sets', 'student_access', 'group')

    def get_group(self, instance):
        group = Group.objects.filter(student_group=instance)
        serializer = GroupSerializer(group, many = True)
        return serializer.data

    def get_full_name(self, instance):
        return (instance.first_name + ' ' + instance.last_name)

    def get_student_access(self, instance):
        assessment_pk = self.context['assessment_pk']

        question_sets = QuestionSet.objects.filter(assessment=assessment_pk)
        for access in QuestionSetAccess.objects.filter(student=instance, question_set__in=question_sets):
            if QuestionSetAnswer.objects.filter(question_set_access=access, session__student=instance, complete=True):
                return True
        return False

    def get_question_sets(self, instance):
        assessment_pk = self.context['assessment_pk']
        question_set_score = []

        for question_set in QuestionSet.objects.filter(assessment=assessment_pk):

            if question_set.evaluated:
                total_answers = Question.objects.filter(question_set=question_set).exclude(question_type='SEL').count()
                access = QuestionSetAccess.objects.filter(question_set=question_set, student=instance)

                if access:
                    if QuestionSetAnswer.objects.filter(question_set_access=access.first(), complete=True):
                        earliest_question_set_answer = QuestionSetAnswer.objects.filter(
                            question_set_access=access.first(),
                            complete=True
                        ).earliest('start_date')

                        total_correct_answers = Answer.objects.filter(
                            question_set_answer=earliest_question_set_answer,
                            valid=True
                        ).exclude(question__question_type='SEL').count()

                        correct_answers_percentage = 0

                        if (total_answers != 0):
                            correct_answers_percentage = round((total_correct_answers / total_answers) * 100, 1)

                        question_set_score_dict = {
                            question_set.name: correct_answers_percentage
                        }
                        question_set_score.append(question_set_score_dict)
                    else:
                        question_set_score_dict = {
                            question_set.name: 'not_started'
                        }
                        question_set_score.append(question_set_score_dict)

                else:
                    question_set_score_dict = {
                        question_set.name: None
                    }
                    question_set_score.append(question_set_score_dict)
            else:
                question_set_score_dict = {
                    question_set.name: 'not_evaluated'
                }
                question_set_score.append(question_set_score_dict)

        return question_set_score


class QuestionSetLisForDashboardSerializer(serializers.ModelSerializer):

    started = serializers.SerializerMethodField()

    class Meta:
        model = QuestionSet
        fields = ('id', 'name', 'evaluated', 'started')

    def get_started(self, instance):

        started = False

        if QuestionSetAnswer.objects.filter(question_set_access__question_set=instance, complete=True):
            started = True

        return started


class AssessmentListForDashboardSerializer(serializers.ModelSerializer):

    question_sets = serializers.SerializerMethodField()
    evaluated = serializers.SerializerMethodField()
    started = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'evaluated', 'question_sets', 'started')

    def get_question_sets(self, instance):

        supervisor = self.context['supervisor']
        students = User.objects.filter(created_by=supervisor)
        question_sets = []

        #Iterate through question_sets
        for question_set in QuestionSet.objects.filter(assessment=instance, evaluated=True):
            accesses = QuestionSetAccess.objects.filter(question_set=question_set, student__in=students)
            total_answers = Question.objects.filter(question_set=question_set).exclude(question_type='SEL').count()
            students_average = []

            #Iterate through the supervisors student to get question_set accesses
            for access in accesses:
                #For each question_set access, check for completed question_set answers
                if QuestionSetAnswer.objects.filter(question_set_access=access, complete=True):
                    #Get the first try
                    earliest_question_set_answer = QuestionSetAnswer.objects.filter(
                        question_set_access=access,
                        complete=True
                    ).earliest('start_date')

                    #Get correct answers for this first try
                    total_correct_answers = Answer.objects.filter(
                        question_set_answer=earliest_question_set_answer,
                        valid=True
                    ).exclude(question__question_type='SEL').count()

                    percentage = 0

                    if(total_answers != 0):
                        percentage = round((total_correct_answers / total_answers) * 100, 1)

                    students_average.append(percentage)

            if len(students_average) != 0:
                question_set_dict = {
                    'id': question_set.id,
                    'name': question_set.name,
                    'average': round(sum(students_average)/len(students_average), 1)
                }
            else :
                question_set_dict = {
                    'id': question_set.id,
                    'name': question_set.name,
                    'average': None
                }
            question_sets.append(question_set_dict)

        return question_sets


    def get_evaluated(self, instance):

        evaluated = False

        for question_set in QuestionSet.objects.filter(assessment=instance):

            if question_set.evaluated == True:
                evaluated = True

        return evaluated

    def get_started(self, instance):
        started = False
        for question_set in self.get_question_sets(instance):
            if question_set['average'] != None:
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
        question_set_pk = self.context['question_set_pk']
        total_answers = 0
        students = User.objects.filter(created_by=supervisor)

        for access in QuestionSetAccess.objects.filter(question_set=question_set_pk, student__in=students):

            if QuestionSetAnswer.objects.filter(question_set_access=access, session__student__in=students, complete=True):
                earliest_question_set_answer = QuestionSetAnswer.objects.filter(
                    question_set_access=access,
                    session__student__in=students,
                    complete=True
                ).earliest('start_date')

                total_answers = total_answers + \
                    Answer.objects.filter(
                        question_set_answer=earliest_question_set_answer, question=instance).count()

        return total_answers

    def get_correct_answers_count(self,  instance):

        supervisor = self.context['supervisor']
        question_set_pk = self.context['question_set_pk']
        total_correct_answers = 0
        students = User.objects.filter(created_by=supervisor)

        for access in QuestionSetAccess.objects.filter(question_set=question_set_pk, student__in=students):

            if QuestionSetAnswer.objects.filter(question_set_access=access, session__student__in=students, complete=True):
                earliest_question_set_answer = QuestionSetAnswer.objects.filter(
                    question_set_access=access,
                    session__student__in=students,
                    complete=True
                ).earliest('start_date')

                total_correct_answers = total_correct_answers + Answer.objects.filter(
                    question_set_answer=earliest_question_set_answer, question=instance, valid=True).count()

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


class StudentsByQuestionSetAccessSerializer(serializers.ModelSerializer):

    student = NestedRelatedField(
        model=User, serializer_class=UserFullNameSerializer, many=False)
    question_set_first_try = serializers.SerializerMethodField()

    class Meta:
        model = QuestionSetAccess
        fields = ('id', 'student', 'question_set_first_try')

    def get_question_set_first_try(self, instance):

        if QuestionSetAnswer.objects.filter(question_set_access=instance, complete=True):
            return QuestionSetAnswer.objects.filter(question_set_access=instance, complete=True).values().earliest('start_date')
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

class GroupTableSerializer(serializers.ModelSerializer):
    """
    Groups table serializer.
    """

    students_count = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField()
    # Average is the global average score of students in this group for all the assessments they're assigned
    average = serializers.SerializerMethodField()
    # Average of each assessment to which students in this group are assigned
    assessments_average = serializers.SerializerMethodField()
    # Group average is the average score of all the students of the same group
    group_average = serializers.SerializerMethodField()
    # Score average of all the students of the same grade
    grade_average = serializers.SerializerMethodField()
    # Speed is the average speed of all students of the groups to answer questions
    speed = serializers.SerializerMethodField()
    # Honey is the average of effort amongst all the students
    honey = serializers.SerializerMethodField()
    class Meta:
        model = Group
        fields = '__all__'

    def __get_question_sets(self, instance):
        if (not hasattr(self, 'get_question_sets')) or (hasattr(self, 'instance_name') and self.instance_name!=instance.name):
            print('instance=  ', instance)
            students = User.objects.filter(group=instance)
            question_sets = QuestionSetAccess.objects.filter(student_id__in=students).select_related('question_set', 'question_set__assessments').values_list('question_set', flat=True)
            self.get_question_sets = question_sets
            self.instance_name = instance.name
            return question_sets
        return self.get_question_sets
    
    def get_students_count(self, instance):
        return User.objects.filter(group=instance).count()
        
    def get_questions_count(self, instance):
        question_sets = self.__get_question_sets(instance)
        questions = Question.objects.filter(question_set__in=question_sets, question_set__questionsetaccess__student__group=instance).distinct()
        return questions.count()

    # Need to not return duplicates
    # Some groups are taking 1.45s to load, could be optimized
    def get_assessments_average(self, instance):
        if (not hasattr(self, 'assessments_average')) or (hasattr(self, 'instance_average_name') and self.instance_average_name!=instance.name):
            start_time = time.perf_counter()
            question_sets = self.__get_question_sets(instance)
            if question_sets:
                assessments_id = QuestionSet.objects.filter(pk__in=question_sets).values_list('assessment', flat=True).distinct()
                assessments = Assessment.objects.filter(id__in=assessments_id)
                assessments_average = []
                assessments_average = calculate_assessments_score(assessments)
                self.assessments_average = assessments_average
                self.instance_average_name = instance.name
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                print(f"The execution time of get_assessments_average is: {execution_time}")
                return assessments_average
            else:
                self.assessments_average = None
                return None
        return self.assessments_average


    def get_average(self, instance):
        assessments_average = self.get_assessments_average(instance)
        if assessments_average:
            filtered_assessments_average = []
            for assessment in assessments_average:
                if assessment and assessment > 0:
                    filtered_assessments_average.append(assessment)
            if len(filtered_assessments_average):
                return sum(filtered_assessments_average) / len(filtered_assessments_average)
        else:
            return None

    # to investigate
    def get_group_average(self, instance):
        start_time = time.perf_counter()
        students = User.objects.filter(group=instance)
        score_list = []
        for student in students:
            assessments = list(Assessment.objects.filter(
                questionset__questionsetaccess__student=student
            ).distinct().values_list('id', flat=True))
            for assessment in assessments:
                assessment_result = calculate_student_score(assessment, student.id)
                if assessment_result and assessment_result > 0:
                    score_list.append(assessment_result)
        if len(score_list):
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            print(f"The execution time of get_group_average is: {execution_time}")
            return sum(score_list) / len(score_list)
        return None

    def get_grade_average(self, instance):
        start_time = time.perf_counter()
        student_grades = [grade for grade in User.objects.filter(group=instance).values_list('grade', flat=True).distinct()]
        if len(student_grades) and student_grades.count(student_grades[0]) == len(student_grades):
            grade = student_grades[0]
            students = User.objects.filter(grade=grade)
            score_list = []
            for student in students:
                assessments = list(Assessment.objects.filter(
                    grade=grade,
                    questionset__questionsetaccess__student=student
                ).distinct().values_list('id', flat=True))
                for assessment in assessments:
                    assessment_result = calculate_student_score(assessment, student.id)
                    if assessment_result and assessment_result > 0:
                        score_list.append(assessment_result)
            if len(score_list) > 0:
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                print(f"The execution time of get_grade_average is: {execution_time}")
                return sum(score_list) / len(score_list)
        return None


    def get_speed(self, instance):
        students = User.objects.filter(group=instance)
        students_average = []
        # get the average speed of each student
        for student in students:
            student_answers = Answer.objects.filter(question_set_answer__session__student=student)
            if student_answers:
                student_result = student_answers.annotate(
                    durations = ExpressionWrapper(F('end_datetime') - F('start_datetime'), output_field=fields.DurationField()),
                ).aggregate(Avg('durations'))['durations__avg']
                students_average.append(student_result)

        if len(students_average) > 0:
            return sum(students_average, datetime.timedelta()) / len(students_average)
        else:
            return None

    def get_honey(self, instance):
        students = User.objects.filter(group=instance)
        effort_average = 0
        students_effort = Profile.objects.filter(student__in=students)
        if students_effort:
            students_effort = students_effort.aggregate(Avg('effort'))['effort__avg']
            effort_average = round(students_effort, 1)
        return effort_average