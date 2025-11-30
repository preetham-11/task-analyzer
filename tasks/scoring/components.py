from datetime import date, timedelta

def calculate_urgency(due_date, today=None):
    """
    Calculate urgency score (0-100) based on business days until due.
    Weekends are excluded from the count.
    
    Scoring:
    - Overdue (past) or TODAY: +100
    - 1-3 business days: +50
    - 4-7 business days: +25
    - 8-14 business days: +10
    - 15+ business days: +0
    """
    if today is None:
        today = date.today()
    
    # Calculate business days between today and due_date
    business_days = 0
    current = today
    
    # If overdue or today, return max urgency
    if due_date <= today:
        return 100
    
    # Count business days (Monday=0, Sunday=6)
    while current < due_date:
        current += timedelta(days=1)
        # Monday to Friday are business days (0-4)
        if current.weekday() < 5:
            business_days += 1
    
    # Score based on business days
    if business_days <= 3:
        return 50
    elif business_days <= 7:
        return 25
    elif business_days <= 14:
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
    """
    Calculate dependency bonus based on how many tasks are blocked.
    Each blocked task adds 20 points (max 100).
    
    Args:
        blocked_count: Number of tasks blocked by this task
    
    Returns:
        int: Dependency score (0-100 points, 20 per blocked task)
    """
    if blocked_count is None:
        blocked_count = 0
    
    blocked_count = int(blocked_count)
    
    # 20 points per blocked task, max 100
    return min(blocked_count * 20, 100)
