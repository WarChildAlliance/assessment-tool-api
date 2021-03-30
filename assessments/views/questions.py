from admin.lib.viewsets import ModelViewSet

from ..models import (Attachment, Question, QuestionInput, QuestionSelect,
                      QuestionSort, QuestionNumberLine, SelectOption, SortOption)
from ..serializers import (AttachmentSerializer, QuestionInputSerializer,
                           QuestionSelectSerializer, QuestionSerializer,
                           QuestionSortSerializer, QuestionNumberLineSerializer,
                           SelectOptionSerializer, SortOptionSerializer)

from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class QuestionsViewSet(ModelViewSet):
    """
    Questions viewset.
    """

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filterset_fields = ['question_type']
    search_fields = ['title', 'hint']
    
    def list(self, request):
        print('this is a list')
        print(request)
        return Response(QuestionSerializer(self.queryset, many=True).data)


    def retrieve(self, request, pk=None):
        print('this is a retrieve')
        print(request)
        question = get_object_or_404(self.queryset, pk=pk)
        return Response(serializer_class(question).data)




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
