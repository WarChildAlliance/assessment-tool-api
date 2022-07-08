from users.models import User
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.permissions import HasAccess, IsSupervisor
from django.views.generic import CreateView
from datetime import date

from admin.lib.viewsets import ModelViewSet

from .models import (Assessment, AssessmentTopic, AssessmentTopicAccess,
                     Attachment, DraggableOption, Question)
from .serializers import (AssessmentDeepSerializer, AssessmentSerializer,
                          AssessmentTopicAccessSerializer,
                          AssessmentTopicSerializer, AttachmentSerializer, DraggableOptionSerializer,
                          QuestionSerializer)


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


        # Students can access assessments if they're linked to at least one of its topic
        return Assessment.objects.filter(
            assessmenttopic__assessmenttopicaccess__student=user,
            assessmenttopic__assessmenttopicaccess__start_date__lte=date.today(),
            assessmenttopic__assessmenttopicaccess__end_date__gte=date.today()
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
    def get_all(self, request):

        serializer = AssessmentDeepSerializer(
            self.get_queryset(), many=True,
            context={
                'student_pk': int(self.request.user.id)
            }
        )

        return Response(serializer.data, status=201)


class AssessmentTopicsViewSet(ModelViewSet):
    """
    Assessment topics viewset.
    """

    serializer_class = AssessmentTopicSerializer
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
        Queryset to get allowed assessment topics.
        """
        user = self.request.user
        assessment_pk = self.kwargs['assessment_pk']

        if user.is_student():
            return AssessmentTopic.objects.filter(
                assessment=assessment_pk,
                assessmenttopicaccess__student=user,
                assessmenttopicaccess__start_date__lte=date.today(),
                assessmenttopicaccess__end_date__gte=date.today(),
            ).distinct()

        return AssessmentTopic.objects.filter(assessment=assessment_pk)

    def create(self, request, *args, **kwargs):
        """
        Create a new Topic.
        """
        request_data = request.data.copy()

        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
    
    def update(self, request, pk=None, **kwargs):
        """
        Update assessment topic.
        """
        instance = self.get_object()
        request_data = request.data.copy()
        request_order = int(request.data.get('order')) if request.data.get('order') else None

        # Check if topic order changed to reorder all others topics
        # (do not enter here if instance.order = None (has not been set before))
        if (instance.order and request_order) and instance.order != request_order:
            topics = AssessmentTopic.objects.filter(assessment=instance.assessment)

            # Create an array with the topics from the QuerySet
            topics_list = [topic for topic in topics]

            # Places the topic in the position of the array equivalent to its new order
            topic = topics_list[instance.order - 1]
            topics_list.remove(topic)
            topics_list.insert((request_order - 1) if (request_order > 0) else 0, topic)

            # Order of each topic is its position in the array + 1 (order can't be zero)
            for index, topic in enumerate(topics_list):
                topic.order = index + 1
                topic.save()
        
        serializer = self.get_serializer(instance, data=request_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], url_path='reorder')
    def reorder_all_topics(self, request, pk=None, **kwargs):
        """
        Updates the order of all assessment topics.
        """
        # reauest_data = {
        #   'topics': [array with topics ids, where its index in the array is your new order (+1)], 
        #   'assessment_id': <assessment_id>
        # }
        request_data = request.data.copy()
        topics = AssessmentTopic.objects.filter(assessment=request_data['assessment_id'])

        try:
            for topic in topics:
                for index, element in enumerate(request_data['topics']):
                    if (topic.id == element) and (topic.order != index + 1):
                        topic.order = index + 1
                        topic.save()
                        break
        except:
            return Response('An error occurred while trying to update the order of assessments topics', status=500)
                
        return Response('Review topics successfully reordered.', status=200)

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

        topic_pk = self.kwargs['topic_pk']
        assessment_pk = self.kwargs['assessment_pk']

        return Question.objects.filter(
            assessment_topic=topic_pk,
            assessment_topic__assessment=assessment_pk
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

class AssessmentTopicAccessesViewSets(ModelViewSet):
    """
    Assessment topic accesses viewset.
    """

    serializer_class = AssessmentTopicAccessSerializer
    permission_classes = [IsAuthenticated, IsSupervisor]

    def get_queryset(self):
        """
        Queryset to get assessment topic accesses.
        """
        assessment_pk = self.kwargs['assessment_pk']
        user = self.request.user

        return AssessmentTopicAccess.objects.filter(
            student__created_by=user, topic__assessment__id=assessment_pk)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request, *args, **kwargs):
        """
        Assign assessment topics to students.
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
                    AssessmentTopic.objects.get(
                        Q(id=access.get('topic')),
                        Q(assessment__id=assessment_pk),
                        Q(assessment__created_by=user) | Q(assessment__private=False))
                except:
                    return Response('Cannot create access for unauthorized topics \
                        or topics in another assessment', status=400)

                formatted_data.append({
                    'student': student,
                    'topic': access.get('topic'),
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
