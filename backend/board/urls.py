# board/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('posts/',                          views.PostListCreateView.as_view()),
    path('posts/<int:pk>/',                 views.PostDetailView.as_view()),
    path('posts/<int:post_id>/comments/',   views.CommentListCreateView.as_view()),
    path('comments/<int:pk>/',              views.CommentDetailView.as_view()),
]