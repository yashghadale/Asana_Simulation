import random
from datetime import datetime, timedelta
from typing import List, Dict
from ..models.base import Database, generate_gid
from ..utils.llm_client import GeminiClient
import os

class CommentGenerator:
    def __init__(self, use_gemini: bool = False):
        self.db = Database()
        self.use_gemini = use_gemini
        
        if self.use_gemini:
            try:
                self.gemini = GeminiClient()
            except:
                self.use_gemini = False
        
        # Comment templates for fallback
        self.comment_templates = {
            'question': [
                "Can you clarify the requirements for this?",
                "Do we have design specs I should reference?",
                "What's the deadline for this task?",
                "Who should I coordinate with on this?",
                "Are there any existing examples I should look at?",
                "What's the priority level for this?"
            ],
            'status': [
                "Working on this now.",
                "Started implementation.",
                "In progress - about {percent}% complete.",
                "Blocked on {blocker}. Waiting for {resolution}.",
                "Completed initial implementation. Needs review.",
                "Ready for QA testing.",
                "Deployed to staging environment.",
                "Found an issue: {issue}. Investigating.",
                "All tests passing locally.",
                "Documentation updated."
            ],
            'review': [
                "Looks good! Just one small suggestion: {suggestion}",
                "Can we add error handling for edge cases?",
                "Consider refactoring this for better readability.",
                "Tests are passing, but let's add one more edge case.",
                "Please add more comments for complex logic.",
                "Great work! Approved ✅"
            ],
            'approval': [
                "Approved!",
                "Looks good to me.",
                "✅ Approved - ready for merge.",
                "Approved with minor comments.",
                "LGTM (Looks Good To Me)"
            ],
            'discussion': [
                "Based on our discussion, I think we should {action}.",
                "Following up on our chat about {topic}.",
                "Per our conversation, I've updated {item}.",
                "As discussed in the meeting, {summary}."
            ]
        }
    
    def generate_comment_text(self, task_name: str, comment_type: str = None) -> str:
        """Generate comment text using Gemini or templates"""
        if not comment_type:
            comment_type = random.choice(['question', 'status', 'review', 'approval', 'discussion'])
        
        if self.use_gemini:
            try:
                return self.gemini.generate_comment(task_name, comment_type)
            except:
                pass  # Fall back to templates
        
        # Use templates
        template = random.choice(self.comment_templates[comment_type])
        
        # Format placeholders
        if '{percent}' in template:
            template = template.format(percent=random.randint(20, 90))
        elif '{blocker}' in template:
            blockers = ['API access', 'design approval', 'clarification', 'dependencies']
            resolutions = ['the API team', 'design', 'the PM', 'upstream teams']
            template = template.format(
                blocker=random.choice(blockers),
                resolution=random.choice(resolutions)
            )
        elif '{issue}' in template:
            issues = ['a race condition', 'memory leak', 'performance bottleneck']
            template = template.format(issue=random.choice(issues))
        elif '{suggestion}' in template:
            suggestions = ['use a more descriptive variable name', 'add null checks', 
                          'extract this into a helper function']
            template = template.format(suggestion=random.choice(suggestions))
        elif '{action}' in template:
            actions = ['proceed with option A', 'reconsider the approach', 'schedule a follow-up']
            template = template.format(action=random.choice(actions))
        elif '{topic}' in template:
            topics = ['the implementation approach', 'timeline concerns', 'technical details']
            template = template.format(topic=random.choice(topics))
        elif '{item}' in template:
            items = ['the requirements', 'the timeline', 'the acceptance criteria']
            template = template.format(item=random.choice(items))
        elif '{summary}' in template:
            summaries = ['we decided to proceed with the current approach',
                        'the deadline was extended by one week',
                        'we agreed to add more test coverage']
            template = template.format(summary=random.choice(summaries))
        
        return template
    
    def generate_comments(self, tasks: List[Dict], users: List[Dict]) -> List[Dict]:
        """Generate comments for tasks"""
        comments = []
        
        # Determine how many comments to generate
        total_comments = min(len(tasks) * 2, 1000)  # Max 1000 comments or 2 per task
        
        for _ in range(total_comments):
            task = random.choice(tasks)
            user = random.choice(users)
            
            # Generate comment timestamp (after task creation, before now if task not completed)
            task_created = datetime.fromisoformat(task['created_at'].replace('Z', '+00:00'))
            
            # If task is completed, comments should be before completion
            if task.get('completed_at'):
                task_completed = datetime.fromisoformat(task['completed_at'].replace('Z', '+00:00'))
                max_date = task_completed
            else:
                max_date = datetime.now()
            
            # Generate comment time (weighted toward recent after creation)
            days_after = random.triangular(0, (max_date - task_created).days, 3)
            comment_time = task_created + timedelta(days=days_after)
            
            # Ensure comment is during working hours (9 AM - 6 PM)
            hour = random.randint(9, 17)
            minute = random.randint(0, 59)
            comment_time = comment_time.replace(hour=hour, minute=minute, second=0)
            
            # Generate comment text
            comment_text = self.generate_comment_text(task['name'])
            
            comment = {
                'id': generate_gid(),
                'task_id': task['id'],
                'user_id': user['id'],
                'text': comment_text,
                'created_at': comment_time.isoformat(),
                'is_pinned': random.random() < 0.02  # 2% chance of being pinned
            }
            
            comments.append(comment)
        
        return comments