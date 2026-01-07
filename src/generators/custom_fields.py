import random
import json
from typing import List, Dict
from ..models.base import Database, generate_gid

class CustomFieldGenerator:
    def __init__(self):
        self.db = Database()
        
        # Common custom field types in Asana
        self.field_templates = [
            {
                'name': 'Priority',
                'field_type': 'enum',
                'options': ['P0 - Critical', 'P1 - High', 'P2 - Medium', 'P3 - Low']
            },
            {
                'name': 'Status',
                'field_type': 'enum',
                'options': ['Not Started', 'In Progress', 'In Review', 'Done', 'Blocked']
            },
            {
                'name': 'Effort',
                'field_type': 'enum',
                'options': ['XS (1)', 'S (2)', 'M (3)', 'L (5)', 'XL (8)', 'XXL (13)']
            },
            {
                'name': 'Department',
                'field_type': 'enum',
                'options': ['Engineering', 'Product', 'Design', 'Marketing', 'Sales', 'Support']
            },
            {
                'name': 'Target Release',
                'field_type': 'text',
                'options': None
            },
            {
                'name': 'Estimated Hours',
                'field_type': 'number',
                'options': None
            },
            {
                'name': 'Due Date',
                'field_type': 'date',
                'options': None
            },
            {
                'name': 'Assignee',
                'field_type': 'person',
                'options': None
            },
            {
                'name': 'Customer Impact',
                'field_type': 'enum',
                'options': ['High', 'Medium', 'Low', 'None']
            },
            {
                'name': 'QA Status',
                'field_type': 'enum',
                'options': ['Not Tested', 'In Testing', 'Passed', 'Failed', 'N/A']
            }
        ]
    
    def generate_custom_fields_for_project(self, project_id: str) -> List[Dict]:
        """Generate custom fields for a specific project"""
        fields = []
        
        # Each project gets 2-5 custom fields
        num_fields = random.randint(2, 5)
        selected_templates = random.sample(self.field_templates, num_fields)
        
        for template in selected_templates:
            field = {
                'id': generate_gid(),
                'name': template['name'],
                'field_type': template['field_type'],
                'enum_options': json.dumps(template['options']) if template['options'] else None,
                'project_id': project_id,
                'created_at': '2024-01-01T00:00:00'
            }
            fields.append(field)
        
        return fields
    
    def generate_field_values(self, field_definitions: List[Dict], tasks: List[Dict]) -> List[Dict]:
        """Generate values for custom fields"""
        field_values = []
        
        # Get all users for person type fields
        users = self.db.query("SELECT id FROM users")
        user_ids = [u['id'] for u in users] if users else []
        
        for task in tasks:
            # Each task gets values for 0-3 custom fields from its project
            task_fields = [f for f in field_definitions if f['project_id'] == task['project_id']]
            
            if not task_fields:
                continue
            
            num_values = random.randint(0, min(3, len(task_fields)))
            selected_fields = random.sample(task_fields, num_values)
            
            for field in selected_fields:
                value = self._generate_field_value(field, task, user_ids)
                
                if value is not None:
                    field_value = {
                        'id': generate_gid(),
                        'task_id': task['id'],
                        'field_id': field['id'],
                        'value': value,
                        'created_at': task['created_at'],
                        'updated_at': task['created_at']
                    }
                    field_values.append(field_value)
        
        return field_values
    
    def _generate_field_value(self, field: Dict, task: Dict, user_ids: List[str]) -> str:
        """Generate appropriate value for a field type"""
        field_type = field['field_type']
        
        if field_type == 'enum':
            options = json.loads(field['enum_options']) if field['enum_options'] else []
            if options:
                return random.choice(options)
        
        elif field_type == 'text':
            if field['name'] == 'Target Release':
                releases = ['Q4 2024', 'Q1 2025', 'Next Sprint', 'Beta Release', 'v2.5.0']
                return random.choice(releases)
            else:
                return f"Sample value for {field['name']}"
        
        elif field_type == 'number':
            if field['name'] == 'Estimated Hours':
                return str(random.randint(1, 40))
            else:
                return str(random.randint(1, 100))
        
        elif field_type == 'date':
            # Generate a date near the task due date
            if task.get('due_date'):
                return task['due_date']
            else:
                # Random future date
                from datetime import datetime, timedelta
                future_date = datetime.now() + timedelta(days=random.randint(7, 90))
                return future_date.strftime('%Y-%m-%d')
        
        elif field_type == 'person' and user_ids:
            return random.choice(user_ids)
        
        return None