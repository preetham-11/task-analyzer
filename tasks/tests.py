from django.test import TestCase
from datetime import date, timedelta
from .scoring.components import (
    calculate_urgency, calculate_importance, calculate_effort, calculate_dependencies
)
from .scoring.strategies import apply_weights, get_valid_strategies
from .scoring.analyzer import score_single_task, analyze_tasks


class ScoringComponentsTests(TestCase):
    """Test cases for scoring algorithm components."""
    
    # ==================== URGENCY TESTS ====================
    
    def test_calculate_urgency_overdue(self):
        """Test urgency calculation for overdue tasks."""
        past_date = date.today() - timedelta(days=1)
        urgency = calculate_urgency(past_date)
        self.assertEqual(urgency, 100)
    
    def test_calculate_urgency_today(self):
        """Test urgency calculation for tasks due today."""
        urgency = calculate_urgency(date.today())
        self.assertEqual(urgency, 100)
    
    def test_calculate_urgency_near_term(self):
        """Test urgency calculation for tasks due in 1-3 days."""
        near_date = date.today() + timedelta(days=2)
        urgency = calculate_urgency(near_date)
        self.assertEqual(urgency, 50)
    
    def test_calculate_urgency_medium_term(self):
        """Test urgency calculation for tasks due in 4-7 days."""
        medium_date = date.today() + timedelta(days=5)
        urgency = calculate_urgency(medium_date)
        self.assertEqual(urgency, 25)
    
    def test_calculate_urgency_long_term(self):
        """Test urgency calculation for tasks due in 8-14 days."""
        long_date = date.today() + timedelta(days=10)
        urgency = calculate_urgency(long_date)
        self.assertEqual(urgency, 10)
    
    def test_calculate_urgency_far_future(self):
        """Test urgency calculation for tasks due in 15+ days."""
        far_date = date.today() + timedelta(days=20)
        urgency = calculate_urgency(far_date)
        self.assertEqual(urgency, 0)
    
    # ==================== IMPORTANCE TESTS ====================
    
    def test_calculate_importance_valid_range(self):
        """Test importance calculation with valid ratings."""
        self.assertEqual(calculate_importance(1), 10)
        self.assertEqual(calculate_importance(5), 50)
        self.assertEqual(calculate_importance(10), 100)
    
    def test_calculate_importance_edge_cases(self):
        """Test importance calculation with edge cases."""
        self.assertEqual(calculate_importance(0), 10)  # Clamped to 1
        self.assertEqual(calculate_importance(15), 100)  # Clamped to 10
        self.assertEqual(calculate_importance(None), 50)  # Default to 5
    
    # ==================== EFFORT TESTS ====================
    
    def test_calculate_effort_quick_task(self):
        """Test effort calculation for quick tasks (< 1.5 hrs)."""
        self.assertEqual(calculate_effort(1), 15)
        self.assertEqual(calculate_effort(1.4), 15)
    
    def test_calculate_effort_medium_task(self):
        """Test effort calculation for medium tasks (1.5-3 hrs)."""
        self.assertEqual(calculate_effort(1.5), 5)
        self.assertEqual(calculate_effort(2.5), 5)
        self.assertEqual(calculate_effort(3), 5)
    
    def test_calculate_effort_long_task(self):
        """Test effort calculation for long tasks (> 3 hrs)."""
        self.assertEqual(calculate_effort(4), -5)
        self.assertEqual(calculate_effort(10), -5)
    
    def test_calculate_effort_edge_cases(self):
        """Test effort calculation with edge cases."""
        self.assertEqual(calculate_effort(None), 5)  # Default to 2 hrs
        self.assertEqual(calculate_effort("invalid"), 5)  # Invalid input defaults to 2
    
    # ==================== DEPENDENCIES TESTS ====================
    
    def test_calculate_dependencies_none(self):
        """Test dependency calculation with no blocked tasks."""
        self.assertEqual(calculate_dependencies(0), 0)
    
    def test_calculate_dependencies_one(self):
        """Test dependency calculation with one blocked task."""
        self.assertEqual(calculate_dependencies(1), 20)
    
    def test_calculate_dependencies_multiple(self):
        """Test dependency calculation with multiple blocked tasks."""
        self.assertEqual(calculate_dependencies(2), 50)
        self.assertEqual(calculate_dependencies(5), 50)


