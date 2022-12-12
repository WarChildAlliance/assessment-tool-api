from users.models import User
from django.db.models import Q, Case, When
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from users.permissions import HasAccess, IsSupervisor
from django.views.generic import CreateView
from datetime import date

from admin.lib.viewsets import ModelViewSet

from .models import (Assessment, QuestionSet, QuestionSetAccess, NumberRange,
                     Attachment, DraggableOption, LearningObjective, Question, Topic)
from .serializers import (AssessmentDeepSerializer, AssessmentSerializer,
                          QuestionSetAccessSerializer,
                          QuestionSetSerializer, AttachmentSerializer, DraggableOptionSerializer,
                          QuestionSerializer, TopicSerializer, LearningObjectiveSerializer, NumberRangeSerializer)


class AssessmentsViewSet(ModelViewSet):
    """
    Assessments viewset.
    """

    serializer_class = AssessmentSerializer
    filterset_fields = ['grade', 'private', 'country', 'language', 'subject']
    search_fields = ['title', 'subject']

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        if self.action == 'retrieve':
            permission_classes.append(HasAccess)
        elif self.action == 'destroy' or self.action == 'update':
            permission_classes.append(HasAccess)
            permission_classes.append(IsSupervisor)
        elif self.action == 'create':
            permission_classes.append(IsSupervisor)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Queryset to get allowed assessments.
        """
        user = self.request.user

        if user.is_supervisor():
            # Using Q in order to filter with a NOT condition
            return Assessment.objects.filter(Q(created_by=user) | Q(private=False))


        # Students can access assessments if they're linked to at least one of its question_set
        return Assessment.objects.filter(
            questionset__questionsetaccess__student=user,
            questionset__questionsetaccess__start_date__lte=date.today(),
            questionset__questionsetaccess__end_date__gte=date.today()
        ).distinct()


    def create(self, request):
        """
        Create a new Assessment.
        """

        user = self.request.user
        request_data = request.data.copy()
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    # THIS IS ONLY TEMPORARY FOR PRE-SEL AND POST-SEL, TODO REMOVE AFTERWARD

    def list(self, request, *args, **kwargs):

        serializer = AssessmentSerializer(
            self.get_queryset(), many=True,
            context={
                'student_pk': int(self.request.user.id)
            }
        )

        return Response(serializer.data)
    # END OF TEMPORARY

    @action(detail=False, methods=['get'], serializer_class=AssessmentDeepSerializer)
    def get_assessments(self, request):

        serializer = AssessmentDeepSerializer(
            self.get_queryset().order_by('-questionset__questionsetaccess__start_date'), many=True,
            context={
                'student_pk': int(self.request.user.id)
            }
        )

        return Response(serializer.data, status=201)


class QuestionSetsViewSet(ModelViewSet):
    """
    Question sets viewset.
    """

    serializer_class = QuestionSetSerializer
    filterset_fields = ['name', 'assessment']
    search_fields = ['name']

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated, HasAccess]
        if self.action == 'destroy' or self.action == 'update' or self.action == 'create':
            permission_classes.append(IsSupervisor)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Queryset to get allowed assessment question_sets.
        """
        user = self.request.user
        assessment_pk = self.kwargs['assessment_pk']

        if user.is_student():
            return QuestionSet.objects.filter(
                assessment=assessment_pk,
                questionsetaccess__student=user,
                questionsetaccess__start_date__lte=date.today(),
                questionsetaccess__end_date__gte=date.today(),
            ).distinct()

        return QuestionSet.objects.filter(assessment=assessment_pk)

    def create(self, request, *args, **kwargs):
        """
        Create a new QuestionSet.
        """
        request_data = request.data.copy()

        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, pk=None, **kwargs):
        """
        Update assessment question_set.
        """
        instance = self.get_object()
        request_data = request.data.copy()
        request_order = int(request.data.get('order')) if request.data.get('order') else None

        # Check if question_set order changed to reorder all others question_sets
        # (do not enter here if instance.order = None (has not been set before))
        if (instance.order and request_order) and instance.order != request_order:
            question_sets = QuestionSet.objects.filter(assessment=instance.assessment)

            # Create an array with the question_sets from the QuerySet
            question_sets_list = [question_set for question_set in question_sets]

            # Places the question_set in the position of the array equivalent to its new order
            question_set = question_sets_list[instance.order - 1]
            question_sets_list.remove(question_set)
            question_sets_list.insert((request_order - 1) if (request_order > 0) else 0, question_set)

            # Order of each question_set is its position in the array + 1 (order can't be zero)
            for index, question_set in enumerate(question_sets_list):
                question_set.order = index + 1
                question_set.save()

            # If assessment has the “Contains SEL questions” set as true, and if there were SEL questions in the first question_set
            # make sure the questions are in the first question_set after reordering the question_sets
            sel_questions = Question.objects.filter(question_type='SEL', question_set__assessment=instance.assessment)
            if instance.assessment.sel_question and sel_questions:
                first_question_set = question_sets_list[0]
                sel_questions.update(question_set=first_question_set)
                # order question_set's QuerySet all_questions so SEL questions are at the beginning
                all_questions = Question.objects.filter(question_set=first_question_set).order_by(Case(When(question_type='SEL', then=0), default=1))
                # Order of each question is its position in the array + 1 (order can't be zero)
                for index, question in enumerate(all_questions):
                    question.order = index + 1
                    question.save()

        serializer = self.get_serializer(instance, data=request_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], url_path='reorder')
    def reorder_all_question_sets(self, request, pk=None, **kwargs):
        """
        Updates the order of all assessment question_sets.
        """
        # reauest_data = {
        #   'question_sets': [array with question_sets ids, where its index in the array is your new order (+1)],
        #   'assessment_id': <assessment_id>
        # }
        request_data = request.data.copy()
        question_sets = QuestionSet.objects.filter(assessment=request_data['assessment_id'])

        try:
            for question_set in question_sets:
                for index, element in enumerate(request_data['question_sets']):
                    if (question_set.id == element) and (question_set.order != index + 1):
                        question_set.order = index + 1
                        question_set.save()
                        break

            # If assessment has the “Contains SEL questions” set as true, and if there were SEL questions in the first question_set
            # make sure the questions are in the first question_set after reordering the question_sets
            sel_questions = Question.objects.filter(question_type='SEL', question_set__assessment__id=request_data['assessment_id'])
            first_question_set = request_data['question_sets'][0]
            if question_sets[0].assessment.sel_question and sel_questions:
                sel_questions.update(question_set_id=first_question_set)
                # order question_set's QuerySet all_questions so SEL questions are at the beginning
                all_questions = Question.objects.filter(question_set_id=first_question_set).order_by(Case(When(question_type='SEL', then=0), default=1))
                # Order of each question is its position in the array + 1 (order can't be zero)
                for index, question in enumerate(all_questions):
                    question.order = index + 1
                    question.save()
        except:
            return Response('An error occurred while trying to update the order of assessments question_sets', status=500)

        return Response('QuestionSets successfully reordered.', status=200)


