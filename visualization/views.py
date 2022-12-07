
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action

from django.shortcuts import get_object_or_404

from users.models import User, Group
from visualization.serializers import GroupTableSerializer, StudentLinkedAssessmentsSerializer, UserTableSerializer, AssessmentTableSerializer, QuestionTableSerializer, AssessmentTopicTableSerializer, AssessmentAnswerTableSerializer, TopicAnswerTableSerializer, QuestionAnswerTableSerializer, AnswerTableSerializer, AbstractAnswerTableSerializer, AnswerInputTableSerializer, AnswerNumberLineTableSerializer, AnswerSelectTableSerializer, AnswerSortTableSerializer, QuestionDetailsTableSerializer, ScoreByTopicSerializer, AssessmentListForDashboardSerializer, TopicLisForDashboardSerializer, QuestionOverviewSerializer, StudentsByTopicAccessSerializer, StudentAnswersSerializer

from assessments.models import Assessment, AssessmentTopic, Question, AssessmentTopicAccess

from answers.models import AssessmentTopicAnswer, AnswerSession, Answer, AnswerInput, AnswerNumberLine, AnswerSelect, AnswerSort

from django.db.models import Q

from admin.lib.viewsets import ModelViewSet


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
        users = User.objects.filter(created_by=self.request.user, role=User.UserRole.STUDENT)

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
            assessmenttopic__assessmenttopicaccess__student=student_pk
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
           
        topic = self.request.query_params.get('topic')
        if topic:
            topics = AssessmentTopic.objects.filter(id=topic)
            assessments = assessments.filter(assessmenttopic__in=topics).distinct()

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

        subtopic = self.request.query_params.get('subtopic')
        if subtopic:
            assessments = assessments.filter(subtopic=subtopic)

        number_range = self.request.query_params.get('number_range')
        if number_range:
            assessments = assessments.filter(assessmenttopic__question__number_range=number_range)

        question_types = self.request.query_params.getlist('question_types[]', None)
        if question_types:
            questions = Question.objects.filter(question_type__in=question_types)
            assessments = assessments.filter(assessmenttopic__question__in=questions).distinct()

        learning_objectives = self.request.query_params.getlist('learning_objectives[]', None)
        if learning_objectives:
            assessments = assessments.filter(assessmenttopic__learning_objective__in=learning_objectives).distinct()

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


