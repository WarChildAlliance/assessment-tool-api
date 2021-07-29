
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from users.models import User
from visualization.serializers import StudentLinkedAssessmentsSerializer, UserTableSerializer, AssessmentTableSerializer, QuestionTableSerializer, AssessmentTopicTableSerializer, AssessmentAnswerTableSerializer, TopicAnswerTableSerializer, QuestionAnswerTableSerializer, AnswerTableSerializer, AbstractAnswerTableSerializer, AnswerInputTableSerializer, AnswerNumberLineTableSerializer, AnswerSelectTableSerializer, AnswerSortTableSerializer, QuestionDetailsTableSerializer, ScoreByTopicSerializer, AssessmentListForDashboardSerializer, TopicLisForDashboardSerializer, QuestionOverviewSerializer, StudentsByTopicAccessSerializer, StudentAnswersSerializer

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

    def get_queryset(self):
        """
        Queryset to get allowed users.
        """
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

        return Assessment.objects.filter(Q(created_by=self.request.user) | Q(private=False))

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

        assessment_pk = int(self.kwargs.get('assessment_pk', None))
        return AssessmentTopic.objects.filter(assessment=assessment_pk)

    def create(self, request):
        return Response('Unauthorized', status=403)

    def update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def partial_update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def destroy(self, request, pk=None):
        return Response('Unauthorized', status=403)


class QuestionsTableViewset(ModelViewSet):
    """
    Assessment topics table viewset
    """

    serializer_class = QuestionTableSerializer

    def get_queryset(self):
        """
        Queryset to get allowed assessment topics table.
        """

        topic_pk = int(self.kwargs.get('topic_pk', None))

        return Question.objects.filter(
            assessment_topic=topic_pk
        )
    
    def retrieve(self, request, *args, **kwargs):
        question_pk = self.kwargs.get('pk', None)
        question = get_object_or_404(self.get_queryset().select_subclasses(), pk=question_pk)
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
        return Response('Unauthorized', status=403)

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
        return Response('Unauthorized', status=403)

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
        question = get_object_or_404(self.get_queryset().select_subclasses(), pk=question_pk)
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

class AssessmentListForDashboard(ModelViewSet):

    serializer_class = AssessmentListForDashboardSerializer

    def get_queryset(self):
        """
        Queryset to get allowed assessments for table.
        """

        return Assessment.objects.filter(Q(created_by=self.request.user) | Q(private=False))
    
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

        return AssessmentTopic.objects.filter(assessment=assessment_pk)


class QuestionOverviewViewSet(ModelViewSet):

    serializer_class = QuestionOverviewSerializer

    def get_queryset(self):

        topic_pk = int(self.kwargs.get('topic_pk', None))

        return Question.objects.filter(
            assessment_topic=topic_pk
        )
    
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

        return AssessmentTopicAccess.objects.filter(topic=topic_pk, student__in=students)


class StudentAnswersViewSet(ModelViewSet):

    serializer_class = StudentAnswersSerializer

    def get_queryset(self):

        topic_pk = int(self.kwargs.get('topic_pk', None))
        assessment_topic_answer_pk = int(self.kwargs.get('assessment_topic_answer_pk', None))

        return Answer.objects.filter(question__assessment_topic=topic_pk, topic_answer=assessment_topic_answer_pk)
    
    def retrieve(self, request, *args, **kwargs):
        answer_pk = self.kwargs.get('pk', None)
        answer = get_object_or_404(self.get_queryset().select_subclasses(), pk=answer_pk)
        serializer = AnswerTableSerializer(answer, many=False)  
        return Response(serializer.data)
    