class ScoringStrategyTests(TestCase):
    """Test cases for scoring strategies and total score calculation."""
    
    # ==================== STRATEGY WEIGHT TESTS ====================
    
    def test_smart_balance_strategy(self):
        """Test smart_balance strategy applies equal weights (all 1x)."""
        # urgency=50, importance=80, effort=5, dependencies=20
        score = apply_weights(50, 80, 5, 20, 'smart_balance')
        expected = 50 + 80 + 5 + 20  # All weights are 1
        self.assertEqual(score, expected)
    
    def test_fastest_wins_strategy(self):
        """Test fastest_wins strategy prioritizes effort (3x weight)."""
        # urgency=50, importance=80, effort=15, dependencies=20
        score = apply_weights(50, 80, 15, 20, 'fastest_wins')
        expected = int(round(50 * 0.5 + 80 * 1 + 15 * 3 + 20 * 1))
        self.assertEqual(score, expected)
    
    def test_high_impact_strategy(self):
        """Test high_impact strategy prioritizes importance (3x weight)."""
        # urgency=50, importance=80, effort=5, dependencies=20
        score = apply_weights(50, 80, 5, 20, 'high_impact')
        expected = int(round(50 * 1 + 80 * 3 + 5 * 0.5 + 20 * 1))
        self.assertEqual(score, expected)
    
    def test_deadline_driven_strategy(self):
        """Test deadline_driven strategy prioritizes urgency (3x weight)."""
        # urgency=50, importance=80, effort=5, dependencies=20
        score = apply_weights(50, 80, 5, 20, 'deadline_driven')
        expected = int(round(50 * 3 + 80 * 1 + 5 * 0.5 + 20 * 1))
        self.assertEqual(score, expected)
    
    def test_invalid_strategy_fallback(self):
        """Test that invalid strategy falls back to smart_balance."""
        score = apply_weights(50, 80, 5, 20, 'invalid_strategy')
        expected = 50 + 80 + 5 + 20  # Falls back to smart_balance
        self.assertEqual(score, expected)
    
    def test_get_valid_strategies(self):
        """Test that all 4 strategies are available."""
        strategies = get_valid_strategies()
        self.assertEqual(len(strategies), 4)
        self.assertIn('smart_balance', strategies)
        self.assertIn('fastest_wins', strategies)
        self.assertIn('high_impact', strategies)
        self.assertIn('deadline_driven', strategies)


