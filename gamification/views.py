from rest_framework.response import Response
from rest_framework.decorators import action

from django.shortcuts import render
from admin.lib.viewsets import ModelViewSet
from .serializers import ProfileSerializer, TopicCompetencySerializer

from .models import Profile, TopicCompetency

class ProfileViewSet(ModelViewSet):

    serializer_class=ProfileSerializer
    
    def list(self, request):
        return Response('Cannot list profiles', status=403)
    
    def retrieve(self, request, pk=None):
        return Response('Cannot retrieve profile', status=403)

    def create(self, request):
        return Response('Cannot create profile', status=403)

    def update(self, request, pk=None):
        return Response('Cannot update profile', status=403)

    def partial_update(self, request, pk=None):
        return Response('Cannot update profile', status=403)

    def destroy(self, request, pk=None):
        return Response('Cannot delete profile', status=403)

    @action(detail=False)
    def get_self(self, request):
        """
        Get logged-in user's profile information
        """
        user = self.request.user
        student_profile = Profile.objects.get(student=user)
        serializer = self.get_serializer(student_profile)
        return Response(serializer.data, status=200)
    

class TopicCompetencyViewSet(ModelViewSet):

    serializer_class=TopicCompetencySerializer
    filterset_fields = ['topic']

    def get_queryset(self):
        return TopicCompetency.objects.filter(profile__student=self.request.user)

    def retrieve(self, request, pk=None):
        topic_competencies = self.get_queryset().get(
            topic=pk
        )
        serializer = self.get_serializer(topic_competencies)
        return Response(serializer.data, status=200)

    def update(self, request, pk=None):
        return Response('Cannot update profile', status=403)

    def partial_update(self, request, pk=None):
        return Response('Cannot partially update profile', status=403)

    def destroy(self, request, pk=None):
        return Response('Cannot delete profile', status=403)