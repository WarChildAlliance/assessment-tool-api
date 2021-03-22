import random
import string

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.models import User
from users.permissions import HasAccess, IsSupervisor
from users.serializers import UserSerializer


def student_key_generator():
    """
    Generate a random 6-digit string of numbers.
    """
    key = ''.join(random.choice(string.digits) for x in range(6))
    if User.objects.filter(username=key).exists():
        key = student_key_generator()
    return key


class CustomAuthToken(ObtainAuthToken):
    """
    Custom auth token management.
    """

    def post(self, request, *arg, **kwargs):
        """
        Return user auth token, checking data is valid depending on group
        Parameters: username, password (optional)
        """
        username = request.data.get('username')

        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response('Unknown user', status=400)

        if user.role and user.role == User.UserRole.STUDENT:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'user_first_name': user.first_name,
                'user_last_name': user.last_name,
            })

        serializer = self.serializer_class(data=request.data,
                                        context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'user_first_name': user.first_name,
            'user_last_name': user.last_name,
            'user_email': user.email,
        })


class UsersViewSet(ModelViewSet):
    """
    List all users.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_fields = ['role', 'country', 'language']
    search_fields = ['first_name', 'last_name', 'username', 'role']

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        if self.action == 'retrieve' or self.action == 'update':
            permission_classes.append(HasAccess)
        elif self.action == 'destroy':
            permission_classes.append(HasAccess)
            permission_classes.append(IsSupervisor)
        else:
            permission_classes.append(IsSupervisor)
        return [permission() for permission in permission_classes]

    def create(self, request):
        """
        Create a new user.
        """
        request_data = request.data.copy()

        if request_data.get('role') == User.UserRole.STUDENT:
            request_data['username'] = student_key_generator()

        if request_data.get('role') == User.UserRole.SUPERVISOR:
            if not request_data.get('email'):
                return Response('No email specified', status=400)
            request_data['username'] = request_data.get('email')

        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, pk=None, **kwargs):
        """
        Update a user (acts as partial_update).
        """
        kwargs['partial'] = True
        return super().update(request, pk, **kwargs)

    @action(detail=True)
    def update_student_code(self, request, pk=None):
        """
        Update student code.
        """
        user = self.get_object()
        if not user.is_student():
            return Response('Cannot generate code for non student user.', status=400)
        user.username = student_key_generator()
        user.save()
        return Response(user.username, status=200)
