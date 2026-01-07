"""
Template-based text generation without API calls.
"""
import random
from typing import List, Dict
from faker import Faker

fake = Faker()

class TextGenerator:
    """Generate realistic text using templates"""
    
    def __init__(self):
        # Task title templates
        self.engineering_templates = [
            "{component} - {action} - {detail}",
            "[{component}] {action}: {detail}",
            "{action} {component} {detail}",
            "Bug: {issue} in {component}"
        ]
        
        self.marketing_templates = [
            "{campaign} - {deliverable}",
            "{deliverable} for {campaign}",
            "{channel}: {action} for {campaign}"
        ]
        
        self.components = [
            'API Gateway', 'Authentication Service', 'Database Layer', 
            'Frontend Components', 'Mobile App', 'Backend API',
            'Payment Processing', 'Notification System', 'Search Engine'
        ]
        
        self.engineering_actions = [
            'Implement', 'Refactor', 'Optimize', 'Fix', 'Test',
            'Document', 'Upgrade', 'Migrate', 'Integrate', 'Deploy'
        ]
        
        self.marketing_actions = [
            'Create', 'Launch', 'Optimize', 'Analyze', 'Update',
            'Promote', 'Schedule', 'Review', 'Finalize'
        ]
        
        self.details = [
            'for enterprise customers', 'with improved performance',
            'using new framework', 'for better user experience',
            'with security enhancements', 'for mobile responsiveness'
        ]
        
        self.campaigns = [
            'Q4 Launch', 'Black Friday Sale', 'User Conference',
            'Webinar Series', 'Content Marketing'
        ]
        
        self.deliverables = [
            'landing page', 'email sequence', 'social media posts',
            'whitepaper', 'case study', 'video content'
        ]
    
    def generate_task_title(self, project_type: str, context: Dict = None) -> str:
        """Generate realistic task title"""
        if project_type in ['sprint', 'bug_tracking', 'engineering']:
            return self._generate_engineering_title()
        elif project_type == 'campaign':
            return self._generate_marketing_title()
        elif project_type == 'okr':
            return self._generate_okr_title()
        else:
            return self._generate_general_title()
    
    def _generate_engineering_title(self) -> str:
        """Generate engineering task title"""
        template = random.choice(self.engineering_templates)
        
        if 'component' in template:
            template = template.replace('{component}', random.choice(self.components))
        if 'action' in template:
            template = template.replace('{action}', random.choice(self.engineering_actions))
        if 'detail' in template:
            template = template.replace('{detail}', random.choice(self.details))
        if 'issue' in template:
            issues = ['memory leak', 'race condition', 'null pointer', 'performance issue']
            template = template.replace('{issue}', random.choice(issues))
        
        return template
    
    def _generate_marketing_title(self) -> str:
        """Generate marketing task title"""
        template = random.choice(self.marketing_templates)
        
        template = template.replace('{campaign}', random.choice(self.campaigns))
        template = template.replace('{deliverable}', random.choice(self.deliverables))
        if '{channel}' in template:
            template = template.replace('{channel}', random.choice(['Email', 'Social Media', 'Blog']))
        if '{action}' in template:
            template = template.replace('{action}', random.choice(self.marketing_actions))
        
        return template
    
    def _generate_okr_title(self) -> str:
        """Generate OKR-related task title"""
        objectives = ['Increase user engagement', 'Improve conversion rate', 'Reduce churn']
        metrics = ['DAU/MAU ratio', 'conversion rate', 'NPS score']
        actions = ['implement', 'optimize', 'redesign']
        
        templates = [
            "{objective}: {action} {metric}",
            "{metric} improvement for {objective}",
            "{action} {metric} to support {objective}"
        ]
        
        template = random.choice(templates)
        return template.format(
            objective=random.choice(objectives),
            metric=random.choice(metrics),
            action=random.choice(actions)
        )
    
    def _generate_general_title(self) -> str:
        """Generate general task title"""
        verbs = ['Complete', 'Review', 'Update', 'Prepare', 'Coordinate']
        nouns = ['project plan', 'meeting notes', 'status report', 'documentation']
        return f"{random.choice(verbs)} {random.choice(nouns)}"
    
    def generate_description(self, task_title: str) -> str:
        """Generate realistic task description"""
        # Distribution: 20% empty, 50% short, 30% detailed
        desc_type = random.choices(['empty', 'short', 'detailed'], 
                                  weights=[0.2, 0.5, 0.3])[0]
        
        if desc_type == 'empty':
            return None
        
        if desc_type == 'short':
            templates = [
                "Complete this task as per requirements.",
                "See attached specifications.",
                "Follow the standard procedure.",
                "Coordinate with team members as needed."
            ]
            return random.choice(templates)
        
        # Detailed description
        sections = []
        
        # Objective section
        objectives = [
            f"## Objective\nImplement {task_title.lower()} to improve system performance and user experience.",
            f"## Goal\nComplete {task_title.lower()} as part of ongoing platform improvements.",
            f"## Purpose\nAddress {task_title.lower()} to enhance user experience and system reliability."
        ]
        sections.append(random.choice(objectives))
        
        # Requirements (70% chance)
        if random.random() < 0.7:
            num_reqs = random.randint(2, 4)
            reqs = []
            for _ in range(num_reqs):
                req_templates = [
                    f"- Must support {random.randint(100, 1000)} concurrent users",
                    f"- Should be compatible with {random.choice(['all modern browsers', 'iOS/Android'])}",
                    f"- Needs to integrate with {random.choice(['Stripe', 'SendGrid', 'AWS'])}",
                    f"- Must follow {random.choice(['security', 'accessibility'])} guidelines"
                ]
                reqs.append(random.choice(req_templates))
            
            sections.append(f"## Requirements\n" + "\n".join(reqs))
        
        # Acceptance Criteria (60% chance)
        if random.random() < 0.6:
            num_criteria = random.randint(2, 3)
            criteria = []
            for _ in range(num_criteria):
                crit_templates = [
                    f"- All tests pass",
                    f"- Code review completed by 2 team members",
                    f"- Documentation updated in Confluence",
                    f"- No regression in existing functionality"
                ]
                criteria.append(random.choice(crit_templates))
            
            sections.append(f"## Acceptance Criteria\n" + "\n".join(criteria))
        
        return "\n\n".join(sections)