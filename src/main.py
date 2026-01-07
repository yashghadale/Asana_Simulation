#!/usr/bin/env python3
"""
Main orchestration script for Asana simulation data generation.
"""

import os
import sys
import logging
import random
import json
from datetime import datetime
from dotenv import load_dotenv

# FORCE DISABLE GEMINI - Override environment variables
os.environ['USE_GEMINI_FOR_TITLES'] = 'false'
os.environ['USE_GEMINI_FOR_DESCRIPTIONS'] = 'false'
os.environ['USE_GEMINI_FOR_COMMENTS'] = 'false'

# Windows-specific encoding fix
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.base import Database, generate_gid
from src.generators.users import UserGenerator
from src.generators.teams import TeamGenerator
from src.generators.projects import ProjectGenerator
from src.generators.tasks import TaskGenerator
from src.generators.comments import CommentGenerator
from src.generators.tags import TagGenerator
from src.utils.validators import validate_database

# Import missing generators if they exist
try:
    from src.generators.custom_fields import CustomFieldGenerator
    HAS_CUSTOM_FIELDS = True
except ImportError:
    HAS_CUSTOM_FIELDS = False
    print("Warning: CustomFieldGenerator not found")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/generation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def clear_existing_database(db_path: str):
    """Clear existing database file if it exists"""
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            logger.info(f"Removed existing database: {db_path}")
        except Exception as e:
            logger.warning(f"Could not remove existing database: {e}")

def create_organization(db: Database) -> str:
    """Create organization/workspace entry"""
    org_data = {
        'id': "1202178706740001",  # Asana-style GID
        'name': os.getenv('COMPANY_NAME', 'TechFlow Solutions'),
        'domain': os.getenv('COMPANY_DOMAIN', 'techflowsolutions.com'),
        'created_at': datetime(2023, 1, 1).isoformat(),
        'is_personal': False
    }
    
    db.insert('organizations', org_data)
    logger.info(f"Created organization: {org_data['name']}")
    return org_data['id']

def generate_statistics(db: Database) -> dict:
    """Generate statistics about the generated data"""
    stats = {}
    
    queries = {
        'Total Users': "SELECT COUNT(*) as count FROM users",
        'Active Users': "SELECT COUNT(*) as count FROM users WHERE is_active = 1",
        'Total Teams': "SELECT COUNT(*) as count FROM teams",
        'Total Projects': "SELECT COUNT(*) as count FROM projects",
        'Active Projects': "SELECT COUNT(*) as count FROM projects WHERE status = 'active'",
        'Total Tasks': "SELECT COUNT(*) as count FROM tasks",
        'Completed Tasks': "SELECT COUNT(*) as count FROM tasks WHERE completed = 1",
        'Tasks with Due Dates': "SELECT COUNT(*) as count FROM tasks WHERE due_date IS NOT NULL",
        'Overdue Tasks': "SELECT COUNT(*) as count FROM tasks WHERE due_date < DATE('now') AND completed = 0",
        'Unassigned Tasks': "SELECT COUNT(*) as count FROM tasks WHERE assignee_id IS NULL",
        'Total Comments': "SELECT COUNT(*) as count FROM comments",
        'Total Tags': "SELECT COUNT(*) as count FROM tags",
        'Tasks with Subtasks': "SELECT COUNT(DISTINCT parent_task_id) as count FROM tasks WHERE parent_task_id IS NOT NULL",
        'Total Sections': "SELECT COUNT(*) as count FROM sections",
        'Total Custom Fields': "SELECT COUNT(*) as count FROM custom_field_definitions",
        'Total Custom Field Values': "SELECT COUNT(*) as count FROM custom_field_values",
    }
    
    for name, query in queries.items():
        try:
            result = db.query(query)
            stats[name] = result[0]['count'] if result else 0
        except Exception:
            stats[name] = 0  # Table might not exist
    
    # Additional complex stats
    if stats['Total Projects'] > 0:
        stats['Avg Tasks per Project'] = round(stats['Total Tasks'] / stats['Total Projects'], 1)
    else:
        stats['Avg Tasks per Project'] = 0
    
    if stats['Total Tasks'] > 0:
        completion_rate = (stats['Completed Tasks'] / stats['Total Tasks']) * 100
        stats['Completion Rate'] = f"{completion_rate:.1f}%"
        
        if stats['Tasks with Due Dates'] > 0:
            overdue_rate = (stats['Overdue Tasks'] / stats['Tasks with Due Dates']) * 100
            stats['Overdue Rate'] = f"{overdue_rate:.1f}%"
        else:
            stats['Overdue Rate'] = "0.0%"
    else:
        stats['Completion Rate'] = "0.0%"
        stats['Overdue Rate'] = "0.0%"
    
    return stats

