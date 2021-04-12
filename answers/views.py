from django.db.models import Q

from admin.lib.viewsets import ModelViewSet

from .models import Answer, AnswerSession, AssessmentTopicAnswer
from .serializers import (AnswerSerializer, AnswerSessionSerializer,
                          AssessmentTopicAnswerSerializer)


class AnswersViewSet(ModelViewSet):
    """
    Answers viewset.
    """

    serializer_class = AnswerSerializer
    # TODO: Add permissions

    def get_queryset(self):
        """
        Queryset to get allowed answers.
        """

        student_id = self.kwargs.get('student_id', None)

        return Answer.objects.filter(
            topic_answer__session__student=student_id
        )


class AnswerSessionsViewSet(ModelViewSet):
    """
    Answer sessions viewset.
    """

    serializer_class = AnswerSessionSerializer

    def get_queryset(self):
        """
        Queryset to get allowed sessions.
        """

        student_id = self.kwargs.get('student_id', None)
        return AnswerSession.objects.filter(student=student_id)


class AssessmentTopicAnswersViewSet(ModelViewSet):
    """
    Topic answers viewset.
    """

    serializer_class = AssessmentTopicAnswerSerializer

    def get_queryset(self):
        """
        Queryset to get allowed topic answers.
        """

        student_id = self.kwargs.get('student_id', None)
        return AssessmentTopicAnswer.objects.filter(session__student=student_id)
