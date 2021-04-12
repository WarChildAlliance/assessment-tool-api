from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

# Create a router and register our viewsets with it.
router = SimpleRouter()
router.register(r'(?P<student_id>\d+)/sessions', views.AnswerSessionsViewSet,
    basename='answer-session')
# /answers/<student_id>/sessions/
# /answers/<student_id>/sessions/{session_pk}/
router.register(r'(?P<student_id>\d+)/topics', views.AssessmentTopicAnswersViewSet,
    basename='answer-topic')
# /answers/<student_id>/topics/
# /answers/<student_id>/topics/{topic_pk}/
router.register(r'(?P<student_id>\d+)', views.AnswersViewSet, basename='answers')
# /answers/<student_id>/
# /answers/<student_id>/{answer_pk}/

urlpatterns = [
    path('', include(router.urls)),
]