class QuestionsViewSet(ModelViewSet):
    """
    Questions viewset.
    """

    serializer_class = QuestionSerializer

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated, HasAccess]
        if self.action == 'destroy' or self.action == 'update' or self.action == 'create':
            permission_classes.append(IsSupervisor)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Queryset to get allowed questions.
        """

        question_set_pk = self.kwargs['question_set_pk']
        assessment_pk = self.kwargs['assessment_pk']

        return Question.objects.filter(
            question_set=question_set_pk,
            question_set__assessment=assessment_pk
        ).exclude(
            Q(question_type='SEL') & (~Q(question_set__order=1) | Q(question_set__assessment__sel_question=False))
        ).select_subclasses()

    def create(self, request, *args, **kwargs):
        """
        Create a new Question.
        """
        request_data = request.data.copy()

        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    @action(detail=False, methods=['put'], url_path='reorder')
    def reorder_all_questions(self, request, pk=None, **kwargs):
        """
        Updates the order of all questions.
        """
        # reauest_data = {
        #   'questions': [array with questions ids, where its index in the array is your new order (+1)],
        #   'question_set': <question_set'>
        # }
        request_data = request.data.copy()
        questions = Question.objects.filter(question_set=request_data['question_set']).select_subclasses()

        try:
            for question in questions:
                for index, element in enumerate(request_data['questions']):
                    if (question.id == element) and (question.order != index + 1):
                        question.order = index + 1
                        question.save()
                        break
        except:
            return Response('An error occurred while trying to update the order of the questions', status=500)

        return Response('Questions successfully reordered.', status=200)

    @action(detail=False, methods=['get'], url_path='all')
    def get_all_questions_type(self, request):
        accessible_assessments = AssessmentsViewSet.get_queryset(self)
        request_question_type = self.request.query_params.get('type').split(',')

        questions = Question.objects.filter(question_set__assessment__in=accessible_assessments, question_type=request_question_type).select_subclasses()
        serializer = QuestionSerializer(questions, many=True)

        return Response(serializer.data, status=200)


class GeneralAttachmentsViewSet(ModelViewSet):
    """
    Attachments viewset.
    """

    model = Attachment
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Queryset to get allowed assessments.
        """
        if not self.request.user.role == User.UserRole.SUPERVISOR:
            return None

        return Attachment.objects.distinct()

    def list(self, request, *args, **kwargs):
        return Response('Cannot list attachments', status=403)

    def retrieve(self, request, *args, **kwargs):
        return Response('Cannot retrieve attachment', status=403)


