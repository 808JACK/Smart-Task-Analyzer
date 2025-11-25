from datetime import date, timedelta
from typing import List, Dict, Set

class TaskScorer:
    """
    Core scoring algorithm for task prioritization.
    This is the MOST IMPORTANT part of the assignment.
    """
    
    def __init__(self, strategy='smart_balance'):
        self.strategy = strategy
        self.weights = self._get_weights()
    
    def _get_weights(self):
        """Configure weights based on strategy"""
        strategies = {
            'smart_balance': {
                'urgency': 0.35,
                'importance': 0.30,
                'effort': 0.15,
                'dependencies': 0.20
            },
            'fastest_wins': {
                'urgency': 0.20,
                'importance': 0.20,
                'effort': 0.50,
                'dependencies': 0.10
            },
            'high_impact': {
                'urgency': 0.15,
                'importance': 0.60,
                'effort': 0.10,
                'dependencies': 0.15
            },
            'deadline_driven': {
                'urgency': 0.60,
                'importance': 0.20,
                'effort': 0.05,
                'dependencies': 0.15
            }
        }
        return strategies.get(self.strategy, strategies['smart_balance'])
    
    def is_weekend(self, check_date: date) -> bool:
        """Check if date falls on weekend (Saturday=5, Sunday=6)"""
        return check_date.weekday() >= 5
    
    def count_business_days(self, start_date: date, end_date: date) -> int:
        """Count business days between two dates (excluding weekends)"""
        if start_date > end_date:
            return 0
        
        business_days = 0
        current = start_date
        
        while current <= end_date:
            if not self.is_weekend(current):
                business_days += 1
            current += timedelta(days=1)
        
        return business_days
    
    def calculate_urgency_score(self, due_date_str: str) -> float:
        """
        Calculate urgency based on due date with date intelligence.
        Considers weekends when calculating urgency.
        Returns 0-100 score where higher = more urgent.
        """
        try:
            if isinstance(due_date_str, str):
                due_date = date.fromisoformat(due_date_str)
            else:
                due_date = due_date_str
            
            today = date.today()
            calendar_days = (due_date - today).days
            
            # Calculate business days (excluding weekends)
            business_days = self.count_business_days(today, due_date)
            
            # If due on weekend, reduce urgency slightly
            weekend_penalty = 0
            if self.is_weekend(due_date):
                weekend_penalty = 5
            
            # Past due: maximum urgency with penalty
            if calendar_days < 0:
                return 100 + min(abs(calendar_days) * 5, 100)
            
            # Due today or tomorrow: very high urgency
            if calendar_days <= 1:
                return 95 - weekend_penalty
            
            # Due within a week: high urgency (use business days)
            if calendar_days <= 7:
                if business_days <= 3:  # 3 or fewer business days
                    return 90 - weekend_penalty
                return 85 - (business_days * 2) - weekend_penalty
            
            # Due within 2 weeks: moderate urgency
            if calendar_days <= 14:
                return 70 - (business_days - 5) * 2 - weekend_penalty
            
            # Due within a month: declining urgency
            if calendar_days <= 30:
                return max(50 - (business_days - 10) * 1.5, 20) - weekend_penalty
            
            # Far future: low urgency
            return max(20 - (calendar_days - 30) * 0.5, 5)
            
        except (ValueError, TypeError):
            return 50  # Default if date is invalid
    
    def calculate_effort_score(self, estimated_hours: float) -> float:
        """
        Calculate effort score. Lower effort = higher score for quick wins.
        Returns 0-100 score.
        """
        if estimated_hours <= 0:
            return 50
        
        # Quick tasks (< 2 hours) get high scores
        if estimated_hours < 2:
            return 90
        
        # Medium tasks (2-8 hours)
        if estimated_hours <= 8:
            return 70 - (estimated_hours - 2) * 5
        
        # Large tasks (8+ hours)
        return max(30 - (estimated_hours - 8) * 2, 10)
    
    def calculate_importance_score(self, importance: int) -> float:
        """
        Normalize importance (1-10) to 0-100 scale.
        """
        return min(max(importance, 1), 10) * 10
    
    def calculate_dependency_score(self, task_id: str, all_tasks: List[Dict]) -> float:
        """
        Calculate dependency score based on how many tasks depend on this one.
        Returns 0-100 score.
        """
        # Count how many tasks list this task as a dependency
        dependent_count = sum(
            1 for t in all_tasks 
            if task_id in t.get('dependencies', [])
        )
        
        if dependent_count == 0:
            return 30  # Base score
        
        # More dependents = higher score (blocking tasks)
        return min(30 + (dependent_count * 25), 100)
    
    def detect_circular_dependencies(self, tasks: List[Dict]) -> Set[str]:
        """
        Detect circular dependencies using DFS.
        Returns set of task IDs involved in cycles.
        """
        task_map = {t['id']: t.get('dependencies', []) for t in tasks}
        circular = set()
        
        def has_cycle(task_id, visited, rec_stack):
            visited.add(task_id)
            rec_stack.add(task_id)
            
            for dep in task_map.get(task_id, []):
                if dep not in visited:
                    if has_cycle(dep, visited, rec_stack):
                        circular.add(task_id)
                        return True
                elif dep in rec_stack:
                    circular.add(task_id)
                    circular.add(dep)
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        visited = set()
        for task_id in task_map:
            if task_id not in visited:
                has_cycle(task_id, visited, set())
        
        return circular
    
    def calculate_priority_score(self, task: Dict, all_tasks: List[Dict]) -> Dict:
        """
        Main scoring function. Returns task with added score and breakdown.
        """
        # Extract task data with defaults
        task_id = task.get('id', str(hash(task.get('title', ''))))
        due_date = task.get('due_date', str(date.today() + timedelta(days=30)))
        estimated_hours = task.get('estimated_hours', 5)
        importance = task.get('importance', 5)
        
        # Calculate individual scores
        urgency = self.calculate_urgency_score(due_date)
        effort = self.calculate_effort_score(estimated_hours)
        importance_score = self.calculate_importance_score(importance)
        dependency = self.calculate_dependency_score(task_id, all_tasks)
        
        # Calculate weighted final score
        final_score = (
            urgency * self.weights['urgency'] +
            importance_score * self.weights['importance'] +
            effort * self.weights['effort'] +
            dependency * self.weights['dependencies']
        )
        
        # Add score and breakdown to task
        task['priority_score'] = round(final_score, 2)
        task['score_breakdown'] = {
            'urgency': round(urgency, 1),
            'importance': round(importance_score, 1),
            'effort': round(effort, 1),
            'dependencies': round(dependency, 1),
            'final': round(final_score, 2)
        }
        
        return task
    
    def score_and_sort_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """
        Score all tasks and return them sorted by priority.
        """
        # Check for circular dependencies
        circular = self.detect_circular_dependencies(tasks)
        
        # Score each task
        scored_tasks = []
        for task in tasks:
            scored_task = self.calculate_priority_score(task, tasks)
            
            # Flag circular dependencies
            task_id = task.get('id', str(hash(task.get('title', ''))))
            if task_id in circular:
                scored_task['has_circular_dependency'] = True
            
            scored_tasks.append(scored_task)
        
        # Sort by priority score (descending)
        return sorted(scored_tasks, key=lambda x: x['priority_score'], reverse=True)
