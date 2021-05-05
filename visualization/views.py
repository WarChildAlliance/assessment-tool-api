from django.shortcuts import render

from admin.lib.viewsets import ModelViewSet

from rest_framework.response import Response


class HelloWorldViewSet(ModelViewSet):
    """
    Hello world viewset.
    """

    def hello_world(self):
        return Reponse('Hello')