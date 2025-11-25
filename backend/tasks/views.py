from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .scoring import TaskScorer

@csrf_exempt
@require_http_methods(["POST"])
def analyze_tasks(request):
    """
    POST /api/tasks/analyze/
    Accept list of tasks and return them sorted by priority score.
    """
    try:
        data = json.loads(request.body)
        tasks = data.get('tasks', [])
        strategy = data.get('strategy', 'smart_balance')
        
        if not tasks:
            return JsonResponse({
                'error': 'No tasks provided'
            }, status=400)
        
        # Validate tasks
        for i, task in enumerate(tasks):
            if not task.get('title'):
                return JsonResponse({
                    'error': f'Task at index {i} missing title'
                }, status=400)
        
        # Score and sort tasks
        scorer = TaskScorer(strategy=strategy)
        sorted_tasks = scorer.score_and_sort_tasks(tasks)
        
        return JsonResponse({
            'tasks': sorted_tasks,
            'strategy': strategy,
            'total_count': len(sorted_tasks)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def suggest_tasks(request):
    """
    POST /api/tasks/suggest/
    Return top 3 tasks with explanations.
    """
    try:
        data = json.loads(request.body)
        tasks = data.get('tasks', [])
        strategy = data.get('strategy', 'smart_balance')
        
        if not tasks:
            return JsonResponse({
                'error': 'No tasks provided'
            }, status=400)
        
        # Score and sort tasks
        scorer = TaskScorer(strategy=strategy)
        sorted_tasks = scorer.score_and_sort_tasks(tasks)
        
        # Get top 3 with explanations
        suggestions = []
        for i, task in enumerate(sorted_tasks[:3]):
            explanation = generate_explanation(task, i + 1)
            suggestions.append({
                'rank': i + 1,
                'task': task,
                'explanation': explanation
            })
        
        return JsonResponse({
            'suggestions': suggestions,
            'strategy': strategy
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


def generate_explanation(task: dict, rank: int) -> str:
    """Generate human-readable explanation for why task was prioritized."""
    breakdown = task.get('score_breakdown', {})
    reasons = []
    
    # Check urgency
    if breakdown.get('urgency', 0) > 85:
        reasons.append("due very soon or overdue")
    elif breakdown.get('urgency', 0) > 70:
        reasons.append("approaching deadline")
    
    # Check importance
    if breakdown.get('importance', 0) >= 80:
        reasons.append("marked as highly important")
    
    # Check effort
    if breakdown.get('effort', 0) > 80:
        reasons.append("quick win (low effort)")
    
    # Check dependencies
    if breakdown.get('dependencies', 0) > 50:
        reasons.append("blocks other tasks")
    
    # Check for circular dependencies
    if task.get('has_circular_dependency'):
        reasons.append("⚠️ has circular dependency issue")
    
    if not reasons:
        reasons.append("good balance of all factors")
    
    reason_text = ", ".join(reasons)
    return f"Ranked #{rank}: {reason_text.capitalize()}. Score: {task['priority_score']}"
