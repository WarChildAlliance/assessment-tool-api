from datetime import date

from django.db.models.signals import post_save
from gamification.signals import on_topic_answer_submission

from assessments.models import AssessmentTopicAccess, Question
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.permissions import HasAccess, IsStudent
from gamification.models import Profile, TopicCompetency

from admin.lib.viewsets import ModelViewSet

from .models import Answer, AnswerSession, AssessmentTopicAnswer
from .serializers import (AnswerSerializer, AnswerSessionFullSerializer,
                          AnswerSessionSerializer,
                          AssessmentTopicAnswerFullSerializer,
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
        student_id = int(self.kwargs.get('student_id', None))

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

    @action(detail=False, methods=['post'], serializer_class=AnswerSessionFullSerializer)
    def create_all(self, request, **kwargs):
        """
        Create a session, its topic answers and its answers.
        """
        student_id = int(self.kwargs.get('student_id', None))
        request_data = request.data.copy()

        for topic_answer in request_data.get('assessment_topic_answers', []):
            topic_id = None

            # Get topic_access
            if topic_answer.get('topic', None):
                topic_id = topic_answer.get('topic')
                try:
                    topic_access = AssessmentTopicAccess.objects.get(
                        Q(topic=topic_id),
                        Q(student=student_id),
                        Q(start_date__lte=date.today()) | Q(
                            start_date__isnull=True),
                        Q(end_date__gte=date.today()) | Q(end_date__isnull=True)
                    )
                    topic_answer['topic_access'] = topic_access
                    topic_answer.pop('topic')
                except ObjectDoesNotExist:
                    return Response('Student does not have access to this topic', status=400)

            if not topic_answer['topic_access']:
                return Response('No topic access defined', status=400)
            
            # Check if topic answer is complete
            if topic_id is None:
                topic_id = AssessmentTopicAccess.objects.values_list(
                    'topic__id', flat=True).get(id=topic_answer.get('topic_access'))
            count_questions_in_topic = Question.objects.filter(assessment_topic=topic_id).count()
            count_questions_answered = len(topic_answer['answers'])
            topic_answer['complete'] = (count_questions_answered == count_questions_in_topic)

        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

class AssessmentTopicAnswersViewSet(ModelViewSet):
    """
    Topic answers viewset.
    """

    filterset_fields = ['topic_access__topic', 'complete']

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
        student_id = int(self.kwargs.get('student_id', None))

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

    def create(self, request, **kwargs):
        """
        Create a new topic answer.
        """
        request_data = request.data.copy()
        student_id = int(kwargs.get('student_id', None))

        if request_data.get('topic', None):
            try:
                topic_access = AssessmentTopicAccess.objects.get(
                    Q(topic=request_data.get('topic')),
                    Q(student=student_id),
                    Q(start_date__isnull=True) | Q(start_date__lte=date.today()),
                    Q(end_date__isnull=True) | Q(end_date__gte=date.today())
                )
                request_data['topic_access'] = topic_access.id
                request_data.pop('topic')
            except ObjectDoesNotExist:
                return Response('Student does not have access to this topic', status=400)

        if not request_data['topic_access']:
            return Response('No topic access defined', status=400)

        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, pk=None, **kwargs):
        """
        Update a topic answer.
        """
        partial = True
        instance = self.get_object()

        request_data = request.data.copy()
        new_amount = request_data.get('topic_competency', None)


        topic_id = instance.topic_access.topic.id
        count_questions_in_topic = Question.objects.filter(assessment_topic=topic_id).count()
        count_questions_answered = Answer.objects.filter(topic_answer=instance.id).count()
        request_data['complete'] = (count_questions_answered == count_questions_in_topic)

        profile = Profile.objects.get(student = instance.topic_access.student.id)

        # Updating the topic competency from the front
        if (TopicCompetency.objects.filter(profile=profile, topic=instance.topic_access.topic).exists()):

            current_competency = TopicCompetency.objects.get(profile=profile, topic=instance.topic_access.topic)

            if (new_amount > current_competency.competency):
                current_competency.competency = new_amount
                current_competency.save()

        # If no matching topic competency exists, create a new one with the new value
        else:

            TopicCompetency.objects.create(profile=profile, topic=instance.topic_access.topic, competency=new_amount)

        serializer = self.get_serializer(instance, data=request_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], serializer_class=AssessmentTopicAnswerFullSerializer)
    def create_all(self, request, **kwargs):
        """
        Create a topic answer and its answers.
        """
        request_data = request.data.copy()
        student_id = int(self.kwargs.get('student_id', None))
        topic_id = None


        if request_data.get('topic', None):
            topic_id = request_data.get('topic')
            try:
                topic_access = AssessmentTopicAccess.objects.get(
                    Q(topic=topic_id),
                    Q(student=student_id),
                    Q(start_date__lte=date.today()) | Q(start_date__isnull=True),
                    Q(end_date__gte=date.today()) | Q(end_date__isnull=True)
                )
                request_data['topic_access'] = topic_access.id
                request_data.pop('topic')
            except ObjectDoesNotExist:
                return Response('Student does not have access to this topic', status=400)

        if not request_data.get('topic_access', None):
            return Response('No topic access defined', status=400)

        # Check if topic answer is complete
        if topic_id is None:
            topic_id = AssessmentTopicAccess.objects.values_list(
                'topic__id', flat=True).get(id=request_data.get('topic_access'))
        count_questions_in_topic = Question.objects.filter(assessment_topic=topic_id).count()
        count_questions_answered = len(request_data['answers'])
        request_data['complete'] = (count_questions_answered == count_questions_in_topic)

        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
