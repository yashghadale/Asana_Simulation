import random
from datetime import datetime, timedelta
from typing import List, Dict
from faker import Faker
from ..models.base import Database, generate_gid

fake = Faker()

class TeamGenerator:
    def __init__(self):
        self.db = Database()
        
        # Team name patterns (from actual Asana workspaces)
        self.team_patterns = {
            'engineering': [
                "Platform {noun}",
                "{adjective} Infrastructure",
                "{product} Engineering",
                "DevOps & {noun}",
                "Mobile {noun}"
            ],
            'product': [
                "{product} Product",
                "Growth {noun}",
                "User {noun}",
                "Product {noun}"
            ],
            'design': [
                "UX {noun}",
                "Design {noun}",
                "Product Design",
                "Creative {noun}"
            ],
            'marketing': [
                "Growth Marketing",
                "Content {noun}",
                "Demand Generation",
                "Brand {noun}"
            ],
            'sales': [
                "Enterprise Sales",
                "Sales {noun}",
                "Account Management",
                "Business Development"
            ],
            'operations': [
                "Business Operations",
                "People {noun}",
                "Finance {noun}",
                "Legal {noun}"
            ],
            'support': [
                "Customer Success",
                "Technical Support",
                "Customer {noun}",
                "Support {noun}"
            ]
        }
        
        self.adjectives = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Core', 'Strategic',
                          'Technical', 'Product', 'Growth', 'Revenue', 'Platform']
        self.nouns = ['Team', 'Squad', 'Group', 'Pod', 'Crew', 'Unit', 'Division']
        self.products = ['Enterprise', 'Platform', 'Mobile', 'Web', 'API', 'Cloud',
                        'Analytics', 'Dashboard', 'Workflow', 'Automation']
        
        # Team size distribution
        self.team_size_distribution = {
            3: 0.05,   # 5% tiny teams
            4: 0.10,   # 10% small
            5: 0.15,   # 15%
            6: 0.20,   # 20% (most common for agile teams)
            7: 0.15,   # 15%
            8: 0.12,   # 12%
            9: 0.10,   # 10%
            10: 0.08,  # 8%
            12: 0.05   # 5% large teams
        }
    
    def generate_team_name(self, department: str) -> str:
        """Generate realistic team name"""
        pattern = random.choice(self.team_patterns[department])
        
        replacements = {
            '{adjective}': random.choice(self.adjectives),
            '{noun}': random.choice(self.nouns),
            '{product}': random.choice(self.products)
        }
        
        for placeholder, value in replacements.items():
            pattern = pattern.replace(placeholder, value)
        
        return pattern
    
    def generate_teams(self, count: int = 30, org_id: str = None) -> List[Dict]:
        """Generate teams with realistic distributions"""
        if org_id is None:
            org_id = generate_gid()  # Default organization
        
        teams = []
        departments = list(self.team_patterns.keys())
        
        # Department distribution for teams
        dept_weights = [0.30, 0.15, 0.10, 0.20, 0.15, 0.05, 0.05]  # engineering-heavy
        
        for i in range(count):
            dept = random.choices(departments, weights=dept_weights)[0]
            
            # Fix: Calculate date manually instead of using Faker with invalid format
            now = datetime.now()
            eighteen_months_ago = now - timedelta(days=18*30)  # Approximate 18 months
            one_month_ago = now - timedelta(days=30)  # Approximate 1 month
            
            team = {
                'id': generate_gid(),
                'name': self.generate_team_name(dept),
                'description': fake.paragraph(nb_sentences=2),
                'organization_id': org_id,
                'department': dept,
                'created_at': fake.date_time_between(start_date=eighteen_months_ago, end_date=one_month_ago)
            }
            teams.append(team)
        
        return teams
    
    def assign_team_members(self, users: List[Dict], teams: List[Dict]) -> List[Dict]:
        """Assign users to teams with realistic patterns"""
        memberships = []
        
        # Get users by department for better matching
        users_by_dept = {}
        for user in users:
            dept = user['department']
            if dept not in users_by_dept:
                users_by_dept[dept] = []
            users_by_dept[dept].append(user)
        
        for team in teams:
            team_dept = team['department']
            
            # Determine team size
            size = random.choices(
                list(self.team_size_distribution.keys()),
                weights=list(self.team_size_distribution.values())
            )[0]
            
            # Get potential members (prefer same department, but allow cross-functional)
            potential_members = []
            if team_dept in users_by_dept:
                potential_members.extend(users_by_dept[team_dept])
            
            # Add some cross-functional members (20% of team)
            cross_functional_count = int(size * 0.2)
            for dept, dept_users in users_by_dept.items():
                if dept != team_dept:
                    potential_members.extend(random.sample(dept_users, 
                                                         min(2, len(dept_users))))
            
            # Shuffle and select team members
            if len(potential_members) == 0:
                continue  # Skip if no potential members
            
            selected_users = random.sample(potential_members, min(size, len(potential_members)))
            
            # Assign roles (1 team lead, rest members)
            for i, user in enumerate(selected_users):
                role = 'team_lead' if i == 0 else 'member'
                
                membership = {
                    'id': generate_gid(),
                    'team_id': team['id'],
                    'user_id': user['id'],
                    'role': role,
                    'joined_at': fake.date_time_between(
                        start_date=team['created_at'],
                        end_date='now'
                    )
                }
                memberships.append(membership)
        
        return memberships