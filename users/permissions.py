from assessments.models import Assessment, AssessmentTopic, Question
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
        Returns whether the user has access to the requested object
        """

        if isinstance(obj, User):
            if request.user and request.user.is_student():
                return request.user.id == obj.id
            if request.user and request.user.is_supervisor():
                # TODO: Update to check student was created by supervisor
                return request.user.id == obj.id or obj.is_student()

        if isinstance(obj, Assessment):
            if request.user and request.user.is_student():
                return Assessment.objects.filter(
                    assessmenttopic__assessmenttopicaccess__student=request.user,
                    id=obj.id
                ).exists()
            if request.user and request.user.is_supervisor():
                if request.method in permissions.SAFE_METHODS:
                    return (not obj.private) or obj.created_by == request.user
                else:
                    return obj.created_by == request.user

        if isinstance(obj, AssessmentTopic):
            if request.user and request.user.is_student():
                return AssessmentTopic.objects.filter(
                    assessmenttopicaccess__student=request.user,
                    id=obj.id
                ).exists()
            if request.user and request.user.is_supervisor():
                if request.method in permissions.SAFE_METHODS:
                    return not obj.assessment.private or obj.assessment.created_by == request.user
                else:
                    return obj.assessment.created_by == request.user

        if isinstance(obj, Question):
            if request.user and request.user.is_student():
                return Question.objects.filter(
                    assessment_topic__assessmenttopicaccess__student=request.user,
                    id=obj.id
                ).exists()
            if request.user and request.user.is_supervisor():
                if request.method in permissions.SAFE_METHODS:
                    return (not obj.assessment_topic.assessment.private or
                            obj.assessment_topic.assessment.created_by == request.user)
                else:
                    return obj.assessment_topic.assessment.created_by == request.user

        return True
