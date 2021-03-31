from admin.lib.viewsets import ModelViewSet
from rest_framework.response import Response

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
        user = self.request.user
        if user.is_supervisor():
            return Assessment.objects.all()
      
        return Assessment.objects.filter(private=False)

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
