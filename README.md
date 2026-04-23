# AI Personality Mirror - Web Application

A web application that analyzes text to determine MBTI personality type and sentiment.

---

## Features

- **Text-based Personality Analysis**: Submit text to get MBTI type and sentiment analysis
- **MBTI Classification**: Predicts Myers-Briggs personality type (INTJ, ENFP, ISTJ, etc.)
- **Sentiment Analysis**: Determines if the text is positive or negative
- **API Endpoints**: REST API for integrating with other applications

---

## Installation

### Prerequisites
- Python 3.9+
- Django 5.2+

### Setup

```bash
# Navigate to project
cd d:\ai_personality_mirror

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Server

```bash
cd django_app
python manage.py runserver
# Server runs at http://127.0.0.1:8000/
```

---

## Deployment on Render

This project is ready for deployment on [Render](https://render.com).

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following environment variables:
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: Your Render domain
   - `DJANGO_SECRET_KEY`: A secure secret key
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn django_app.wsgi --bind 0.0.0.0:$PORT`

---

## API Reference

### Analyze Personality (Web)

**POST** `/analyze/`

Request:
```html
<form method="POST">
    <textarea name="text"></textarea>
    <button type="submit">Analyze</button>
</form>
```

Response:
```json
{
    "mbti": "INTJ",
    "sentiment": "positive"
}
```

### App Usage API

**POST** `/api/usage/`

Request:
```json
{
    "apps": [
        {"package_name": "com.whatsapp", "duration": 120},
        {"package_name": "com.youtube", "duration": 180}
    ]
}
```

---

## Project Structure

```
ai_personality_mirror/
├── django_app/           # Web backend
│   ├── analyzer/         # Personality analysis views
│   ├── settings.py       # Django configuration
│   └── manage.py
├── models/              # Pretrained ML models
├── templates/           # Django HTML templates
├── requirements.txt     # Python dependencies
└── Procfile             # Render deployment config
```

---

## Technologies Used

| Component | Technology |
|-----------|-----------|
| **Backend** | Django 5.2, Python 3.9+ |
| **ML/AI** | scikit-learn, TF-IDF, Naive Bayes |
| **Server** | Gunicorn, WhiteNoise |
| **Deployment** | Render |

---

## License

This project is for educational purposes.

---

## Contributing

Ideas for improvements:
- [ ] Cloud sync dashboard
- [ ] Weekly behavior reports
- [ ] Mood tracking correlation
- [ ] Machine learning on personal behavior patterns
