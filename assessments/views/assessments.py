from admin.lib.viewsets import ModelViewSet
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
import datetime

from ..models import Assessment, AssessmentTopic, AssessmentTopicAccess, Question
from ..serializers import AssessmentSerializer, AssessmentTopicSerializer, QuestionSerializer

from users.models import User


class AssessmentsViewSet(ModelViewSet):
    """
    Assessments viewset.
    """

    serializer_class = AssessmentSerializer
    filterset_fields = ['grade', 'private', 'country', 'language', 'subject']
    search_fields = ['title', 'subject']

    def get_queryset(self):
        """
        Queryset to get allowed assessments
        """
        # Student can access assessments if they're linked to at least one of its topic
        user = self.request.user
        if not user.is_supervisor():
            if user.is_student():

                accessible_assessments = Assessment.objects.filter(assessmenttopic__assessmenttopicaccess__student=user).distinct()

                return accessible_assessments
            return Assessment.objects.filter(private=False)
        
        # Using Q in order to filter with a NOT condition
        return Assessment.objects.exclude(~Q(created_by=user), Q(private=True))


    def list(self, request):

        return Response(AssessmentSerializer(self.get_queryset(), many=True).data)

    
    def retrieve(self, request, pk=None):

        return Response(AssessmentSerializer(get_object_or_404(self.get_queryset(), id=pk), many=False).data)

class AssessmentTopicsViewSet(ModelViewSet):
    """
    Assessment topics viewset.
    """

    queryset = AssessmentTopic.objects.all()
    serializer_class = AssessmentTopicSerializer
    filterset_fields = ['name', 'order', 'assessment']
    search_fields = ['name']

    def list(self, request, assessment_pk=None):

        target_assessment = get_object_or_404(AssessmentsViewSet.get_queryset(self), id=assessment_pk)

        assessment_topics = AssessmentTopic.objects.filter(assessment_id=target_assessment.id)
        
        return Response(AssessmentTopicSerializer(assessment_topics, many=True).data)

    def retrieve(self, request, assessment_pk=None, pk=None):

        return Response("Not Implemented", status=501)
