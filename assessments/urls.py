from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(r'topics', views.AssessmentTopicsViewSet)
router.register(r'questions', views.QuestionsViewSet)
router.register(r'questions_inputs', views.QuestionsInputViewSet)
router.register(r'questions_selects', views.QuestionsSelectViewSet)
router.register(r'questions_sorts', views.QuestionsSortViewSet)
router.register(r'questions_number_lines', views.QuestionsNumberLineViewSet)
router.register(r'attachments', views.AttachmentsViewSet)
router.register(r'select_options', views.SelectOptionsViewSet)
router.register(r'sort_options', views.SortOptionsViewSet)
router.register(r'', views.AssessmentsViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
