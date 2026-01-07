"""
Validation utilities for data consistency.
"""
from datetime import datetime
from typing import List, Tuple

def validate_database(db) -> List[str]:
    """Validate database for consistency issues"""
    issues = []
    
    # 1. Check temporal consistency
    issues.extend(validate_temporal_consistency(db))
    
    # 2. Check relational integrity
    issues.extend(validate_relational_integrity(db))
    
    # 3. Check business logic
    issues.extend(validate_business_logic(db))
    
    return issues

def validate_temporal_consistency(db) -> List[str]:
    """Validate timestamp logic"""
    issues = []
    
    # Tasks completed before creation
    query = """
    SELECT id, name FROM tasks 
    WHERE completed_at IS NOT NULL 
    AND completed_at < created_at
    """
    results = db.query(query)
    for row in results:
        issues.append(f"Task {row['id']} completed before creation")
    
    # Comments created before task creation
    query = """
    SELECT c.id, c.task_id FROM comments c
    JOIN tasks t ON c.task_id = t.id
    WHERE c.created_at < t.created_at
    """
    results = db.query(query)
    for row in results:
        issues.append(f"Comment {row['id']} created before task {row['task_id']}")
    
    # Subtasks completed before parent task
    query = """
    SELECT child.id, child.name FROM tasks child
    JOIN tasks parent ON child.parent_task_id = parent.id
    WHERE child.completed_at IS NOT NULL 
    AND parent.completed_at IS NOT NULL
    AND child.completed_at > parent.completed_at
    """
    results = db.query(query)
    for row in results:
        issues.append(f"Subtask {row['id']} completed after parent task")
    
    return issues

def validate_relational_integrity(db) -> List[str]:
    """Validate foreign key relationships"""
    issues = []
    
    # Orphaned tasks (no project)
    query = """
    SELECT t.id, t.name FROM tasks t
    LEFT JOIN projects p ON t.project_id = p.id
    WHERE p.id IS NULL
    """
    results = db.query(query)
    for row in results:
        issues.append(f"Task {row['id']} has no project")
    
    # Tasks in non-existent sections
    query = """
    SELECT t.id, t.name FROM tasks t
    LEFT JOIN sections s ON t.section_id = s.id
    WHERE t.section_id IS NOT NULL AND s.id IS NULL
    """
    results = db.query(query)
    for row in results:
        issues.append(f"Task {row['id']} has invalid section")
    
    # Comments on non-existent tasks
    query = """
    SELECT c.id FROM comments c
    LEFT JOIN tasks t ON c.task_id = t.id
    WHERE t.id IS NULL
    """
    results = db.query(query)
    for row in results:
        issues.append(f"Comment {row['id']} has no task")
    
    return issues

def validate_business_logic(db) -> List[str]:
    """Validate business rules"""
    issues = []
    
    # Check due date distribution
    query = """
    SELECT 
        CASE 
            WHEN due_date IS NULL THEN 'no_due_date'
            WHEN due_date < DATE('now') THEN 'overdue'
            WHEN due_date <= DATE('now', '+7 days') THEN 'this_week'
            WHEN due_date <= DATE('now', '+30 days') THEN 'this_month'
            ELSE 'future'
        END as category,
        COUNT(*) as count
    FROM tasks
    GROUP BY category
    """
    results = db.query(query)
    
    total = sum(row['count'] for row in results)
    distributions = {row['category']: row['count']/total for row in results}
    
    # Expected distributions (from research)
    expected = {
        'no_due_date': 0.10,
        'overdue': 0.05,
        'this_week': 0.25,
        'this_month': 0.40,
        'future': 0.20
    }
    
    for category, expected_pct in expected.items():
        actual_pct = distributions.get(category, 0)
        if abs(actual_pct - expected_pct) > 0.15:  # 15% tolerance
            issues.append(f"Due date distribution off for {category}: "
                         f"expected {expected_pct*100}%, got {actual_pct*100}%")
    
    # Check unassigned task percentage
    query = "SELECT COUNT(*) as total FROM tasks"
    total_tasks = db.query(query)[0]['total']
    
    query = "SELECT COUNT(*) as unassigned FROM tasks WHERE assignee_id IS NULL"
    unassigned = db.query(query)[0]['unassigned']
    
    unassigned_pct = unassigned / total_tasks if total_tasks > 0 else 0
    if abs(unassigned_pct - 0.15) > 0.05:  # Should be ~15%
        issues.append(f"Unassigned tasks: expected ~15%, got {unassigned_pct*100:.1f}%")
    
    return issues