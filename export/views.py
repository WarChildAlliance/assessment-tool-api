from django.shortcuts import render
from answers.models import Answer
from export.serializers import CompleteStudentAnswersSerializer
from admin.lib.viewsets import ModelViewSet


class CompleteStudentAnswersViewSet(ModelViewSet):
    """
    Exposes all answers from all students
    """
    serializer_class = CompleteStudentAnswersSerializer

    def get_queryset(self):
        return Answer.objects.all()