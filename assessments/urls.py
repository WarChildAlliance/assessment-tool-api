from django.urls import include, path, re_path

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

topics_per_assessment = views.AssessmentsViewSet.as_view({
    'get': 'topics_per_assessment',
})

attachments_list_for_question = views.AttachmentsViewSet.as_view({
    'get': 'list_for_question',
})

attachement_detail = views.AttachmentsViewSet.as_view({
    'get': 'retrieve',
})

questions_list_for_assessment_topic = views.AssessmentsViewSet.as_view({
    'get': 'questions_list_for_assessment_topic'
})

question_detail_for_assessment_topic = views.QuestionsViewSet.as_view({
    'get': 'retrieve',
})

urlpatterns = [
    path('', assessments_list, name='assessments-list'),
    path('<int:pk>/', assessments_detail, name='assessments-detail'),
    path('questions/', questions_list, name='questions-list'),
    re_path(r'^(?P<assessment_id>.+)/topics/$', topics_per_assessment, name="topics_per_assessment"),
    re_path(r'^(?P<assessment_id>.+)/topics/(?P<topic_id>.+)/questions/$', questions_list_for_assessment_topic, name='questions-list-for-assessment-topic'),
    re_path(r'^(?P<assessment_id>.+)/topics/(?P<topic_id>.+)/questions/(?P<question_id>.+)/$', question_detail_for_assessment_topic, name='question-detail'),
    path('attachments_for_question/<int:pk>/',
         attachments_list_for_question, name='attachments-list-for-question'),
    path('attachments/<int:pk>/', attachement_detail, name='attachments-detail'),
]
