from django.urls import include, path
from django.conf.urls.static import static
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()

router.register(r'topics', views.TopicsViewSet, basename='topics')
# generates:
# /assessments/topics/

router.register(r'learning-objectives', views.LearningObjectivesViewSet, basename='learning-objectives')
# generates:
# /assessments/learning-objectives/
# /assessments/learning-objectives/{learning_objective_pk}/

router.register(r'number-ranges', views.NumberRangesViewSet, basename='number-ranges')
# generates:
# /assessments/number-ranges/
# /assessments/number-ranges/{number-ranges_pk}/

router.register(r'questions', views.QuestionsViewSet, basename='all-questions-type')
# generates:
# /assessments/questions/all/

router.register(r'', views.AssessmentsViewSet, basename='assessments')
# generates:
# /assessments/
# /assessments/{assessment_pk}/

""" router.register(r'attachments', views.AttachmentsViewSet, basename='attachments') """
# We would like a single route for attachments but this doesn't work because Django thinks that
#  in the route "assessments/attachments/", "attachments" is the primary key of an assessment...

assessments_router = routers.NestedSimpleRouter(
    router, r'', lookup='assessment')
assessments_router.register(
    r'question-sets', views.QuestionSetsViewSet, basename='assessment-question-sets')
assessments_router.register(
    r'accesses', views.QuestionSetAccessesViewSets, basename='assessment-accesses')
assessments_router.register(
    r'attachments', views.GeneralAttachmentsViewSet, basename='assessment-attachments')
# generates:
# /assessments/{assessment_pk}/question-sets/
# /assessments/{assessment_pk}/question-sets/reorder/
# /assessments/{assessment_pk}/question-sets/{question_set_pk}/
# /assessments/{assessment_pk}/accesses/
# /assessments/{assessment_pk}/accesses/{question_set_access_pk}/
# /assessments/{assessment_pk}/attachments/
# /assessments/{assessment_pk}/attachments/{attachment_pk}

# TODO Shouldn't be that way
# /assessments/{assessment_pk}/attachments/
# /assessments/{assessment_pk}/attachments/{attachment_pk}

question_sets_router = routers.NestedSimpleRouter(
    assessments_router, r'question-sets', lookup='question_set')
question_sets_router.register(r'questions', views.QuestionsViewSet,
                       basename='question-sets-questions')
# generates:
# /assessments/{assessment_pk}/question-sets/{question_set_pk}/questions/
# /assessments/{assessment_pk}/question-sets/{question_set_pk}/questions/reorder/
# /assessments/{assessment_pk}/question-sets/{question_set_pk}/questions/{question_pk}/

questions_router = routers.NestedSimpleRouter(
    question_sets_router, r'questions', lookup='question')
questions_router.register(
    r'attachments', views.AttachmentsViewSet, basename='question-attachments')
questions_router.register(
    r'draggable', views.DraggableOptionsViewSet, basename='draggable-options')
# generates:
# /assessments/{assessment_pk}/question-sets/{question_set_pk}/questions/{question_pk}/attachments/
# /assessments/{assessment_pk}/question-sets/{question_set_pk}/questions/{question_pk}/attachments/{attachment_pk}/
# /assessments/{assessment_pk}/question-sets/{question_set_pk}/questions/{question_pk}/draggable/
# /assessments/{assessment_pk}/question-sets/{question_set_pk}/questions/{question_pk}/draggable/{draggable_option_pk}

urlpatterns = [
    path('', include(router.urls)),
    path('', include(assessments_router.urls)),
    path('', include(question_sets_router.urls)),
    path('', include(questions_router.urls)),
]