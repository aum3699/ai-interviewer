import numpy as np
import os


class VoiceAnalyzer:
    def __init__(self):
        self.whisper_model = None
        
    def transcribe(self, audio_bytes):
        return {
            'text': '',
            'language': 'en',
            'confidence': 0.5
        }
    
    def analyze_stress(self, audio_bytes):
        return {
            'stress_score': 0.5,
            'pitch_mean': 0,
            'pitch_variability': 0,
            'speaking_rate': 0,
            'volume_mean': 0
        }
    
    def calculate_answer_relevance(self, question, answer_text):
        if not answer_text or not question:
            return 0.5
        
        question_words = set(question.lower().split())
        answer_words = set(answer_text.lower().split())
        
        common_words = question_words.intersection(answer_words)
        relevance = len(common_words) / (len(question_words) + 0.01)
        
        return min(relevance, 1.0)