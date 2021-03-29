from admin.lib.viewsets import ModelViewSet
from rest_framework.response import Response


from ..models import (Attachment, Question, QuestionInput, QuestionSelect,
                      QuestionSort, SelectOption, SortOption)
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
        return Response("You retrieved attachments for question %s" % (pk))
