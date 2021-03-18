from django.contrib.auth.models import Group
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer.
    """

    group = serializers.CharField(source='groups.name')
    password = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email',
                  'password', 'last_login', 'group', 'language', 'country']

    def validate_group(self, value):
        """
        Validate group field.
        """
        if value != 'Student' and value != 'Supervisor':
            raise serializers.ValidationError('Group must be Student or Supervisor.')
        return value

    def validate(self, data):
        """
        Check that supervisors have a password.
        """
        if ('groups' in data and data['groups']['name'] == 'Supervisor' and
                (data['password'] is None or data['password'] == '')):
            raise serializers.ValidationError('Supervisor must have a password.')
        return data

    def create(self, validated_data):
        """
        Create a new user.
        """
        group_name = validated_data['groups']['name']
        validated_data['groups'] = Group.objects.get(name=group_name)
        if group_name == 'Student':
            validated_data['password'] = None
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data, **kwargs):
        """
        Update a user.
        """
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.language = validated_data.get('language', instance.language)
        instance.country = validated_data.get('country', instance.country)

        if ('groups' in validated_data and
                validated_data['groups']['name'] != instance.groups__name):
            instance.groups = Group.objects.get(name=validated_data['groups']['name'])

        if instance.is_supervisor() and 'password' in validated_data:
            instance.set_password(validated_data.get('password'))

        instance.save()
        return instance