class AttachmentsViewSet(ModelViewSet, CreateView):
    """
    Attachments viewset.
    """

    model = Attachment
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Queryset to get attachments.
        """

        question_pk = self.kwargs['question_pk']

        return Attachment.objects.filter(question=question_pk)


class DraggableOptionsViewSet(ModelViewSet, CreateView):
    """
    Draggable option viewset.
    """
    model = DraggableOption
    serializer_class = DraggableOptionSerializer

    def get_queryset(self):
        """
        Queryset to get draggable options.
        """
        question_pk = self.kwargs['question_pk']

        return DraggableOption.objects.filter(question_drag_and_drop=question_pk)


class QuestionSetAccessesViewSets(ModelViewSet):
    """
    Question set accesses viewset.
    """

    serializer_class = QuestionSetAccessSerializer
    permission_classes = [IsAuthenticated, IsSupervisor]

    def get_queryset(self):
        """
        Queryset to get assessment question_set accesses.
        """
        assessment_pk = self.kwargs['assessment_pk']
        user = self.request.user

        return QuestionSetAccess.objects.filter(
            student__created_by=user, question_set__assessment__id=assessment_pk)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request, *args, **kwargs):
        """
        Assign assessment question_sets to students.
        """
        assessment_pk = kwargs.get('assessment_pk')
        user = request.user
        formatted_data = []

        for student in request.data['students']:
            try:
                User.objects.get(
                    id=student, created_by=user, role=User.UserRole.STUDENT)
            except:
                return Response('Cannot create access for unauthorized students', status=400)
            for access in request.data['accesses']:
                try:
                    QuestionSet.objects.get(
                        Q(id=access.get('question_set')),
                        Q(assessment__id=assessment_pk),
                        Q(assessment__created_by=user) | Q(assessment__private=False))
                except:
                    return Response('Cannot create access for unauthorized question_sets \
                        or question_sets in another assessment', status=400)

                if Question.objects.filter(question_set=access.get('question_set')).count() == 0:
                    return Response('Cannot create access for question_sets without questions', status=400)

                formatted_data.append({
                    'student': student,
                    'question_set': access.get('question_set'),
                    'start_date': access.get('start_date', None),
                    'end_date': access.get('end_date', None)
                })

        if len(formatted_data) == 0:
            return Response('No data', status=400)

        serializer = self.get_serializer(data=formatted_data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)


class TopicsViewSet(GenericViewSet, ListModelMixin):
    """
    Topic viewset
    """
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated, IsSupervisor]

    def get_queryset(self):
        """
        Queryset to get topics.
        """
        topics = Topic.objects.all()
        subject = self.request.query_params.get('subject', None)
        if subject:
            topics = topics.filter(subject=subject)

        return topics


class LearningObjectivesViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    """
    Learning objectives viewset.
    """
    serializer_class = LearningObjectiveSerializer
    permission_classes = [IsAuthenticated, IsSupervisor]

    def get_queryset(self):
        learning_objectives = LearningObjective.objects.all()

        grade = self.request.query_params.get('grade', None)
        if grade:
            learning_objectives = learning_objectives.filter(grade=grade)

        subject = self.request.query_params.get('subject', None)
        if subject:
            learning_objectives = learning_objectives.filter(topic__subject=subject)

        topic = self.request.query_params.get('topic', None)
        if topic:
            learning_objectives = learning_objectives.filter(topic=topic)

        return learning_objectives


class NumberRangesViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    """
    Number ranges viewset.
    """
    serializer_class = NumberRangeSerializer
    permission_classes = [IsAuthenticated, IsSupervisor]

    def get_queryset(self):
        number_ranges = NumberRange.objects.all()

        grade = self.request.query_params.get('grade', None)
        if grade:
            number_ranges = number_ranges.filter(grade=grade)

        return number_ranges