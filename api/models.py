from django.db import models
from authentication.models import User
from django.utils import timezone

class ErrorLog(models.Model):
    LEVEL_CHOICES = (
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    )

    message = models.TextField()  # Short error message or summary
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='error_logs'
    )  # Nullable user reference
    timestamp = models.DateTimeField(default=timezone.now)  # Auto-set timestamp
    stack_trace = models.TextField(blank=True)  # Full stack trace, optional
    request_path = models.CharField(max_length=255, blank=True)  # URL path
    status_code = models.IntegerField(null=True, blank=True)  # HTTP status code
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='ERROR'
    )  # Log level
    method = models.CharField(max_length=10, blank=True)  # HTTP method (GET, POST, etc.)
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Client IP
    error_type = models.CharField(max_length=100, blank=True, null=True)  # Exception type (e.g., TypeError)


    class Meta:
        ordering = ['-timestamp']  # Latest errors first
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['level']),
        ]  # Optimize common queries

    def __str__(self):
        return f"{self.level} at {self.timestamp}: {self.message[:50]}"