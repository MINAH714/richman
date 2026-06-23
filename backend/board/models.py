# board/models.py
from django.db import models
from django.conf import settings


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('free',   '자유'),
        ('review', '금융상품 리뷰'),
        ('flex',   '자랑/인증'),
        ('qna',    '질문'),
    ]

    author      = models.ForeignKey(
                      settings.AUTH_USER_MODEL,
                      on_delete=models.CASCADE,
                      related_name='posts',
                  )
    category    = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='free')
    title       = models.CharField(max_length=200)
    content     = models.TextField()
    view_count  = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.get_category_display()}] {self.title}'


class Comment(models.Model):
    post        = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author      = models.ForeignKey(
                      settings.AUTH_USER_MODEL,
                      on_delete=models.CASCADE,
                      related_name='comments',
                  )
    content     = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} - {self.content[:20]}'