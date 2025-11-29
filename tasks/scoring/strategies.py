STRATEGIES = {
    'smart_balance': {
        'urgency': 1,
        'importance': 1,
        'effort': 1,
        'dependencies': 1,
        'description': 'All factors weighted equally'
    },
    'fastest_wins': {
        'urgency': 0.5,
        'importance': 1,
        'effort': 3,
        'dependencies': 1,
        'description': 'Prioritize quick tasks'
    },
    'high_impact': {
        'urgency': 1,
        'importance': 3,
        'effort': 0.5,
        'dependencies': 1,
        'description': 'Prioritize important tasks'
    },
    'deadline_driven': {
        'urgency': 3,
        'importance': 1,
        'effort': 0.5,
        'dependencies': 1,
        'description': 'Prioritize urgent tasks'
    }
}


def apply_weights(urgency, importance, effort, dependencies, strategy='smart_balance'):
    """Apply strategy weights to components and return final score."""
    if strategy not in STRATEGIES:
        strategy = 'smart_balance'
    
    weights = STRATEGIES[strategy]
    
    score = (
        urgency * weights['urgency'] +
        importance * weights['importance'] +
        effort * weights['effort'] +
        dependencies * weights['dependencies']
    )
    
    return int(round(score))


def get_valid_strategies():
    """Return list of valid strategy names."""
    return list(STRATEGIES.keys())
