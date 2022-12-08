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

question_sets_router = routers.NestedSimpleRouter(
    router, r'assessments', lookup='assessment')
question_sets_router.register(r'question-sets', views.QuestionSetReportViewSet, basename="question-sets")
# url: /export/assessments/{assessment_pk}/question-setss/{question_set_pk}
#
questions_router = routers.NestedSimpleRouter(
    question_sets_router, r'question-sets', lookup='question_set')
questions_router.register(r'questions', views.QuestionReportViewSet, basename="questions")
#url: /export/assessments/{assessment_pk}/question-sets/{question_set_pk}/questions/{question_pk}

urlpatterns = [
    path('', include(router.urls)),
    path('', include(question_sets_router.urls)),
    path('', include(questions_router.urls))
]
