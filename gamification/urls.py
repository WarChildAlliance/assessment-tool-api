from django.urls import include, path
from rest_framework_nested import routers

from . import views

# Create a router and register our viewsets with it.
router = routers.SimpleRouter()

router.register(r'profiles', views.ProfileViewSet,
                basename='profiles')
# generates :
# /gamification/profiles/get_self/

router.register(r'avatars', views.AvatarViewSet,
                basename='avatars')
# generates :
# /gamification/avatars/
# /gamification/avatars/<avatar_pk>/

router.register(r'topic-competencies', views.TopicCompetencyViewSet,
                basename='topic-competencies')
# generates :
# /gamification/topic_competencies/
# /gamification/topic_competencies/<topic_pk>/

urlpatterns = [
    path('', include(router.urls)),
]
