from django.shortcuts import render
from rest_framework.response import Response
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
    

    def retrieve(self, request, pk=None):
        return Response('Cannot retrieve export', status=403)

class SupervisorStudentAnswerViewSet(ModelViewSet):

    serializer_class = AnswerTableSerializer

    def get_queryset(self):
        supervisor_id = int(self.kwargs.get('supervisor_id', None))
        return Answer.objects.filter(topic_answer__topic_access__student__created_by=supervisor_id).select_subclasses().order_by('topic_answer__topic_access__student', 'topic_answer__topic_access__topic__assessment', 'topic_answer__topic_access__topic', 'topic_answer__start_date', 'question')

