from django.urls import include, path

from . import views

# WORKS
assessments_list = views.AssessmentsViewSet.as_view({
    'get': 'list',
})

# WORKS
assessments_detail = views.AssessmentsViewSet.as_view({
    'get': 'retrieve',
})

# WORKS
questions_list = views.QuestionsViewSet.as_view({
    'get': 'list',
})

# WORKS
attachments_list_for_question = views.AttachmentsViewSet.as_view({
    'get': 'list_for_question',
})

# WORKS
attachement_detail = views.AttachmentsViewSet.as_view({
    'get': 'retrieve',
})

# All the questions for one topic
questions_list_for_assessment_topic = views.QuestionsViewSet.as_view({
    'get': 'questions_list_for_assessment_topic'
})

# Get one question
question_detail_for_assessment_topic = views.QuestionsViewSet.as_view({
    'get': 'question_detail_for_assessment_topic'
})

urlpatterns = [
    path('', assessments_list, name='assessments-list'),
    path('<int:pk>/', assessments_detail, name='assessments-detail'),
    path('questions/', questions_list, name='questions-list'),
    path('<int:assessment_pk>/topic/<int:topic_pk>/questions/', questions_list_for_assessment_topic, name='questions-list-for-assessment-topic'),
    path('<int:assessment_pk>/topic/<int:topic_pk>/questions/<int:question_pk>/', question_detail_for_assessment_topic, name='question-detail'),
    path('attachments_for_question/<int:pk>/',
         attachments_list_for_question, name='attachments-list-for-question'),
    path('attachments/<int:pk>/', attachement_detail, name='attachments-detail'),
]
