from .components import (
    calculate_urgency, calculate_importance, calculate_effort, calculate_dependencies
)
from .validators import parse_date, detect_circular_dependencies, count_blocked_tasks
from .strategies import apply_weights


def generate_explanation(urgency, importance, effort, dependencies):
    """
    Generate human-readable explanation of score breakdown.
    
    Converts numeric scores into words:
    """
    parts = []
    
    if urgency == 100:
        parts.append("OVERDUE: Maximum urgency")
    elif urgency == 50:
        parts.append("Due in 0-3 days: High urgency")
    elif urgency == 25:
        parts.append("Due in 4-7 days: Medium urgency")
    elif urgency == 10:
        parts.append("Due in 8-14 days: Low urgency")
    else:
        parts.append("15+ days away: No urgency")
    
    if importance >= 80:
        parts.append("Very important (8-10/10)")
    elif importance >= 50:
        parts.append("Moderately important (5-7/10)")
    else:
        parts.append("Less important (1-4/10)")
    
    if effort == 15:
        parts.append("Quick task (under 1.5 hrs)")
    elif effort == 5:
        parts.append("Medium length (1.5-3 hrs)")
    else:
        parts.append("Long task (3+ hrs)")
    
    if dependencies > 0:
        parts.append(f"Blocks other tasks (+{dependencies})")
    
    return " | ".join(parts)


def assign_priority_level(score):
    """
    Convert numeric score to priority label.
    
    Returns: 'HIGH' (red), 'MEDIUM' (yellow), or 'LOW' (green)
    """
    if score >= 150:
        return 'HIGH'
    elif score >= 50:
        return 'MEDIUM'
    else:
        return 'LOW'


def score_single_task(task, all_tasks, strategy='smart_balance'):
    """
    Score ONE task with all 4 components.
    
    Returns dictionary with:
    {
        'score': 165,
        'urgency': 50,
        'importance': 80,
        'effort': 5,
        'dependencies': 0,
        'explanation': '...',
        'priority_level': 'HIGH'
    }
    """
    urgency = calculate_urgency(parse_date(task.get('due_date')))
    importance = calculate_importance(task.get('importance', 5))
    effort = calculate_effort(task.get('estimated_hours', 2))
    
    task_id = task.get('id') or task.get('title')
    blocked_count = count_blocked_tasks(task_id, all_tasks)
    dependencies = calculate_dependencies(blocked_count)
    
    score = apply_weights(urgency, importance, effort, dependencies, strategy)
    
    return {
        'score': score,
        'urgency': urgency,
        'importance': importance,
        'effort': effort,
        'dependencies': dependencies,
        'explanation': generate_explanation(urgency, importance, effort, dependencies),
        'priority_level': assign_priority_level(score)
    }


def analyze_tasks(tasks, strategy='smart_balance'):
    """
    Main analysis function.
    
    Takes list of tasks and returns them scored and sorted.
    
    Returns:
    {
        'success': True/False,
        'message': 'Successfully analyzed 5 tasks',
        'results': [scored_task_1, scored_task_2, ...],
        'error': None or error message
    }
    """
    if not isinstance(tasks, list) or len(tasks) == 0:
        return {
            'success': True if len(tasks) == 0 else False,
            'message': 'No tasks provided' if len(tasks) == 0 else 'Invalid input',
            'results': [],
            'error': None if len(tasks) == 0 else 'tasks must be a list'
        }
    
    has_cycles, cycle_message = detect_circular_dependencies(tasks)
    if has_cycles:
        return {
            'success': False,
            'message': 'Circular dependency detected',
            'results': [],
            'error': cycle_message
        }
    
    scored_tasks = []
    
    for i, task in enumerate(tasks):
        try:
            if not isinstance(task, dict):
                continue
            
            task['id'] = task.get('id', i)
            
            score_info = score_single_task(task, tasks, strategy)
            
            task_result = {
                'id': task['id'],
                'title': task.get('title', 'Untitled'),
                'due_date': str(task.get('due_date', '')),
                'importance': task.get('importance', 5),
                'estimated_hours': task.get('estimated_hours', 2),
                'priority_score': score_info['score'],
                'urgency': score_info['urgency'],
                'importance_score': score_info['importance'],
                'effort': score_info['effort'],
                'dependencies_count': score_info['dependencies'],
                'explanation': score_info['explanation'],
                'priority_level': score_info['priority_level']
            }
            
            scored_tasks.append(task_result)
        
        except Exception:
            continue
    
    scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return {
        'success': True,
        'message': f'Successfully analyzed {len(scored_tasks)} tasks',
        'results': scored_tasks,
        'error': None
    }


def get_top_suggestions(tasks, strategy='smart_balance', count=3):
    """
    Get top N tasks for /suggest/ endpoint.
    
    Returns top 3 (or N) tasks formatted for suggestions.
    
    Returns:
    {
        'success': True/False,
        'suggestions': [
            {
                'title': 'Fix login bug',
                'reason': 'Due in 0-3 days...',
                'priority': 'HIGH',
                'due_date': '2025-11-30',
                'priority_score': 165
            }
        ],
        'message': 'Top 3 tasks for today'
    }
    """
    analysis = analyze_tasks(tasks, strategy)
    
    if not analysis['success']:
        return {
            'success': False,
            'suggestions': [],
            'message': analysis['error']
        }
    
    top_tasks = analysis['results'][:count]
    
    suggestions = [
        {
            'title': task['title'],
            'reason': task['explanation'],
            'priority': task['priority_level'],
            'due_date': task['due_date'],
            'priority_score': task['priority_score']
        }
        for task in top_tasks
    ]
    
    return {
        'success': True,
        'suggestions': suggestions,
        'message': f'Top {len(suggestions)} tasks for today'
    }
