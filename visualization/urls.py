from django.urls import include, path
from rest_framework_nested import routers

from . import views

# Create a router and register our viewsets with it.
router = routers.SimpleRouter()

router.register(r'assessments', views.AssessmentTableViewSet,
                basename='assessments-visualization')
# generates
# /visualization/assessments/

assessments_router = routers.NestedSimpleRouter(
    router, r'assessments', lookup='assessment')
assessments_router.register(
    r'topics', views.AssessmentTopicsTableViewset, basename='topic-visualization')
# generates :
# /visualization/assessments/{assessment_pk}/topics/


questions_router = routers.NestedSimpleRouter(
    assessments_router, r'topics', lookup='topic')
questions_router.register(
    r'questions', views.QuestionsTableViewset, basename='question-visualization')
# generates :
# /visualization/assessments/{assessment_pk}/topics/{topic_pk}/questions/


router.register(r'students', views.UserTableViewSet,
                basename='students-visualization')
# generates
# /visualization/students/

router.register(r'students_assessments/(?P<student_pk>\d+)', views.UserAssessmentTreeViewset, 
                basename='student-assessments-visualization')

router.register(r'student_answers/(?P<student_pk>\d+)/sessions',
                views.AnswerSessionsTableViewSet, basename="sessions-visualization")
# generates
# /visualization/student_answers/{student_pk}/sessions/

router.register(r'student_answers/(?P<student_pk>\d+)/assessments',
                views.AssessmentAnswersTableViewSet, basename="assessment-visualization")
# generates
# /visualization/student_answers/{student_pk}/assessments/

answers_router = routers.NestedSimpleRouter(
    router, r'student_answers/(?P<student_pk>\d+)/assessments', lookup='assessment')
answers_router.register(
    r'topics', views.TopicAnswersTableViewSet, basename='topic-visualization')
# generates
# /visualization/student_answers/{student_pk}/assessments/{assessment_pk}/topics/

questions_answers_router = routers.NestedSimpleRouter(
    answers_router, r'topics', lookup='topic')
questions_answers_router.register(
    r'questions', views.QuestionAnswersTableViewSet, basename='question-visualization')
# generates
# /visualization/student_answers/{student_pk}/assessments/{assessment_pk}/topics/{topic_pk}/questions/

urlpatterns = [
    path('', include(router.urls)),
    path('', include(assessments_router.urls)),
    path('', include(questions_router.urls)),
    path('', include(answers_router.urls)),
    path('', include(questions_answers_router.urls)),
]
