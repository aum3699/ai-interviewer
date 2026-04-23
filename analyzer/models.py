from django.db import models
from django.utils import timezone

class AnalysisHistory(models.Model):
    user_text = models.TextField()
    mbti_type = models.CharField(max_length=10)
    emotion = models.CharField(max_length=20)
    confidence_level = models.IntegerField(default=50)
    social_score = models.IntegerField(default=50)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
