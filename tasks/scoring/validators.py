from dateutil import parser
from datetime import date

def parse_date(date_string):
    """Parse any date format. Returns date object or today if invalid."""
    if isinstance(date_string, date):
        return date_string
    
    if not date_string:
        return date.today()
    
    try:
        parsed = parser.parse(date_string)
        return parsed.date()
    except (ValueError, TypeError, AttributeError):
        return date.today()


def detect_circular_dependencies(tasks):
    """
    Detect circular dependencies using DFS.
    Returns (has_cycles, error_message)
    """
    if not isinstance(tasks, list) or not tasks:
        return False, ""
    
    task_ids = set()
    task_dependencies = {}
    
    for task in tasks:
        if isinstance(task, dict):
            task_id = task.get('id') or task.get('title')
            task_ids.add(task_id)
            deps = task.get('dependencies', [])
            task_dependencies[task_id] = deps if isinstance(deps, list) else []
    
    def has_cycle(task_id, visited, path):
        if task_id in path:
            return True, list(path) + [task_id]
        if task_id in visited:
            return False, []
        
        visited.add(task_id)
        new_path = path + [task_id]
        
        for dep_id in task_dependencies.get(task_id, []):
            has_cycl, cycle_path = has_cycle(dep_id, visited, new_path)
            if has_cycl:
                return True, cycle_path
        
        return False, []
    
    visited = set()
    for task_id in task_ids:
        if task_id not in visited:
            has_cycl, cycle_path = has_cycle(task_id, visited, [])
            if has_cycl:
                cycle_str = " -> ".join(str(x) for x in cycle_path)
                return True, f"Circular dependency detected: {cycle_str}"
    
    return False, ""


def count_blocked_tasks(task_id, all_tasks):
    """Count how many tasks depend on (are blocked by) task_id."""
    blocked_count = 0
    
    for task in all_tasks:
        if isinstance(task, dict):
            dependencies = task.get('dependencies', [])
            if isinstance(dependencies, list) and task_id in dependencies:
                blocked_count += 1
    
    return blocked_count
