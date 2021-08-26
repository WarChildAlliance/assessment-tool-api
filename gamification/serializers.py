from admin.lib.serializers import NestedRelatedField
from rest_framework import serializers
from .models import Avatar, Profile, TopicCompetency

from django.db.models import Sum


class TopicCompetencySerializer(serializers.ModelSerializer):

    class Meta:
        model = TopicCompetency
        fields = '__all__'

class AvatarSerializer(serializers.ModelSerializer):

    # Defines if the avatar has been unlocked by the student or not
    unlocked = serializers.SerializerMethodField()
    # Defines if the avatar is currently selected by the student or not
    selected = serializers.SerializerMethodField()

    class Meta:
        model = Avatar
        fields = ('id', 'image', 'effort_cost', 'unlocked', 'selected')

    def get_unlocked(self, instance):

        if not ('student_pk' in self.context):
            return None

        student_pk = self.context['student_pk']

        return instance.unlocked_on_profile.filter(student=student_pk).exists()

    def get_selected(self, instance):

        if not ('student_pk' in self.context):
            return None

        student_pk = self.context['student_pk']

        return instance.selected_on_profile.filter(student=student_pk).exists()



class ProfileSerializer(serializers.ModelSerializer):
    """
    Profile serializer.
    """

    # Total of all competency for all topics
    total_competency = serializers.SerializerMethodField()

    topics_competencies = NestedRelatedField(
        model=TopicCompetency, serializer_class=TopicCompetencySerializer, many=True, required=False, source='topiccompetency_set')

    current_avatar = NestedRelatedField(
        model=Avatar, serializer_class=AvatarSerializer, many=False, required=False)

    class Meta:
        model = Profile
        fields = ('id', 'student', 'effort', 'total_competency', 'current_avatar', 'unlocked_avatars', 'topics_competencies')

    def get_total_competency(self, instance):
        
        total_competency = TopicCompetency.objects.filter(profile=instance).aggregate(Sum('competency'))['competency__sum']

        if not (total_competency):
            total_competency = 0

        return total_competency