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
# /assessments/{assessment_pk}/topics/{topic_pk}/

topics_router = routers.NestedSimpleRouter(assessments_router, r'topics', lookup='topic')
topics_router.register(r'questions', views.QuestionsViewSet, basename='questions-for-topic')
## generates:
# /assessments/{assessment_pk}/topics/{topic_pk}/questions/
# /assessments/{assessment_pk}/topics/{topic_pk}/questions/{question_pk}/

questions_router = routers.NestedSimpleRouter(topics_router, r'questions', lookup='question')
questions_router.register(r'attachments', views.AttachmentsViewSet, basename='attachments')
## generates:
# /assessments/{assessment_pk}/topics/{topic_pk}/questions/{question_pk}/attachments/
# /assessments/{assessment_pk}/topics/{topic_pk}/questions/{question_pk}/attachments/{attachment_pk}/

urlpatterns = [
    path('', include(router.urls)),
    path('', include(assessments_router.urls)),
    path('', include(topics_router.urls)),
    path('', include(questions_router.urls)),
]
