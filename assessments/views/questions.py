from admin.lib.viewsets import ModelViewSet
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


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

    def retrieve(self, request, pk=None, **kwargs):

        question_id = kwargs['question_id']
        response_question = self.get_queryset().filter(id=question_id)
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

    def list_for_question(self, request, pk=None):

        if self.request.user.is_student():

            # Fetch the question we want the attachments from
            requested_question = Question.objects.get(pk=pk)

            requested_assessment = requested_question.assessment_topic.assessment

            accessible_assessments = AssessmentsViewSet.get_queryset(self)

            requested_question_is_accessible = accessible_assessments.filter(id=requested_assessment.id).exists()

            if (requested_question_is_accessible):

                response_attachments = Attachment.objects.filter(question_id=pk)
                serializer = AttachmentSerializer(response_attachments, many=True)

                return Response(serializer.data)

            return Response('You dont have access to this assessment', status=403)

