from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import joblib
from pathlib import Path
import json
import time
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "models"

mbti_model = joblib.load(MODEL_DIR / "mbti_model.pkl")
mbti_vec = joblib.load(MODEL_DIR / "mbti_vec.pkl")
mbti_enc = joblib.load(MODEL_DIR / "mbti_enc.pkl")
sent_model = joblib.load(MODEL_DIR / "sent_model.pkl")
sent_vec = joblib.load(MODEL_DIR / "sent_vec.pkl")

APP_CATEGORIES = {
    "whatsapp": "social", "instagram": "social", "facebook": "social",
    "messenger": "social", "telegram": "social", "discord": "social",
    "snapchat": "social", "tiktok": "entertainment", "youtube": "entertainment",
    "netflix": "entertainment", "spotify": "entertainment", "prime": "entertainment",
    "chrome": "productivity", "gmail": "productivity", "slack": "productivity",
    "zoom": "productivity", "meet": "productivity", "drive": "productivity",
    "keep": "productivity", "notes": "productivity"
}

def home(request):
    return render(request, "index.html")

def analyze_personality(request):
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if not text:
            return render(request, "index.html", {"error": "Please enter text to analyze."})

        mbti_features = mbti_vec.transform([text])
        mbti_pred = mbti_model.predict(mbti_features.reshape(1, -1))
        mbti_type = mbti_enc.inverse_transform(mbti_pred)[0]

        sent_features = sent_vec.transform([text])
        sent_pred = sent_model.predict(sent_features.reshape(1, -1))[0]
        sentiment = "positive" if int(sent_pred) == 1 else "negative"

        return render(request, "result.html", {"mbti": mbti_type, "sentiment": sentiment})

    return render(request, "index.html")

