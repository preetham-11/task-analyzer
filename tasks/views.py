from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from .scoring import analyze_tasks, get_top_suggestions, get_valid_strategies
from .scoring.validators import detect_circular_dependencies


@api_view(['POST'])
def analyze_tasks_view(request):
    """
    POST /api/tasks/analyze/
    
    Analyzes and prioritizes a list of tasks.
    
    Request format:
    {
        "tasks": [
            {
                "title": "Fix login bug",
                "due_date": "2025-11-30",
                "importance": 8,
                "estimated_hours": 3,
                "dependencies": []
            }
        ],
        "strategy": "smart_balance"
    }
    
    Response format:
    {
        "success": true,
        "message": "Successfully analyzed 1 tasks",
        "strategy": "smart_balance",
        "total_tasks": 1,
        "results": [
            {
                "id": 0,
                "title": "Fix login bug",
                "priority_score": 165,
                "priority_level": "HIGH",
                "explanation": "Due in 0-3 days...",
                "urgency": 50,
                "importance_score": 80,
                "effort": 5,
                "dependencies_count": 0
            }
        ]
    }
    """
    try:
        data = request.data
        tasks = data.get('tasks', [])
        strategy = data.get('strategy', 'smart_balance')
        
        if not isinstance(tasks, list):
            return Response({
                'success': False,
                'message': 'Invalid request format',
                'error': 'tasks must be a list'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(tasks) == 0:
            return Response({
                'success': True,
                'message': 'No tasks provided',
                'strategy': strategy,
                'total_tasks': 0,
                'results': []
            }, status=status.HTTP_200_OK)
        
        valid_strategies = get_valid_strategies()
        if strategy not in valid_strategies:
            return Response({
                'success': False,
                'message': 'Invalid strategy',
                'error': f'Strategy must be one of: {", ".join(valid_strategies)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        has_cycles, cycle_message = detect_circular_dependencies(tasks)
        if has_cycles:
            return Response({
                'success': False,
                'message': 'Circular dependency detected',
                'error': cycle_message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        analysis_result = analyze_tasks(tasks, strategy)
        
        if not analysis_result['success']:
            return Response({
                'success': False,
                'message': analysis_result['message'],
                'error': analysis_result['error']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'message': analysis_result['message'],
            'strategy': strategy,
            'total_tasks': len(analysis_result['results']),
            'results': analysis_result['results']
        }, status=status.HTTP_200_OK)
    
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Invalid JSON format',
            'error': 'Request body must be valid JSON'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Server error occurred',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
def suggest_tasks_view(request):
    """
    GET /api/tasks/suggest/?strategy=smart_balance
    POST /api/tasks/suggest/
    
    Returns top 3 tasks to work on today.
    
    Request (POST):
    {
        "tasks": [...],
        "strategy": "smart_balance"
    }
    
    Query params (GET):
    - tasks: JSON array of tasks
    - strategy: sorting strategy
    
    Response format:
    {
        "success": true,
        "strategy": "smart_balance",
        "message": "Top 3 tasks for today",
        "suggestions": [
            {
                "title": "Fix login bug",
                "reason": "Due in 0-3 days: High urgency | Very important (8-10/10) | ...",
                "priority": "HIGH",
                "due_date": "2025-11-28",
                "priority_score": 165
            }
        ]
    }
    """
    try:
        if request.method == 'GET':
            tasks_str = request.GET.get('tasks')
            strategy = request.GET.get('strategy', 'smart_balance')
            
            if not tasks_str:
                return Response({
                    'success': False,
                    'message': 'No tasks provided',
                    'suggestions': []
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                tasks = json.loads(tasks_str)
            except json.JSONDecodeError:
                return Response({
                    'success': False,
                    'message': 'Invalid tasks JSON format',
                    'suggestions': []
                }, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            data = request.data
            tasks = data.get('tasks', [])
            strategy = data.get('strategy', 'smart_balance')
        
        if not isinstance(tasks, list) or len(tasks) == 0:
            return Response({
                'success': False,
                'message': 'No tasks provided',
                'suggestions': []
            }, status=status.HTTP_400_BAD_REQUEST)
        
        valid_strategies = get_valid_strategies()
        if strategy not in valid_strategies:
            return Response({
                'success': False,
                'message': 'Invalid strategy',
                'suggestions': []
            }, status=status.HTTP_400_BAD_REQUEST)
        
        has_cycles, cycle_message = detect_circular_dependencies(tasks)
        if has_cycles:
            return Response({
                'success': False,
                'message': 'Circular dependency detected',
                'error': cycle_message,
                'suggestions': []
            }, status=status.HTTP_400_BAD_REQUEST)
        
        suggestions_result = get_top_suggestions(tasks, strategy, count=3)
        
        if not suggestions_result['success']:
            return Response({
                'success': False,
                'message': suggestions_result['message'],
                'suggestions': []
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'strategy': strategy,
            'message': suggestions_result['message'],
            'suggestions': suggestions_result['suggestions']
        }, status=status.HTTP_200_OK)
    
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Invalid JSON format',
            'suggestions': []
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Server error occurred',
            'error': str(e),
            'suggestions': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