def print_distributions(db: Database):
    """Print important data distributions"""
    logger.info("\n" + "="*60)
    logger.info("DATA DISTRIBUTIONS")
    logger.info("="*60)
    
    try:
        # Task priority distribution
        priorities = db.query("""
            SELECT priority, COUNT(*) as count 
            FROM tasks 
            WHERE priority IS NOT NULL
            GROUP BY priority 
            ORDER BY 
                CASE priority 
                    WHEN 'urgent' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END
        """)
        
        if priorities:
            total_priority = sum(p['count'] for p in priorities)
            logger.info("\nTask Priority Distribution:")
            for p in priorities:
                percentage = (p['count'] / total_priority * 100) if total_priority > 0 else 0
                logger.info(f"  {p['priority'].upper():<7}: {p['count']:>4} tasks ({percentage:5.1f}%)")
    except Exception as e:
        logger.error(f"Failed to get priority distribution: {e}")
    
    try:
        # Due date distribution
        due_stats = db.query("""
            SELECT 
                CASE 
                    WHEN due_date IS NULL THEN 'No due date'
                    WHEN due_date < DATE('now') THEN 'Overdue'
                    WHEN due_date <= DATE('now', '+7 days') THEN 'Due this week'
                    WHEN due_date <= DATE('now', '+30 days') THEN 'Due this month'
                    ELSE 'Future due date'
                END as category,
                COUNT(*) as count
            FROM tasks
            GROUP BY category
        """)
        
        if due_stats:
            total_due = sum(d['count'] for d in due_stats)
            logger.info("\nDue Date Distribution:")
            for d in due_stats:
                percentage = (d['count'] / total_due * 100) if total_due > 0 else 0
                logger.info(f"  {d['category']:<20}: {d['count']:>4} tasks ({percentage:5.1f}%)")
    except Exception as e:
        logger.error(f"Failed to get due date distribution: {e}")
    
    try:
        # Project type distribution
        project_types = db.query("""
            SELECT project_type, COUNT(*) as count 
            FROM projects 
            GROUP BY project_type
        """)
        
        if project_types:
            total_projects = sum(p['count'] for p in project_types)
            logger.info("\nProject Type Distribution:")
            for p in project_types:
                percentage = (p['count'] / total_projects * 100) if total_projects > 0 else 0
                logger.info(f"  {p['project_type'].replace('_', ' ').title():<15}: {p['count']:>4} projects ({percentage:5.1f}%)")
    except Exception as e:
        logger.error(f"Failed to get project type distribution: {e}")
    
    try:
        # Team department distribution
        team_depts = db.query("""
            SELECT department, COUNT(*) as count 
            FROM teams 
            GROUP BY department
        """)
        
        if team_depts:
            logger.info("\nTeam Department Distribution:")
            for d in team_depts:
                logger.info(f"  {d['department'].title():<15}: {d['count']:>4} teams")
    except Exception as e:
        logger.error(f"Failed to get team department distribution: {e}")

