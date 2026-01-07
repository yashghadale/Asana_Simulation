import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import numpy as np
from ..models.base import Database, generate_gid
from ..utils.text_generator import TextGenerator
import os

class TaskGenerator:
    def __init__(self, use_gemini: bool = False):
        self.db = Database()
        self.text_gen = TextGenerator()
        
        # REAL engineering components (from actual SaaS companies)
        self.engineering_components = [
            "Authentication Service", "Payment Gateway", "Checkout API", 
            "User Dashboard", "Mobile App (iOS)", "Mobile App (Android)",
            "Admin Portal", "Database Layer", "Email Service", 
            "Notification System", "Analytics Pipeline", "Search Index",
            "File Upload Service", "Real-time Chat", "Reporting Engine",
            "CI/CD Pipeline", "Kubernetes Cluster", "Monitoring Stack",
            "API Gateway", "Message Queue", "Cache Layer"
        ]
        
        # REAL engineering actions
        self.engineering_actions = [
            "Fix", "Implement", "Optimize", "Refactor", "Migrate",
            "Add", "Remove", "Update", "Secure", "Test",
            "Document", "Deploy", "Monitor", "Scale", "Backup"
        ]
        
        # REAL engineering issues
        self.engineering_issues = [
            "memory leak", "race condition", "deadlock", "null pointer",
            "performance bottleneck", "security vulnerability", "data corruption",
            "connection timeout", "resource exhaustion", "dependency conflict"
        ]
        
        # REAL marketing campaigns
        self.marketing_campaigns = [
            "Q3 Product Launch", "Enterprise Sales Push", "Holiday Season Promo",
            "User Conference 2024", "Partner Program Expansion", "Competitive Analysis",
            "Customer Success Stories", "Social Media Blitz", "Email Newsletter Series",
            "SEO Optimization Sprint", "Analytics Dashboard Redesign"
        ]
        
        # REAL marketing deliverables
        self.marketing_deliverables = [
            "landing page", "email sequence", "social media calendar",
            "case study", "whitepaper", "video tutorial",
            "sales deck", "product demo", "blog post series",
            "webinar", "press release", "customer testimonial"
        ]
        
        # REAL operations tasks
        self.operations_tasks = [
            "vendor contract renewal", "budget planning Q3", "team offsite planning",
            "OKR review meeting", "compliance audit preparation", "security training",
            "tool evaluation", "process documentation", "risk assessment",
            "capacity planning", "disaster recovery test"
        ]
        
        # Due date distribution (REALISTIC - based on industry benchmarks)
        self.due_date_distribution = [
            (3, 0.15),     # 15% within 3 days (urgent)
            (7, 0.30),     # 30% within 1 week
            (14, 0.25),    # 25% within 2 weeks (sprints)
            (30, 0.20),    # 20% within 1 month
            (60, 0.07),    # 7% within 2 months
            (None, 0.03)   # 3% no due date
        ]
        
        # Priority distribution (REALISTIC)
        self.priority_distribution = {
            'urgent': 0.05,   # 5% urgent (P0)
            'high': 0.15,     # 15% high (P1)
            'medium': 0.60,   # 60% medium (P2)
            'low': 0.20       # 20% low (P3)
        }
        
        # Effort (story points) distribution
        self.effort_distribution = {
            1: 0.30,   # 30% trivial
            2: 0.25,   # 25% small  
            3: 0.20,   # 20% medium
            5: 0.15,   # 15% large
            8: 0.08,   # 8% very large
            10: 0.02   # 2% epic
        }
        
        # Project type completion rates (based on Asana benchmarks)
        self.completion_rates = {
    'sprint': 0.85,      # 85% complete (was 78%)
    'bug_tracking': 0.75, # 75% complete (was 65%)
    'campaign': 0.80,     # 80% complete (was 70%)
    'okr': 0.70,         # 70% complete (was 60%)
    'ongoing': 0.60,     # 60% complete (was 45%)
    'adhoc': 0.65        # 65% complete (was 55%)
}
    
    def _generate_engineering_detail(self, component: str) -> str:
        """Generate specific engineering detail"""
        details = {
            "Authentication Service": [
                "OAuth 2.0 for enterprise SSO",
                "MFA with biometric support",
                "Session management for mobile",
                "JWT token rotation",
                "Passwordless login flow"
            ],
            "Payment Gateway": [
                "Stripe integration for EU",
                "PCI compliance audit",
                "Failed payment retry logic",
                "Subscription billing cycles",
                "Tax calculation for 50+ countries"
            ],
            "Checkout API": [
                "cart persistence for 30 days",
                "coupon code validation",
                "shipping rate calculation",
                "inventory reservation system",
                "order confirmation emails"
            ],
            "Database Layer": [
                "query optimization for reports",
                "connection pooling setup",
                "backup automation to S3",
                "index optimization",
                "read replica failover"
            ]
        }
        
        return random.choice(details.get(component, [
            "performance improvement",
            "security enhancement",
            "scalability upgrade",
            "monitoring integration"
        ]))
    
    def _generate_engineering_description(self, component: str, action: str, detail: str) -> str:
        """Generate REAL engineering description"""
        objectives = [
            f"## Objective\n{action.lower()} {component} to {detail}\n\n## Acceptance Criteria\n- [ ] Code review completed\n- [ ] Unit tests passing (>90% coverage)\n- [ ] Integration tests added\n- [ ] Performance benchmarks met\n- [ ] Documentation updated\n\n## Implementation Notes\nFocus on maintainability and scalability. Coordinate with QA team for testing.",
            f"### Background\nCurrent {component} needs {action.lower()} for {detail}\n\n### Requirements\n1. Design review with architecture team\n2. Implement with proper error handling\n3. Add comprehensive logging\n4. Performance testing required\n5. Rollout plan with feature flag\n\n### Success Metrics\n- Latency < 100ms\n- 99.9% availability\n- Zero regressions",
            f"**Goal**: {action} {component} - {detail}\n\n**Technical Requirements**:\n- Use established patterns from codebase\n- Follow security best practices\n- Implement proper monitoring\n- Include rollback procedure\n\n**Dependencies**:\n- Team: Backend Engineering\n- Tools: Jenkins, Datadog\n- Timeline: 3-5 days"
        ]
        
        return random.choice(objectives)
    
    def _generate_bug_description(self, component: str, issue: str) -> str:
        """Generate REAL bug description"""
        descriptions = [
            f"## Bug Report: {issue} in {component}\n\n**Severity**: {'P0 - Critical' if random.random() < 0.3 else 'P1 - High'}\n\n**Steps to Reproduce**:\n1. Navigate to {random.choice(['checkout', 'dashboard', 'settings'])}\n2. Perform {random.choice(['rapid clicks', 'concurrent requests', 'large data input'])}\n3. Observe {random.choice(['error 500', 'memory spike', 'UI freeze'])}\n\n**Expected Behavior**:\nSystem should handle the condition gracefully\n\n**Actual Behavior**:\n{random.choice(['Crash with stack trace', 'Memory leak 2GB/hour', 'CPU at 100%'])}\n\n**Environment**:\n- Version: v2.{random.randint(1, 15)}.{random.randint(0, 9)}\n- Browser: Chrome {random.randint(90, 120)}\n- OS: {random.choice(['macOS 14', 'Windows 11', 'Ubuntu 22.04'])}",
            f"### Issue: {issue.upper()}\n**Component**: {component}\n**Priority**: {'URGENT' if random.random() < 0.2 else 'HIGH'}\n\n**Description**:\nCustomers reporting {random.choice(['failed transactions', 'slow page loads', 'data loss'])} when using {component}.\n\n**Impact**:\n- Affects {random.randint(5, 50)}% of users\n- {random.choice(['Blocks checkout', 'Prevents login', 'Corrupts data'])}\n- Business impact: ${random.randint(1000, 50000)}/day\n\n**Root Cause Analysis**:\nSuspected {random.choice(['race condition', 'memory leak', 'database deadlock'])} in {random.choice(['cache layer', 'API endpoint', 'background job'])}.\n\n**Fix Required By**:\n{random.choice(['EOD today', 'Next release (Friday)', 'Within 48 hours'])}"
        ]
        
        return random.choice(descriptions)
    
    def _generate_marketing_description(self, campaign: str, deliverable: str) -> str:
        """Generate REAL marketing description"""
        descriptions = [
            f"## Campaign: {campaign}\n**Deliverable**: {deliverable}\n\n**Target Audience**:\n- {random.choice(['Enterprise decision makers', 'SMB owners', 'Developers', 'Marketing managers'])}\n- Geography: {random.choice(['North America', 'EMEA', 'APAC', 'Global'])}\n\n**Key Messages**:\n1. {random.choice(['Increase productivity by 40%', 'Reduce costs by 30%', 'Improve team collaboration'])}\n2. {random.choice(['Easy integration with existing tools', 'Enterprise-grade security', '24/7 customer support'])}\n\n**Success Metrics**:\n- {random.randint(100, 1000)} leads generated\n- CTR > {random.randint(2, 5)}%\n- Conversion rate > {random.randint(1, 3)}%\n\n**Timeline**:\n- Draft: {random.randint(1, 3)} days\n- Review: 2 days\n- Final: 1 day",
            f"### {deliverable.title()} for {campaign}\n\n**Purpose**:\nCreate engaging content that demonstrates {random.choice(['product value', 'customer success', 'technical superiority'])}.\n\n**Content Requirements**:\n- Tone: {random.choice(['Professional yet approachable', 'Technical but accessible', 'Inspirational and data-driven'])}\n- Length: {random.choice(['500-800 words', '3-5 minute video', '10-15 slides'])}\n- Call to action: {random.choice(['Schedule a demo', 'Start free trial', 'Download whitepaper'])}\n\n**Brand Guidelines**:\n- Use brand colors (#1A56DB, #FF6B6B)\n- Include customer logos\n- Follow voice & tone guide\n\n**Deadline**:\n{random.choice(['Friday EOD', 'Next Tuesday', 'End of month'])}"
        ]
        
        return random.choice(descriptions)
    
    def _generate_operations_description(self, task: str, quarter: str) -> str:
        """Generate REAL operations description"""
        return f"""## Operations Task: {task}
**Quarter**: {quarter} 2024

**Context**:
This task supports {random.choice(['business continuity', 'regulatory compliance', 'team efficiency', 'cost optimization'])}.

**Scope**:
- {random.choice(['Review all vendor contracts', 'Document current processes', 'Assess security risks', 'Plan team capacity'])}
- {random.choice(['Identify cost savings opportunities', 'Streamline approval workflows', 'Improve communication channels', 'Enhance reporting'])}
- {random.choice(['Implement tracking mechanisms', 'Establish KPIs', 'Create documentation', 'Train team members'])}

**Stakeholders**:
- {random.choice(['Finance team', 'Legal department', 'Engineering leads', 'HR partners'])}
- {random.choice(['Department heads', 'Executive team', 'External auditors', 'Vendor partners'])}

**Success Criteria**:
- Completed by {random.choice(['quarter end', 'fiscal year end', 'next board meeting'])}
- {random.choice(['100% compliance', '20% efficiency gain', '$50K cost reduction', 'Zero audit findings'])}

**Timeline**:
Week 1: Research & planning
Week 2: Execution
Week 3: Review & adjustments
Week 4: Documentation & handoff"""
    
    def generate_task_title(self, project_type: str, context: Dict = None) -> str:
        """Generate REAL task title based on project type"""
        department = context.get('team_department', 'engineering') if context else 'engineering'
        
        if project_type == 'bug_tracking':
            component = random.choice(self.engineering_components)
            issue = random.choice(self.engineering_issues)
            priority = random.choices(['urgent', 'high', 'medium'], weights=[0.3, 0.5, 0.2])[0]
            return f"{priority.upper()}: Fix {issue} in {component}"
        
        elif project_type == 'campaign':
            campaign = random.choice(self.marketing_campaigns)
            deliverable = random.choice(self.marketing_deliverables)
            return f"{campaign}: Create {deliverable}"
        
        elif project_type in ['okr', 'ongoing', 'adhoc']:
            if department == 'engineering':
                component = random.choice(self.engineering_components)
                action = random.choice(self.engineering_actions)
                detail = self._generate_engineering_detail(component)
                return f"{component} - {action} - {detail}"
            elif department == 'marketing':
                campaign = random.choice(self.marketing_campaigns[:3])  # Top 3 campaigns
                return f"{campaign}: {random.choice(['Performance review', 'Budget planning', 'Metrics analysis'])}"
            elif department == 'operations':
                task = random.choice(self.operations_tasks)
                quarter = random.choice(['Q1', 'Q2', 'Q3', 'Q4'])
                return f"{quarter}: {task}"
            else:
                # Generic but realistic
                verbs = ['Complete', 'Review', 'Update', 'Prepare', 'Analyze']
                nouns = ['monthly report', 'team metrics', 'project plan', 'budget forecast', 'risk assessment']
                return f"{random.choice(verbs)} {random.choice(nouns)}"
        
        elif project_type == 'sprint':
            if department == 'engineering':
                component = random.choice(self.engineering_components)
                action = random.choice(['Implement', 'Fix', 'Optimize', 'Test', 'Refactor'])
                detail = random.choice([
                    f"for {random.choice(['mobile', 'enterprise', 'performance'])}",
                    f"with {random.randint(2, 8)} point estimate",
                    f"as part of sprint {random.randint(1, 10)}"
                ])
                return f"{component}: {action} {detail}"
            else:
                return f"Sprint {random.randint(1, 10)}: {random.choice(['Deliverable review', 'Retrospective planning', 'Demo preparation'])}"
        
        # Fallback - still realistic
        domains = ['API', 'Database', 'UI', 'Infrastructure', 'Security', 'Testing']
        actions = ['Update', 'Improve', 'Fix', 'Add', 'Remove', 'Optimize']
        targets = ['performance', 'security', 'usability', 'reliability', 'scalability']
        
        return f"{random.choice(domains)}: {random.choice(actions)} {random.choice(targets)}"
    
    def generate_description(self, task_title: str, project_type: str) -> str:
        """Generate REAL description based on task title and type"""
        # Extract components from title for more relevant description
        title_lower = task_title.lower()
        
        if any(keyword in title_lower for keyword in ['fix', 'bug', 'error', 'issue', 'memory', 'crash']):
            component = next((c for c in self.engineering_components if c.lower() in title_lower), 
                           random.choice(self.engineering_components))
            issue = next((i for i in self.engineering_issues if i in title_lower), 
                        random.choice(self.engineering_issues))
            return self._generate_bug_description(component, issue)
        
        elif any(keyword in title_lower for keyword in ['campaign', 'marketing', 'social', 'email', 'content']):
            campaign = next((c for c in self.marketing_campaigns if c.lower() in title_lower), 
                          random.choice(self.marketing_campaigns))
            deliverable = next((d for d in self.marketing_deliverables if d in title_lower), 
                             random.choice(self.marketing_deliverables))
            return self._generate_marketing_description(campaign, deliverable)
        
        elif any(keyword in title_lower for keyword in ['q1', 'q2', 'q3', 'q4', 'quarter', 'budget', 'vendor']):
            quarter = next((q for q in ['Q1', 'Q2', 'Q3', 'Q4'] if q in task_title), 'Q3')
            task = next((t for t in self.operations_tasks if t in title_lower), 
                       random.choice(self.operations_tasks))
            return self._generate_operations_description(task, quarter)
        
        # Generic but detailed description
        templates = [
            f"""## Task: {task_title}

**Objective**:
{random.choice([
    'Improve system performance and reliability',
    'Enhance user experience and engagement',
    'Increase operational efficiency and reduce costs',
    'Strengthen security posture and compliance'
])}

**Scope**:
- {random.choice(['Design and implement solution', 'Conduct research and analysis', 'Create documentation and training materials'])}
- {random.choice(['Test across all supported platforms', 'Validate with stakeholders', 'Measure impact and results'])}
- {random.choice(['Deploy to production environment', 'Train team members', 'Update related documentation'])}

**Success Criteria**:
- {random.choice(['90%+ user satisfaction', '20% performance improvement', 'Zero regressions', 'On-time delivery'])}
- {random.choice(['All tests passing', 'Documentation complete', 'Stakeholder sign-off', 'Metrics tracked'])}

**Timeline**:
- Estimated effort: {random.randint(2, 10)} days
- Start: {random.choice(['Immediately', 'Next sprint', 'After dependencies clear'])}
- Target completion: {random.choice(['End of week', 'Month-end', 'Next release'])}""",
            
            f"""### {task_title}

**Background**:
This work supports our {random.choice(['Q3 objectives', 'product roadmap', 'team goals', 'customer commitments'])}.

**Requirements**:
1. {random.choice(['Follow established patterns', 'Use approved tools and frameworks', 'Adhere to security guidelines'])}
2. {random.choice(['Coordinate with dependent teams', 'Communicate progress regularly', 'Document decisions and rationale'])}
3. {random.choice(['Test thoroughly before deployment', 'Measure impact post-deployment', 'Gather feedback from users'])}

**Dependencies**:
- {random.choice(['Design assets from UX team', 'API specifications from backend', 'Content from marketing'])}
- {random.choice(['Approval from legal/compliance', 'Budget allocation from finance', 'Resources from operations'])}

**Risks & Mitigations**:
- Risk: {random.choice(['Timeline delays', 'Scope creep', 'Technical debt'])}
- Mitigation: {random.choice(['Regular check-ins', 'Clear requirements', 'Phased delivery'])}"""
        ]
        
        return random.choice(templates)
    
    def generate_due_date(self, created_at: datetime, project_type: str) -> datetime:
        """Generate REALISTIC due date (FIXED overdue rate)"""
        # Adjust distribution based on project type
        if project_type == 'sprint':
            adjusted_distribution = [
                (7, 0.60),   # 60% within sprint (1 week)
                (14, 0.30),  # 30% 2 weeks
                (30, 0.08),  # 8% next sprint
                (None, 0.02) # 2% no due date
            ]
        elif project_type == 'bug_tracking':
            adjusted_distribution = [
                (1, 0.40),   # 40% within 1 day (urgent bugs)
                (3, 0.35),   # 35% within 3 days
                (7, 0.20),   # 20% within 1 week
                (None, 0.05) # 5% no due date
            ]
        else:
            adjusted_distribution = self.due_date_distribution
        
        choice = random.choices(
            [d[0] for d in adjusted_distribution],
            weights=[d[1] for d in adjusted_distribution]
        )[0]
        
        if choice is None:
            return None
        
        # Use realistic distribution (not uniform)
        if random.random() < 0.7:
            # Most tasks due soon
            due_days = int(random.triangular(1, choice, choice * 0.3))
        else:
            # Some tasks due later
            due_days = random.randint(int(choice * 0.5), choice)
        
        due_date = created_at + timedelta(days=due_days)
        
        # Avoid weekends for business tasks
        if project_type not in ['bug_tracking', 'adhoc']:
            while due_date.weekday() >= 5:  # Saturday or Sunday
                due_date += timedelta(days=1)
        
        # Ensure due date is in the future (not overdue in generation)
        # Only 10% should be overdue
        if random.random() < 0.1 and created_at > datetime.now() - timedelta(days=30):
            overdue_days = random.randint(1, 14)
            due_date = created_at - timedelta(days=overdue_days)
        else:
            # Ensure due date is in the future (not overdue)
            if due_date and due_date < datetime.now():
                # Reschedule to future
                due_date = datetime.now() + timedelta(days=random.randint(1, 30))
        
        return due_date
    
    def generate_completion_info(self, created_at: datetime, due_date: datetime, 
                               project_type: str) -> Tuple[bool, datetime]:
        """Generate completion status with REALISTIC patterns"""
        # Base completion probability
        base_rate = self.completion_rates.get(project_type, 0.65)
        
        # Adjust based on time factors
        adjustment = 1.0
        
        if due_date:
            now = datetime.now()
            if due_date < now:  # Overdue
                days_overdue = (now - due_date).days
                if days_overdue > 60:
                    adjustment = 0.3  # Very low chance if long overdue
                elif days_overdue > 30:
                    adjustment = 0.5
                elif days_overdue > 7:
                    adjustment = 0.7
                else:
                    adjustment = 0.8  # Slightly reduced for recent overdue
            else:  # Not yet due
                days_remaining = (due_date - now).days
                if days_remaining > 30:
                    adjustment = 0.8  # Less urgency
                elif days_remaining > 7:
                    adjustment = 1.0
                elif days_remaining > 3:
                    adjustment = 1.2  # More urgency
                else:
                    adjustment = 1.5  # High urgency
        
        completion_prob = base_rate * adjustment
        
        # Add random variation
        completion_prob *= random.uniform(0.9, 1.1)
        completion_prob = max(0.1, min(0.95, completion_prob))
        
        is_completed = random.random() < completion_prob
        
        if not is_completed:
            return False, None
        
        # Generate realistic completion time
        if due_date:
            # Most tasks complete around due date
            if due_date > created_at:
                days_to_complete = (due_date - created_at).days
                # Some complete early, some late
                if random.random() < 0.7:  # 70% complete on time or early
                    actual_days = int(random.triangular(1, days_to_complete, days_to_complete * 0.7))
                else:  # 30% complete late
                    actual_days = days_to_complete + random.randint(1, 7)
            else:  # Overdue task completing
                actual_days = random.randint(1, 14)  # Quick fix for overdue
        else:
            # No due date - lognormal distribution
            actual_days = max(1, int(np.random.lognormal(mean=2.0, sigma=0.6)))
        
        completed_at = created_at + timedelta(days=min(actual_days, 180))
        
        # Ensure completion is before now and after creation
        completed_at = min(completed_at, datetime.now())
        completed_at = max(completed_at, created_at + timedelta(hours=1))
        
        return True, completed_at
    
    def _generate_created_at(self, project_created_str: str) -> datetime:
        """Generate realistic creation timestamp - FIXED version"""
        # Convert project_created from string to datetime
        if isinstance(project_created_str, str):
            try:
                project_created = datetime.fromisoformat(project_created_str.replace('Z', '+00:00'))
            except:
                project_created = datetime.now() - timedelta(days=180)
        else:
            project_created = project_created_str
        
        # Tasks are created after project creation
        days_since_project = (datetime.now() - project_created).days
        
        if days_since_project <= 0:
            return project_created
        
        # More tasks created recently
        days_ago = min(days_since_project, 
                      int(np.random.exponential(scale=days_since_project * 0.3)))
        
        created_at = datetime.now() - timedelta(days=days_ago)
        
        # Adjust to working hours (9 AM - 6 PM, Mon-Fri)
        hour = random.randint(9, 17)
        minute = random.randint(0, 59)
        
        created_at = created_at.replace(hour=hour, minute=minute, second=0)
        
        # Ensure it's a weekday (85% of tasks)
        if random.random() < 0.85:
            while created_at.weekday() >= 5:
                created_at -= timedelta(days=1)
        
        return created_at
    
    def _get_team_members(self, team_id: str) -> List[Dict]:
        """Get members for a team from database"""
        sql = """
        SELECT u.* FROM users u
        JOIN team_memberships tm ON u.id = tm.user_id
        WHERE tm.team_id = ?
        """
        return self.db.query(sql, (team_id,))
    
    def _get_team_name(self, team_id: str) -> str:
        """Get team name from database"""
        sql = "SELECT name FROM teams WHERE id = ?"
        result = self.db.query(sql, (team_id,))
        return result[0]['name'] if result else "Engineering"
    
    def _get_team_department(self, team_id: str) -> str:
        """Get department for a team from database"""
        sql = "SELECT department FROM teams WHERE id = ?"
        result = self.db.query(sql, (team_id,))
        return result[0]['department'] if result else 'engineering'
    
    def _select_assignee(self, team_members: List[Dict]) -> str:
        """Select assignee with realistic distribution"""
        # 15% unassigned (Asana benchmark)
        if random.random() < 0.15 or not team_members:
            return None
        
        # Pareto distribution: 20% of users do 80% of work
        if random.random() < 0.8:
            # Select from top 20% active users
            active_users = [m for m in team_members if m.get('is_active', True)]
            if not active_users:
                return None
            
            top_users = active_users[:max(1, len(active_users) // 5)]
            return random.choice(top_users)['id']
        else:
            # Select from all users
            return random.choice(team_members)['id']
    
    def generate_tasks(self, projects: List[Dict], sections: List[Dict], 
                      users: List[Dict], count_per_project: int = 20) -> List[Dict]:
        """Generate REALISTIC tasks for all projects"""
        all_tasks = []
        
        for project in projects:
            # Get project-specific sections
            project_sections = [s for s in sections if s['project_id'] == project['id']]
            if not project_sections:
                continue
            
            # Get team members for this project
            team_members = self._get_team_members(project['team_id'])
            if not team_members:
                continue
            
            # Get team department for realistic task generation
            team_dept = self._get_team_department(project['team_id'])
            
            # Determine task count for this project (varied)
            task_count = random.randint(int(count_per_project * 0.7), 
                                       int(count_per_project * 1.3))
            
            for i in range(task_count):
                # Create task with realistic attributes
                created_at = self._generate_created_at(project['created_at'])
                
                # Generate REAL task title and description
                context = {
                    'project_name': project['name'],
                    'team_name': self._get_team_name(project['team_id']),
                    'team_department': team_dept
                }
                
                task_title = self.generate_task_title(project['project_type'], context)
                
                task = {
                    'id': generate_gid(),
                    'name': task_title,
                    'description': self.generate_description(task_title, project['project_type']),
                    'project_id': project['id'],
                    'section_id': random.choice(project_sections)['id'],
                    'assignee_id': self._select_assignee(team_members),
                    'parent_task_id': None,
                    'due_date': None,
                    'due_time': random.choice([None, '09:00', '14:00', '17:00']),
                    'start_date': created_at.date().isoformat() if random.random() < 0.3 else None,
                    'completed': False,
                    'completed_at': None,
                    'created_at': created_at.isoformat(),
                    'updated_at': created_at.isoformat(),
                    'priority': random.choices(
                        list(self.priority_distribution.keys()),
                        weights=list(self.priority_distribution.values())
                    )[0],
                    'effort': random.choices(
                        list(self.effort_distribution.keys()),
                        weights=list(self.effort_distribution.values())
                    )[0] if random.random() < 0.7 else None,
                    'is_blocked': random.random() < 0.08,  # 8% blocked (realistic)
                    'blocked_reason': random.choice([
                        'Waiting on design assets',
                        'Blocked by external API',
                        'Need product clarification',
                        'Dependent on other team',
                        'Technical debt cleanup needed'
                    ]) if random.random() < 0.08 else None
                }
                
                # Generate due date
                due_date = self.generate_due_date(created_at, project['project_type'])
                if due_date:
                    task['due_date'] = due_date.date().isoformat()
                
                # Generate completion info
                task['completed'], completed_at = self.generate_completion_info(
                    created_at, due_date, project['project_type']
                )
                
                if task['completed'] and completed_at:
                    task['completed_at'] = completed_at.isoformat()
                    task['updated_at'] = completed_at.isoformat()
                
                all_tasks.append(task)
        
        return all_tasks
    
    def _create_subtask(self, parent_task: Dict, users: List[Dict]) -> Dict:
        """Create a subtask for a parent task"""
        created_at = datetime.fromisoformat(parent_task['created_at'].replace('Z', '+00:00'))
        subtask_created = created_at + timedelta(days=random.randint(0, 3))
        
        # Generate realistic subtask title
        subtask_verbs = ['Research', 'Design', 'Implement', 'Test', 'Document', 'Review', 'Debug']
        subtask_targets = ['requirements', 'architecture', 'core logic', 'edge cases', 'API endpoints', 'UI components']
        
        subtask = {
            'id': generate_gid(),
            'name': f"{random.choice(subtask_verbs)} {random.choice(subtask_targets)} for {parent_task['name'][:50]}",
            'description': f"## Subtask for: {parent_task['name']}\n\nComplete this subtask as part of the parent task delivery.",
            'project_id': parent_task['project_id'],
            'section_id': parent_task['section_id'],
            'assignee_id': parent_task['assignee_id'],
            'parent_task_id': parent_task['id'],
            'due_date': parent_task.get('due_date'),
            'completed': random.random() < 0.7,
            'created_at': subtask_created.isoformat(),
            'updated_at': subtask_created.isoformat(),
            'priority': parent_task.get('priority', 'medium')
        }
        
        # Set completion timestamp if completed
        if subtask['completed']:
            days_to_complete = random.randint(1, 7)
            subtask['completed_at'] = (subtask_created + timedelta(days=days_to_complete)).isoformat()
        
        return subtask