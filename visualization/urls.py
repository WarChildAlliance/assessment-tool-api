from django.urls import include, path
from rest_framework_nested import routers


from . import views

# Create a router and register our viewsets with it.

router = routers.SimpleRouter()


router.register(r'assessments', views.AssessmentTableViewSet, basename='assessments')

assessments_router = routers.NestedSimpleRouter(router, r'assessments', lookup='assessment')
assessments_router.register(r'topics', views.AssessmentTopicsTableViewset, basename='assessment-topics')


""" 
router.register(r'assessment_answers', views.AssessmentTableViewSet, basename='answers')

answers_router = routers.NestedSimpleRouter(router, r'assessment_answers', lookup='answers')
answers_router.register(r'topics', views.AssessmentTopicsTableViewset, basename='answers-topics')

 """

router.register(r'users', views.UserTableViewSet, basename='users')

router.register(r'sessions', views.AnswerSessionsTableViewSet, basename='sessions')

router.register(r'student_answers/(?P<student_pk>\d+)/assessments', views.AssessmentAnswersTableViewSet, basename="assessment")

answers_router = routers.NestedSimpleRouter(router, r'student_answers/(?P<student_pk>\d+)/assessments', lookup='assessment')

#localhost:8002/visualization/student_answers/<student_pk>/assessments/

answers_router.register(r'topics', views.TopicAnswersTableViewSet, basename='topic')

questions_router = routers.NestedSimpleRouter(answers_router, r'topics', lookup='topic')

questions_router.register(r'questions', views.AssessmentTopicsTableViewset, basename='question')



urlpatterns = [
    path('', include(router.urls)),
    path('', include(assessments_router.urls)),
    path('', include(answers_router.urls)),
    path('', include(questions_router.urls)),
]
