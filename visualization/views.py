
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action

from django.shortcuts import get_object_or_404
from django.db.models.functions import Lower
from django.db.models import Q

from users.models import User, Group
from visualization.serializers import GroupTableSerializer, StudentLinkedAssessmentsSerializer, UserTableSerializer, AssessmentTableSerializer, QuestionTableSerializer, QuestionSetTableSerializer, AssessmentAnswerTableSerializer, QuestionSetAnswerTableSerializer, QuestionAnswerTableSerializer, AnswerTableSerializer, AbstractAnswerTableSerializer, AnswerInputTableSerializer, AnswerNumberLineTableSerializer, AnswerSelectTableSerializer, AnswerSortTableSerializer, QuestionDetailsTableSerializer, ScoreByQuestionSetSerializer, AssessmentListForDashboardSerializer, QuestionSetLisForDashboardSerializer, QuestionOverviewSerializer, StudentsByQuestionSetAccessSerializer, StudentAnswersSerializer
from assessments.models import Assessment, QuestionSet, Question, QuestionSetAccess
from answers.models import QuestionSetAnswer, AnswerSession, Answer, AnswerInput, AnswerNumberLine, AnswerSelect, AnswerSort
from admin.lib.viewsets import ModelViewSet

import datetime

class UserTableViewSet(ModelViewSet):
    """
    Users table viewset.
    """

    serializer_class = UserTableSerializer
    filterset_fields = ['first_name', 'role',
                        'country', 'language', 'created_by']
    filter_backends = [OrderingFilter]
    ordering_fields = ['id']

    def get_queryset(self):
        """
        Queryset to get allowed users.
        """
        users = self.__get_students()
        language = self.request.query_params.get('language')
        if language:
            users = users.filter(language__code=language)

        country = self.request.query_params.get('country')
        if country:
            users = users.filter(country__code=country)

        group = self.request.query_params.get('group')
        if group:
            users = users.filter(group=group)

        return users

    def list(self, request, *args, **kwargs):
        serializer = UserTableSerializer(
            self.get_queryset(), many=True,
            context={
                'assessments': self.__get_assessments(),
                'question_sets': self.__get_question_sets()
            }
        )
        return Response(serializer.data)

    def __get_assessments(self):
        return Assessment.objects.filter(
            questionset__questionsetaccess__student__in=self.__get_students(),
            questionset__questionsetaccess__start_date__lte=datetime.date.today(),
            questionset__questionsetaccess__end_date__gte=datetime.date.today()
        ).distinct()

    def __get_question_sets(self):
        return QuestionSet.objects.filter(questionsetaccess__student__in=self.__get_students()).distinct()

    def __get_students(self):
        return User.objects.filter(created_by=self.request.user, role=User.UserRole.STUDENT)

    def create(self, request):
        return Response('Unauthorized', status=403)

    def update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def partial_update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def destroy(self, request, pk=None):
        return Response('Unauthorized', status=403)


class StudentLinkedAssessmentsViewSet(ModelViewSet):

    def get_queryset(self):

        student_pk = int(self.kwargs.get('student_pk', None))

        return Assessment.objects.filter(
            questionset__questionsetaccess__student=student_pk
        ).distinct()

    def list(self, request, *args, **kwargs):

        serializer = StudentLinkedAssessmentsSerializer(
            self.get_queryset(), many=True,
            context={
                'student_pk': int(self.kwargs.get('student_pk', None))
            }
        )

        return Response(serializer.data)


