from rest_framework.response import Response
from rest_framework.decorators import action

from django.shortcuts import render
from admin.lib.viewsets import ModelViewSet
from .serializers import AvatarSerializer, ProfileSerializer, TopicCompetencySerializer

from .models import Avatar, Profile, TopicCompetency


class ProfileViewSet(ModelViewSet):

    serializer_class = ProfileSerializer

    def list(self, request):
        return Response('Cannot list profiles', status=403)

    def retrieve(self, request, pk=None):
        return Response('Cannot retrieve profile', status=403)

    def create(self, request):
        return Response('Cannot create profile', status=403)


    def put(self, request, **kwargs):
        user = self.request.user
        student_profile = Profile.objects.get(student=user)
        profile = request.data.get("profile")
        print("profile", profile)
        request_data = request.data.copy()
        serializer = self.get_serializer(student_profile, data = profile)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        print("self", self)
        return Response(serializer.data)

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
        try:
            student_profile = Profile.objects.get(student=user)
            serializer = self.get_serializer(student_profile)
            return Response(serializer.data, status=200)
        except:
            return Response(None, status=200)



class TopicCompetencyViewSet(ModelViewSet):

    serializer_class = TopicCompetencySerializer
    filterset_fields = ['topic']

    def get_queryset(self):
        return TopicCompetency.objects.filter(profile__student=self.request.user)

    def retrieve(self, request, pk=None):
        topic_competencies = self.get_queryset().get(
            topic=pk
        )
        serializer = self.get_serializer(topic_competencies)
        return Response(serializer.data, status=200)

    def destroy(self, request, pk=None):
        return Response('Cannot delete topic competency', status=403)


class AvatarViewSet(ModelViewSet):

    serializer_class = AvatarSerializer

    def get_queryset(self):
        return Avatar.objects.all()

    def list(self, request, *args, **kwargs):

        serializer = AvatarSerializer(
            self.get_queryset(), many=True,
            context={
                'student_pk': int(self.request.user.id)
            }
        )

        return Response(serializer.data)

    def update(self, request, **kwargs):
        return Response('Cannot update avatar', status=403)

    def partial_update(self, request, pk=None):
        return Response('Cannot partially update avatar', status=403)

    def destroy(self, request, pk=None):
        return Response('Cannot delete avatar', status=403)

    @action(detail=False, methods=['post'])
    def select(self, request, **kwargs):
        """
        Select an avatar
        """

        student_profile = Profile.objects.get(student=self.request.user)
        previous_avatar = student_profile.current_avatar

        new_avatar = Avatar.objects.get(id=request.data.get("avatar_id"))

        if not (student_profile.unlocked_avatars.filter(id=new_avatar.id).exists()):
            return Response('Avatar has to be unlocked first', status=403)

        student_profile.current_avatar = new_avatar
        student_profile.save()

        previous_avatar.selected = False
        previous_avatar.save

        new_avatar.selected = True
        new_avatar.save()

        serializer = AvatarSerializer(
            new_avatar,
            many=False,
            context={
                'student_pk': int(self.request.user.id)
            })

        return Response(serializer.data, status=200)

    @action(detail=False, methods=['post'])
    def unlock(self, request, **kwargs):
        """
        Unlock an avatar
        """

        student_profile = Profile.objects.get(student=self.request.user)

        avatar_id = request.data.get("avatar_id")

        avatar_to_unlock = Avatar.objects.get(id=avatar_id)

        if (student_profile.unlocked_avatars.filter(id=avatar_to_unlock.id).exists()):
            return Response('Avatar is already unlocked', status=403)

        if (student_profile.effort < avatar_to_unlock.effort_cost):
            return Response('Need more effort points to unlock the avatar', status=403)

        student_profile.unlocked_avatars.add(avatar_to_unlock)
        student_profile.effort = student_profile.effort - avatar_to_unlock.effort_cost
        student_profile.save()

        serializer = AvatarSerializer(
            avatar_to_unlock,
            many=False,
            context={
                'student_pk': int(self.request.user.id)
            })

        return Response(serializer.data, status=200)
