from rest_framework import serializers

from admin.lib.serializers import NestedRelatedField

from .models import Language, Country, User
from assessments.models import Assessment
from answers.models import AnswerSession, AssessmentTopicAnswer


class LanguageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Language
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer.
    """

    password = serializers.CharField(
        required=False, allow_blank=True, write_only=True)
    language = NestedRelatedField(
        model=Language, serializer_class=LanguageSerializer)
    country = NestedRelatedField(
        model=Country, serializer_class=CountrySerializer)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email',
                  'password', 'last_login', 'role', 'language', 'country', 'created_by']
        extra_kwargs = {'created_by': {
            'default': serializers.CurrentUserDefault(),
            'write_only': True
        }}

    def validate(self, data):
        """
        Check that supervisors have a password, that student usernames cannot be changed
        or have a set password.
        """
        if self.instance and self.instance.is_student() and 'username' in data:
            raise serializers.ValidationError(
                'Student code cannot be changed.')

        if self.instance and self.instance.is_student() and 'password' in data:
            raise serializers.ValidationError(
                'Student cannot have a password.')

        if (not self.instance and data['role'] == 'SUPERVISOR' and
                (data['password'] is None or data['password'] == '')):
            raise serializers.ValidationError(
                'Supervisor must have a password.')

        if (not self.instance and data['role'] == 'STUDENT' and
                (not 'country' in data or not 'language' in data)):
            raise serializers.ValidationError(
                'Student must have a language and a country')

        return data

    def create(self, validated_data):
        """
        Create a new user.
        """
        if validated_data['role'] == User.UserRole.STUDENT:
            validated_data['password'] = None
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data, **kwargs):
        """
        Update a user.
        """
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.language = validated_data.get('language', instance.language)
        instance.country = validated_data.get('country', instance.country)
        instance.role = validated_data.get('role', instance.role)

        if instance.is_supervisor() and 'password' in validated_data:
            instance.set_password(validated_data.get('password'))

        instance.save()
        return instance


class UserTableSerializer(serializers.ModelSerializer):
    """
    Users table serializer.
    """

    # Student's full name
    full_name = serializers.SerializerMethodField()
    # Last session
    last_session = serializers.SerializerMethodField()
    # Number of topics completed by the student
    completed_topics_count = serializers.SerializerMethodField()
    # Number of assessments that the student is linked to
    assessments_count = serializers.SerializerMethodField()

    # Languages and countries formatted information
    language_name = serializers.SerializerMethodField()
    language_code = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    country_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'last_session', 'completed_topics_count',
                  'assessments_count', 'language_name', 'language_code', 'country_name', 'country_code')

    def get_full_name(self, instance):
        return (instance.first_name + ' ' + instance.last_name)

    def get_last_session(self, instance):

        last_session = AnswerSession.objects.filter(student=instance).last()
        if not last_session:
            return
        else:
            return last_session.start_date

    def get_completed_topics_count(self, instance):
        return len(AssessmentTopicAnswer.objects.filter(topic_access__student=instance, complete=True))

    def get_assessments_count(self, instance):
        return len(Assessment.objects.filter(assessmenttopic__assessmenttopicaccess__student=instance))

    def get_language_name(self, instance):
        return instance.language.name_en
        
    def get_language_code(self, instance):
        return instance.language.code

    def get_country_name(self, instance):
        return instance.country.name_en
    
    def get_country_code(self, instance):
        return instance.country.code