# board/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import F
from .models import Post, Comment
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    CommentSerializer,
)
from .permissions import IsAuthorOrReadOnly


# ── 게시글 ──────────────────────────────────────────────

class PostListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/board/posts/             - 목록 (작성자, 제목, 작성일 표시)
         ?category=review             - 분류별 필터링
    POST /api/board/posts/             - 작성 (category 드롭다운 선택값 포함)
    """
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Post.objects.all()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/board/posts/<pk>/      - 상세 (댓글 리스트 포함, 조회수 +1)
    PUT    /api/board/posts/<pk>/      - 수정 (본인만)
    PATCH  /api/board/posts/<pk>/      - 부분 수정 (본인만)
    DELETE /api/board/posts/<pk>/      - 삭제 (본인만)
    """
    queryset = Post.objects.all()
    permission_classes = [IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Post.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# ── 댓글 ────────────────────────────────────────────────

class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/board/posts/<post_id>/comments/   - 해당 게시글 댓글 목록
    POST /api/board/posts/<post_id>/comments/   - 댓글 작성
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'])

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            post_id=self.kwargs['post_id'],
        )


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    PUT    /api/board/comments/<pk>/   - 댓글 수정 (본인만)
    PATCH  /api/board/comments/<pk>/   - 댓글 부분 수정 (본인만)
    DELETE /api/board/comments/<pk>/   - 댓글 삭제 (본인만)
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]