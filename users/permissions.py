from rest_framework import permissions

from users.models import User


class IsSupervisor(permissions.BasePermission):
    """
    Permission to ensure the user is a supervisor
    """

    message = 'Only a supervisor can perform this action.'

    def has_permission(self, request, view):
        """
        Returns whether the user is a supervisor or not
        """
        if request.user and request.user.is_supervisor():
            return True
        return False


class IsStudent(permissions.BasePermission):
    """
    Permission to ensure the user is a student
    """

    message = 'Only a student can perform this action.'

    def has_permission(self, request, view):
        """
        Returns whether the user is a student or not
        """
        if request.user and request.user.is_student():
            return True
        return False


class HasAccess(permissions.BasePermission):
    """
    Permission to ensure the user is requesting its own data
    """

    message = 'The current user cannot perform this action'

    def has_object_permission(self, request, view, obj):
        """
        Returns whether the user is the user requested
        """
        if isinstance(obj, User):
            if request.user and request.user.is_student():
                return request.user.id == obj.id
            if request.user and request.user.is_supervisor():
                return request.user.id == obj.id or obj.is_student()
        return True
