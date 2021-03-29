from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'', views.AssessmentsViewSet)
router.register(r'topics', views.AssessmentTopicsViewSet)
router.register(r'questions', views.QuestionsViewSet)
router.register(r'question_inputs', views.QuestionsInputViewSet)
router.register(r'question_selects', views.QuestionsSelectViewSet)
router.register(r'question_sorts', views.QuestionsSortViewSet)
router.register(r'attachments', views.AttachmentsViewSet)
router.register(r'select_options', views.SelectOptionsViewSet)
router.register(r'sort_options', views.SortOptionsViewSet)
# Not sure about what we should remove in all that

assessments_list = views.AssessmentsViewSet.as_view({
    'get': 'list',
})
assessments_detail = views.AssessmentsViewSet.as_view({
    'get': 'retrieve',
})

questions_list = views.QuestionsViewSet.as_view({
    'get': 'list',
})

attachments_list_for_question = views.AttachmentsViewSet.as_view({
    'get': 'list_for_question',
})
attachement_detail = views.AttachmentsViewSet.as_view({
    'get': 'retrieve',
})


urlpatterns = [
    #path('', include(router.urls)),
    path('', assessments_list, name='assessments-list'),
    path('<int:pk>/', assessments_detail, name='assessments-detail'),
    path('questions/', questions_list, name='questions-list'),
    path('attachments_for_question/<int:pk>/',
         attachments_list_for_question, name='attachments-list-for-question'),
    path('attachments/<int:pk>/', attachement_detail, name='attachments-detail'),
]
