from rest_framework import serializers
from .models import Profile, TopicCompetency

from django.db.models import Sum

class ProfileSerializer(serializers.ModelSerializer):
    """
    Profile serializer.
    """

    total_competency = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('id', 'student', 'effort', 'total_competency')

    def get_total_competency(self, instance):
        
        return TopicCompetency.objects.filter(profile=instance).aggregate(Sum('competency'))['competency__sum']


class TopicCompetencySerializer(serializers.ModelSerializer):

    class Meta:
        model = TopicCompetency
        fields = '__all__'