from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet

router = DefaultRouter()

urlpatterns = [
    path('chat/', ChatViewSet.as_view()),
]