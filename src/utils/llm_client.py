"""
Gemini API client for text generation.
"""
import os
import random
import time
from typing import List, Optional
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-pro')
        self.temperature = float(os.getenv('GEMINI_TEMPERATURE', 0.8))
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                'temperature': self.temperature,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 1024,
            }
        )
        
        # Fallback templates in case API fails
        self.fallback_templates = FallbackTemplates()
    
    def generate(self, prompt: str, temperature: Optional[float] = None, 
                max_tokens: int = 256) -> str:
        """
        Generate text using Gemini API with fallback to templates.
        """
        try:
            # Use provided temperature or default
            current_temp = temperature if temperature is not None else self.temperature
            
            # Configure generation
            generation_config = genai.types.GenerationConfig(
                temperature=current_temp,
                top_p=0.95,
                top_k=40,
                max_output_tokens=max_tokens,
            )
            
            # Call Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract text from response
            if response and response.text:
                return response.text.strip()
            else:
                raise ValueError("Empty response from Gemini")
                
        except Exception as e:
            print(f"Gemini API error: {e}. Using fallback template.")
            # Fallback to template-based generation
            return self.fallback_templates.generate_from_prompt(prompt)
    
    def batch_generate(self, prompts: List[str], max_retries: int = 3) -> List[str]:
        """
        Generate multiple texts with rate limiting handling.
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            retries = 0
            while retries < max_retries:
                try:
                    result = self.generate(prompt)
                    results.append(result)
                    
                    # Small delay to avoid rate limits (Gemini is generous, but be safe)
                    if i % 10 == 0 and i > 0:
                        time.sleep(1)
                    
                    break
                    
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        print(f"Failed after {max_retries} retries for prompt {i}")
                        results.append(self.fallback_templates.generate_from_prompt(prompt))
                    else:
                        # Exponential backoff
                        time.sleep(2 ** retries)
        
        return results
    
    def generate_task_titles(self, project_type: str, count: int = 5, 
                           context: dict = None) -> List[str]:
        """
        Generate realistic task titles for a specific project type.
        """
        prompt = self._build_task_title_prompt(project_type, count, context)
        
        try:
            response = self.generate(prompt, temperature=0.9, max_tokens=300)
            
            # Parse response (assuming one title per line)
            titles = [line.strip() for line in response.split('\n') if line.strip()]
            
            # Filter out any markdown or numbering
            clean_titles = []
            for title in titles:
                # Remove numbering like "1.", "2.", etc.
                if title[0].isdigit() and (title[1] == '.' or title[1] == ')'):
                    title = title[2:].strip()
                elif title.startswith('- '):
                    title = title[2:].strip()
                
                clean_titles.append(title)
            
            return clean_titles[:count]
            
        except Exception as e:
            print(f"Error generating titles: {e}")
            return self.fallback_templates.generate_task_titles(project_type, count)
    
    def _build_task_title_prompt(self, project_type: str, count: int, 
                               context: dict = None) -> str:
        """Build prompt for task title generation"""
        
        prompt_templates = {
            'sprint': f"""
            Generate {count} realistic software engineering task titles for a sprint in a B2B SaaS company.
            
            Follow these patterns:
            1. [Component/Module] - [Action Verb] - [Specific Detail]
            2. [Component]: [Action] [Detail]
            3. [Action] [Component] for [Purpose]
            
            Examples:
            - "API Gateway - Implement - Rate limiting for enterprise tier"
            - "Authentication Service: Refactor OAuth 2.0 flow"
            - "Fix memory leak in image processing module"
            - "Mobile App: Optimize startup time on iOS"
            
            Project: {context.get('project_name', 'Platform Development')}
            Team: {context.get('team_name', 'Backend Engineering')}
            
            Generate {count} diverse and realistic task titles:
            """,
            
            'bug_tracking': f"""
            Generate {count} realistic bug report titles for a B2B SaaS company.
            
            Follow these patterns:
            1. [Component]: [Issue] when [Condition]
            2. Bug: [Specific problem] in [Module]
            3. Fix: [Issue] affecting [Feature]
            
            Examples:
            - "User Profile: Image upload fails for files > 10MB"
            - "Bug: Dashboard crashes when filtering by date range"
            - "Mobile: App freezes when switching between tabs offline"
            - "API: 500 error on POST /users endpoint with malformed JSON"
            
            Project: {context.get('project_name', 'Bug Fixing')}
            
            Generate {count} diverse and realistic bug titles:
            """,
            
            'campaign': f"""
            Generate {count} realistic marketing task titles for a B2B SaaS company.
            
            Follow these patterns:
            1. [Campaign] - [Deliverable] - [Channel]
            2. [Action] [Deliverable] for [Campaign]
            3. [Channel]: [Task] for [Audience]
            
            Examples:
            - "Q4 Launch - Landing page - Website"
            - "Create email sequence for webinar attendees"
            - "Social Media: Design carousel for product update"
            - "Case study: Enterprise customer success story"
            
            Campaign: {context.get('campaign_name', 'Q4 Marketing')}
            
            Generate {count} diverse and realistic marketing task titles:
            """,
            
            'okr': f"""
            Generate {count} realistic OKR-related task titles for a B2B SaaS company.
            
            Follow these patterns:
            1. [Metric]: [Action] to achieve [Target]
            2. [Objective] - [Key Result Initiative]
            3. Improve [Metric] by [Action]
            
            Examples:
            - "User Engagement: Implement push notifications to increase DAU by 15%"
            - "Revenue Growth - Launch enterprise pricing tier"
            - "Improve NPS score by streamlining onboarding flow"
            - "Customer Retention: Add feature usage analytics dashboard"
            
            Objective: {context.get('objective', 'Improve Product Metrics')}
            
            Generate {count} diverse and realistic OKR task titles:
            """
        }
        
        return prompt_templates.get(project_type, prompt_templates['sprint'])
    
    def generate_task_description(self, task_title: str, project_type: str) -> str:
        """
        Generate detailed task description.
        """
        prompt = f"""
        Write a detailed task description for a {project_type} project in a B2B SaaS company.
        
        Task: {task_title}
        
        Include the following sections in markdown format:
        1. Objective (1-2 sentences explaining the goal)
        2. Requirements (bullet points of technical/business requirements)
        3. Acceptance Criteria (bullet points of success metrics)
        4. Notes (optional, for additional context)
        
        Make it realistic, concise, and actionable. Use appropriate technical depth.
        
        Description:
        """
        
        try:
            return self.generate(prompt, temperature=0.7, max_tokens=500)
        except:
            return self.fallback_templates.generate_description(task_title)
    
    def generate_comment(self, task_title: str, comment_type: str = None) -> str:
        """
        Generate realistic comment for a task.
        """
        if not comment_type:
            comment_type = random.choice(['question', 'status', 'review', 'approval'])
        
        prompts = {
            'question': f"""
            Write a realistic question comment about this task in a project management tool:
            Task: {task_title}
            
            The comment should be:
            - Professional but conversational
            - Asking for clarification or information
            - 1-2 sentences maximum
            
            Example formats:
            "Can you clarify the requirements for this?"
            "Do we have design specs I should reference?"
            "What's the deadline for this task?"
            
            Comment:
            """,
            
            'status': f"""
            Write a realistic status update comment about this task in a project management tool:
            Task: {task_title}
            
            The comment should be:
            - Brief update on progress
            - Mention any blockers if relevant
            - Professional tone
            
            Example formats:
            "Working on this now, should be done by EOD."
            "Blocked on API access, waiting for the backend team."
            "Completed initial implementation, needs code review."
            
            Comment:
            """,
            
            'review': f"""
            Write a realistic code review comment about this task in a project management tool:
            Task: {task_title}
            
            The comment should be:
            - Constructive feedback
            - Technical but clear
            - Suggest improvements
            
            Example formats:
            "Can we add error handling for edge cases?"
            "Consider refactoring this method for better readability."
            "Tests are passing, but let's add one more edge case."
            
            Comment:
            """
        }
        
        prompt = prompts.get(comment_type, prompts['question'])
        
        try:
            return self.generate(prompt, temperature=0.8, max_tokens=150)
        except:
            return self.fallback_templates.generate_comment(task_title)


class FallbackTemplates:
    """Fallback template generator in case API fails"""
    
    def __init__(self):
        self.templates = TaskTemplates()
    
    def generate_from_prompt(self, prompt: str) -> str:
        """Generate text from prompt using templates"""
        if 'task title' in prompt.lower() or 'generate' in prompt.lower():
            # Extract project type from prompt
            for ptype in ['sprint', 'bug', 'campaign', 'marketing', 'okr']:
                if ptype in prompt.lower():
                    titles = self.generate_task_titles(ptype, 3)
                    return "\n".join(titles)
        
        return "Task details to be determined."
    
    def generate_task_titles(self, project_type: str, count: int) -> List[str]:
        return self.templates.get_titles(project_type, count)
    
    def generate_description(self, task_title: str) -> str:
        return self.templates.get_description()
    
    def generate_comment(self, task_title: str) -> str:
        return self.templates.get_comment()


class TaskTemplates:
    """Comprehensive template library for fallback"""
    
    def __init__(self):
        # Engineering task templates
        self.eng_components = ['API Gateway', 'Auth Service', 'Database', 'Frontend', 
                              'Mobile App', 'Backend API', 'Payment System', 'Notifications']
        self.eng_actions = ['Implement', 'Refactor', 'Fix', 'Optimize', 'Add', 'Update', 
                           'Migrate', 'Integrate', 'Secure', 'Test']
        self.eng_details = ['for enterprise customers', 'with improved performance', 
                           'using new framework', 'for better UX', 'with security fixes']
        
        # Bug templates
        self.bug_components = ['User Profile', 'Dashboard', 'Mobile App', 'API', 
                              'Payment Flow', 'Search', 'Notifications']
        self.bug_issues = ['crashes when', 'fails to load', 'shows error when', 
                          'is slow when', 'does not save', 'displays incorrectly']
        self.bug_conditions = ['offline', 'with large data', 'on mobile', 'after update', 
                              'with specific browser', 'under high load']
        
        # Marketing templates
        self.campaigns = ['Q4 Launch', 'Webinar', 'Product Update', 'Case Study', 
                         'Email Campaign', 'Social Media Blitz']
        self.deliverables = ['landing page', 'email sequence', 'social posts', 
                            'whitepaper', 'video', 'presentation']
    
    def get_titles(self, project_type: str, count: int) -> List[str]:
        if project_type in ['sprint', 'engineering']:
            return self._get_engineering_titles(count)
        elif project_type in ['bug_tracking', 'bug']:
            return self._get_bug_titles(count)
        elif project_type in ['campaign', 'marketing']:
            return self._get_marketing_titles(count)
        else:
            return self._get_general_titles(count)
    
    def _get_engineering_titles(self, count: int) -> List[str]:
        titles = []
        for _ in range(count):
            template = random.choice([
                f"{random.choice(self.eng_components)} - {random.choice(self.eng_actions)} - {random.choice(self.eng_details)}",
                f"{random.choice(self.eng_components)}: {random.choice(self.eng_actions)} {random.choice(self.eng_details)}",
                f"{random.choice(self.eng_actions)} {random.choice(self.eng_components).lower()} {random.choice(self.eng_details)}"
            ])
            titles.append(template)
        return titles
    
    def _get_bug_titles(self, count: int) -> List[str]:
        titles = []
        for _ in range(count):
            template = random.choice([
                f"Bug: {random.choice(self.bug_issues)} {random.choice(self.bug_conditions)}",
                f"{random.choice(self.bug_components)}: {random.choice(self.bug_issues)} {random.choice(self.bug_conditions)}",
                f"Fix {random.choice(self.bug_components).lower()} {random.choice(self.bug_issues)}"
            ])
            titles.append(template)
        return titles
    
    def _get_marketing_titles(self, count: int) -> List[str]:
        titles = []
        for _ in range(count):
            template = random.choice([
                f"{random.choice(self.campaigns)} - {random.choice(self.deliverables)}",
                f"Create {random.choice(self.deliverables)} for {random.choice(self.campaigns)}",
                f"Design {random.choice(self.deliverables)} for {random.choice(self.campaigns)} campaign"
            ])
            titles.append(template)
        return titles
    
    def _get_general_titles(self, count: int) -> List[str]:
        verbs = ['Complete', 'Review', 'Update', 'Prepare', 'Coordinate']
        nouns = ['project plan', 'documentation', 'report', 'analysis', 'proposal']
        return [f"{random.choice(verbs)} {random.choice(nouns)}" for _ in range(count)]
    
    def get_description(self) -> str:
        return "Complete this task as per requirements. See documentation for details."
    
    def get_comment(self) -> str:
        comments = [
            "Can you clarify the requirements?",
            "Working on this now.",
            "Completed, needs review.",
            "Blocked on dependencies.",
            "Ready for testing."
        ]
        return random.choice(comments)