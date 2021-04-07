from admin.lib.viewsets import ModelViewSet
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
import datetime



from ..models import (Attachment, Question, QuestionInput, QuestionSelect,
                      QuestionSort, QuestionNumberLine, SelectOption, SortOption, AssessmentTopic, AssessmentTopicAccess, Assessment)
from ..serializers import (AttachmentSerializer, QuestionInputSerializer, QuestionNumberLineSerializer,
                           QuestionSelectSerializer, QuestionSerializer,
                           QuestionSortSerializer, SelectOptionSerializer,
                           SortOptionSerializer, AssessmentSerializer)

from .assessments import AssessmentsViewSet

from users.models import User


class QuestionsViewSet(ModelViewSet):
    """
    Questions viewset.
    """

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filterset_fields = ['question_type']
    search_fields = ['title', 'hint']

    def list_all(self, request):

        return Response(QuestionSerializer(Question.objects.all(), many=True).data)


    def list(self, request, assessment_pk=None, topic_pk=None):
        user = self.request.user

        questions = Question.objects.none()

        if user.is_student():

            questions = Question.objects.filter(assessment_topic__assessmenttopicaccess__start_date__lt=datetime.date.today(), assessment_topic__assessmenttopicaccess__end_date__gt=datetime.date.today(), assessment_topic__id=topic_pk, assessment_topic__assessment__id=assessment_pk)

        elif user.is_supervisor():

            questions = Question.objects.filter(assessment_topic__id=topic_pk)

        return Response(QuestionSerializer(questions, many=True).data)

    def retrieve(self, request, assessment_pk=None, topic_pk=None, pk=None):

        user = self.request.user

        question = Question.objects.none()

        if user.is_student():

            question = get_object_or_404(Question.objects.filter(assessment_topic__assessmenttopicaccess__start_date__lt=datetime.date.today(), assessment_topic__assessmenttopicaccess__end_date__gt=datetime.date.today(), assessment_topic__id=topic_pk, assessment_topic__assessment__id=assessment_pk), id=pk)

        elif user.is_supervisor():

            question = get_object_or_404(Question.objects.filter(assessment_topic__id=topic_pk), id=pk)

        response_question = Question.objects.filter(id=pk)
        serializer = QuestionSerializer(response_question, many=True)

        return Response(serializer.data)



class QuestionsInputViewSet(ModelViewSet):
    """
    Questions input viewset.
    """
    queryset = QuestionInput.objects.all()
    serializer_class = QuestionInputSerializer
    search_fields = ['title', 'hint']


class QuestionsSelectViewSet(ModelViewSet):
    """
    Questions select viewset.
    """
    queryset = QuestionSelect.objects.all()
    serializer_class = QuestionSelectSerializer


class QuestionsSortViewSet(ModelViewSet):
    """
    Questions sort viewset.
    """

    queryset = QuestionSort.objects.all()
    serializer_class = QuestionSortSerializer


class QuestionsNumberLineViewSet(ModelViewSet):
    """
    Questions number line viewset.
    """

    queryset = QuestionNumberLine.objects.all()
    serializer_class = QuestionNumberLineSerializer


class SelectOptionsViewSet(ModelViewSet):
    """
    Select options viewset.
    """

    queryset = SelectOption.objects.all()
    serializer_class = SelectOptionSerializer
    filterset_fields = ['id', 'value', 'valid']
    search_fields = ['value', 'valid']


class SortOptionsViewSet(ModelViewSet):
    """
    Sort options viewset.
    """

    queryset = SortOption.objects.all()
    serializer_class = SortOptionSerializer
    filterset_fields = ['id', 'value', 'category']
    search_fields = ['value', 'category']


class AttachmentsViewSet(ModelViewSet):
    """
    Attachments viewset.
    """

    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer

    def list(self, request, questions_pk=None):

        user = self.request.user

        if self.request.user.is_supervisor():

            response_attachments = Attachment.objects.filter((Q(question_id__assessment_topic__assessment__created_by=user) | Q(question_id__assessment_topic__assessment__private=False)), question_id=questions_pk).distinct()
            
        else :
            
            response_attachments = Attachment.objects.filter(question_id__assessment_topic__assessmenttopicaccess__student=user, question_id=questions_pk).distinct()

        return Response(AttachmentSerializer(response_attachments, many=True).data)
        


    def retrieve(self, request, questions_pk=None, pk=None):

        return Response("Not Implemented", status=501)