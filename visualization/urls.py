from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'hello_world', views.HelloWorldViewSet, basename='hello-world')

urlpatterns = [
    path('', include(router.urls)),
]
