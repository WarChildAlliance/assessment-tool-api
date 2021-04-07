from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'', views.AssessmentsViewSet, basename='assessments')
## generates:
# /assessments/
# /assessments/{assessment_pk}/

assessments_router = routers.NestedSimpleRouter(router, r'', lookup='assessment')
assessments_router.register(r'topics', views.AssessmentTopicsViewSet, basename='assessment-topics')
## generates:
# /assessments/{assessment_pk}/topics/
# /assessments/{assessment_pk}/topics/{topic_pk}/ <-- We don't want this one

topics_router = routers.NestedSimpleRouter(assessments_router, r'topics', lookup='topic')
topics_router.register(r'questions', views.QuestionsViewSet, basename='questions-for-topic')
## generates:
# /assessments/{assessment_pk}/topics/{topic_pk}/questions/
# /assessments/{assessment_pk}/topics/{topic_pk}/questions/{question_pk}/

questions_router = routers.SimpleRouter()
questions_router.register(r'questions', views.QuestionsViewSet, basename='questions')

attachments_router = routers.NestedSimpleRouter(questions_router, r'questions', lookup='questions')
attachments_router.register(r'attachments', views.AttachmentsViewSet, basename='attachments')
## generates:
# /questions/{question_pk}/attachments/
# /questions/{question_pk}/attachments/{attachment_pk}/ <-- We don't want this one

# TODO Customize this route to return exactly what we want
# For now, it returns every questions for any user, which is dangerous !!
questions_list_all = views.QuestionsViewSet.as_view({'get': 'list_all'})

urlpatterns = [
    path('', include(router.urls)),
    path('', include(assessments_router.urls)),
    path('', include(topics_router.urls)),
    path('', include(attachments_router.urls)),
    path('questions/all/', questions_list_all, name='questions-list-all'),
]