def main():
    """Main generation pipeline"""
    logger.info(">>> Starting Asana RL Environment Simulation")
    logger.info("="*60)
    
    start_time = datetime.now()
    
    # Load configuration
    load_dotenv()
    
    # Display configuration (with 5000 users scale)
    config = {
        'total_users': int(os.getenv('TOTAL_USERS', 5000)),
        'total_teams': int(os.getenv('TOTAL_TEAMS', 80)),
        'total_projects': int(os.getenv('TOTAL_PROJECTS', 400)),
        'company_domain': os.getenv('COMPANY_DOMAIN', 'techflowsolutions.com'),
        'company_name': os.getenv('COMPANY_NAME', 'TechFlow Solutions'),
        'use_gemini': False,  # Force disabled
        'gemini_model': 'none'
    }
    
    logger.info("Configuration:")
    for key, value in config.items():
        logger.info(f"  {key}: {value}")
    
    # First, clear any existing database
    db_path = 'output/asana_simulation.sqlite'
    clear_existing_database(db_path)
    
    # Initialize database
    db = Database()
    logger.info("\nStep 1: Initializing database schema...")
    try:
        db.initialize()  # Remove clear_existing parameter
        logger.info("Database schema created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)
    
    # Step 1: Create Organization
    logger.info("\nStep 2: Creating organization...")
    org_id = create_organization(db)
    
    # Step 2: Generate Users
    logger.info(f"\nStep 3: Generating {config['total_users']} users...")
    try:
        user_gen = UserGenerator(company_domain=config['company_domain'])
        users = user_gen.generate_users(config['total_users'])
        user_gen.save_users(users)
        logger.info(f"Generated {len(users)} users")
    except Exception as e:
        logger.error(f"Failed to generate users: {e}")
        sys.exit(1)
    
    # Step 3: Generate Teams
    logger.info(f"\nStep 4: Generating {config['total_teams']} teams...")
    try:
        team_gen = TeamGenerator()
        teams = team_gen.generate_teams(config['total_teams'], org_id)
        db.insert_many('teams', teams)
        logger.info(f"Generated {len(teams)} teams")
    except Exception as e:
        logger.error(f"Failed to generate teams: {e}")
        sys.exit(1)
    
    # Step 4: Assign Team Memberships
    logger.info("\nStep 5: Assigning team memberships...")
    try:
        memberships = team_gen.assign_team_members(users, teams)
        db.insert_many('team_memberships', memberships)
        logger.info(f"Created {len(memberships)} team memberships")
    except Exception as e:
        logger.error(f"Failed to assign team memberships: {e}")
        sys.exit(1)
    
    # Step 5: Generate Projects
    logger.info(f"\nStep 6: Generating {config['total_projects']} projects...")
    try:
        project_gen = ProjectGenerator()
        projects = project_gen.generate_projects(config['total_projects'], teams)
        db.insert_many('projects', projects)
        logger.info(f"Generated {len(projects)} projects")
    except Exception as e:
        logger.error(f"Failed to generate projects: {e}")
        sys.exit(1)
    
    # Step 6: Generate Sections for each project
    logger.info("\nStep 7: Generating project sections...")
    try:
        all_sections = []
        for project in projects:
            sections = project_gen.generate_sections(project['id'])
            all_sections.extend(sections)
        
        db.insert_many('sections', all_sections)
        logger.info(f"Generated {len(all_sections)} sections")
    except Exception as e:
        logger.error(f"Failed to generate sections: {e}")
        sys.exit(1)
    
    # Step 7: Generate Tasks (Most Important Step)
    logger.info("\nStep 8: Generating tasks...")
    logger.info("   Using template-based generation (Gemini disabled)")
    
    try:
        task_gen = TaskGenerator(use_gemini=False)
        
        # Get all users from database for assignment
        all_users = db.query("SELECT id, department FROM users")
        
        tasks = task_gen.generate_tasks(projects, all_sections, all_users)
        db.insert_many('tasks', tasks)
        logger.info(f"Generated {len(tasks)} tasks")
        
        # Show sample tasks
        if tasks:
            logger.info("\nSample generated tasks:")
            sample_tasks = random.sample(tasks, min(5, len(tasks)))
            for i, task in enumerate(sample_tasks, 1):
                logger.info(f"  {i}. {task['name']}")
                if task['description'] and len(task['description']) > 0:
                    desc_preview = task['description'][:80] + "..." if len(task['description']) > 80 else task['description']
                    logger.info(f"     Desc: {desc_preview}")
    except Exception as e:
        logger.error(f"Failed to generate tasks: {e}")
        sys.exit(1)
    
    # Step 8: Generate Subtasks (10% of tasks have subtasks)
    logger.info("\nStep 9: Generating subtasks...")
    try:
        # Get parent tasks (non-subtasks)
        all_tasks_from_db = db.query("SELECT * FROM tasks WHERE parent_task_id IS NULL")
        subtask_parents = [t for t in all_tasks_from_db if random.random() < 0.1][:50]
        
        subtasks = []
        for parent in subtask_parents:
            num_subtasks = random.randint(1, 5)
            for i in range(num_subtasks):
                subtask = {
                    'id': generate_gid(),
                    'name': f"{parent['name']} - Subtask {i+1}",
                    'description': f"Detailed work for {parent['name']}",
                    'project_id': parent['project_id'],
                    'section_id': parent['section_id'],
                    'assignee_id': parent['assignee_id'] if random.random() < 0.7 else None,
                    'parent_task_id': parent['id'],
                    'due_date': None,
                    'priority': parent['priority'],
                    'completed': random.random() < 0.7,
                    'created_at': parent['created_at']
                }
                subtasks.append(subtask)
        
        if subtasks:
            db.insert_many('tasks', subtasks)
            logger.info(f"Generated {len(subtasks)} subtasks")
        else:
            logger.info("No subtasks generated (based on probability)")
    except Exception as e:
        logger.error(f"Failed to generate subtasks: {e}")
        # Continue, subtasks are optional
    
    # Step 9: Generate Comments
    logger.info("\nStep 10: Generating comments...")
    try:
        comment_gen = CommentGenerator(use_gemini=False)
        
        # Get tasks for comments
        all_tasks_for_comments = db.query("SELECT id, created_at, name FROM tasks ORDER BY RANDOM() LIMIT 500")
        
        if all_tasks_for_comments:
            comments = comment_gen.generate_comments(all_tasks_for_comments, all_users)
            db.insert_many('comments', comments)
            logger.info(f"Generated {len(comments)} comments")
            
            # Show sample comments
            if comments:
                logger.info("\nSample comments:")
                sample_comments = random.sample(comments, min(3, len(comments)))
                for i, comment in enumerate(sample_comments, 1):
                    task_name = next((t['name'] for t in all_tasks_for_comments if t['id'] == comment['task_id']), 'Unknown task')
                    comment_preview = comment['text'][:60] + "..." if len(comment['text']) > 60 else comment['text']
                    logger.info(f"  {i}. On '{task_name[:30]}...': {comment_preview}")
        else:
            logger.info("No tasks available for comments")
    except Exception as e:
        logger.error(f"Failed to generate comments: {e}")
        # Continue, comments are optional
    
    # Step 10: Generate Tags and Associations
    logger.info("\nStep 11: Generating tags...")
    try:
        tag_gen = TagGenerator()
        tags = tag_gen.generate_tags()
        db.insert_many('tags', tags)
        
        # Get some tasks to tag
        tasks_to_tag = db.query("SELECT id FROM tasks ORDER BY RANDOM() LIMIT 300")
        
        # Associate tags with tasks
        task_tags = tag_gen.associate_tags_with_tasks(tasks_to_tag)
        db.insert_many('task_tags', task_tags)
        
        logger.info(f"Generated {len(tags)} tags and {len(task_tags)} associations")
        
        # Show sample tags
        if tags:
            logger.info("\nSample tags:")
            sample_tags = random.sample(tags, min(8, len(tags)))
            tag_names = [t['name'] for t in sample_tags]
            logger.info(f"  {', '.join(tag_names)}")
    except Exception as e:
        logger.error(f"Failed to generate tags: {e}")
        # Continue, tags are optional
    
    # Step 11: Generate Custom Fields (if generator exists)
    if HAS_CUSTOM_FIELDS:
        logger.info("\nStep 12: Generating custom fields...")
        try:
            custom_field_gen = CustomFieldGenerator()
            
            # Generate custom fields for some projects
            project_ids = [p['id'] for p in projects[:20]]  # First 20 projects
            custom_fields = []
            
            for project_id in project_ids:
                fields = custom_field_gen.generate_custom_fields_for_project(project_id)
                custom_fields.extend(fields)
            
            if custom_fields:
                db.insert_many('custom_field_definitions', custom_fields)
                logger.info(f"Generated {len(custom_fields)} custom field definitions")
                
                # Add values for some tasks
                tasks_for_custom_fields = db.query("SELECT * FROM tasks LIMIT 100")
                field_values = custom_field_gen.generate_field_values(custom_fields, tasks_for_custom_fields)
                db.insert_many('custom_field_values', field_values)
                logger.info(f"Generated {len(field_values)} custom field values")
            else:
                logger.info("No custom fields generated")
        except Exception as e:
            logger.error(f"Failed to generate custom fields: {e}")
            # Continue, custom fields are optional
    else:
        logger.warning("\nStep 12: Skipping custom fields (generator not found)")
    
    # Final Validation
    logger.info("\nStep 13: Validating database...")
    try:
        issues = validate_database(db)
        
        if issues:
            logger.warning(f"Found {len(issues)} validation issues:")
            for issue in issues[:10]:  # Show first 10 issues
                logger.warning(f"  * {issue}")
            if len(issues) > 10:
                logger.warning(f"  ... and {len(issues) - 10} more issues")
        else:
            logger.info("Database validation passed!")
    except Exception as e:
        logger.error(f"Validation failed: {e}")
    
    # Generate and Display Statistics
    logger.info("\n" + "="*60)
    logger.info("GENERATION COMPLETE - FINAL STATISTICS")
    logger.info("="*60)
    
    try:
        stats = generate_statistics(db)
        for key, value in stats.items():
            logger.info(f"{key:<30}: {value}")
        
        # Print distributions
        print_distributions(db)
    except Exception as e:
        logger.error(f"Failed to generate statistics: {e}")
    
    # Calculate and display generation time
    end_time = datetime.now()
    generation_time = end_time - start_time
    
    logger.info("\n" + "="*60)
    logger.info("GENERATION SUMMARY")
    logger.info("="*60)
    logger.info(f"Start time: {start_time.strftime('%H:%M:%S')}")
    logger.info(f"End time:   {end_time.strftime('%H:%M:%S')}")
    logger.info(f"Duration:   {generation_time}")
    logger.info(f"Database:   {db.db_path}")
    logger.info(f"Scale:      {config['total_users']} users, {config['total_projects']} projects")
    
    # Show some sample queries users can run
    logger.info("\n" + "="*60)
    logger.info("SAMPLE QUERIES TO EXPLORE DATA")
    logger.info("="*60)
    logger.info("1. All tasks in a project:")
    logger.info("   SELECT t.name, u.name as assignee, t.due_date")
    logger.info("   FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id")
    logger.info("   WHERE t.project_id = (SELECT id FROM projects LIMIT 1)")
    logger.info("")
    logger.info("2. Overdue tasks by team:")
    logger.info("   SELECT t.name as team, COUNT(*) as overdue_tasks")
    logger.info("   FROM teams t")
    logger.info("   JOIN projects p ON t.id = p.team_id")
    logger.info("   JOIN tasks tk ON p.id = tk.project_id")
    logger.info("   WHERE tk.due_date < DATE('now') AND tk.completed = 0")
    logger.info("   GROUP BY t.name")
    logger.info("")
    logger.info("3. User workload:")
    logger.info("   SELECT u.name, COUNT(t.id) as task_count")
    logger.info("   FROM users u")
    logger.info("   LEFT JOIN tasks t ON u.id = t.assignee_id")
    logger.info("   GROUP BY u.name")
    logger.info("   ORDER BY task_count DESC")
    logger.info("")
    logger.info("Explore with: sqlite3 output/asana_simulation.sqlite")
    
    logger.info("\n" + "="*60)
    logger.info(">>> ASANA SIMULATION GENERATION COMPLETE!")
    logger.info("="*60)

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nGeneration interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\nGeneration failed with error: {e}")
        sys.exit(1)