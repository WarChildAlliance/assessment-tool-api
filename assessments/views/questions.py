from admin.lib.viewsets import ModelViewSet
from rest_framework.response import Response


from ..models import (Attachment, Question, QuestionInput, QuestionSelect,
                      QuestionSort, SelectOption, SortOption, AssessmentTopic, AssessmentTopicAccess)
from ..serializers import (AttachmentSerializer, QuestionInputSerializer,
                           QuestionSelectSerializer, QuestionSerializer,
                           QuestionSortSerializer, SelectOptionSerializer,
                           SortOptionSerializer)


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

        responseAttachments = Attachment.objects.filter(question_id=pk)
        serializer = AttachmentSerializer(responseAttachments, many=True)
        return Response(serializer.data)
