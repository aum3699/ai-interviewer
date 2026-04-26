from django.db import models
from django.contrib.auth.models import User


class InterviewSession(models.Model):
    MODE_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    resume_text = models.TextField(blank=True, default='')
    skills = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_score = models.FloatField(default=0)
    recommendation = models.CharField(max_length=50, blank=True, default='')
    
    def __str__(self):
        return f"Session {self.session_id} - {self.mode}"


class Question(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    category = models.CharField(max_length=100, blank=True, default='')
    difficulty = models.CharField(max_length=10, default='medium')
    expected_keywords = models.JSONField(default=list)
    order_index = models.IntegerField(default=0)  # Order of question in interview

    class Meta:
        ordering = ['order_index']

    def __str__(self):
        return self.question_text[:50]


class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer')
    answer_text = models.TextField(blank=True, default='')
    answer_audio_path = models.CharField(max_length=500, blank=True, default='')
    transcription = models.TextField(blank=True, default='')
    
    relevance_score = models.FloatField(default=0)
    eye_contact_score = models.FloatField(default=0)
    emotion_score = models.FloatField(default=0)
    voice_stress_score = models.FloatField(default=0)
    total_score = models.FloatField(default=0)
    
    emotions_detected = models.JSONField(default=dict)
    eye_contact_frames = models.IntegerField(default=0)
    tension_level = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Answer for Q{self.question.id}"


class FaceFrame(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='face_frames')
    frame_number = models.IntegerField()
    emotion = models.CharField(max_length=50)
    confidence = models.FloatField()
    eye_contact = models.BooleanField()
    timestamp = models.FloatField()
    
    class Meta:
        ordering = ['frame_number']