class AssessmentTopicsTableViewset(ModelViewSet):
    """
    Assessment topics table viewset
    """

    serializer_class = AssessmentTopicTableSerializer

    def get_queryset(self):
        """
        Queryset to get allowed assessment topics table.
        """
        accessible_assessments = AssessmentTableViewSet.get_queryset(self)
        assessment_pk = int(self.kwargs.get('assessment_pk', None))

        return AssessmentTopic.objects.filter(
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
        topics = AssessmentTopic.objects.filter(assessment__in=accessible_assessments)

        serializer = AssessmentTopicTableSerializer(topics, many=True)

        return Response(serializer.data, status=200)

class QuestionsTableViewset(ModelViewSet):
    """
    Assessment topics table viewset
    """

    serializer_class = QuestionTableSerializer

    def get_queryset(self):
        """
        Queryset to get allowed assessment topics table.
        """
        accessible_topics = AssessmentTopicsTableViewset.get_queryset(self)
        topic_pk = int(self.kwargs.get('topic_pk', None))
        assessment_pk = int(self.kwargs.get('assessment_pk', None))

        questions = Question.objects.filter(
            assessment_topic=topic_pk,
            assessment_topic__in=accessible_topics,
            assessment_topic__assessment=assessment_pk
        )

        grade = self.request.query_params.get('grade')
        if grade:
            questions = questions.filter(assessment_topic__assessment__grade=grade)
        
        subtopic = self.request.query_params.get('subtopic')
        if subtopic:
            questions = questions.filter(assessment_topic__assessment__subtopic=subtopic)

        number_range = self.request.query_params.get('number_range')
        if number_range:
            questions = questions.filter(number_range=number_range)

        question_types = self.request.query_params.getlist('question_types[]', None)
        if question_types:
            questions = questions.filter(question_type__in=question_types)

        learning_objectives = self.request.query_params.getlist('learning_objectives[]', None)
        if learning_objectives:
            questions = questions.filter(assessment_topic__learning_objective__in=learning_objectives)

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
            assessmenttopic__assessmenttopicaccess__assessment_topic_answers__session__student=student_pk
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


class TopicAnswersTableViewSet(ModelViewSet):
    """
    Assessment topics per student's answers table viewset
    """

    serializer_class = TopicAnswerTableSerializer

    def get_queryset(self):
        """
        Queryset to get assessment topics per student's answers.
        """
        student_pk = int(self.kwargs.get('student_pk', None))
        assessment_pk = int(self.kwargs.get('assessment_pk', None))

        return AssessmentTopic.objects.filter(
            assessmenttopicaccess__student=student_pk,
            assessment=assessment_pk
        )

    def list(self, request, *args, **kwargs):

        serializer = TopicAnswerTableSerializer(
            self.get_queryset(), many=True,
            context={
                'assessment_pk': int(self.kwargs.get('assessment_pk', None)),
                'student_pk': int(self.kwargs.get('student_pk', None))
            }
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        topic_pk = self.kwargs.get('pk', None)
        assessment = get_object_or_404(
            self.get_queryset(), pk=topic_pk)
        serializer = TopicAnswerTableSerializer(assessment, many=False, context={
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
        topic_pk = int(self.kwargs.get('topic_pk', None))

        return Question.objects.filter(
            assessment_topic__assessmenttopicaccess__student=student_pk,
            assessment_topic__assessment=assessment_pk,
            assessment_topic=topic_pk
        )

    def list(self, request, *args, **kwargs):

        serializer = QuestionAnswerTableSerializer(
            self.get_queryset(), many=True,
            context={
                'student_pk': int(self.kwargs.get('student_pk', None)),
                'assessment_pk': int(self.kwargs.get('assessment_pk', None)),
                'topic_pk': int(self.kwargs.get('topic_pk', None))
            }
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        question_pk = self.kwargs.get('pk', None)
        question = get_object_or_404(
            self.get_queryset().select_subclasses(), pk=question_pk)
        serializer = QuestionAnswerTableSerializer(question, many=False)
        return Response(serializer.data)

    def create(self, request):
        return Response('Unauthorized', status=403)

    def update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def partial_update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def destroy(self, request, pk=None):
        return Response('Unauthorized', status=403)


class ScoreByTopicViewSet(ModelViewSet):
    """
    Score By Topic view set. Used on the dashboard (assessments multi-select and select filter)
    """
    serializer_class = ScoreByTopicSerializer

    def get_queryset(self):

        assessment_pk = int(self.kwargs.get('assessment_pk', None))
        user = self.request.user

        return User.objects.filter(created_by=user)

    def list(self, request, *args, **kwargs):

        serializer = ScoreByTopicSerializer(
            self.get_queryset(), many=True,
            context={
                'assessment_pk': int(self.kwargs.get('assessment_pk', None))
            }
        )

        return Response(serializer.data)

class GroupScoreByTopicViewSet(ModelViewSet):
    """
    Score By Topic filtering by group view set.
    TODO evaluate if it is necessary to change the information obtained here or add more information for the dashboard (to do so: create GroupScoreByTopicViewSet own serializer?)
    """
    serializer_class = ScoreByTopicSerializer

    def get_queryset(self):
        group_pk = int(self.kwargs.get('group_pk', None))
        user = self.request.user

        return User.objects.filter(created_by=user, group=group_pk)

    def list(self, request, *args, **kwargs):

        serializer = ScoreByTopicSerializer(
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


class TopicListForDashboard(ModelViewSet):

    serializer_class = TopicLisForDashboardSerializer

    def get_queryset(self):

        assessment_pk = int(self.kwargs.get('assessment_pk', None))

        return AssessmentTopic.objects.filter(assessment=assessment_pk, archived=False)


class QuestionOverviewViewSet(ModelViewSet):

    serializer_class = QuestionOverviewSerializer

    def get_queryset(self):

        topic_pk = int(self.kwargs.get('topic_pk', None))

        questions = Question.objects.filter(
            Q(assessment_topic=topic_pk) & ~Q(question_type='SEL')
        )

        groups = self.request.query_params.getlist('groups[]')
        if groups:
            questions = questions.filter(
                assessment_topic__assessmenttopicaccess__student__group__in=groups
            )
        return questions

    def list(self, request, *args, **kwargs):

        serializer = QuestionOverviewSerializer(
            self.get_queryset(), many=True,
            context={
                'supervisor': self.request.user,
                'assessment_pk': int(self.kwargs.get('assessment_pk', None)),
                'topic_pk': int(self.kwargs.get('topic_pk', None)),
            }
        )

        return Response(serializer.data)


class StudentsByTopicAccessViewSet(ModelViewSet):

    serializer_class = StudentsByTopicAccessSerializer

    def get_queryset(self):

        topic_pk = int(self.kwargs.get('topic_pk', None))
        students = User.objects.filter(created_by=self.request.user)

        groups = self.request.query_params.getlist('groups[]')
        if groups:
            students = students.filter(group__in=groups)

        return AssessmentTopicAccess.objects.filter(topic=topic_pk, student__in=students)


class StudentAnswersViewSet(ModelViewSet):

    serializer_class = StudentAnswersSerializer
    ordering_fields = ('answer__question_id')

    def get_queryset(self):

        topic_pk = int(self.kwargs.get('topic_pk', None))
        assessment_topic_answer_pk = int(
            self.kwargs.get('assessment_topic_answer_pk', None))

        return Answer.objects.filter(question__assessment_topic=topic_pk, topic_answer=assessment_topic_answer_pk).exclude(question__question_type='SEL')

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