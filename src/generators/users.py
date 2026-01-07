import random
from datetime import datetime, timedelta
from typing import List, Dict
from faker import Faker
import re

fake = Faker()

class UserGenerator:
    def __init__(self, company_domain: str = "example.com"):
        self.company_domain = company_domain
        
        # Realistic job titles by department
        self.job_titles = {
            'engineering': ['Software Engineer', 'Senior Software Engineer', 'Engineering Manager', 
                           'DevOps Engineer', 'QA Engineer', 'Frontend Developer', 'Backend Developer',
                           'Tech Lead', 'Principal Engineer', 'Engineering Director'],
            'product': ['Product Manager', 'Senior Product Manager', 'Product Owner', 
                       'Director of Product', 'Product Designer', 'Product Analyst', 'VP of Product'],
            'design': ['UX Designer', 'UI Designer', 'Product Designer', 'Design Manager',
                      'Creative Director', 'Visual Designer', 'Design Lead'],
            'marketing': ['Marketing Manager', 'Content Strategist', 'Growth Marketer',
                         'SEO Specialist', 'Social Media Manager', 'Marketing Director',
                         'Brand Manager', 'VP of Marketing'],
            'sales': ['Account Executive', 'Sales Development Rep', 'Sales Manager',
                     'Account Manager', 'Customer Success Manager', 'Sales Director',
                     'Business Development Manager', 'VP of Sales'],
            'operations': ['Operations Manager', 'Business Analyst', 'Project Manager',
                          'Operations Specialist', 'Operations Director', 'Process Manager',
                          'VP of Operations'],
            'support': ['Support Engineer', 'Technical Support', 'Customer Support Rep',
                       'Support Manager', 'Customer Success Specialist', 'Head of Support']
        }
        
        # Department distribution based on B2B SaaS benchmarks
        self.department_distribution = {
            'engineering': 0.35,  # 35% engineers
            'product': 0.10,      # 10% product
            'design': 0.08,       # 8% design
            'marketing': 0.15,    # 15% marketing
            'sales': 0.18,        # 18% sales
            'operations': 0.08,   # 8% operations
            'support': 0.06       # 6% support
        }
        
        # Role distribution (based on Asana permission patterns)
        self.role_distribution = {
            'owner': 0.02,    # 2% owners
            'admin': 0.08,    # 8% admins
            'member': 0.85,   # 85% members
            'guest': 0.05     # 5% guests
        }
    
    def generate_email(self, name: str, existing_emails: set = None) -> str:
        """Generate unique corporate email"""
        if existing_emails is None:
            existing_emails = set()
        
        # Clean the name
        name = name.strip()
        parts = name.split(' ', 1)
        if len(parts) == 2:
            first, last = parts
        else:
            first = parts[0]
            last = 'user'
        
        first = first.lower()
        last = last.lower()
        
        # Remove special characters
        first = re.sub(r'[^a-z]', '', first)
        last = re.sub(r'[^a-z]', '', last)
        
        if not last or len(last) < 2:
            last = 'user'
        
        email_patterns = [
            f"{first}.{last}",
            f"{first[0]}{last}",
            f"{first}_{last}",
            f"{first}{last[0]}",
            f"{first[0]}.{last}",
            f"{first}.{last[0]}",
        ]
        
        # Try patterns
        for pattern in email_patterns:
            email = f"{pattern}@{self.company_domain}"
            if email not in existing_emails:
                return email
        
        # If all patterns fail, add numbers
        import uuid
        for i in range(1, 1000):
            email = f"{first}.{last}{i}@{self.company_domain}"
            if email not in existing_emails:
                return email
        
        # Last resort
        return f"{first}.{uuid.uuid4().hex[:6]}@{self.company_domain}"
    
    def generate_users(self, count: int = 5000) -> List[Dict]:
        """Generate realistic users for B2B SaaS company"""
        users = []
        generated_emails = set()
        
        for i in range(count):
            # Generate unique name and email
            for attempt in range(5):  # Try 5 times
                # Generate name with realistic demographics
                region = random.choices(['us', 'india', 'uk', 'other'], 
                                       weights=[0.6, 0.2, 0.1, 0.1])[0]
                
                if region == 'us':
                    name = fake.name()
                elif region == 'india':
                    first_names = ['Arjun', 'Priya', 'Rahul', 'Sneha', 'Vikram', 'Anjali', 
                                  'Raj', 'Meera', 'Sanjay', 'Kavita', 'Amit', 'Deepak', 
                                  'Suresh', 'Neha', 'Pooja', 'Rohan']
                    last_names = ['Sharma', 'Patel', 'Kumar', 'Singh', 'Reddy', 'Gupta',
                                 'Mehta', 'Desai', 'Joshi', 'Nair', 'Verma', 'Yadav',
                                 'Shah', 'Choudhary', 'Mishra', 'Bose']
                    name = f"{random.choice(first_names)} {random.choice(last_names)}"
                elif region == 'uk':
                    name = fake.name()
                else:
                    # International names
                    name = fake.name()
                
                email = self.generate_email(name, generated_emails)
                if email not in generated_emails:
                    generated_emails.add(email)
                    break
            else:
                # If can't generate unique, use fallback
                import uuid
                name = f"User {i+1000}"
                email = f"user.{uuid.uuid4().hex[:8]}@{self.company_domain}"
                generated_emails.add(email)
            
            # Determine department
            dept = random.choices(
                list(self.department_distribution.keys()),
                weights=list(self.department_distribution.values())
            )[0]
            
            # Job title based on department and seniority
            seniority = random.choices(['junior', 'mid', 'senior', 'lead'], 
                                      weights=[0.25, 0.40, 0.25, 0.10])[0]
            
            # Get available titles for this department
            dept_titles = self.job_titles.get(dept, ['Team Member'])
            
            if seniority == 'junior':
                title = dept_titles[0] if dept_titles else 'Team Member'
            elif seniority == 'mid':
                title = random.choice(dept_titles[:min(3, len(dept_titles))]) if dept_titles else 'Team Member'
            elif seniority == 'senior':
                base_title = random.choice(dept_titles) if dept_titles else 'Team Member'
                title = f"Senior {base_title}"
            else:  # lead/manager
                # Filter for leadership titles
                leadership_titles = [t for t in dept_titles if any(word in t for word in ['Manager', 'Lead', 'Director', 'Head', 'VP'])]
                if leadership_titles:
                    title = random.choice(leadership_titles)
                else:
                    title = f"{dept.title()} Lead"
            
            # Determine role
            role = random.choices(
                list(self.role_distribution.keys()),
                weights=list(self.role_distribution.values())
            )[0]
            
            # Generate GID for Asana compatibility
            import uuid
            gid = str(uuid.uuid4())[:16]  # Simplified GID format
            
            # Create user
            user = {
                'id': gid,
                'name': name,
                'email': email,
                'role': role,
                'department': dept,
                'job_title': title,
                'timezone': random.choice(['America/New_York', 'America/Los_Angeles', 
                                          'Europe/London', 'Asia/Kolkata', 'UTC']),
                'created_at': fake.date_time_between(start_date='-2y', end_date='now').isoformat(),
                'last_active': fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
                'is_active': random.choices([True, False], weights=[0.95, 0.05])[0]
            }
            
            users.append(user)
        
        return users
    
    def save_users(self, users: List[Dict]):
        """Save users to database"""
        from src.models.base import Database
        db = Database()
        db.insert_many('users', users)
        print(f"Saved {len(users)} users to database")