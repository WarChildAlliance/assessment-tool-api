from django.urls import include, path
from rest_framework_nested import routers

from . import views

# Create a router and register our viewsets with it.
router = routers.SimpleRouter()

router.register(r'profiles', views.ProfileViewSet,
                basename='profiles')
# generates :
# /gamification/profiles/get_self/

router.register(r'topic-competencies', views.TopicCompetencyViewSet,
                basename='topic-competencies')
# generates :
# /gamification/topic_competencies/get_self/
# /gamification/topic_competencies/<topic_pk>/

urlpatterns = [
    path('', include(router.urls)),
]
