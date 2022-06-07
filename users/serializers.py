from datetime import date

from rest_framework import serializers

from admin.lib.serializers import NestedRelatedField

from .models import Language, Country, User, Group

class LanguageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Language
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    """
    Group serializer.
    """

    students = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = '__all__'
    
    def get_students(self, instance):
        students = User.objects.filter(group=instance).values_list('id', flat=True)
        return students

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
    group = NestedRelatedField(
        model=Group, allow_null=True, serializer_class=GroupSerializer)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'group',
                  'password', 'last_login', 'role', 'language', 'country', 'created_by',
                  'is_active']
        extra_kwargs = {'created_by': {
            'default': serializers.CurrentUserDefault(),
            'write_only': True
        }}

    def validate(self, data):
        """
        Check that supervisors have a password, and that student usernames cannot
        be changed or have a set password.
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
            validated_data['active_status_updated_on'] = date.today()
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

        if instance.is_student():
            instance.group = validated_data.get('group', instance.group)
            is_active = validated_data.get('is_active', instance.is_active)
            if is_active != instance.is_active:
                instance.is_active = is_active
                instance.active_status_updated_on = date.today()

        if instance.is_supervisor() and 'password' in validated_data:
            instance.set_password(validated_data.get('password'))

        instance.save()
        return instance