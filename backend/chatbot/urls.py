# backend/chatbot/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("sessions/", views.ChatSessionListView.as_view()),
    path("sessions/<uuid:session_id>/messages/", views.ChatMessageView.as_view()),
]