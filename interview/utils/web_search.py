import os
import random
import requests
from typing import List
from bs4 import BeautifulSoup

# Try to load .env, but continue if not found
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class WebSearchEngine:
    """Web search for interview questions - uses API + web crawling + built-in dataset"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # Get API keys from environment
        self.tavily_api_key = os.getenv('TAVILY_API_KEY', '')
        self.google_api_key = os.getenv('GOOGLE_API_KEY', '')
        self.google_cse_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID', '')
        
        self.edu_sources = [
            'https://www.careeraddict.com/interview-questions-and-answers',
            'https://www.thebalancecareers.com/job-interview-questions-and-answers',
            'https://www.glassdoor.com/interview/index.htm',
            'https://www.indeed.com/career-advice/interviews',
        ]
    
    def search_questions(self, query: str, num_results: int = 10) -> List[str]:
        """Try API first, then web crawling, then built-in bank"""
        
        # Try Tavily API if key is set
        if self.tavily_api_key and not self.tavily_api_key.startswith('your_'):
            try:
                questions = self._search_tavily(query, num_results)
                if questions:
                    return questions
            except Exception as e:
                print(f"Tavily API error: {e}")
        
        # Try Google CSE if keys are set
        if self.google_api_key and self.google_cse_id:
            try:
                questions = self._search_google(query, num_results)
                if questions:
                    return questions
            except Exception as e:
                print(f"Google CSE error: {e}")
        
        # Try web crawling
        try:
            questions = self._crawl_edu_sources(query, num_results)
            if questions:
                return questions
        except Exception as e:
            print(f"Web crawling error: {e}")
        
        # Fallback to built-in dataset
        return self._get_fallback_questions(query, num_results)
    
    def _search_tavily(self, query: str, num_results: int) -> List[str]:
        """Use Tavily AI search API"""
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "max_results": num_results,
            "search_depth": "basic"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        questions = []
        for result in data.get('results', []):
            content = result.get('content', '')
            extracted = self._extract_questions_from_text(content)
            questions.extend(extracted)
        
        return questions[:num_results]
    
    def _search_google(self, query: str, num_results: int) -> List[str]:
        """Use Google Custom Search API"""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key,
            "cx": self.google_cse_id,
            "q": query,
            "num": min(num_results, 10)
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        questions = []
        for item in data.get('items', []):
            snippet = item.get('snippet', '')
            extracted = self._extract_questions_from_text(snippet)
            questions.extend(extracted)
        
        return questions[:num_results]
    
    def _crawl_edu_sources(self, query: str, num_results: int) -> List[str]:
        """Crawl educational career websites"""
        questions = []
        
        urls_to_try = [
            'https://www.thebalancecareers.com/top-10-common-interview-questions',
            'https://www.indeed.com/career-advice/interviewing/top-interview-questions',
            'https://www.glassdoor.com/interview-questions/index.htm',
        ]
        
        for url in urls_to_try:
            try:
                response = requests.get(url, headers=self.headers, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    for p in soup.find_all(['p', 'li', 'h3', 'h4']):
                        text = p.get_text().strip()
                        if '?' in text and len(text) > 30 and len(text) < 250:
                            text = text.split('.')[0] if '.' in text else text
                            if text not in questions:
                                questions.append(text)
            except:
                continue
            
            if len(questions) >= num_results:
                break
        
        if questions:
            random.shuffle(questions)
            return questions[:num_results]
        
        return []
    
    def _extract_questions_from_text(self, text: str) -> List[str]:
        """Extract question-like sentences"""
        import re
        
        questions = []
        patterns = [
            r'[A-Z][^.!?]*\?',
            r'(?:What|How|Why|When|Where|Who|Tell me|Describe|Explain)[^.!?]*\?',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            questions.extend(matches)
        
        return list(set([q.strip() for q in questions if len(q) > 20 and len(q) < 300]))
    
    def _get_fallback_questions(self, query: str, num_results: int) -> List[str]:
        """Built-in question dataset - 100+ questions"""
        fallback_bank = {
            'technical': [
                "What is your experience with this technology?",
                "Describe a challenging technical problem you solved.",
                "How do you stay updated with industry trends?",
                "Explain a complex technical concept to a non-technical person.",
                "What's your approach to debugging a critical issue?",
                "Walk me through a project you built from scratch.",
                "What are the pros and cons of this technology?",
                "How would you optimize a slow-performing system?",
                "Describe your experience with REST APIs.",
                "How do you handle data security?",
                "Explain the difference between SQL and NoSQL.",
                "How do you handle version control?",
                "Describe CI/CD pipeline.",
                "What's your experience with cloud services?",
                "How do you test your code?",
                "What's your favorite programming language and why?",
                "Describe experience with Agile methodology.",
                "How do you handle technical debt?",
                "What's your experience with microservices?",
                "How do you ensure code quality?",
            ],
            'behavioral': [
                "Tell me about yourself.",
                "What are your greatest strengths?",
                "What are your greatest weaknesses?",
                "Why do you want to work here?",
                "Where do you see yourself in 5 years?",
                "Describe a time you faced a conflict at work.",
                "Tell me about a time you failed and what you learned.",
                "How do you handle working under pressure?",
                "What motivates you at work?",
                "Describe your ideal work environment.",
                "Why should we hire you?",
                "What is your expected salary?",
                "What are your career goals?",
                "How do you prioritize tasks?",
                "Describe your leadership style.",
                "Describe a successful project you worked on.",
                "How do you handle constructive feedback?",
                "What is your biggest accomplishment?",
                "How do you work with difficult teammates?",
                "What's your work style?",
            ],
            'hr': [
                "Why are you leaving your current job?",
                "What is your expected salary?",
                "Why should we hire you?",
                "Describe your ideal work environment.",
                "How do you handle feedback and criticism?",
                "What are your career goals?",
                "How do you prioritize tasks?",
                "Describe your leadership style.",
                "How do you handle multiple deadlines?",
                "What's your work style?",
                "What's your notice period?",
                "Are you willing to relocate?",
                "Are you authorized to work?",
                "When can you start?",
                "Are you comfortable with overtime?",
            ]
        }
        
        query_lower = query.lower()
        if any(word in query_lower for word in ['technical', 'coding', 'programming', 'developer', 'python', 'java']):
            category = 'technical'
        elif any(word in query_lower for word in ['behavioral', 'soft skill', 'team', 'conflict']):
            category = 'behavioral'
        else:
            category = 'hr'
        
        questions = fallback_bank[category]
        random.shuffle(questions)
        return questions[:num_results]
    
    def get_mode_specific_query(self, skills: List[str], mode: str, experience: str) -> str:
        """Generate query based on mode"""
        skill_str = ', '.join(skills[:3]) if skills else 'software developer'
        
        mode_templates = {
            'easy': ['basic interview questions for beginner'],
            'medium': ['common interview questions for'],
            'hard': ['advanced senior interview questions for expert'],
        }
        
        modifier = random.choice(mode_templates[mode])
        return f"{modifier} {skill_str}"