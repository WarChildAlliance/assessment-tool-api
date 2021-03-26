from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer.
    """

    password = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email',
                  'password', 'last_login', 'role', 'language', 'country', 'created_by']
        extra_kwargs = {'created_by': {'write_only': True}}

    def validate(self, data):
        """
        Check that supervisors have a password, that student usernames cannot be changed
        or have a set password.
        """
        if self.instance and self.instance.is_student() and 'username' in data:
            raise serializers.ValidationError('Student code cannot be changed.')

        if self.instance and self.instance.is_student() and 'password' in data:
            raise serializers.ValidationError('Student cannot have a password.')

        if (not self.instance and data['role'] == 'SUPERVISOR' and
                (data['password'] is None or data['password'] == '')):
            raise serializers.ValidationError('Supervisor must have a password.')
        
        if (not self.instance and data['role'] == 'STUDENT' and 
                (not 'country' in data or not 'language' in data)):
            raise serializers.ValidationError('Student must have a language and a country')

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
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.language = validated_data.get('language', instance.language)
        instance.country = validated_data.get('country', instance.country)
        instance.role = validated_data.get('role', instance.role)

        if instance.is_supervisor() and 'password' in validated_data:
            instance.set_password(validated_data.get('password'))

        instance.save()
        return instance
