from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.permissions import HasAccess, IsStudent

from admin.lib.viewsets import ModelViewSet

from .models import Answer, AnswerSession, AssessmentTopicAnswer
from .serializers import (AnswerSerializer, AnswerSessionFullSerializer,
                          AnswerSessionSerializer,
                          AssessmentTopicAnswerSerializer)


class AnswersViewSet(ModelViewSet):
    """
    Answers viewset.
    """

    serializer_class = AnswerSerializer

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        if self.action == 'retrieve':
            permission_classes.append(HasAccess)
        elif self.action == 'create':
            permission_classes.append(IsStudent)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Queryset to get allowed answers.
        """
        user = self.request.user
        student_id = self.kwargs.get('student_id', None)

        if user.is_student() and user.id == student_id:
            return Answer.objects.filter(
                topic_answer__session__student=student_id
            ).select_subclasses()
        elif user.is_supervisor():
            return Answer.objects.filter(
                topic_answer__session__student=student_id,
                topic_answer__session__student__created_by=user
            ).select_subclasses()
        else:
            return Answer.objects.none()

    def create(self, request, **kwargs):
        """
        Create a new answer.
        """
        student_id = self.kwargs.get('student_id', None)
        topic_answer = request.data.get('topic_answer')
        if topic_answer is not None:
            has_access = AssessmentTopicAnswer.objects.filter(
                session__student__id=student_id, id=topic_answer).exists()
            if not has_access:
                return Response('Invalid topic answer', status=400)

        return super().create(request, **kwargs)

    def update(self, request, pk=None):
        return Response('Cannot update answer', status=403)

    def partial_update(self, request, pk=None):
        return Response('Cannot update answer', status=403)

    def destroy(self, request, pk=None):
        return Response('Cannot delete answer', status=403)

    @action(detail=False, methods=['post'], serializer_class=AnswerSessionFullSerializer)
    def create_all(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)


class AnswerSessionsViewSet(ModelViewSet):
    """
    Answer sessions viewset.
    """

    serializer_class = AnswerSessionSerializer

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        if self.action == 'retrieve':
            permission_classes.append(HasAccess)
        elif self.action == 'create':
            permission_classes.append(IsStudent)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Queryset to get allowed sessions.
        """
        user = self.request.user
        student_id = int(self.kwargs.get('student_id', None))

        if user.is_student() and user.id == student_id:
            return AnswerSession.objects.filter(student=student_id)
        elif user.is_supervisor():
            return AnswerSession.objects.filter(
                student=student_id,
                student__created_by=user
            )
        else:
            return AnswerSession.objects.none()


class AssessmentTopicAnswersViewSet(ModelViewSet):
    """
    Topic answers viewset.
    """

    serializer_class = AssessmentTopicAnswerSerializer

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        if self.action == 'retrieve':
            permission_classes.append(HasAccess)
        elif self.action == 'create':
            permission_classes.append(IsStudent)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Queryset to get allowed topic answers.
        """
        user = self.request.user
        student_id = self.kwargs.get('student_id', None)

        if user.is_student() and user.id == student_id:
            return AssessmentTopicAnswer.objects.filter(
                session__student=student_id
            )
        elif user.is_supervisor():
            return AssessmentTopicAnswer.objects.filter(
                session__student=student_id,
                session__student__created_by=user
            )
        else:
            return AssessmentTopicAnswer.objects.none()
