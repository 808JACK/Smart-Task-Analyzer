from django.test import TestCase
from datetime import date, timedelta
from .scoring import TaskScorer


class TaskScorerTestCase(TestCase):
    """Unit tests for the TaskScorer algorithm"""
    
    def setUp(self):
        self.scorer = TaskScorer(strategy='smart_balance')
        self.today = date.today()
    
    def test_urgency_score_past_due(self):
        """Test that past due tasks get maximum urgency"""
        past_date = (self.today - timedelta(days=5)).isoformat()
        score = self.scorer.calculate_urgency_score(past_date)
        self.assertGreater(score, 100, "Past due tasks should have urgency > 100")
    
    def test_urgency_score_due_today(self):
        """Test that tasks due today get very high urgency"""
        today_str = self.today.isoformat()
        score = self.scorer.calculate_urgency_score(today_str)
        self.assertGreaterEqual(score, 90, "Tasks due today should have urgency >= 90")
    
    def test_urgency_score_far_future(self):
        """Test that far future tasks get low urgency"""
        future_date = (self.today + timedelta(days=60)).isoformat()
        score = self.scorer.calculate_urgency_score(future_date)
        self.assertLess(score, 30, "Far future tasks should have low urgency")
    
    def test_effort_score_quick_tasks(self):
        """Test that quick tasks get high effort scores"""
        score = self.scorer.calculate_effort_score(1.5)
        self.assertGreater(score, 80, "Quick tasks should get high effort scores")
    
    def test_effort_score_large_tasks(self):
        """Test that large tasks get lower effort scores"""
        score = self.scorer.calculate_effort_score(20)
        self.assertLess(score, 40, "Large tasks should get lower effort scores")
    
    def test_importance_score_normalization(self):
        """Test that importance is properly normalized to 0-100"""
        score_low = self.scorer.calculate_importance_score(1)
        score_high = self.scorer.calculate_importance_score(10)
        self.assertEqual(score_low, 10, "Importance 1 should map to 10")
        self.assertEqual(score_high, 100, "Importance 10 should map to 100")
    
    def test_dependency_score_no_dependents(self):
        """Test tasks with no dependents get base score"""
        tasks = [
            {'id': '1', 'dependencies': []},
            {'id': '2', 'dependencies': []}
        ]
        score = self.scorer.calculate_dependency_score('1', tasks)
        self.assertEqual(score, 30, "Tasks with no dependents should get base score of 30")
    
    def test_dependency_score_with_dependents(self):
        """Test tasks that block others get higher scores"""
        tasks = [
            {'id': '1', 'dependencies': []},
            {'id': '2', 'dependencies': ['1']},
            {'id': '3', 'dependencies': ['1']}
        ]
        score = self.scorer.calculate_dependency_score('1', tasks)
        self.assertGreater(score, 50, "Tasks blocking others should get higher scores")
    
    def test_circular_dependency_detection(self):
        """Test that circular dependencies are detected"""
        tasks = [
            {'id': '1', 'dependencies': ['2']},
            {'id': '2', 'dependencies': ['3']},
            {'id': '3', 'dependencies': ['1']}
        ]
        circular = self.scorer.detect_circular_dependencies(tasks)
        self.assertEqual(len(circular), 3, "All 3 tasks should be flagged as circular")
    
    def test_no_circular_dependency(self):
        """Test that valid dependency chains are not flagged"""
        tasks = [
            {'id': '1', 'dependencies': []},
            {'id': '2', 'dependencies': ['1']},
            {'id': '3', 'dependencies': ['2']}
        ]
        circular = self.scorer.detect_circular_dependencies(tasks)
        self.assertEqual(len(circular), 0, "Valid chains should not be flagged")
    
    def test_calculate_priority_score(self):
        """Test that priority score is calculated correctly"""
        tasks = [
            {
                'id': '1',
                'title': 'Test Task',
                'due_date': self.today.isoformat(),
                'estimated_hours': 2,
                'importance': 8,
                'dependencies': []
            }
        ]
        result = self.scorer.calculate_priority_score(tasks[0], tasks)
        self.assertIn('priority_score', result)
        self.assertIn('score_breakdown', result)
        self.assertGreater(result['priority_score'], 0)
    
    def test_score_and_sort_tasks(self):
        """Test that tasks are properly scored and sorted"""
        tasks = [
            {
                'id': '1',
                'title': 'Low Priority',
                'due_date': (self.today + timedelta(days=30)).isoformat(),
                'estimated_hours': 10,
                'importance': 3,
                'dependencies': []
            },
            {
                'id': '2',
                'title': 'High Priority',
                'due_date': self.today.isoformat(),
                'estimated_hours': 1,
                'importance': 9,
                'dependencies': []
            }
        ]
        sorted_tasks = self.scorer.score_and_sort_tasks(tasks)
        self.assertEqual(len(sorted_tasks), 2)
        self.assertEqual(sorted_tasks[0]['title'], 'High Priority')
        self.assertGreater(
            sorted_tasks[0]['priority_score'],
            sorted_tasks[1]['priority_score']
        )
    
    def test_strategy_fastest_wins(self):
        """Test that fastest_wins strategy prioritizes low effort"""
        scorer = TaskScorer(strategy='fastest_wins')
        self.assertEqual(scorer.weights['effort'], 0.50)
    
    def test_strategy_high_impact(self):
        """Test that high_impact strategy prioritizes importance"""
        scorer = TaskScorer(strategy='high_impact')
        self.assertEqual(scorer.weights['importance'], 0.60)
    
    def test_strategy_deadline_driven(self):
        """Test that deadline_driven strategy prioritizes urgency"""
        scorer = TaskScorer(strategy='deadline_driven')
        self.assertEqual(scorer.weights['urgency'], 0.60)
    
    def test_missing_data_handling(self):
        """Test that missing or invalid data is handled gracefully"""
        tasks = [
            {
                'id': '1',
                'title': 'Incomplete Task'
                # Missing due_date, estimated_hours, importance
            }
        ]
        result = self.scorer.calculate_priority_score(tasks[0], tasks)
        self.assertIn('priority_score', result)
        self.assertGreater(result['priority_score'], 0)
