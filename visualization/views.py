from django.shortcuts import render

from admin.lib.viewsets import ModelViewSet

from rest_framework.response import Response

from users.models import User
from visualization.serializers import UserTableSerializer, AssessmentTableSerializer, AssessmentTopicTableSerializer, AnswerSessionTableSerializer, AssessmentAnswerTableSerializer, TopicAnswerTableSerializer, QuestionAnswerTableSerializer

from assessments.models import Assessment, AssessmentTopic, AssessmentTopicAccess

from answers.models import AssessmentTopicAnswer, AnswerSession

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
        return Response('Cannot create user table', status=403)

    def update(self, request, pk=None):
        return Response('Cannot update user table', status=403)

    def partial_update(self, request, pk=None):
        return Response('Cannot update user table', status=403)

    def destroy(self, request, pk=None):
        return Response('Cannot delete user table', status=403)


class AssessmentTableViewSet(ModelViewSet):
    """
    Assessments table viewset.
    """

    serializer_class = AssessmentTableSerializer
    filterset_fields = ['grade', 'country', 'language', 'subject']

    def get_queryset(self):
        """
        Queryset to get allowed assessments.
        """

        return Assessment.objects.filter(Q(created_by=self.request.user) | Q(private=False))

    def create(self, request):
        return Response('Cannot create user table', status=403)

    def update(self, request, pk=None):
        return Response('Cannot update user table', status=403)

    def partial_update(self, request, pk=None):
        return Response('Cannot update user table', status=403)

    def destroy(self, request, pk=None):
        return Response('Cannot delete user table', status=403)


class AssessmentTopicsTableViewset(ModelViewSet):
    """
    Assessment topics viewset
    """

    serializer_class = AssessmentTopicTableSerializer

    def get_queryset(self):
        """
        Queryset to get allowed assessment topics.
        """

        assessment_pk = int(self.kwargs.get('assessment_pk', None))
        return AssessmentTopic.objects.filter(assessment=assessment_pk)

    def create(self, request):
        return Response('Cannot create user table', status=403)

    def update(self, request, pk=None):
        return Response('Cannot update user table', status=403)

    def partial_update(self, request, pk=None):
        return Response('Cannot update user table', status=403)

    def destroy(self, request, pk=None):
        return Response('Cannot delete user table', status=403)


class AnswerSessionsTableViewSet(ModelViewSet):

    serializer_class = AnswerSessionTableSerializer

    def get_queryset(self):
        """
        Queryset to get allowed sessions.
        """
        user = self.request.user
        student_pk = int(self.kwargs.get('student_pk', None))

        return AnswerSession.objects.filter(
            student=student_pk,
            student__created_by=user
        )

    def create(self, request):
        return Response('Cannot create user table', status=403)

    def update(self, request, pk=None):
        return Response('Cannot update user table', status=403)

    def partial_update(self, request, pk=None):
        return Response('Cannot update user table', status=403)

    def destroy(self, request, pk=None):
        return Response('Cannot delete user table', status=403)


class AssessmentAnswersTableViewSet(ModelViewSet):

    serializer_class = AssessmentAnswerTableSerializer

    def get_queryset(self):
        """
        Queryset to get allowed assessment answers.
        """
        student_pk = int(self.kwargs.get('student_pk', None))
        session_pk = self.request.GET.get('session', None)

        if(session_pk):
            return Assessment.objects.filter(
                assessmenttopic__assessmenttopicaccess__assessment_topic_answers__session__student = student_pk,
                assessmenttopic__assessmenttopicaccess__assessment_topic_answers__session = session_pk
            ).distinct()

        return Assessment.objects.filter(
            assessmenttopic__assessmenttopicaccess__assessment_topic_answers__session__student = student_pk
        ).distinct()


    def list(self, request, *args, **kwargs):

        serializer = AssessmentAnswerTableSerializer(
            self.get_queryset(), many = True,
            context = {
                'student_pk': int(self.kwargs.get('student_pk', None)),
                'session_pk': request.query_params.get('session', None)
                }
            )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        return Response('Cannot access', status=403)

    def create(self, request):
        return Response('Cannot create user table', status=403)

    def update(self, request, pk=None):
        return Response('Cannot update user table', status=403)

    def partial_update(self, request, pk=None):
        return Response('Cannot update user table', status=403)

    def destroy(self, request, pk=None):
        return Response('Cannot delete user table', status=403)


class TopicAnswersTableViewSet(ModelViewSet):

    serializer_class = TopicAnswerTableSerializer

    def get_queryset(self):
        """
        Queryset to get allowed assessment topics answers.
        """
        student_pk = int(self.kwargs.get('student_pk', None))
        assessment_pk = int(self.kwargs.get('assessment_pk', None))

        queryset = AssessmentTopicAnswer.objects.filter(topic_access__student=student_pk, topic_access__topic__assessment=assessment_pk)

        print(queryset)

        return queryset
    
    def create(self, request):
        return Response('Cannot create user table', status=403)

    def update(self, request, pk=None):
        return Response('Cannot update user table', status=403)

    def partial_update(self, request, pk=None):
        return Response('Cannot update user table', status=403)

    def destroy(self, request, pk=None):
        return Response('Cannot delete user table', status=403)


class QuestionAnswersTableViewSet(ModelViewSet):

    serializer_class = QuestionAnswerTableSerializer

    def get_queryset(self):
        """
        Queryset to questions answer.
        """
        student_pk = int(self.kwargs.get('student_pk', None))
        assessment_pk = int(self.kwargs.get('assessment_pk', None))
        topic_pk = int(self.kwargs.get('topic_pk', None))

        return Answer.objects.filter(topic_answer__topic_access_topic=topic_pk, topic_answer__topic_access__student=student_pk)
    
    def create(self, request):
        return Response('Cannot create user table', status=403)

    def update(self, request, pk=None):
        return Response('Cannot update user table', status=403)

    def partial_update(self, request, pk=None):
        return Response('Cannot update user table', status=403)

    def destroy(self, request, pk=None):
        return Response('Cannot delete user table', status=403)
    

