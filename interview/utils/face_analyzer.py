import cv2
import numpy as np
import os


class FaceAnalyzer:
    def __init__(self):
        # Load pre-trained models for face detection and analysis
        self.face_cascade = None
        self.eye_cascade = None
        self._initialize_cascades()
        
    def _initialize_cascades(self):
        """Initialize OpenCV cascade classifiers"""
        try:
            # Get the path to OpenCV's built-in cascades
            cv2_base_dir = os.path.dirname(os.path.abspath(cv2.__file__))
            
            # Face cascade
            face_cascade_path = os.path.join(cv2_base_dir, 'data', 'haarcascade_frontalface_default.xml')
            if os.path.exists(face_cascade_path):
                self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
            
            # Eye cascade
            eye_cascade_path = os.path.join(cv2_base_dir, 'data', 'haarcascade_eye.xml')
            if os.path.exists(eye_cascade_path):
                self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
        except Exception as e:
            print(f"Warning: Could not load OpenCV cascades: {e}")
            # Fallback to basic detection
            pass
    
    def analyze_frame(self, frame):
        """Analyze a video frame for face, eye contact, emotion, and tension"""
        if frame is None or self.face_cascade is None:
            return {
                'eye_contact': False,
                'tension': 0.5,
                'emotion': 'neutral',
                'has_face': False
            }
        
        try:
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            if len(faces) == 0:
                return {
                    'eye_contact': False,
                    'tension': 0.5,
                    'emotion': 'neutral',
                    'has_face': False
                }
            
            # Take the largest face (assuming it's the main subject)
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = largest_face
            
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            
            # Detect eyes within the face region
            eyes = []
            if self.eye_cascade is not None:
                eyes = self.eye_cascade.detectMultiScale(
                    face_roi,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(20, 20)
                )
            
            # Determine eye contact (simplified: if eyes detected and looking forward)
            eye_contact = len(eyes) >= 2  # Both eyes detected
            
            # Simple emotion detection based on facial features (placeholder)
            # In a real implementation, you'd use a trained emotion recognition model
            emotion = self._detect_emotion(face_roi)
            
            # Simple tension detection based on facial rigidity (placeholder)
            tension = self._detect_tension(face_roi)
            
            return {
                'eye_contact': eye_contact,
                'tension': tension,
                'emotion': emotion,
                'has_face': True,
                'face_rectangle': (x, y, w, h),
                'eyes_detected': len(eyes)
            }
            
        except Exception as e:
            print(f"Error in face analysis: {e}")
            return {
                'eye_contact': False,
                'tension': 0.5,
                'emotion': 'neutral',
                'has_face': False
            }
    
    def _detect_emotion(self, face_roi):
        """Simple emotion detection based on facial features"""
        # This is a simplified placeholder - in reality you'd use a trained model
        # For now, we'll return neutral most of the time with occasional variations
        import random
        emotions = ['neutral', 'happy', 'surprised', 'thinking', 'concerned']
        # Return neutral 70% of the time, others randomly
        if random.random() < 0.7:
            return 'neutral'
        return random.choice([e for e in emotions if e != 'neutral'])
    
    def _detect_tension(self, face_roi):
        """Simple tension detection based on facial rigidity"""
        # This is a simplified placeholder - in reality you'd analyze micro-expressions
        # For now, return a low tension value most of the time
        import random
        # Return tension between 0.0 and 0.4 most of the time (relaxed)
        # Occasionally higher values to simulate stress
        if random.random() < 0.8:
            return random.uniform(0.0, 0.4)
        else:
            return random.uniform(0.4, 0.8)