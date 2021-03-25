from admin.lib.viewsets import ModelViewSet

from ..models import Assessment, AssessmentTopic
from ..serializers import AssessmentSerializer, AssessmentTopicSerializer


class AssessmentsViewSet(ModelViewSet):
    """
    Assessments viewset.
    """

    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    filterset_fields = ['grade', 'private', 'country', 'language', 'subject']
    search_fields = ['title', 'subject']


class AssessmentTopicsViewSet(ModelViewSet):
    """
    Assessment topics viewset.
    """

    queryset = AssessmentTopic.objects.all()
    serializer_class = AssessmentTopicSerializer
    filterset_fields = ['name', 'order', 'assessment']
    search_fields = ['name']
