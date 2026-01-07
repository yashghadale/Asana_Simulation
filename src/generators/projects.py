import random
from datetime import datetime, timedelta
from typing import List, Dict
from faker import Faker
from ..models.base import Database, generate_gid

fake = Faker()

class ProjectGenerator:
    def __init__(self):
        self.db = Database()
        
        # Project name patterns by type
        self.project_patterns = {
            'sprint': [
                "{product} Sprint {number}",
                "{team} Sprint Planning",
                "Sprint: {feature} Implementation"
            ],
            'bug_tracking': [
                "{product} Bug Fixing",
                "Critical Bug Resolution",
                "{team} Bug Triage"
            ],
            'campaign': [
                "{campaign} Marketing Campaign",
                "Q{quarter} Marketing Initiatives",
                "{product} Launch Campaign"
            ],
            'okr': [
                "Q{quarter} OKRs - {objective}",
                "{department} OKR Tracking",
                "Annual Objective: {goal}"
            ],
            'ongoing': [
                "{product} Maintenance",
                "{team} Ongoing Work",
                "Continuous Improvement"
            ],
            'adhoc': [
                "{department} Ad-hoc Requests",
                "Urgent: {task}",
                "Special Project: {initiative}"
            ]
        }
        
        # Product names for a B2B SaaS company
        self.products = [
            'Enterprise Platform', 'Mobile App', 'Analytics Dashboard',
            'API Gateway', 'Admin Portal', 'Customer Portal',
            'Reporting Suite', 'Integration Hub', 'Automation Engine'
        ]
        
        self.teams = ['Platform', 'Mobile', 'Web', 'Backend', 'Frontend', 
                     'DevOps', 'Data', 'Security']
        
        self.campaigns = ['Q4 Launch', 'User Conference', 'Webinar Series',
                         'Product Hunt Launch', 'Enterprise Onboarding']
        
        self.departments = ['Engineering', 'Product', 'Marketing', 'Sales', 
                           'Customer Success', 'Operations']
        
        self.objectives = [
            'Increase User Engagement', 'Improve Conversion Rate',
            'Reduce Churn', 'Increase Revenue', 'Improve NPS Score'
        ]
        
        # Project status distribution
        self.status_distribution = {
            'active': 0.65,      # 65% active
            'completed': 0.25,   # 25% completed
            'on_hold': 0.08,     # 8% on hold
            'archived': 0.02     # 2% archived
        }
        
        # Project type distribution
        self.type_distribution = {
            'sprint': 0.35,      # 35% sprints
            'bug_tracking': 0.20, # 20% bug tracking
            'campaign': 0.15,    # 15% campaigns
            'okr': 0.10,         # 10% OKR tracking
            'ongoing': 0.15,     # 15% ongoing
            'adhoc': 0.05        # 5% ad-hoc
        }
        
        # Project color palette (Asana colors)
        self.colors = [
            'blue', 'green', 'orange', 'red', 'purple',
            'pink', 'lime', 'sky', 'grey', 'yellow'
        ]
    
    def generate_project_name(self, project_type: str) -> str:
        """Generate realistic project name"""
        pattern = random.choice(self.project_patterns[project_type])
        
        replacements = {
            '{product}': random.choice(self.products),
            '{team}': random.choice(self.teams),
            '{campaign}': random.choice(self.campaigns),
            '{department}': random.choice(self.departments),
            '{objective}': random.choice(self.objectives),
            '{goal}': fake.catch_phrase(),
            '{initiative}': fake.bs(),
            '{feature}': fake.word().title() + ' Feature',
            '{task}': fake.job(),
            '{number}': str(random.randint(1, 30)),
            '{quarter}': str(random.randint(1, 4))
        }
        
        name = pattern
        for placeholder, value in replacements.items():
            if placeholder in name:
                name = name.replace(placeholder, value)
                break
        
        return name
    
    def generate_projects(self, count: int, teams: List[Dict]) -> List[Dict]:
        """Generate realistic projects"""
        projects = []
        
        # Calculate date ranges
        now = datetime.now()
        eighteen_months_ago = now - timedelta(days=18*30)  # Approximate 18 months
        one_month_ago = now - timedelta(days=30)  # Approximate 1 month
        
        for i in range(count):
            # Select project type
            project_type = random.choices(
                list(self.type_distribution.keys()),
                weights=list(self.type_distribution.values())
            )[0]
            
            # Select team
            team = random.choice(teams)
            
            # Generate project dates - FIXED: Use calculated dates
            created_at = fake.date_time_between(start_date=eighteen_months_ago, end_date=one_month_ago)
            
            # Determine project status
            status = random.choices(
                list(self.status_distribution.keys()),
                weights=list(self.status_distribution.values())
            )[0]
            
            # Generate start and due dates based on status
            start_date = None
            due_date = None
            
            if status != 'archived':
                start_date = created_at.date()
                
                if status == 'completed':
                    # Completed projects have past due dates
                    due_date = start_date + timedelta(days=random.randint(7, 90))
                elif status == 'active':
                    # Active projects have future due dates
                    due_date = start_date + timedelta(days=random.randint(30, 180))
                elif status == 'on_hold':
                    # On-hold projects may or may not have due dates
                    if random.random() < 0.5:
                        due_date = start_date + timedelta(days=random.randint(60, 365))
            
            # Select project owner from team members
            team_members = self._get_team_members(team['id'])
            owner_id = random.choice(team_members)['user_id'] if team_members else None
            
            project = {
                'id': generate_gid(),
                'name': self.generate_project_name(project_type),
                'description': self._generate_description(project_type, team['name']),
                'team_id': team['id'],
                'owner_id': owner_id,
                'color': random.choice(self.colors),
                'is_public': random.random() < 0.3,  # 30% public
                'project_type': project_type,
                'status': status,
                'start_date': start_date.isoformat() if start_date else None,
                'due_date': due_date.isoformat() if due_date else None,
                'created_at': created_at.isoformat(),
                'updated_at': created_at.isoformat()
            }
            
            projects.append(project)
        
        return projects
    
    def generate_sections(self, project_id: str) -> List[Dict]:
        """Generate sections for a project"""
        sections = []
        
        # Standard sections for most projects
        standard_sections = [
            {'name': 'To Do', 'position': 1},
            {'name': 'In Progress', 'position': 2},
            {'name': 'In Review', 'position': 3},
            {'name': 'Done', 'position': 4}
        ]
        
        # Custom sections based on project type
        custom_sections = {
            'sprint': ['Backlog', 'This Sprint', 'Next Sprint', 'Icebox'],
            'bug_tracking': ['Triage', 'Investigating', 'Fixing', 'Testing', 'Verified'],
            'campaign': ['Ideation', 'Planning', 'Production', 'Launch', 'Analysis'],
            'okr': ['Planning', 'In Progress', 'At Risk', 'Completed', 'Archived'],
            'ongoing': ['Backlog', 'This Week', 'Next Week', 'Blocked', 'Completed']
        }
        
        # Select sections
        if random.random() < 0.7:  # 70% use standard sections
            selected_sections = standard_sections
        else:
            # Mix standard and custom
            selected_sections = standard_sections[:2]  # Keep To Do and In Progress
            project_type = self._get_project_type(project_id)
            if project_type in custom_sections:
                custom = random.sample(custom_sections[project_type], 2)
                for i, name in enumerate(custom, start=3):
                    selected_sections.append({'name': name, 'position': i})
        
        # Generate section records
        for section_data in selected_sections:
            section = {
                'id': generate_gid(),
                'name': section_data['name'],
                'project_id': project_id,
                'position': section_data['position'],
                'created_at': datetime.now().isoformat()
            }
            sections.append(section)
        
        return sections
    
    def _generate_description(self, project_type: str, team_name: str) -> str:
        """Generate project description"""
        # 20% chance of empty description
        if random.random() < 0.2:
            return None
        
        templates = [
            f"This project tracks {project_type.replace('_', ' ')} work for the {team_name} team.",
            f"Collaboration space for {team_name} team's {project_type.replace('_', ' ')} initiatives.",
            f"Manage and track all {project_type.replace('_', ' ')} tasks for {team_name}."
        ]
        
        description = random.choice(templates)
        
        # Add more detail 50% of the time
        if random.random() < 0.5:
            detail = f"\n\nObjectives:\n- {fake.sentence()}\n- {fake.sentence()}\n- {fake.sentence()}"
            description += detail
        
        return description
    
    def _get_team_members(self, team_id: str) -> List[Dict]:
        """Get members for a team"""
        sql = """
        SELECT user_id FROM team_memberships 
        WHERE team_id = ? 
        ORDER BY RANDOM() 
        LIMIT 10
        """
        return self.db.query(sql, (team_id,))
    
    def _get_project_type(self, project_id: str) -> str:
        """Get project type from database"""
        sql = "SELECT project_type FROM projects WHERE id = ?"
        result = self.db.query(sql, (project_id,))
        return result[0]['project_type'] if result else 'sprint'