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
    
    def topics_list_for_assessment(self, request, pk=None, **kwargs):

        target_assessment = get_object_or_404(self.get_queryset(), id=kwargs['assessment_id'])

        assessment_topics = AssessmentTopic.objects.filter(assessment_id=target_assessment.id)
        
        return Response(AssessmentTopicSerializer(assessment_topics, many=True).data)

    
    def questions_list_for_assessment_topic(self, request, pk=None, **kwargs):
        user = self.request.user

        questions = Question.objects.none()

        if user.is_student():

            questions = Question.objects.filter(assessment_topic__assessmenttopicaccess__start_date__lt=datetime.date.today(), assessment_topic__assessmenttopicaccess__end_date__gt=datetime.date.today(), assessment_topic__id=kwargs['topic_id'], assessment_topic__assessment__id=kwargs['assessment_id'])

        elif user.is_supervisor():

            questions = Question.objects.filter(assessment_topic__id=kwargs['topic_id'])

        return Response(QuestionSerializer(questions, many=True).data)

        
    def question_detail_for_assessment_topic(self, request, pk=None, **kwargs):
        user = self.request.user

        question = Question.objects.none()

        if user.is_student():

            question = get_object_or_404(Question.objects.filter(assessment_topic__assessmenttopicaccess__start_date__lt=datetime.date.today(), assessment_topic__assessmenttopicaccess__end_date__gt=datetime.date.today(), assessment_topic__id=kwargs['topic_id'], assessment_topic__assessment__id=kwargs['assessment_id']), id=kwargs['question_id'])

        elif user.is_supervisor():

            question = get_object_or_404(Question.objects.filter(assessment_topic__id=kwargs['topic_id']), id=kwargs['question_id'])

        return Response(QuestionSerializer(question, many=False).data)

        

class AssessmentTopicsViewSet(ModelViewSet):
    """
    Assessment topics viewset.
    """

    queryset = AssessmentTopic.objects.all()
    serializer_class = AssessmentTopicSerializer
    filterset_fields = ['name', 'order', 'assessment']
    search_fields = ['name']
