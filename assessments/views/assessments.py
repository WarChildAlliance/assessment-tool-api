from admin.lib.viewsets import ModelViewSet
from rest_framework.response import Response
from django.db.models import Q

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
    
    def topics_per_assessment(self, request, pk=None, **kwargs):        
        assessment_id = kwargs['assessment_id']

        # Check if the user has access to assessment
        if self.get_queryset().filter(id=assessment_id).exists():
            assessment = self.get_queryset().filter(id=assessment_id)
            topics_response = AssessmentTopic.objects.filter(assessment=assessment[0])
            serializer = AssessmentTopicSerializer(topics_response, many=True)
            return Response(serializer.data)
        
        return Response('You dont have access to this assessment', status=403)
    
    def questions_list_for_assessment_topic(self, request, pk=None, **kwargs):
        user = self.request.user
        assessment_id = kwargs['assessment_id']
        assessment = self.get_queryset().filter(id=assessment_id)
        topic_id = kwargs['topic_id']
        topic = AssessmentTopic.objects.filter(id=topic_id)

        if user.is_student():
            # Check if the student has access to this topic
            if AssessmentTopicAccess.objects.filter(topic=topic[0]).exists():
                accessible_topic = AssessmentTopicAccess.objects.filter(topic=topic[0]).exists()
                questions_response = Question.objects.filter(assessment_topic=topic[0])
                serializer = QuestionSerializer(questions_response, many=True)
                return Response(serializer.data)
            else:
                return Response('You dont have access to this assessment', status=403)
        
        if user.is_supervisor:
            if assessment.exists():
                questions_response = Question.objects.filter(assessment_topic=topic[0])
                serializer = QuestionSerializer(questions_response, many=True)
                return Response(serializer.data)
            else:
                return Response('You dont have access to this assessment', status=403)


class AssessmentTopicsViewSet(ModelViewSet):
    """
    Assessment topics viewset.
    """

    queryset = AssessmentTopic.objects.all()
    serializer_class = AssessmentTopicSerializer
    filterset_fields = ['name', 'order', 'assessment']
    search_fields = ['name']
