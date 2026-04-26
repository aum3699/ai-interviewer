import json
import uuid
import base64
import os
import numpy as np
import cv2
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

from .models import InterviewSession, Question, Answer, FaceFrame
from .utils.resume_parser import ResumeParser
from .utils.question_generator import QuestionGenerator
from .utils.face_analyzer import FaceAnalyzer
from .utils.voice_analyzer import VoiceAnalyzer


resume_parser = ResumeParser()
question_generator = QuestionGenerator()
face_analyzer = FaceAnalyzer()
voice_analyzer = VoiceAnalyzer()


from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

def index(request):
    return render(request, 'index.html')


def permission(request):
    if request.method == 'POST':
        # Handle permission grant
        request.session['permissions_granted'] = True
        # Check if resume is already uploaded
        if 'resume_data' in request.session:
            return redirect('interview')
        else:
            return redirect('resume_upload')
    return render(request, 'permission.html')


def resume_upload(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        file_path = default_storage.save(f'resumes/{resume_file.name}', ContentFile(resume_file.read()))
        full_path = default_storage.path(file_path)
        resume_data = resume_parser.parse(full_path)
        request.session['resume_data'] = resume_data
        return redirect('mode_select')
    
    return render(request, 'resume_upload.html')


def mode_select(request):
    if request.method == 'POST':
        mode = request.POST.get('mode')
        if mode in ['easy', 'medium', 'hard']:
            request.session['interview_mode'] = mode
            return redirect('interview')
    
    return render(request, 'mode_select.html')


def interview(request):
    if 'interview_session_id' not in request.session:
        session_id = str(uuid.uuid4())[:8]
        resume_data = request.session.get('resume_data', {})
        mode = request.session.get('interview_mode', 'medium')

        interview_session = InterviewSession.objects.create(
            session_id=session_id,
            mode=mode,
            resume_text=resume_data.get('full_text', ''),
            skills=resume_data.get('skills', []),
            user=request.user if request.user.is_authenticated else None
        )

        # Generate 30 structured questions (10 personal + 10 basic + 10 hard)
        questions = question_generator.generate_questions(
            skills=resume_data.get('skills', []),
            mode=mode,
            experience_years=resume_data.get('experience_years', '0'),
            num_questions=30  # Now generating 30 questions
        )

        for i, q_text in enumerate(questions):
            Question.objects.create(
                session=interview_session,
                question_text=q_text,
                difficulty=question_generator.get_question_difficulty(q_text),
                order_index=i  # Store order
            )

        request.session['interview_session_id'] = session_id
        request.session['current_question_index'] = 0
        request.session['answers'] = []

    session_id = request.session['interview_session_id']
    interview_session = InterviewSession.objects.get(session_id=session_id)
    questions = list(interview_session.questions.all().order_by('order_index'))
    current_index = request.session.get('current_question_index', 0)

    context = {
        'session_id': session_id,
        'mode': interview_session.mode,
        'total_questions': len(questions),
        'current_question': questions[current_index] if current_index < len(questions) else None,
        'current_index': current_index,
        'progress': int((current_index / len(questions)) * 100) if questions else 0,
        'questions_remaining': len(questions) - current_index,
        'permissions_granted': request.session.get('permissions_granted', False)
    }

    return render(request, 'interview.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def submit_answer(request):
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    session_id = data.get('session_id')
    question_id = data.get('question_id')
    answer_text = data.get('answer_text', '')
    face_frames = data.get('face_frames', [])
    
    if not session_id or not question_id:
        return JsonResponse({'status': 'error', 'message': 'Missing parameters'}, status=400)
    
    try:
        interview_session = InterviewSession.objects.get(session_id=session_id)
        question = Question.objects.get(id=question_id)
    except InterviewSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=404)
    except Question.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Question not found'}, status=404)
    
    # REAL SCORING LOGIC based on answer content
    answer_lower = answer_text.lower()
    question_lower = question.question_text.lower()
    
    # 1. Calculate relevance score (keyword matching)
    keywords = ['i', 'my', 'experience', 'worked', 'project', 'team', 'learned', 'success', 'challenge', 'solve', 'use', 'developed', 'created', 'built', 'managed', 'lead', 'collaborated']
    question_keywords = [w for w in question_lower.split() if len(w) > 3]
    answer_keywords = [w for w in answer_lower.split() if w in keywords]
    relevance = min(len(answer_keywords) / max(len(question_keywords), 1), 1.0)
    relevance = max(relevance, 0.3)  # min 30%
    
    # 2. Answer length score
    word_count = len(answer_text.split())
    if word_count < 10:
        length_score = 0.3
    elif word_count < 30:
        length_score = 0.6
    elif word_count < 50:
        length_score = 0.8
    else:
        length_score = 1.0
    
    # 3. Eye contact and emotion analysis from face frames
    eye_contact_count = 0
    emotion_counts = {}
    total_tension = 0.0
    analyzed_frames_count = 0
    frame_analyses = []  # store per-frame analysis for storage

    if face_frames:
        for frame_data in face_frames:
            image_data = frame_data.get('image')
            if not image_data:
                continue
            try:
                # Extract base64 part (strip data URL prefix if present)
                if ',' in image_data:
                    b64_data = image_data.split(',', 1)[1]
                else:
                    b64_data = image_data
                img_bytes = base64.b64decode(b64_data)
                nparr = np.frombuffer(img_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if frame is None:
                    continue
                analysis = face_analyzer.analyze_frame(frame)
                if analysis.get('eye_contact'):
                    eye_contact_count += 1
                emotion = analysis.get('emotion', 'neutral')
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                tension = analysis.get('tension', 0.5)
                total_tension += tension
                analyzed_frames_count += 1
                frame_analyses.append({
                    'frame_number': frame_data.get('frame_number', 0),
                    'emotion': emotion,
                    'confidence': 0.8,  # placeholder confidence
                    'eye_contact': analysis.get('eye_contact', False),
                    'timestamp': frame_data.get('timestamp', 0)
                })
            except Exception as e:
                print(f"Error analyzing frame: {e}")
                continue

    if analyzed_frames_count > 0:
        eye_score = eye_contact_count / analyzed_frames_count
        avg_tension = total_tension / analyzed_frames_count
        dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'neutral'
    else:
        eye_score = 0.5
        avg_tension = 0.5
        dominant_emotion = 'neutral'
        frame_analyses = []
    
    # 4. Stress score (based on answer content)
    stress_words = ['nervous', 'worried', 'anxious', 'scared', 'fail', 'not sure', 'maybe']
    confident_words = ['confident', 'sure', 'experienced', 'managed', 'led', 'created', 'developed', 'solved', 'accomplished']
    
    stress_count = sum(1 for w in stress_words if w in answer_lower)
    confident_count = sum(1 for w in confident_words if w in answer_lower)
    
    if confident_count > stress_count:
        stress_score = 0.8
    elif confident_count > 0:
        stress_score = 0.5
    else:
        stress_score = 0.4
    
    # 5. Factual correctness score (for questions with definite answers)
    correctness_score = _evaluate_factual_correctness(question, answer_text)
    
    # Calculate total score (weighted average)
    # Adjust weights to include correctness
    total_score = (relevance * 0.3 + length_score * 0.2 + eye_score * 0.15 + stress_score * 0.15 + correctness_score * 0.2) * 100
    
    # Ensure realistic scores
    total_score = min(max(total_score, 20), 100)
    
    # Determine emotion based on content
    if total_score >= 70:
        emotion = 'confident'
    elif total_score >= 50:
        emotion = 'neutral'
    else:
        emotion = 'uncertain'
    
    answer = Answer.objects.create(
        question=question,
        answer_text=answer_text[:2000],  # Limit answer length
        relevance_score=relevance,
        eye_contact_score=eye_score,
        emotion_score=stress_score,
        voice_stress_score=stress_score,
        total_score=total_score,
        emotions_detected={'dominant': dominant_emotion, 'counts': emotion_counts},
        eye_contact_frames=eye_contact_count,
        tension_level=avg_tension
    )
    
    for fa in frame_analyses:
        FaceFrame.objects.create(
            answer=answer,
            frame_number=fa['frame_number'],
            emotion=fa['emotion'],
            confidence=fa['confidence'],
            eye_contact=fa['eye_contact'],
            timestamp=fa['timestamp']
        )
    
    # Save data dump for this answer
    _save_data_dump(interview_session, question, answer, face_frames)
    
    return JsonResponse({
        'status': 'success',
        'score': total_score,
        'relevance': relevance,
        'eye_contact': eye_score,
        'stress': stress_score,
        'length_score': length_score,
        'quality_score': correctness_score
    })


def next_question(request):
    session_id = request.GET.get('session_id')
    
    try:
        interview_session = InterviewSession.objects.get(session_id=session_id)
    except InterviewSession.DoesNotExist:
        return JsonResponse({'has_next': False, 'completed': True})
    
    questions = list(interview_session.questions.all().order_by('order_index'))
    current_index = request.session.get('current_question_index', 0)
    
    if current_index + 1 < len(questions):
        request.session['current_question_index'] = current_index + 1
        return JsonResponse({
            'has_next': True,
            'next_question': questions[current_index + 1].question_text,
            'next_question_id': questions[current_index + 1].id,
            'progress': int(((current_index + 1) / len(questions)) * 100),
            'current_index': current_index + 1
        })
    else:
        return JsonResponse({
            'has_next': False,
            'completed': True
        })


def result(request):
    session_id = request.session.get('interview_session_id')
    
    if not session_id:
        return redirect('index')
    
    interview_session = InterviewSession.objects.get(session_id=session_id)
    questions = interview_session.questions.all()
    
    total_score = 0
    question_scores = []
    
    for q in questions:
        try:
            if hasattr(q, 'answer'):
                total_score += q.answer.total_score
                question_scores.append({
                    'question': q.question_text,
                    'score': q.answer.total_score,
                    'relevance': q.answer.relevance_score,
                    'eye_contact': q.answer.eye_contact_score
                })
        except Answer.DoesNotExist:
            pass
    
    avg_score = total_score / len(questions) if questions else 0
    
    if avg_score < 50:
        recommendation = "Start with EASY mode"
    elif avg_score < 70:
        recommendation = "Practice MEDIUM mode"
    else:
        recommendation = "Ready for HARD mode"
    
    selected_mode = interview_session.mode
    if selected_mode == 'hard' and avg_score < 60:
        mode_verification = "You selected HARD mode but scored below 60%. Consider practicing MEDIUM mode first."
    elif selected_mode == 'medium' and avg_score < 50:
        mode_verification = "Medium mode was challenging for you. Try EASY mode to build confidence."
    elif selected_mode == 'easy' and avg_score > 80:
        mode_verification = "You're ready for MEDIUM or HARD mode!"
    else:
        mode_verification = f"Good job! Keep practicing at {selected_mode.upper()} level."
    
    context = {
        'session': interview_session,
        'total_score': avg_score,
        'question_scores': question_scores,
        'recommendation': recommendation,
        'mode_verification': mode_verification,
        'selected_mode': selected_mode,
        'total_questions': len(questions)
    }
    
    return render(request, 'result.html', context)


def dashboard(request):
    """Dashboard page showing statistics and recent interviews"""
    sessions = InterviewSession.objects.all().order_by('-created_at')[:10]
    
    total_interviews = sessions.count()
    total_questions = Question.objects.count()
    
    # Calculate average score
    total_score = 0
    count = 0
    for session in sessions:
        for question in session.questions.all():
            try:
                if hasattr(question, 'answer'):
                    total_score += question.answer.total_score
                    count += 1
            except:
                pass
    
    avg_score = total_score / count if count > 0 else 0
    
    context = {
        'total_interviews': total_interviews,
        'avg_score': int(avg_score),
        'total_questions': total_questions,
        'current_streak': 7,  # Placeholder
        'recent_interviews': sessions
    }
    
    return render(request, 'dashboard.html', context)


def myinterviews(request):
    """My Interviews page showing all interview history"""
    sessions = InterviewSession.objects.all().order_by('-created_at')
    
    context = {
        'interviews': sessions
    }
    
    return render(request, 'myinterviews.html', context)


def profile(request):
    """Profile page for user settings"""
    context = {
        'user_name': 'John Doe',
        'user_email': 'john@example.com',
        'profession': 'Software Engineer',
        'experience': '5 years'
    }
    
    return render(request, 'profile.html', context)


def _evaluate_factual_correctness(question, answer_text):
    """
    Evaluate if answer is factually correct for questions with definite answers
    Returns a score between 0.0 and 1.0
    """
    # For now, return a neutral score - in a real implementation,
    # this would use NLP models or knowledge bases to verify facts
    # This is a placeholder that could be enhanced with APIs like:
    # - Google Fact Check API
    # - Wolfram Alpha API
    # - Wikipedia API for verification
    # - Specialized domain APIs (medical, technical, etc.)
    
    question_lower = question.question_text.lower()
    answer_lower = answer_text.lower()
    
    # Simple heuristic: if question contains certain words, apply basic fact checking
    # This is very basic and would be replaced with actual fact-checking APIs
    
    # Questions asking for definitions or explanations
    if any(word in question_lower for word in ['what is', 'define', 'explain', 'describe']):
        # Check if answer has reasonable length and contains key terms
        if len(answer_text.split()) >= 5:
            return 0.7  # Assume mostly correct for now
        else:
            return 0.3  # Too short likely incorrect
    
    # Questions asking for numbers, dates, specifics
    elif any(word in question_lower for word in ['how many', 'when', 'what year', 'how much']):
        # Check if answer contains numbers
        import re
        if re.search(r'\d+', answer_text):
            return 0.8  # Contains a number, likely partially correct
        else:
            return 0.2  # No number when expected
    
    # Yes/no questions
    elif question_lower.strip().endswith('?') and any(word in question_lower for word in ['is', 'are', 'was', 'were', 'do', 'does', 'can', 'could']):
        # Simple check for yes/no indicators
        yes_indicators = ['yes', 'yeah', 'yep', 'correct', 'right', 'true', 'affirmative']
        no_indicators = ['no', 'nope', 'not', 'false', 'negative']
        
        has_yes = any(indicator in answer_lower for indicator in yes_indicators)
        has_no = any(indicator in answer_lower for indicator in no_indicators)
        
        if has_yes and not has_no:
            return 0.8  # Leaning yes
        elif has_no and not has_yes:
            return 0.8  # Leaning no
        elif has_yes and has_no:
            return 0.4  # Contradictory
        else:
            return 0.5  # Unclear
    
    # Default: return neutral score for open-ended questions
    return 0.6


def _save_data_dump(interview_session, question, answer, face_frames):
    """Save interview data to files for analysis and dataset creation"""
    try:
        # Create data dumps directory if it doesn't exist
        data_dump_dir = os.path.join(settings.BASE_DIR, 'data_dumps')
        os.makedirs(data_dump_dir, exist_ok=True)
        
        # Create session-specific file
        session_file = os.path.join(data_dump_dir, f"session_{interview_session.session_id}.json")
        
        # Prepare data to save
        data = {
            'session_id': interview_session.session_id,
            'mode': interview_session.mode,
            'created_at': interview_session.created_at.isoformat(),
            'completed_at': interview_session.completed_at.isoformat() if interview_session.completed_at else None,
            'user_id': interview_session.user.id if interview_session.user else None,
            'resume_text': interview_session.resume_text,
            'skills': interview_session.skills,
            'question': {
                'id': question.id,
                'text': question.question_text,
                'category': question.category,
                'difficulty': question.difficulty,
                'order': question.order
            },
            'answer': {
                'text': answer.answer_text,
                'relevance_score': answer.relevance_score,
                'eye_contact_score': answer.eye_contact_score,
                'emotion_score': answer.emotion_score,
                'voice_stress_score': answer.voice_stress_score,
                'total_score': answer.total_score,
                'emotions_detected': answer.emotions_detected,
                'eye_contact_frames': answer.eye_contact_frames,
                'tension_level': answer.tension_level,
                'created_at': answer.created_at.isoformat()
            },
            'face_frames': face_frames,
            'timestamp': str(uuid.uuid4())
        }
        
        # Append to session file (read existing data, append new answer, write back)
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                session_data = json.load(f)
        else:
            session_data = {
                'session_info': {
                    'session_id': interview_session.session_id,
                    'mode': interview_session.mode,
                    'created_at': interview_session.created_at.isoformat(),
                    'user_id': interview_session.user.id if interview_session.user else None,
                    'resume_text': interview_session.resume_text,
                    'skills': interview_session.skills
                },
                'answers': []
            }
        
        session_data['answers'].append(data)
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
            
        # Also create a CSV file for easy analysis
        _append_to_csv_dump(interview_session, question, answer, face_frames)
        
    except Exception as e:
        # Log error but don't break the interview flow
        print(f"Error saving data dump: {e}")


def _append_to_csv_dump(interview_session, question, answer, face_frames):
    """Append interview data to CSV file for analysis"""
    try:
        data_dump_dir = os.path.join(settings.BASE_DIR, 'data_dumps')
        csv_file = os.path.join(data_dump_dir, 'interview_data.csv')
        
        # Calculate average emotion confidence from face frames
        avg_emotion_confidence = 0.0
        if face_frames:
            emotion_confidences = [f.get('confidence', 0.5) for f in face_frames]
            avg_emotion_confidence = sum(emotion_confidences) / len(emotion_confidences)
        
        # Count eye contact frames
        eye_contact_count = sum(1 for f in face_frames if f.get('eye_contact', False))
        
        # Prepare CSV row
        csv_row = [
            interview_session.session_id,
            interview_session.mode,
            question.id,
            question.question_text[:100],  # Truncate for CSV
            answer.answer_text[:200],      # Truncate for CSV
            answer.relevance_score,
            answer.eye_contact_score,
            answer.emotion_score,
            answer.voice_stress_score,
            answer.total_score,
            answer.emotions_detected.get('dominant', 'neutral'),
            eye_contact_count,
            len(face_frames),
            avg_emotion_confidence,
            answer.tension_level,
            interview_session.created_at.isoformat(),
            answer.created_at.isoformat()
        ]
        
        # Write header if file doesn't exist
        file_exists = os.path.exists(csv_file)
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            import csv
            writer = csv.writer(f)
            
            if not file_exists:
                header = [
                    'session_id', 'mode', 'question_id', 'question_text', 'answer_text',
                    'relevance_score', 'eye_contact_score', 'emotion_score', 
                    'voice_stress_score', 'total_score', 'dominant_emotion',
                    'eye_contact_frames', 'total_frames', 'avg_emotion_confidence',
                    'tension_level', 'session_created_at', 'answer_created_at'
                ]
                writer.writerow(header)
            
            writer.writerow(csv_row)
            
    except Exception as e:
        print(f"Error saving CSV dump: {e}")