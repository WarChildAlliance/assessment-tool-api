from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.permissions import HasAccess, IsSupervisor

from admin.lib.viewsets import ModelViewSet

from .models import (Assessment, AssessmentTopic, AssessmentTopicAccess,
                     Attachment, Question)
from .serializers import (AssessmentSerializer,
                          AssessmentTopicAccessSerializer,
                          AssessmentTopicSerializer, AttachmentSerializer,
                          QuestionSerializer)


class AssessmentsViewSet(ModelViewSet):
    """
    Assessments viewset.
    """

    serializer_class = AssessmentSerializer
    filterset_fields = ['grade', 'private', 'country', 'language', 'subject']
    search_fields = ['title', 'subject']

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        if self.action == 'retrieve':
            permission_classes.append(HasAccess)
        elif self.action == 'destroy' or self.action == 'update':
            permission_classes.append(HasAccess)
            permission_classes.append(IsSupervisor)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Queryset to get allowed assessments.
        """
        user = self.request.user

        if user.is_supervisor():
            # Using Q in order to filter with a NOT condition
            return Assessment.objects.filter(Q(created_by=user) | Q(private=False))

        # Students can access assessments if they're linked to at least one of its topic
        return Assessment.objects.filter(
            assessmenttopic__assessmenttopicaccess__student=user
        ).distinct()


class AssessmentTopicsViewSet(ModelViewSet):
    """
    Assessment topics viewset.
    """

    serializer_class = AssessmentTopicSerializer
    filterset_fields = ['name', 'order', 'assessment']
    search_fields = ['name']

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        if self.action == 'retrieve':
            permission_classes.append(HasAccess)
        elif self.action == 'destroy' or self.action == 'update':
            permission_classes.append(HasAccess)
            permission_classes.append(IsSupervisor)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Queryset to get allowed assessment topics.
        """

        user = self.request.user
        assessment_pk = self.kwargs['assessment_pk']
        if user.is_student():
            return AssessmentTopic.objects.filter(
                assessment=assessment_pk,
                assessmenttopicaccess__student=user
            ).distinct()
        return AssessmentTopic.objects.filter(assessment=assessment_pk)


class QuestionsViewSet(ModelViewSet):
    """
    Questions viewset.
    """

    serializer_class = QuestionSerializer

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        if self.action == 'retrieve':
            permission_classes.append(HasAccess)
        elif self.action == 'destroy' or self.action == 'update':
            permission_classes.append(HasAccess)
            permission_classes.append(IsSupervisor)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Queryset to get allowed questions.
        """

        topic_pk = self.kwargs['topic_pk']
        assessment_pk = self.kwargs['assessment_pk']

        return Question.objects.filter(
            assessment_topic=topic_pk, assessment_topic__assessment=assessment_pk
        ).select_subclasses()


class AttachmentsViewSet(ModelViewSet):
    """
    Attachments viewset.
    """

    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Queryset to get attachments.
        """

        question_pk = self.kwargs['question_pk']

        return Attachment.objects.filter(question=question_pk)


class AssessmentTopicAccessesViewSets(ModelViewSet):
    """
    Assessment topic accesses viewset.
    """

    serializer_class = AssessmentTopicAccessSerializer
    parmission_classes = [IsAuthenticated, IsSupervisor]

    def get_queryset(self):
        """
        Queryset to get assessment topic accesses.
        """
        assessment_pk = self.kwargs['assessment_pk']
        user = self.request.user

        return AssessmentTopicAccess.objects.filter(
            student__created_by=user, topic__assessment__id=assessment_pk)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request, *args, **kwargs):
        """
        Assign assessment topics to students.
        """

        formatted_data = []
        for student in request.data['students']:
            for access in request.data['accesses']:
                formatted_data.append({
                    'student': student,
                    'topic': access['topic'],
                    'start_date': access['start_date'],
                    'end_date': access['end_date']
                })

        serializer = self.get_serializer(data=formatted_data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
