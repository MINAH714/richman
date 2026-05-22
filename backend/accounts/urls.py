from django.urls import path
from .views import TestView
from .views import SignupView
from .views import SignupView, MeView


urlpatterns = [
    path('test/', TestView.as_view()),
    path('signup/', SignupView.as_view()),
    path('me/', MeView.as_view()),
]