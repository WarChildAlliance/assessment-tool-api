from django.urls import include, path
from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()

router.register(r'answers', views.CompleteStudentAnswersViewSet,
                basename='answers-export')
#url: /export/answers

router.register(r'(?P<supervisor_id>\d+)/answers',
                views.SupervisorStudentAnswerViewSet, basename='answer-supervisor')
#url: /export/<supervisor_id>/answers
#url: /export/<supervisor_id>/answers/<assessment_id>

router.register(r'assessments', views.AssessmentReportViewSet, basename='assessments-export')
# url: /export/assessments/{assessment_pk}

topics_router = routers.NestedSimpleRouter(
    router, r'assessments', lookup='assessment')
topics_router.register(r'topics', views.AssessmentTopicReportViewSet, basename="topics")
# url: /export/assessments/{assessment_pk}/topics/{topic_pk}
#
questions_router = routers.NestedSimpleRouter(
    topics_router, r'topics', lookup='topic')
questions_router.register(r'questions', views.QuestionReportViewSet, basename="questions")
#url: /export/assessments/{assessment_pk}/topics/{topic_pk}/questions/{question_pk}

urlpatterns = [
    path('', include(router.urls)),
    path('', include(topics_router.urls)),
    path('', include(questions_router.urls))
]
