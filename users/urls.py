from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'languages', views.LanguagesViewSet, basename='language')
router.register(r'countries', views.CountriesViewSet, basename='countries')
router.register(r'', views.UsersViewSet, basename='user')

urlpatterns = [
    path('token-auth/', views.CustomAuthToken.as_view()),
    path('', include(router.urls)),
]
