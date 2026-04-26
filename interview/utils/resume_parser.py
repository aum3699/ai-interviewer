import re
import spacy
import docx2txt
import pdfplumber

nlp = spacy.load('en_core_web_sm')


class ResumeParser:
    def __init__(self):
        self.skill_keywords = [
            'python', 'java', 'javascript', 'react', 'django', 'flask',
            'sql', 'mongodb', 'aws', 'docker', 'kubernetes', 'tensorflow',
            'pytorch', 'machine learning', 'data analysis', 'agile', 'scrum',
            'project management', 'leadership', 'communication', 'nodejs',
            'typescript', 'git', 'linux', 'rest api', 'graphql',
            'reactjs', 'angular', 'vue', 'nextjs', 'express',
            'postgresql', 'mysql', 'redis', 'elasticsearch',
            'ci/cd', 'jenkins', 'gitlab', 'github actions'
        ]
    
    def parse(self, file_path):
        if file_path.endswith('.pdf'):
            with pdfplumber.open(file_path) as pdf:
                text = ''.join(page.extract_text() or '' for page in pdf.pages)
        elif file_path.endswith('.docx'):
            text = docx2txt.process(file_path)
        else:
            text = ""
        
        return self._extract_info(text)
    
    def _extract_info(self, text):
        doc = nlp(text.lower())
        
        skills = []
        for skill in self.skill_keywords:
            if skill in text.lower():
                skills.append(skill.capitalize())
        
        exp_pattern = r'(\d+)\+?\s*(?:years?|yrs?)'
        experience_matches = re.findall(exp_pattern, text.lower())
        experience = experience_matches[0] if experience_matches else "0"
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email = re.findall(email_pattern, text)
        email = email[0] if email else ""
        
        lines = text.split('\n')
        name = lines[0].strip() if lines else "Candidate"
        
        return {
            'name': name,
            'email': email,
            'skills': skills[:10],
            'experience_years': experience,
            'full_text': text[:5000]
        }