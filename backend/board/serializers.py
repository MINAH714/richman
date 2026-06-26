# board/serializers.py
from rest_framework import serializers
from .models import Post, Comment


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.nickname', read_only=True)
    is_owner    = serializers.SerializerMethodField()

    class Meta:
        model  = Comment
        fields = [
            'id', 'post', 'author', 'author_name', 'content',
            'created_at', 'updated_at', 'is_owner',
        ]
        read_only_fields = ['author', 'post']

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.author_id == request.user.id)


class PostListSerializer(serializers.ModelSerializer):
    """목록용 - 작성자, 제목, 작성일, 카테고리, 댓글 수만"""
    author_name      = serializers.CharField(source='author.nickname', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    comment_count     = serializers.SerializerMethodField()

    class Meta:
        model  = Post
        fields = [
            'id', 'author_name', 'category', 'category_display',
            'title', 'created_at', 'view_count', 'comment_count',
        ]

    def get_comment_count(self, obj):
        return obj.comments.count()


class PostDetailSerializer(serializers.ModelSerializer):
    """상세 페이지용 - 본문 + 댓글 리스트 포함"""
    author_name      = serializers.CharField(source='author.nickname', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    comments          = CommentSerializer(many=True, read_only=True)
    is_owner           = serializers.SerializerMethodField()

    class Meta:
        model  = Post
        fields = [
            'id', 'author', 'author_name', 'category', 'category_display',
            'title', 'content', 'view_count', 'created_at', 'updated_at',
            'comments', 'is_owner',
        ]
        read_only_fields = ['author']

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.author_id == request.user.id)


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """작성/수정용 - 분류 드롭다운 선택값(category) 포함"""
    class Meta:
        model  = Post
        fields = ['id', 'category', 'title', 'content']