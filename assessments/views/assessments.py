from admin.lib.viewsets import ModelViewSet
from rest_framework.response import Response
from django.db.models import Q

from ..models import Assessment, AssessmentTopic, AssessmentTopicAccess
from ..serializers import AssessmentSerializer, AssessmentTopicSerializer

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
        # Student can access assessments if they're linked to at least one of its topid
        user = self.request.user
        if not user.is_supervisor():
            if user.is_student():
                accessible_assessments_for_student = []
                for assessment_topic_access in AssessmentTopicAccess.objects.filter(student=user):
                    accessible_assessments_for_student.append(assessment_topic_access.topic.assessment.id)
                return Assessment.objects.filter(id__in=accessible_assessments_for_student).distinct()
            return Assessment.objects.filter(private=False)

        # Using Q in order to filter with a NOT condition
        return Assessment.objects.exclude(~Q(created_by=user), Q(private=True))

    def retrieve(self, request, pk=None):

        response_assessment = self.get_queryset().filter(pk=pk)
        serializer = AssessmentSerializer(response_assessment, many=True)

        return Response(serializer.data)


class AssessmentTopicsViewSet(ModelViewSet):
    """
    Assessment topics viewset.
    """

    queryset = AssessmentTopic.objects.all()
    serializer_class = AssessmentTopicSerializer
    filterset_fields = ['name', 'order', 'assessment']
    search_fields = ['name']
