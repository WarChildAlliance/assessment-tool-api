from django.urls import include, path
from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()

router.register(r'answers', views.CompleteStudentAnswersViewSet,
                basename='answers')



urlpatterns = [
    path('', include(router.urls))
]
