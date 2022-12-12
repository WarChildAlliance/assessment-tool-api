from answers.models import Answer
from assessments.models import Assessment, QuestionSet, Question
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

    def has_permission(self, request, view):
        """
        Returns whether the can access the sub-resourc
        """
        if view.basename == 'assessment-question-sets':
            assessment_pk = view.kwargs['assessment_pk']
            try:
                assessment = Assessment.objects.get(id=assessment_pk)
                return self.has_object_permission(request, view, assessment)
            except:
                return False

        if view.basename == 'question-sets-questions':
            question_set_pk = view.kwargs['question_set_pk']
            try:
                question_set = QuestionSet.objects.get(id=question_set_pk)
                return self.has_object_permission(request, view, question_set)
            except:
                return False

        return True

    def has_object_permission(self, request, view, obj):
        """
        Returns whether the user has access to the requested object
        """
        if isinstance(obj, User):
            if request.user and request.user.is_student():
                return request.user.id == obj.id
            if request.user and request.user.is_supervisor():
                return request.user.id == obj.id or (obj.is_student() and obj.created_by == request.user)

        if isinstance(obj, Assessment):
            if request.user and request.user.is_student():
                return Assessment.objects.filter(
                    questionset__questionsetaccess__student=request.user,
                    id=obj.id
                ).exists()
            if request.user and request.user.is_supervisor():
                if request.method in permissions.SAFE_METHODS:
                    return (not obj.private) or obj.created_by == request.user
                else:
                    return obj.created_by == request.user

        if isinstance(obj, QuestionSet):
            if request.user and request.user.is_student():
                return QuestionSet.objects.filter(
                    questionsetaccess__student=request.user,
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
                    question_set__questionsetaccess__student=request.user,
                    id=obj.id
                ).exists()
            if request.user and request.user.is_supervisor():
                if request.method in permissions.SAFE_METHODS:
                    return (not obj.question_set.assessment.private or
                            obj.question_set.assessment.created_by == request.user)
                else:
                    return obj.question_set.assessment.created_by == request.user

        if isinstance(obj, Answer):
            if request.user and request.user.is_student():
                return obj.question_set_answer.session.student == request.user
            if request.user and request.user.is_supervisor():
                return obj.question_set_answer.session.student.created_by == request.user

        return True
