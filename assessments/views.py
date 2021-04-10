from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from admin.lib.viewsets import ModelViewSet

from .models import Assessment, AssessmentTopic, Attachment, Question
from .serializers import (AssessmentSerializer, AssessmentTopicSerializer,
                          AttachmentSerializer, QuestionSerializer)


class AssessmentsViewSet(ModelViewSet):
    """
    Assessments viewset.
    """

    serializer_class = AssessmentSerializer
    filterset_fields = ['grade', 'private', 'country', 'language', 'subject']
    search_fields = ['title', 'subject']

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

    def get_queryset(self):
        """
        Queryset to get allowed assessment topics.
        """

        assessment_pk = self.kwargs['assessment_pk']
        return AssessmentTopic.objects.filter(assessment=assessment_pk)


class QuestionsViewSet(ModelViewSet):
    """
    Questions viewset.
    """

    serializer_class = QuestionSerializer

    def get_queryset(self):
        """
        Queryset to get allowed questions.
        """

        topic_pk = self.kwargs['topic_pk']

        return Question.objects.filter(assessment_topic=topic_pk)


class AttachmentsViewSet(ModelViewSet):
    """
    Attachments viewset.
    """

    serializer_class = AttachmentSerializer

    def get_queryset(self):
        """
        Queryset to get attachments.
        """

        question_pk = self.kwargs['question_pk']

        return Attachment.objects.filter(question=question_pk)
