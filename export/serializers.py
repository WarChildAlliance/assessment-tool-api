from answers.models import Answer
from rest_framework import serializers

class CompleteStudentAnswersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = '__all__'