@csrf_exempt
def api_usage(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            app_usage = data.get('app_usage', [])
            device_data = data.get('device_data', {})

            # Analyze app usage patterns
            analysis = analyze_app_usage(app_usage)

            # Analyze device data if provided
            if device_data:
                device_analysis = analyze_device_data(device_data)
                analysis.update(device_analysis)

            return JsonResponse({
                'status': 'success',
                'analysis': analysis,
                'timestamp': str(datetime.now())
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def analyze_app_usage(app_usage):
    """Analyze app usage patterns like the Android app"""
    total_time = sum(item.get('time', 0) for item in app_usage)

    # Categorize apps
    categories = {
        'social': 0,
        'entertainment': 0,
        'productivity': 0,
        'browsing': 0,
        'other': 0
    }

    app_categories = {
        'whatsapp': 'social', 'instagram': 'social', 'facebook': 'social',
        'telegram': 'social', 'discord': 'social', 'snapchat': 'social',
        'tiktok': 'entertainment', 'youtube': 'entertainment', 'netflix': 'entertainment',
        'spotify': 'entertainment', 'chrome': 'browsing', 'firefox': 'browsing',
        'code': 'productivity', 'notepad': 'productivity', 'word': 'productivity'
    }

    for app in app_usage:
        app_name = app.get('name', '').lower()
        time_spent = app.get('time', 0)

        category = 'other'
        for key, cat in app_categories.items():
            if key in app_name:
                category = cat
                break

        categories[category] += time_spent

    # Determine personality based on usage
    personality = "Balanced User"
    insights = []

    if categories['social'] > total_time * 0.4:
        personality = "Social Media Enthusiast"
        insights.append("You spend significant time on social platforms")
    elif categories['entertainment'] > total_time * 0.5:
        personality = "Entertainment Lover"
        insights.append("You enjoy media consumption")
    elif categories['productivity'] > total_time * 0.4:
        personality = "Productive User"
        insights.append("You focus on productive activities")

    return {
        'total_time_hours': round(total_time / 3600, 1),
        'categories': {k: round(v / 3600, 1) for k, v in categories.items()},
        'personality': personality,
        'insights': insights,
        'top_apps': sorted(app_usage, key=lambda x: x.get('time', 0), reverse=True)[:5]
    }

def analyze_device_data(device_data):
    """Analyze device data (messages, contacts, calls) for personality insights"""
    messages = device_data.get('messages', {})
    contacts = device_data.get('contacts', {})
    calls = device_data.get('calls', {})

    total_messages = messages.get('total_messages', 0)
    total_contacts = contacts.get('total_contacts', 0)
    total_calls = calls.get('total_calls', 0)

    # Communication style analysis
    if total_messages > 200:
        communication_style = "Very Active"
    elif total_messages > 50:
        communication_style = "Moderately Active"
    else:
        communication_style = "Reserved"

    # Social network analysis
    device_personality = []
    if total_contacts > 100:
        device_personality.append("Large social network")
    elif total_contacts > 30:
        device_personality.append("Moderate social network")
    else:
        device_personality.append("Selective social circle")

    if total_messages > 100:
        device_personality.append("Highly communicative")
    elif total_messages > 20:
        device_personality.append("Moderately communicative")
    else:
        device_personality.append("Reserved communicator")

    if total_calls > 50:
        device_personality.append("Frequent phone user")
    elif total_calls > 10:
        device_personality.append("Regular phone user")
    else:
        device_personality.append("Light phone user")

    return {
        'communication_style': communication_style,
        'device_personality': device_personality,
        'device_stats': {
            'messages': total_messages,
            'contacts': total_contacts,
            'calls': total_calls
        }
    }

def device_analysis(request):
    """Web interface for device data analysis"""
    if request.method == "POST":
        try:
            # Get data from form
            messages_data = {
                'total_messages': int(request.POST.get('total_messages', 0)),
                'sent_messages': int(request.POST.get('sent_messages', 0)),
                'received_messages': int(request.POST.get('received_messages', 0))
            }

            contacts_data = {
                'total_contacts': int(request.POST.get('total_contacts', 0)),
                'contacts_with_phones': int(request.POST.get('contacts_with_phones', 0))
            }

            calls_data = {
                'total_calls': int(request.POST.get('total_calls', 0)),
                'incoming_calls': int(request.POST.get('incoming_calls', 0)),
                'outgoing_calls': int(request.POST.get('outgoing_calls', 0)),
                'total_call_minutes': int(request.POST.get('total_call_minutes', 0))
            }

            device_data = {
                'messages': messages_data,
                'contacts': contacts_data,
                'calls': calls_data
            }

            analysis = analyze_device_data(device_data)

            return render(request, "device_results.html", {
                'analysis': analysis,
                'device_data': device_data
            })

        except Exception as e:
            return render(request, "device_analysis.html", {
                'error': f"Error analyzing data: {str(e)}"
            })

    return render(request, "device_analysis.html")

@csrf_exempt
def api_device_analysis(request):
    """API endpoint for device data analysis"""
    if request.method == "POST":
        try:
            device_data = json.loads(request.body)
            analysis = analyze_device_data(device_data)

            return JsonResponse({
                'status': 'success',
                'analysis': analysis
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def check_mobile_data(request):
    """Check if mobile app has sent data"""
    # In a real implementation, this would check a database
    # For now, return a placeholder response
    return JsonResponse({
        'has_data': False,
        'message': 'Mobile data sync not implemented yet'
    })

@csrf_exempt
def api_usage_analysis(request):
    """API endpoint for app usage analysis from mobile/web sync"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            apps = data.get("apps", [])
            
            total_social = 0
            total_entertainment = 0
            total_productivity = 0
            total_usage = 0
            top_app = None
            top_time = 0

            for app in apps:
                package = app.get("package_name", "").lower()
                duration = app.get("duration", 0)
                total_usage += duration

                category = "other"
                for key, cat in APP_CATEGORIES.items():
                    if key in package:
                        category = cat
                        break

                if category == "social":
                    total_social += duration
                elif category == "entertainment":
                    total_entertainment += duration
                elif category == "productivity":
                    total_productivity += duration

                if duration > top_time:
                    top_time = duration
                    top_app = app.get("app_name", package)

            total_hours = total_usage / 3600000
            social_hours = total_social / 3600000
            entertainment_hours = total_entertainment / 3600000
            productivity_hours = total_productivity / 3600000

            dominant = get_dominant_category(total_social, total_entertainment, total_productivity)
            insight = generate_insight(dominant, total_hours, social_hours, entertainment_hours, productivity_hours)
            mood = determine_mood(dominant, total_hours, social_hours)
            health_score = calculate_health_score(total_hours, social_hours, entertainment_hours, productivity_hours)

            return JsonResponse({
                "total_hours": round(total_hours, 1),
                "dominant_category": dominant,
                "insight": insight,
                "mood": mood,
                "health_score": health_score,
                "top_app": top_app,
                "breakdown": {
                    "social": round(social_hours, 1),
                    "entertainment": round(entertainment_hours, 1),
                    "productivity": round(productivity_hours, 1)
                }
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Use POST"}, status=405)

def get_dominant_category(social, entertainment, productivity):
    if social >= entertainment and social >= productivity:
        return "social"
    if entertainment >= social and entertainment >= productivity:
        return "entertainment"
    if productivity > social and productivity > entertainment:
        return "productive"
    return "balanced"

def generate_insight(category, total_hours, social_hours, entertainment_hours, productivity_hours):
    if total_hours < 1:
        return "You're barely using your phone today. Great digital wellbeing!"

    if category == "social":
        if total_hours >= 5:
            return f"Heavy social media user ({total_hours}h). You love staying connected but consider taking breaks."
        elif total_hours >= 3:
            return f"Moderate social media use ({total_hours}h). You're socially active but balanced."
        return "Light social media user. You maintain healthy boundaries."

    if category == "entertainment":
        if total_hours >= 5:
            return f"Binge watcher! {total_hours}h on entertainment apps. Maybe try a new hobby?"
        elif total_hours >= 3:
            return f"Enjoying entertainment ({total_hours}h). Balance is key!"
        return "Casual entertainment consumer."

    if category == "productive":
        if total_hours >= 5:
            return f"Super productive! {total_hours}h on work apps. You're crushing it!"
        elif total_hours >= 3:
            return f"Good productivity focus ({total_hours}h). Keep it up!"
        return "Maintaining healthy productivity."

    return f"Mixed usage pattern. {total_hours}h total across apps. Good variety!"

def determine_mood(category, total_hours, social_hours):
    if total_hours > 6:
        return "drained"
    if category == "social" and social_hours > 3:
        return "connected"
    if category == "productive":
        return "focused"
    return "neutral"

def calculate_health_score(total_hours, social_hours, entertainment_hours, productivity_hours):
    score = 100

    if total_hours > 6:
        score -= 30
    elif total_hours > 4:
        score -= 15
    elif total_hours > 2:
        score -= 5

    if (social_hours + entertainment_hours) > total_hours * 0.7:
        score -= 20
    elif (social_hours + entertainment_hours) > total_hours * 0.5:
        score -= 10

    score += min(20, int(productivity_hours * 2))

    return max(0, min(100, score))
