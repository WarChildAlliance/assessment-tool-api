from django.urls import include, path
from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()

router.register(r'answers', views.CompleteStudentAnswersViewSet,
                basename='answers')
#url: /export/answers

router.register(r'(?P<supervisor_id>\d+)/answers',
                views.SupervisorStudentAnswerViewSet, basename='answer-supervisor')
#url: /export/<supervisor_id>/answers
#url: /export/<supervisor_id>/answers/<assessment_id>

urlpatterns = [
    path('', include(router.urls))
]