class AssessmentTableViewSet(ModelViewSet):
    """
    Assessments table viewset.
    """

    serializer_class = AssessmentTableSerializer
    filterset_fields = ['grade', 'subject', 'country', 'language']

    def get_queryset(self):
        """
        Queryset to get allowed assessments for table.
        """
        assessments = Assessment.objects.filter(Q(created_by=self.request.user) | Q(private=False))

        question_set = self.request.query_params.get('question_set')
        if question_set:
            question_sets = QuestionSet.objects.filter(id=question_set)
            assessments = assessments.filter(questionset__in=question_sets).distinct()

        subject = self.request.query_params.get('subject')
        if subject:
            assessments = assessments.filter(subject=subject)

        language = self.request.query_params.get('language')
        if language:
            assessments = assessments.filter(language__code=language)

        country = self.request.query_params.get('country')
        if country:
            assessments = assessments.filter(country__code=country)

        grade = self.request.query_params.get('grade')
        if grade:
            assessments = assessments.filter(grade=grade)

        topic = self.request.query_params.get('topic')
        if topic:
            assessments = assessments.filter(topic=topic)

        number_range = self.request.query_params.get('number_range')
        if number_range:
            assessments = assessments.filter(questionset__question__number_range=number_range)

        question_types = self.request.query_params.getlist('question_types[]', None)
        if question_types:
            questions = Question.objects.filter(question_type__in=question_types)
            assessments = assessments.filter(questionset__question__in=questions).distinct()

        learning_objectives = self.request.query_params.getlist('learning_objectives[]', None)
        if learning_objectives:
            assessments = assessments.filter(questionset__learning_objective__in=learning_objectives).distinct()

        return assessments

    def list(self, request, *args, **kwargs):

        serializer = AssessmentTableSerializer(
            self.get_queryset(), many=True,
            context={
                'supervisor': self.request.user
            }
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        assessment = self.get_object()
        serializer = AssessmentTableSerializer(assessment)
        return Response(serializer.data)

    def create(self, request):
        return Response('Unauthorized', status=403)

    def update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def partial_update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def destroy(self, request, pk=None):
        return Response('Unauthorized', status=403)


class QuestionSetsTableViewset(ModelViewSet):
    """
    Question sets table viewset
    """

    serializer_class = QuestionSetTableSerializer

    def get_queryset(self):
        """
        Queryset to get allowed assessment question_sets table.
        """
        accessible_assessments = AssessmentTableViewSet.get_queryset(self)
        assessment_pk = int(self.kwargs.get('assessment_pk', None))

        return QuestionSet.objects.filter(
            assessment=assessment_pk,
            assessment__in=accessible_assessments
        )

    def create(self, request):
        return Response('Unauthorized', status=403)

    def update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def partial_update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def destroy(self, request, pk=None):
        return Response('Unauthorized', status=403)

    @action(detail=False, methods=['get'], url_path='all')
    def get_all(self, request):
        accessible_assessments = AssessmentTableViewSet.get_queryset(self)
        question_sets = QuestionSet.objects.filter(assessment__in=accessible_assessments).order_by(Lower('name'))

        serializer = QuestionSetTableSerializer(question_sets, many=True)

        return Response(serializer.data, status=200)

class QuestionsTableViewset(ModelViewSet):
    """
    Question sets table viewset
    """

    serializer_class = QuestionTableSerializer

    def get_queryset(self):
        """
        Queryset to get allowed assessment question_sets table.
        """
        accessible_assessments = AssessmentTableViewSet.get_queryset(self)
        questions = Question.objects.filter(question_set__assessment__in=accessible_assessments)

        question_set_pk = self.kwargs.get('question_set_pk', None)
        assessment_pk = self.kwargs.get('assessment_pk', None)
        if question_set_pk and assessment_pk:
            question_set_pk = int(question_set_pk)
            assessment_pk = int(assessment_pk)
            questions = questions.filter(question_set=question_set_pk, question_set__assessment=assessment_pk)

        grade = self.request.query_params.get('grade')
        if grade:
            questions = questions.filter(question_set__assessment__grade=grade)
        
        topic = self.request.query_params.get('topic')
        if topic:
            assessments = assessments.filter(topic=topic)

        number_range = self.request.query_params.get('number_range')
        if number_range:
            questions = questions.filter(number_range=number_range)

        question_types = self.request.query_params.getlist('question_types[]', None)
        if question_types:
            questions = questions.filter(question_type__in=question_types)

        learning_objectives = self.request.query_params.getlist('learning_objectives[]', None)
        if learning_objectives:
            assessments = assessments.filter(questionset__learning_objective__in=learning_objectives).distinct()

        return questions

    def list(self, request, *args, **kwargs):

        accessible_students = UserTableViewSet.get_queryset(self)

        serializer = QuestionTableSerializer(
            self.get_queryset(), many=True,
            context={
                'accessible_students': accessible_students
            }
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        question_pk = self.kwargs.get('pk', None)
        question = get_object_or_404(
            self.get_queryset().select_subclasses(), pk=question_pk)
        serializer = QuestionDetailsTableSerializer(question, many=False)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='all')
    def get_all(self, request):
        questions = QuestionsTableViewset.get_queryset(self)
        serializer = QuestionTableSerializer(questions, many=True)
        return Response(serializer.data, status=200)

    def create(self, request):
        return Response('Unauthorized', status=403)

    def update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def partial_update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def destroy(self, request, pk=None):
        return Response('Unauthorized', status=403)

class AssessmentAnswersTableViewSet(ModelViewSet):
    """
    Assessments per student's answers table viewset
    """

    serializer_class = AssessmentAnswerTableSerializer

    def get_queryset(self):
        """
        Queryset to get assessments per student's answers.
        """
        student_pk = int(self.kwargs.get('student_pk', None))

        return Assessment.objects.filter(
            questionset__questionsetaccess__question_set_answers__session__student=student_pk
        ).distinct()

    def list(self, request, *args, **kwargs):

        serializer = AssessmentAnswerTableSerializer(
            self.get_queryset(), many=True,
            context={
                'student_pk': int(self.kwargs.get('student_pk', None))
            }
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        assessment_pk = self.kwargs.get('pk', None)
        assessment = get_object_or_404(
            self.get_queryset(), pk=assessment_pk)
        serializer = AssessmentAnswerTableSerializer(assessment, many=False, context={
            'student_pk': int(self.kwargs.get('student_pk', None))
        })
        return Response(serializer.data)

    def create(self, request):
        return Response('Unauthorized', status=403)

    def update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def partial_update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def destroy(self, request, pk=None):
        return Response('Unauthorized', status=403)


class QuestionSetAnswersTableViewSet(ModelViewSet):
    """
    Question sets per student's answers table viewset
    """

    serializer_class = QuestionSetAnswerTableSerializer

    def get_queryset(self):
        """
        Queryset to get assessment question_sets per student's answers.
        """
        student_pk = int(self.kwargs.get('student_pk', None))
        assessment_pk = int(self.kwargs.get('assessment_pk', None))

        return QuestionSet.objects.filter(
            questionsetaccess__student=student_pk,
            assessment=assessment_pk
        )

    def list(self, request, *args, **kwargs):

        serializer = QuestionSetAnswerTableSerializer(
            self.get_queryset(), many=True,
            context={
                'assessment_pk': int(self.kwargs.get('assessment_pk', None)),
                'student_pk': int(self.kwargs.get('student_pk', None))
            }
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        question_set_pk = self.kwargs.get('pk', None)
        assessment = get_object_or_404(
            self.get_queryset(), pk=question_set_pk)
        serializer = QuestionSetAnswerTableSerializer(assessment, many=False, context={
            'assessment_pk': int(self.kwargs.get('assessment_pk', None)),
            'student_pk': int(self.kwargs.get('student_pk', None))
        })
        return Response(serializer.data)

    def create(self, request):
        return Response('Unauthorized', status=403)

    def update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def partial_update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def destroy(self, request, pk=None):
        return Response('Unauthorized', status=403)


class QuestionAnswersTableViewSet(ModelViewSet):
    """
    Questions per student's answers table viewset
    """

    serializer_class = QuestionAnswerTableSerializer

    def get_queryset(self):
        """
        Queryset to get questions per student's answers.
        """
        student_pk = int(self.kwargs.get('student_pk', None))
        assessment_pk = int(self.kwargs.get('assessment_pk', None))
        question_set_pk = int(self.kwargs.get('question_set_pk', None))

        return Question.objects.filter(
            question_set__questionsetaccess__student=student_pk,
            question_set__assessment=assessment_pk,
            question_set=question_set_pk
        )

    def list(self, request, *args, **kwargs):

        serializer = QuestionAnswerTableSerializer(
            self.get_queryset(), many=True,
            context={
                'student_pk': int(self.kwargs.get('student_pk', None)),
                'assessment_pk': int(self.kwargs.get('assessment_pk', None)),
                'question_set_pk': int(self.kwargs.get('question_set_pk', None))
            }
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        question_pk = self.kwargs.get('pk', None)
        question = get_object_or_404(
            self.get_queryset().select_subclasses(), pk=question_pk)
        serializer = QuestionAnswerTableSerializer(question, many=False,
            context={
                'student_pk': int(self.kwargs.get('student_pk', None)),
                'assessment_pk': int(self.kwargs.get('assessment_pk', None)),
                'question_set_pk': int(self.kwargs.get('question_set_pk', None))
            }
        )
        return Response(serializer.data)

    def create(self, request):
        return Response('Unauthorized', status=403)

    def update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def partial_update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def destroy(self, request, pk=None):
        return Response('Unauthorized', status=403)


class ScoreByQuestionSetViewSet(ModelViewSet):
    """
    Score By QuestionSet view set. Used on the dashboard (assessments multi-select and select filter)
    """
    serializer_class = ScoreByQuestionSetSerializer

    def get_queryset(self):

        assessment_pk = int(self.kwargs.get('assessment_pk', None))
        user = self.request.user

        return User.objects.filter(created_by=user)

    def list(self, request, *args, **kwargs):

        serializer = ScoreByQuestionSetSerializer(
            self.get_queryset(), many=True,
            context={
                'assessment_pk': int(self.kwargs.get('assessment_pk', None))
            }
        )

        return Response(serializer.data)

class GroupScoreByQuestionSetViewSet(ModelViewSet):
    """
    Score By QuestionSet filtering by group view set.
    TODO evaluate if it is necessary to change the information obtained here or add more information for the dashboard (to do so: create GroupScoreByQuestionSetViewSet own serializer?)
    """
    serializer_class = ScoreByQuestionSetSerializer

    def get_queryset(self):
        group_pk = int(self.kwargs.get('group_pk', None))
        user = self.request.user

        return User.objects.filter(created_by=user, group=group_pk)

    def list(self, request, *args, **kwargs):

        serializer = ScoreByQuestionSetSerializer(
            self.get_queryset(), many=True,
            context={
                'assessment_pk': int(self.kwargs.get('assessment_pk', None))
            }
        )

        return Response(serializer.data)

class AssessmentListForDashboard(ModelViewSet):

    serializer_class = AssessmentListForDashboardSerializer

    def get_queryset(self):
        """
        Queryset to get allowed assessments for table.
        """
        return Assessment.objects.filter((Q(created_by=self.request.user) | Q(private=False) | ~Q(subject='TUTORIAL')) & Q(archived=False))

    def list(self, request, *args, **kwargs):

        serializer = AssessmentListForDashboardSerializer(
            self.get_queryset(), many=True,
            context={
                'supervisor': self.request.user
            }
        )

        return Response(serializer.data)


class QuestionSetListForDashboard(ModelViewSet):

    serializer_class = QuestionSetLisForDashboardSerializer

    def get_queryset(self):

        assessment_pk = int(self.kwargs.get('assessment_pk', None))

        return QuestionSet.objects.filter(assessment=assessment_pk)


class QuestionOverviewViewSet(ModelViewSet):

    serializer_class = QuestionOverviewSerializer

    def get_queryset(self):

        question_set_pk = int(self.kwargs.get('question_set_pk', None))

        questions = Question.objects.filter(
            Q(question_set=question_set_pk) & ~Q(question_type='SEL')
        )

        groups = self.request.query_params.getlist('groups[]')
        if groups:
            questions = questions.filter(
                question_set__questionsetaccess__student__group__in=groups
            )
        return questions

    def list(self, request, *args, **kwargs):

        serializer = QuestionOverviewSerializer(
            self.get_queryset(), many=True,
            context={
                'supervisor': self.request.user,
                'assessment_pk': int(self.kwargs.get('assessment_pk', None)),
                'question_set_pk': int(self.kwargs.get('question_set_pk', None)),
            }
        )

        return Response(serializer.data)


class StudentsByQuestionSetAccessViewSet(ModelViewSet):

    serializer_class = StudentsByQuestionSetAccessSerializer

    def get_queryset(self):

        question_set_pk = int(self.kwargs.get('question_set_pk', None))
        students = User.objects.filter(created_by=self.request.user)

        groups = self.request.query_params.getlist('groups[]')
        if groups:
            students = students.filter(group__in=groups)

        return QuestionSetAccess.objects.filter(question_set=question_set_pk, student__in=students)


class StudentAnswersViewSet(ModelViewSet):

    serializer_class = StudentAnswersSerializer
    ordering_fields = ('answer__question_id')

    def get_queryset(self):

        question_set_pk = int(self.kwargs.get('question_set_pk', None))
        question_set_answer_pk = int(
            self.kwargs.get('question_set_answer_pk', None))

        return Answer.objects.filter(question__question_set=question_set_pk, question_set_answer=question_set_answer_pk).exclude(question__question_type='SEL')

    def retrieve(self, request, *args, **kwargs):
        answer_pk = self.kwargs.get('pk', None)
        answer = get_object_or_404(
            self.get_queryset().select_subclasses(), pk=answer_pk)
        serializer = AnswerTableSerializer(answer, many=False)
        return Response(serializer.data)

class GroupTableViewSet(ModelViewSet):
    """
    Groups table viewset.
    """
    serializer_class = GroupTableSerializer

    def get_queryset(self):
        return Group.objects.filter(supervisor=self.request.user)