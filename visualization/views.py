
from admin.lib.viewsets import ModelViewSet

from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from users.models import User
from visualization.serializers import UserTableSerializer, AssessmentTableSerializer, QuestionTableSerializer, AssessmentTopicTableSerializer, AnswerSessionTableSerializer, AssessmentAnswerTableSerializer, TopicAnswerTableSerializer, QuestionAnswerTableSerializer, AnswerTableSerializer, AbstractAnswerTableSerializer, AnswerInputTableSerializer, AnswerNumberLineTableSerializer, AnswerSelectTableSerializer, AnswerSortTableSerializer

from assessments.models import Assessment, AssessmentTopic, Question

from answers.models import AssessmentTopicAnswer, AnswerSession, Answer, AnswerInput, AnswerNumberLine, AnswerSelect, AnswerSort

from django.db.models import Q


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

        return User.objects.filter(created_by=self.request.user)

    def create(self, request):
        return Response('Unauthorized', status=403)

    def update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def partial_update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def destroy(self, request, pk=None):
        return Response('Unauthorized', status=403)


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

    def create(self, request):
        return Response('Unauthorized', status=403)

    def update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def partial_update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def destroy(self, request, pk=None):
        return Response('Unauthorized', status=403)


class AnswerSessionsTableViewSet(ModelViewSet):
    """
    Answer sessions table viewset
    """

    serializer_class = AnswerSessionTableSerializer

    def get_queryset(self):
        """
        Queryset to get answer sessions for a student.
        """
        user = self.request.user
        student_pk = int(self.kwargs.get('student_pk', None))

        return AnswerSession.objects.filter(
            student=student_pk,
            student__created_by=user
        )

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
        session_pk = self.request.GET.get('session', None)

        if(session_pk):
            return Assessment.objects.filter(
                assessmenttopic__assessmenttopicaccess__assessment_topic_answers__session__student=student_pk,
                assessmenttopic__assessmenttopicaccess__assessment_topic_answers__session=session_pk
            ).distinct()

        return Assessment.objects.filter(
            assessmenttopic__assessmenttopicaccess__assessment_topic_answers__session__student=student_pk
        ).distinct()

    def list(self, request, *args, **kwargs):

        serializer = AssessmentAnswerTableSerializer(
            self.get_queryset(), many=True,
            context={
                'student_pk': int(self.kwargs.get('student_pk', None)),
                'session_pk': request.query_params.get('session', None)
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
        session_pk = self.request.GET.get('session', None)

        if(session_pk):
            return AssessmentTopicAnswer.objects.filter(
                topic_access__student=student_pk,
                topic_access__topic__assessment=assessment_pk,
                session=session_pk
            )

        return AssessmentTopicAnswer.objects.filter(
            topic_access__student=student_pk,
            topic_access__topic__assessment=assessment_pk
        )

    def list(self, request, *args, **kwargs):

        serializer = TopicAnswerTableSerializer(
            self.get_queryset(), many=True,
            context={
                'assessment_pk': int(self.kwargs.get('assessment_pk', None)),
                'session_pk': request.query_params.get('session', None)
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
        session_pk = self.request.GET.get('session', None)

        if(session_pk):
            return Answer.objects.filter(
                topic_answer__topic_access__student=student_pk,
                topic_answer__topic_access__topic__assessment=assessment_pk,
                topic_answer__topic_access__topic=topic_pk,
                topic_answer__session=session_pk,
            )

        return Answer.objects.filter(
            topic_answer__topic_access__student=student_pk,
            topic_answer__topic_access__topic__assessment=assessment_pk,
            topic_answer__topic_access__topic=topic_pk
        )

    def list(self, request, *args, **kwargs):

        serializer = QuestionAnswerTableSerializer(
            self.get_queryset(), many=True,
            context={
                'student_pk': int(self.kwargs.get('student_pk', None)),
                'assessment_pk': int(self.kwargs.get('assessment_pk', None)),
                'topic_pk': int(self.kwargs.get('topic_pk', None)),
                'session_pk': request.query_params.get('session', None)
            }
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        answer_pk = self.kwargs.get('pk', None)
        answer = get_object_or_404(self.get_queryset().select_subclasses(), pk=answer_pk)
        serializer = AnswerTableSerializer(answer, many=False)  
        return Response(serializer.data)

    def create(self, request):
        return Response('Unauthorized', status=403)

    def update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def partial_update(self, request, pk=None):
        return Response('Unauthorized', status=403)

    def destroy(self, request, pk=None):
        return Response('Unauthorized', status=403)
