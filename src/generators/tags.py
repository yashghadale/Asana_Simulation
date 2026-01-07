import random
from datetime import datetime
from typing import List, Dict
from ..models.base import Database, generate_gid

class TagGenerator:
    def __init__(self):
        self.db = Database()
        
        # Realistic tag names organized by category
        self.tag_categories = {
            'priority': ['critical', 'high-priority', 'low-priority', 'blocker'],
            'status': ['blocked', 'in-review', 'waiting', 'ready', 'needs-info'],
            'type': ['bug', 'feature', 'enhancement', 'documentation', 'maintenance'],
            'team': ['frontend', 'backend', 'mobile', 'devops', 'design', 'qa'],
            'component': ['api', 'ui', 'database', 'security', 'performance', 'accessibility'],
            'release': ['next-release', 'q4-2024', 'beta', 'production'],
            'customer': ['enterprise', 'sme', 'trial', 'paying'],
            'effort': ['quick-win', 'large-effort', 'spike', 'refactor']
        }
        
        # Tag colors (Asana-like color palette)
        self.tag_colors = [
            'blue', 'green', 'orange', 'red', 'purple', 
            'pink', 'lime', 'sky', 'grey', 'yellow'
        ]
    
    def generate_tags(self) -> List[Dict]:
        """Generate realistic tags"""
        tags = []
        tag_names = set()
        
        # Generate tags from each category
        for category, names in self.tag_categories.items():
            for name in names:
                # Use proper timestamp
                created_at = datetime.now().isoformat()
                
                tag = {
                    'id': generate_gid(),
                    'name': name,
                    'color': random.choice(self.tag_colors),
                    'created_at': created_at  # Use proper datetime
                }
                tags.append(tag)
                tag_names.add(name)
        
        # Add some custom/unique tags
        custom_tags = [
            'tech-debt', 'good-first-issue', 'p0', 'p1', 'p2',
            'design-review', 'legal-review', 'compliance', 'oncall',
            'customer-reported', 'internal', 'external'
        ]
        
        for name in custom_tags:
            if name not in tag_names:
                tag = {
                    'id': generate_gid(),
                    'name': name,
                    'color': random.choice(self.tag_colors),
                    'created_at': datetime.now().isoformat()
                }
                tags.append(tag)
        
        return tags
    
    def associate_tags_with_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """Associate tags with tasks realistically"""
        associations = []
        
        # Get all tags from database
        tags = self.db.query("SELECT id, name FROM tags")
        if not tags:
            print("Warning: No tags found in database")
            return associations
        
        for task in tasks:
            # Determine how many tags for this task (0-4, weighted)
            num_tags = random.choices([0, 1, 2, 3, 4], weights=[0.2, 0.3, 0.3, 0.15, 0.05])[0]
            
            if num_tags == 0:
                continue
            
            # Select appropriate tags based on task context
            selected_tags = self._select_tags_for_task(task, tags, num_tags)
            
            for tag in selected_tags:
                # CORRECT: task_tags table only has task_id, tag_id, created_at
                # NO 'id' field!
                association = {
                    'task_id': task['id'],
                    'tag_id': tag['id'],
                    'created_at': task.get('created_at')  # Use task creation time or default
                }
                
                # Ensure created_at is not None
                if not association['created_at']:
                    from datetime import datetime
                    association['created_at'] = datetime.now().isoformat()
                    
                associations.append(association)
        
        return associations
    
    def _select_tags_for_task(self, task: Dict, all_tags: List[Dict], num_tags: int) -> List[Dict]:
        """Select appropriate tags for a task"""
        # Get tag names for easier filtering
        tag_dict = {tag['name']: tag for tag in all_tags}
        selected = []
        
        # Priority tags based on task priority
        if task.get('priority'):
            if task['priority'] == 'urgent':
                if 'critical' in tag_dict:
                    selected.append(tag_dict['critical'])
            elif task['priority'] == 'high':
                if 'high-priority' in tag_dict:
                    selected.append(tag_dict['high-priority'])
            elif task['priority'] == 'low':
                if 'low-priority' in tag_dict:
                    selected.append(tag_dict['low-priority'])
        
        # Status tags if task is blocked
        if task.get('is_blocked'):
            if 'blocked' in tag_dict:
                selected.append(tag_dict['blocked'])
        
        # Type tags based on keywords in task name
        task_lower = task.get('name', '').lower()
        
        # ... rest of your selection logic ...
        
        return selected[:num_tags]