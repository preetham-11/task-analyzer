from datetime import date

def calculate_urgency(due_date, today=None):
    """
    Calculate urgency score (0-100) based on days until due.
    
    Scoring:
    - Overdue (past) or TODAY: +100
    - 1-3 days: +50
    - 4-7 days: +25
    - 8-14 days: +10
    - 15+ days: +0
    """
    if today is None:
        today = date.today()
    
    days_until = (due_date - today).days
    
    if days_until <= 0:
        return 100
    elif days_until <= 3:
        return 50
    elif days_until <= 7:
        return 25
    elif days_until <= 14:
        return 10
    else:
        return 0


def calculate_importance(importance_rating):
    """Scale importance (1-10) to score (10-100). Default 5 if missing."""
    if importance_rating is None:
        importance_rating = 5
    
    importance_rating = max(1, min(10, int(importance_rating)))
    return importance_rating * 10


def calculate_effort(estimated_hours):
    """Calculate effort bonus/penalty. Quick=+15, medium=+5, long=-5."""
    if estimated_hours is None:
        estimated_hours = 2
    
    try:
        estimated_hours = float(estimated_hours)
    except (ValueError, TypeError):
        estimated_hours = 2
    
    if estimated_hours < 1.5:
        return 15
    elif estimated_hours <= 3:
        return 5
    else:
        return -5


def calculate_dependencies(blocked_count):
    """Calculate dependency bonus. 0=+0, 1=+20, 2+=+50."""
    if blocked_count is None:
        blocked_count = 0
    
    blocked_count = int(blocked_count)
    
    if blocked_count == 0:
        return 0
    elif blocked_count == 1:
        return 20
    else:
        return 50
