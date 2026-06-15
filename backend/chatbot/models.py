from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """chat_sessions 테이블"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        db_column='user_id',
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-started_at']

    def __str__(self):
        return f"Session {self.id} - {self.user}"


class ChatMessage(models.Model):
    """chat_messages 테이블"""
    ROLE_CHOICES = [
        ('user', 'user'),
        ('assistant', 'assistant'),
    ]
    INTENT_CHOICES = [
        ('crypto', 'crypto'),
        ('stock', 'stock'),
        ('consumption', 'consumption'),
        ('mixed', 'mixed'),
        ('price_alert', 'price_alert'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        db_column='session_id',
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    intent_type = models.CharField(
        max_length=20, choices=INTENT_CHOICES, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:30]}"