class OverallScoringTests(TestCase):
    """Test cases for overall scoring algorithm and task prioritization."""
    
    def test_single_task_scoring(self):
        """Test scoring a single task with all components."""
        task = {
            'id': 1,
            'title': 'Test Task',
            'due_date': str(date.today() + timedelta(days=2)),  # 50 urgency
            'importance': 8,  # 80 importance
            'estimated_hours': 2  # 5 effort
        }
        result = score_single_task(task, [task], 'smart_balance')
        
        # Verify all components are calculated
        self.assertEqual(result['urgency'], 50)
        self.assertEqual(result['importance'], 80)
        self.assertEqual(result['effort'], 5)
        self.assertEqual(result['dependencies'], 0)
        
        # Verify total score (smart_balance: all weights = 1)
        expected_score = 50 + 80 + 5 + 0
        self.assertEqual(result['score'], expected_score)
    
    def test_task_prioritization_by_urgency(self):
        """Test that more urgent tasks get higher priority."""
        tasks = [
            {
                'id': 1,
                'title': 'Urgent Task',
                'due_date': str(date.today() + timedelta(days=1)),  # 50 urgency
                'importance': 5,
                'estimated_hours': 2
            },
            {
                'id': 2,
                'title': 'Less Urgent Task',
                'due_date': str(date.today() + timedelta(days=10)),  # 10 urgency
                'importance': 5,
                'estimated_hours': 2
            }
        ]
        
        result = analyze_tasks(tasks, 'smart_balance')
        
        # First task should have higher priority due to urgency
        self.assertTrue(result['success'])
        self.assertEqual(len(result['results']), 2)
        self.assertEqual(result['results'][0]['title'], 'Urgent Task')
        self.assertGreater(result['results'][0]['priority_score'], 
                          result['results'][1]['priority_score'])
    
    def test_task_prioritization_by_importance(self):
        """Test that more important tasks get higher priority."""
        tasks = [
            {
                'id': 1,
                'title': 'Important Task',
                'due_date': str(date.today() + timedelta(days=10)),
                'importance': 10,  # 100 importance
                'estimated_hours': 2
            },
            {
                'id': 2,
                'title': 'Less Important Task',
                'due_date': str(date.today() + timedelta(days=10)),
                'importance': 3,  # 30 importance
                'estimated_hours': 2
            }
        ]
        
        result = analyze_tasks(tasks, 'smart_balance')
        
        # First task should have higher priority due to importance
        self.assertTrue(result['success'])
        self.assertEqual(result['results'][0]['title'], 'Important Task')
        self.assertGreater(result['results'][0]['priority_score'], 
                          result['results'][1]['priority_score'])
    
    def test_task_prioritization_by_effort(self):
        """Test that quick tasks get bonus points."""
        tasks = [
            {
                'id': 1,
                'title': 'Quick Task',
                'due_date': str(date.today() + timedelta(days=10)),
                'importance': 5,
                'estimated_hours': 1  # 15 effort bonus
            },
            {
                'id': 2,
                'title': 'Long Task',
                'due_date': str(date.today() + timedelta(days=10)),
                'importance': 5,
                'estimated_hours': 5  # -5 effort penalty
            }
        ]
        
        result = analyze_tasks(tasks, 'smart_balance')
        
        # Quick task should have higher priority
        self.assertTrue(result['success'])
        self.assertEqual(result['results'][0]['title'], 'Quick Task')
        self.assertGreater(result['results'][0]['priority_score'], 
                          result['results'][1]['priority_score'])
    
    def test_strategy_affects_prioritization(self):
        """Test that different strategies produce different prioritization."""
        tasks = [
            {
                'id': 1,
                'title': 'Quick Task',
                'due_date': str(date.today() + timedelta(days=10)),
                'importance': 5,
                'estimated_hours': 1  # Quick
            },
            {
                'id': 2,
                'title': 'Important Task',
                'due_date': str(date.today() + timedelta(days=10)),
                'importance': 10,  # Very important
                'estimated_hours': 5
            }
        ]
        
        # With fastest_wins, quick task should win
        result_fastest = analyze_tasks(tasks, 'fastest_wins')
        self.assertEqual(result_fastest['results'][0]['title'], 'Quick Task')
        
        # With high_impact, important task should win
        result_impact = analyze_tasks(tasks, 'high_impact')
        self.assertEqual(result_impact['results'][0]['title'], 'Important Task')
    
    def test_combined_scoring_realistic_scenario(self):
        """Test realistic scenario with multiple factors."""
        tasks = [
            {
                'id': 1,
                'title': 'Critical Bug Fix',
                'due_date': str(date.today()),  # 100 urgency (overdue/today)
                'importance': 9,  # 90 importance
                'estimated_hours': 2  # 5 effort
            },
            {
                'id': 2,
                'title': 'Nice to Have Feature',
                'due_date': str(date.today() + timedelta(days=30)),  # 0 urgency
                'importance': 4,  # 40 importance
                'estimated_hours': 1  # 15 effort
            }
        ]
        
        result = analyze_tasks(tasks, 'smart_balance')
        
        # Critical bug should be prioritized despite nice-to-have being quicker
        self.assertEqual(result['results'][0]['title'], 'Critical Bug Fix')
        
        # Verify the score breakdown
        bug_task = result['results'][0]
        self.assertEqual(bug_task['urgency'], 100)
        self.assertEqual(bug_task['importance_score'], 90)
        self.assertEqual(bug_task['effort'], 5)
        
        # Total should be 195 (100 + 90 + 5 + 0)
        self.assertEqual(bug_task['priority_score'], 195)
