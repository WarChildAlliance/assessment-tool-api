from django.urls import include, path

from . import views


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
    path('', assessments_list, name='assessments-list'),
    path('<int:pk>/', assessments_detail, name='assessments-detail'),
    path('questions/', questions_list, name='questions-list'),
    path('attachments_for_question/<int:pk>/',
         attachments_list_for_question, name='attachments-list-for-question'),
    path('attachments/<int:pk>/', attachement_detail, name='attachments-detail'),
]
