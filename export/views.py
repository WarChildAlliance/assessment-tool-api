from django.shortcuts import render
from answers.models import Answer
from export.serializers import CompleteStudentAnswersSerializer, AnswerTableSerializer
from admin.lib.viewsets import ModelViewSet


class CompleteStudentAnswersViewSet(ModelViewSet):
    """
    Exposes all answers from all students
    """
    serializer_class = AnswerTableSerializer

    def get_queryset(self):
        return Answer.objects.all().select_subclasses().order_by('topic_answer__topic_access__student', 'topic_answer__topic_access__topic__assessment', 'topic_answer__topic_access__topic', 'topic_answer__start_date', 'question')