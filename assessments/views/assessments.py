from admin.lib.viewsets import ModelViewSet
from rest_framework.response import Response
from django.db.models import Q

from ..models import Assessment, AssessmentTopic
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
        # Student can access assessments dont il a au moins un topic
        user = self.request.user
        if not user.is_supervisor():
            return Assessment.objects.filter(private=False)

        # Using Q in order to filter with a NOT condition
        return Assessment.objects.exclude(~Q(created_by=user), Q(private=True))

    def retrieve(self, request, pk=None):

        responseAssessment = self.get_queryset().filter(pk=pk)
        serializer = AssessmentSerializer(responseAssessment, many=True)

        return Response(serializer.data)


class AssessmentTopicsViewSet(ModelViewSet):
    """
    Assessment topics viewset.
    """

    queryset = AssessmentTopic.objects.all()
    serializer_class = AssessmentTopicSerializer
    filterset_fields = ['name', 'order', 'assessment']
    search_fields = ['name']

    # TODO Get AssessmentTopicAccess linked to student, get AssessmentTopic linked to access, get Assessments
    def accessible_assessments_for_student(self,request, pk=None):
        return Assessment.objects.all()