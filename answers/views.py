from datetime import date

from django.db.models.signals import post_save
from gamification.signals import on_question_set_answer_submission

from assessments.models import QuestionSetAccess, Question
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.permissions import HasAccess, IsStudent
from gamification.models import Profile, QuestionSetCompetency

from admin.lib.viewsets import ModelViewSet

from .models import Answer, AnswerSession, QuestionSetAnswer
from .serializers import (AnswerSerializer, AnswerSessionFullSerializer,
                          AnswerSessionSerializer,
                          QuestionSetAnswerFullSerializer,
                          QuestionSetAnswerSerializer)


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
                question_set_answer__session__student=student_id
            ).select_subclasses()
        elif user.is_supervisor():
            return Answer.objects.filter(
                question_set_answer__session__student=student_id,
                question_set_answer__session__student__created_by=user
            ).select_subclasses()
        else:
            return Answer.objects.none()

    def create(self, request, **kwargs):
        """
        Create a new answer.
        """
        student_id = self.kwargs.get('student_id', None)
        question_set_answer = request.data.get('question_set_answer')
        if question_set_answer is not None:
            has_access = QuestionSetAnswer.objects.filter(
                session__student__id=student_id, id=question_set_answer).exists()
            if not has_access:
                return Response('Invalid question_set answer', status=400)

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
        Create a session, its question_set answers and its answers.
        """
        student_id = int(self.kwargs.get('student_id', None))
        request_data = request.data.copy()

        for question_set_answer in request_data.get('question_set_answers', []):
            question_set_id = None

            # Get question_set_access
            if question_set_answer.get('question_set', None):
                question_set_id = question_set_answer.get('question_set')
                try:
                    question_set_access = QuestionSetAccess.objects.get(
                        Q(question_set=question_set_id),
                        Q(student=student_id),
                        Q(start_date__lte=date.today()) | Q(
                            start_date__isnull=True),
                        Q(end_date__gte=date.today()) | Q(end_date__isnull=True)
                    )
                    question_set_answer['question_set_access'] = question_set_access
                    question_set_answer.pop('question_set')
                except ObjectDoesNotExist:
                    return Response('Student does not have access to this question_set', status=400)

            if not question_set_answer['question_set_access']:
                return Response('No question_set access defined', status=400)

            # Check if question_set answer is complete
            if question_set_id is None:
                question_set_id = QuestionSetAccess.objects.values_list(
                    'question_set__id', flat=True).get(id=question_set_answer.get('question_set_access'))
            count_questions_in_question_set = Question.objects.filter(question_set=question_set_id).count()
            count_questions_answered = len(question_set_answer['answers'])
            question_set_answer['complete'] = (count_questions_answered == count_questions_in_question_set)

        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

class QuestionSetAnswersViewSet(ModelViewSet):
    """
    QuestionSet answers viewset.
    """

    filterset_fields = ['question_set_access__question_set', 'complete']

    serializer_class = QuestionSetAnswerSerializer

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
        Queryset to get allowed question_set answers.
        """
        user = self.request.user
        student_id = int(self.kwargs.get('student_id', None))

        if user.is_student() and user.id == student_id:
            return QuestionSetAnswer.objects.filter(
                session__student=student_id
            )
        elif user.is_supervisor():
            return QuestionSetAnswer.objects.filter(
                session__student=student_id,
                session__student__created_by=user
            )
        else:
            return QuestionSetAnswer.objects.none()

    def create(self, request, **kwargs):
        """
        Create a new question_set answer.
        """
        request_data = request.data.copy()
        student_id = int(kwargs.get('student_id', None))

        if request_data.get('question_set', None):
            try:
                question_set_access = QuestionSetAccess.objects.get(
                    Q(question_set=request_data.get('question_set')),
                    Q(student=student_id),
                    Q(start_date__isnull=True) | Q(start_date__lte=date.today()),
                    Q(end_date__isnull=True) | Q(end_date__gte=date.today())
                )
                request_data['question_set_access'] = question_set_access.id
                request_data.pop('question_set')
            except ObjectDoesNotExist:
                return Response('Student does not have access to this question_set', status=400)

        if not request_data['question_set_access']:
            return Response('No question_set access defined', status=400)

        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, pk=None, **kwargs):
        """
        Update a question_set answer.
        """
        partial = True
        instance = self.get_object()

        request_data = request.data.copy()
        new_amount = request_data.get('question_set_competency', None)


        question_set_id = instance.question_set_access.question_set.id
        count_questions_in_question_set = Question.objects.filter(question_set=question_set_id).count()
        count_questions_answered = Answer.objects.filter(question_set_answer=instance.id).count()
        request_data['complete'] = (count_questions_answered == count_questions_in_question_set)

        profile = Profile.objects.get(student = instance.question_set_access.student.id)

        # Updating the question_set competency from the front
        if (QuestionSetCompetency.objects.filter(profile=profile, question_set=instance.question_set_access.question_set).exists()):

            current_competency = QuestionSetCompetency.objects.get(profile=profile, question_set=instance.question_set_access.question_set)

            if (new_amount > current_competency.competency):
                current_competency.competency = new_amount
                current_competency.save()

        # If no matching question_set competency exists, create a new one with the new value
        else:

            QuestionSetCompetency.objects.create(profile=profile, question_set=instance.question_set_access.question_set, competency=new_amount)

        serializer = self.get_serializer(instance, data=request_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], serializer_class=QuestionSetAnswerFullSerializer)
    def create_all(self, request, **kwargs):
        """
        Create a question_set answer and its answers.
        """
        request_data = request.data.get('cachedAnswers').copy()
        student_id = int(self.kwargs.get('student_id', None))
        question_set_id = None

        new_amount = request_data.get('question_set_competency')
        if (new_amount is None):
            new_amount = 0

        question_set_access = None

        if request_data.get('question_set', None):
            question_set_id = request_data.get('question_set')
            try:
                question_set_access = QuestionSetAccess.objects.get(
                    Q(question_set=question_set_id),
                    Q(student=student_id),
                    Q(start_date__lte=date.today()) | Q(start_date__isnull=True),
                    Q(end_date__gte=date.today()) | Q(end_date__isnull=True)
                )
                request_data['question_set_access'] = question_set_access.id
                request_data.pop('question_set')
            except ObjectDoesNotExist:
                return Response('Student does not have access to this question_set', status=400)

        #if not request_data.get('question_set_access', None):
        #    return Response('No question_set access defined', status=400)


        # Check if question_set answer is complete
        if question_set_id is None:
            question_set_id = QuestionSetAccess.objects.values_list(
                'question_set__id', flat=True).get(id=request_data.get('question_set_access'))
        count_questions_in_question_set = Question.objects.filter(question_set=question_set_id).count()
        count_questions_answered = len(request_data['answers'])
        request_data['complete'] = (count_questions_answered == count_questions_in_question_set)

        profile = Profile.objects.get(student = student_id)
        # Updating the question_set competency from the front
        if (QuestionSetCompetency.objects.filter(profile=profile, question_set=question_set_access.question_set).exists()):

            current_competency = QuestionSetCompetency.objects.get(profile=profile, question_set=question_set_access.question_set)

            if (new_amount > current_competency.competency):
                current_competency.competency = new_amount
                current_competency.save()

        # If no matching question_set competency exists, create a new one with the new value
        else:
            QuestionSetCompetency.objects.create(profile=profile, question_set=question_set_access.question_set, competency=new_amount)

        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
