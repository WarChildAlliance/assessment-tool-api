from django.urls import include, path
from rest_framework_nested import routers

from . import views

# Create a router and register our viewsets with it.
router = routers.SimpleRouter()

router.register(r'assessments', views.AssessmentTableViewSet,
                basename='assessments-visualization')
# generates
# /visualization/assessments/

router.register(r'question-sets', views.QuestionSetsTableViewset,
                basename='all-question-sets-visualization')
# generates
# /visualization/question-sets/all/

router.register(r'questions', views.QuestionsTableViewset,
                basename='all-questions-visualization')
# generates
# /visualization/questions/all/

assessments_router = routers.NestedSimpleRouter(
    router, r'assessments', lookup='assessment')
assessments_router.register(
    r'question-sets', views.QuestionSetsTableViewset, basename='question-sets-visualization')
# generates :
# /visualization/assessments/{assessment_pk}/question-sets/

questions_router = routers.NestedSimpleRouter(
    assessments_router, r'question-sets', lookup='question_set')
questions_router.register(
    r'questions', views.QuestionsTableViewset, basename='question-visualization')
# generates :
# /visualization/assessments/{assessment_pk}/question-sets/{question_set_pk}/questions/


router.register(r'students', views.UserTableViewSet,
                basename='students-visualization')
# generates
# /visualization/students/

router.register(r'groups', views.GroupTableViewSet,
                basename='groups-visualization')
# generates
# /visualization/groups/

router.register(r'students_assessments/(?P<student_pk>\d+)', views.StudentLinkedAssessmentsViewSet, 
                basename='student-assessments-visualization')
# generates
# /visualization/student_answers/{student_pk}/

router.register(r'student_answers/(?P<student_pk>\d+)/assessments',
                views.AssessmentAnswersTableViewSet, basename="assessment-visualization")
# generates
# /visualization/student_answers/{student_pk}/assessments/

answers_router = routers.NestedSimpleRouter(
    router, r'student_answers/(?P<student_pk>\d+)/assessments', lookup='assessment')
answers_router.register(
    r'question-sets', views.QuestionSetAnswersTableViewSet, basename='question-set-visualization')
# generates
# /visualization/student_answers/{student_pk}/assessments/{assessment_pk}/question-sets/

questions_answers_router = routers.NestedSimpleRouter(
    answers_router, r'question-sets', lookup='question_set')
questions_answers_router.register(
    r'questions', views.QuestionAnswersTableViewSet, basename='question-visualization')
# generates
# /visualization/student_answers/{student_pk}/assessments/{assessment_pk}/question-sets/{question_set_pk}/questions/

router.register(r'charts/assessments', views.AssessmentListForDashboard, basename="dashboard-assessment")

dashboard_assessments_router = routers.NestedSimpleRouter(
    router, r'charts/assessments', lookup='assessment')
dashboard_assessments_router.register(
    r'question-sets', views.QuestionSetListForDashboard, basename='dashboard-question-set')

router.register(r'charts/score_by_question_set/(?P<assessment_pk>\d+)', views.ScoreByQuestionSetViewSet, basename="score-by-question-set")
router.register(r'charts/score_by_question_set/(?P<assessment_pk>\d+)/group/(?P<group_pk>\d+)', views.GroupScoreByQuestionSetViewSet, basename="group-score-by-question-set")

router.register(r'charts/assessments/(?P<assessment_pk>\d+)/question-sets/(?P<question_set_pk>\d+)/questions', views.QuestionOverviewViewSet, basename="question-overview")
router.register(r'charts/question-set/(?P<question_set_pk>\d+)/students', views.StudentsByQuestionSetAccessViewSet, basename="students-by-question-sets")
router.register(r'charts/question-set/(?P<question_set_pk>\d+)/student/(?P<question_set_answer_pk>\d+)/answers', views.StudentAnswersViewSet, basename="students_answers")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(assessments_router.urls)),
    path('', include(questions_router.urls)),
    path('', include(answers_router.urls)),
    path('', include(questions_answers_router.urls)),
    path('', include(dashboard_assessments_router.urls))
]
