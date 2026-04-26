import random
from .web_search import WebSearchEngine


class QuestionGenerator:
    def __init__(self):
        self.web_search = WebSearchEngine()

        # Comprehensive question dataset organized by category and difficulty
        self.dataset = {
            'personal': {
                # Questions tailored to candidate's resume background
                'career_history': [
                    "Tell me about your professional journey so far.",
                    "What motivated you to choose your current career path?",
                    "Describe the most challenging project you've worked on.",
                    "What's your biggest professional achievement to date?",
                    "How has your career evolved over the years?",
                    "What role do you see yourself in 5 years?",
                    "Describe a project you're most proud of.",
                    "What inspired you to pursue this field?",
                    "How do you approach learning new technologies?",
                    "What's the most valuable lesson you've learned in your career?",
                ],
                'skills_experience': [
                    "Which of your skills are you most confident about?",
                    "Describe your hands-on experience with your primary technologies.",
                    "How did you develop expertise in your main skill set?",
                    "What's the most complex problem you've solved using your skills?",
                    "How do you stay updated with industry trends?",
                    "Which technology are you most passionate about?",
                    "Describe a time when you had to quickly learn a new skill.",
                    "How do you evaluate which technology to use for a project?",
                    "What's your approach to mastering a new programming language?",
                    "How do you balance depth vs breadth in your technical knowledge?",
                ],
                'work_style': [
                    "How do you approach a new project from scratch?",
                    "Describe your typical workday routine.",
                    "How do you handle tight deadlines and pressure?",
                    "What's your communication style with team members?",
                    "How do you prioritize your tasks?",
                    "Describe your problem-solving methodology.",
                    "How do you handle feedback and criticism?",
                    "What's your approach to teamwork and collaboration?",
                    "How do you ensure work-life balance?",
                    "What drives you to perform at your best?",
                ]
            },
            'basic': {
                # Standard behavioral and HR questions
                'behavioral': [
                    "Tell me about yourself.",
                    "What are your biggest strengths?",
                    "What are your greatest weaknesses?",
                    "Why are you interested in this role?",
                    "What are your career goals?",
                    "Where do you see yourself in 5 years?",
                    "What motivates you at work?",
                    "Describe your ideal work environment.",
                    "What's your greatest accomplishment?",
                    "Why should we hire you?",
                    "How do you handle feedback?",
                    "Describe a time you helped a colleague.",
                    "What's your leadership style?",
                    "How do you handle conflicts at work?",
                    "Tell me about a time you failed and what you learned.",
                ],
                'situational': [
                    "How would you handle a disagreement with a team member?",
                    "What would you do if you missed a critical deadline?",
                    "How do you prioritize when you have multiple urgent tasks?",
                    "What would you do if you strongly disagreed with your manager?",
                    "How would you handle a situation where team members aren't pulling their weight?",
                    "What would you do if you discovered a major bug right before deployment?",
                    "How would you approach onboarding to a new team?",
                    "What would you do if a client is unhappy with the deliverable?",
                    "How would you handle being assigned a task outside your expertise?",
                    "What would you do if you saw a colleague cutting corners?",
                ],
                'cultural': [
                    "What type of company culture do you thrive in?",
                    "How do you contribute to a positive work environment?",
                    "What values are most important to you professionally?",
                    "How do you embrace diversity and inclusion?",
                    "What does innovation mean to you?",
                    "How do you handle change and uncertainty?",
                    "What's your approach to continuous improvement?",
                    "How do you define success?",
                    "What role does ethics play in your work?",
                    "How do you balance speed vs quality?",
                ]
            },
            'hard': {
                # Advanced technical and role-specific questions
                'technical_deep': [
                    "Design a scalable system that handles 1 million concurrent users.",
                    "How would you architect a real-time chat application with message persistence?",
                    "Explain the trade-offs between SQL and NoSQL databases for a high-traffic application.",
                    "How would you implement authentication and authorization in a microservices architecture?",
                    "Design a caching strategy for a read-heavy application with 10M+ daily users.",
                    "Explain how you would handle database migrations without downtime.",
                    "How would you secure a REST API against common vulnerabilities?",
                    "Describe your approach to performance optimization for a slow web application.",
                    "How would you design a message queue system for asynchronous processing?",
                    "Explain eventual consistency vs strong consistency with real-world examples.",
                ],
                'system_design': [
                    "Design Twitter/Instagram feed generation and delivery system.",
                    "Design YouTube video streaming platform at scale.",
                    "Design Uber's ride matching and dispatch system.",
                    "Design a distributed file storage system like Google Drive.",
                    "Design a URL shortening service like bit.ly.",
                    "Design an e-commerce shopping cart and checkout system.",
                    "Design a recommendation engine for Netflix/Amazon.",
                    "Design a notification system supporting millions of devices.",
                    "Design a payment processing system handling $1B+ transactions.",
                    "Design a real-time analytics dashboard for live metrics.",
                ],
                'problem_solving': [
                    "How would you debug a memory leak in a production service?",
                    "A critical service is down - walk me through your incident response process.",
                    "How would you reduce page load time from 5 seconds to under 1 second?",
                    "Your database is experiencing 10x latency spikes - how do you investigate?",
                    "How would you migrate a monolithic application to microservices?",
                    "A new feature requires 6 months of dev time but business needs it in 6 weeks - what do you do?",
                    "How would you implement feature flags for gradual rollouts?",
                    "Your caching layer is experiencing high miss rates - how do you optimize?",
                    "How would you design an A/B testing platform for your organization?",
                    "A security audit reveals SQL injection vulnerabilities - how do you fix?",
                ],
                'leadership_strategy': [
                    "How would you handle a situation where two teams blame each other for production issues?",
                    "You need to cut team budget by 30% - how would you approach this?",
                    "A senior engineer is underperforming - how do you handle it?",
                    "How would you drive adoption of a new technology the team resists?",
                    "Two senior engineers disagree on architecture - how do you decide?",
                    "You need to deliver an impossible deadline - how do you manage stakeholder expectations?",
                    "How would you build a high-performing team from scratch?",
                    "A key team member is burnt out - what's your approach?",
                    "How do you align engineering priorities with business needs?",
                    "How would you handle an ethical dilemma involving data privacy?",
                ]
            }
        }

        # Industry-specific question templates (dynamically filled with user's skills/role)
        self.skill_templates = {
            'general': [
                "How would you apply {skill} to solve a real-world business problem?",
                "What are the latest trends in {skill} and how do you stay current?",
                "Describe a complex {skill} problem you solved and your thought process.",
                "If you had to design a new tool for {skill}, what would it look like?",
                "How do you balance innovation vs stability when working with {skill}?",
            ],
            'role_based': {
                'software_engineer': [
                    "Write clean code for a function that handles pagination.",
                    "How would you test this piece of code for edge cases?",
                    "What's your approach to code reviews?",
                    "How do you ensure your code is maintainable?",
                ],
                'data_scientist': [
                    "How would you approach an imbalanced dataset?",
                    "Explain bias-variance tradeoff with an example.",
                    "How do you validate your machine learning models?",
                    "What's your process for feature engineering?",
                ],
                'product_manager': [
                    "How do you prioritize features for your product?",
                    "How do you say no to stakeholders?",
                    "How do you measure product success?",
                    "What's your approach to user research?",
                ],
                'designer': [
                    "How do you approach a new design project?",
                    "How do you balance aesthetics vs usability?",
                    "Describe your design process from research to handoff.",
                    "How do you ensure your designs are accessible?",
                ]
            }
        }

    def generate_questions(self, skills, mode, experience_years, num_questions=30):
        """
        Generate 30 structured questions:
        - 10 personal (resume-based) questions
        - 10 basic/behavioral questions
        - 10 hard/role-specific questions
        """
        questions = []

        # 1. PERSONAL QUESTIONS (10) - Based on resume details
        personal_questions = self._generate_personal_questions(skills, experience_years, count=10)
        questions.extend(personal_questions)

        # 2. BASIC QUESTIONS (10) - Standard behavioral and situational
        basic_questions = self._generate_basic_questions(mode, count=10)
        questions.extend(basic_questions)

        # 3. HARD QUESTIONS (10) - Role-specific and advanced
        hard_questions = self._generate_hard_questions(skills, mode, experience_years, count=10)
        questions.extend(hard_questions)

        return questions

    def _generate_personal_questions(self, skills, experience_years, count=10):
        """Generate questions specific to candidate's resume and background"""
        questions = []
        skills_list = skills if isinstance(skills, list) else [skills] if skills else []

        # Detect profession/role from skills
        detected_role = self._detect_profession(skills_list)
        
        # Personal/Career history questions (always include)
        personal_base = self.dataset['personal']['career_history'][:5]

        # Skills-based questions (if skills provided)
        skill_questions = []
        if skills_list:
            for skill in skills_list[:5]:  # Top 5 skills
                skill_questions.append(f"Describe your hands-on experience with {skill}.")
                skill_questions.append(f"What's the most complex project you've built using {skill}?")
                skill_questions.append(f"How do you stay updated with the latest developments in {skill}?")
                skill_questions.append(f"Can you walk me through a challenging {skill}-related problem you solved?")

        # Work style questions
        work_style = self.dataset['personal']['work_style'][:3]

        # Add role-specific questions based on detected profession
        role_specific = []
        if detected_role in self.skill_templates['role_based']:
            role_questions = self.skill_templates['role_based'][detected_role]
            # Add 2 role-specific questions
            for i in range(min(2, len(role_questions))):
                role_specific.append(role_questions[i])

        # Combine and shuffle
        all_personal = personal_base + skill_questions + work_style + role_specific
        random.shuffle(all_personal)

        return all_personal[:count]

    def _generate_basic_questions(self, mode, count=10):
        """Generate standard behavioral and situational questions"""
        # Adjust difficulty based on mode
        mode_key = mode if mode in ['easy', 'medium'] else 'medium'

        # Mix of behavioral and situational
        behavioral = self.dataset['basic']['behavioral'][:6]
        situational = self.dataset['basic']['situational'][:3]

        # For medium/hard, include more challenging questions
        if mode in ['medium', 'hard']:
            behavioral.extend(self.dataset['basic']['behavioral'][6:10])
            situational.extend(self.dataset['basic']['situational'][3:6])

        basic_mix = behavioral + situational
        random.shuffle(basic_mix)

        return basic_mix[:count]

    def _generate_hard_questions(self, skills, mode, experience_years, count=10):
        """Generate advanced, role-specific questions"""
        questions = []

        # For easy mode, reduce difficulty; for hard mode, maximum difficulty
        if mode == 'easy':
            hard_subset = self.dataset['hard']['technical_deep'][:3]
            hard_subset.extend(self.dataset['hard']['problem_solving'][:2])
        elif mode == 'medium':
            hard_subset = self.dataset['hard']['technical_deep'][:5]
            hard_subset.extend(self.dataset['hard']['problem_solving'][:3])
            hard_subset.extend(self.dataset['hard']['system_design'][:2])
        else:  # hard mode
            hard_subset = self.dataset['hard']['technical_deep'][:4]
            hard_subset.extend(self.dataset['hard']['system_design'][:4])
            hard_subset.extend(self.dataset['hard']['problem_solving'][:3])
            hard_subset.extend(self.dataset['hard']['leadership_strategy'][:2])

        # Add skill-specific hard questions
        if skills:
            skills_list = skills if isinstance(skills, list) else [skills]
            for skill in skills_list[:3]:
                questions.append(f"Design a system or solution that heavily uses {skill}.")
                questions.append(f"What are the major pitfalls and edge cases when working with {skill}?")

        # Combine with dataset
        final_hard = hard_subset + questions
        random.shuffle(final_hard)

        return final_hard[:count]

    def get_question_difficulty(self, question):
        """Classify question difficulty based on content"""
        question_lower = question.lower()

        # Hard indicators
        hard_words = ['design', 'architecture', 'scalability', 'optimize', 'million', 'billions',
                      'system', 'distributed', 'microservices', 'caching', 'security', 'incident',
                      'debug', 'performance', 'migration', 'crisis', 'unpopular']

        # Medium indicators
        medium_words = ['describe', 'explain', 'experience', 'challenge', 'project',
                       'lead', 'manage', 'approach', 'methodology', 'handle', 'solve']

        if any(word in question_lower for word in hard_words):
            return 'hard'
        elif any(word in question_lower for word in medium_words):
            return 'medium'
        else:
            return 'easy'

    def get_question_category(self, question):
        """Determine which category a question belongs to"""
        question_lower = question.lower()

        # Personal indicators
        personal_indicators = ['your', 'you', 'yourself', 'career', 'professional', 'experience',
                              'journey', 'achievement', 'proud', 'motivated', 'passionate']
        if any(word in question_lower for word in personal_indicators):
            return 'personal'

        # Hard question indicators
        hard_indicators = ['design', 'architect', 'scale', 'optimize', 'debug', 'incident',
                          'how would you', 'what would you do if', 'system', 'production']
        if any(word in question_lower for word in hard_indicators):
            return 'hard'

        # Default to basic
        return 'basic'

    def _detect_profession(self, skills_list):
        """Detect profession/role based on skills"""
        if not skills_list:
            return 'general'
            
        # Convert skills to lowercase for matching
        skills_lower = [skill.lower() for skill in skills_list]
        
        # Define skill mappings to professions
        profession_mapping = {
            'software_engineer': ['python', 'java', 'javascript', 'react', 'nodejs', 'typescript', 
                                'django', 'flask', 'express', 'spring', 'c#', 'c++', 'php', 'ruby',
                                'golang', 'rust', 'swift', 'kotlin', 'scala', 'perl', 'html', 'css'],
            'data_scientist': ['machine learning', 'data analysis', 'statistics', 'python', 'r', 
                             'sql', 'tableau', 'power bi', 'tensorflow', 'pytorch', 'scikit-learn',
                             'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'deep learning',
                             'nlp', 'computer vision', 'big data', 'hadoop', 'spark'],
            'product_manager': ['product management', 'agile', 'scrum', 'roadmap', 'user stories',
                              'market research', 'user experience', 'ux', 'ui', 'analytics',
                              'kpis', 'metrics', 'stakeholder management'],
            'designer': ['design', 'ui', 'ux', 'user experience', 'user interface', 'graphic design',
                        'visual design', 'figma', 'sketch', 'adobe', 'photoshop', 'illustrator',
                        'indesign', 'prototyping', 'wireframing']
        }
        
        # Check each profession
        for profession, required_skills in profession_mapping.items():
            # Count how many required skills are present
            matches = sum(1 for skill in required_skills if any(skill in s.lower() for s in skills_lower))
            # If at least 2 skills match, consider it a match
            if matches >= 2:
                return profession
                
        # Default to general if no specific profession detected
        return 'general'
