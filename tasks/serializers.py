from rest_framework import serializers
from .models import Task
from datetime import date


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializes Task model (from database) to/from JSON.
    
    Used for: Reading/writing tasks to database
    """
    
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'due_date',
            'importance',
            'estimated_hours',
            'dependencies',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_title(self, value):
        """Ensure title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value
    
    def validate_due_date(self, value):
        """Ensure due_date is valid date object."""
        if not isinstance(value, date):
            raise serializers.ValidationError("Invalid date format")
        return value
    
    def validate_importance(self, value):
        """Ensure importance is integer between 1-10."""
        if not isinstance(value, int):
            raise serializers.ValidationError("Importance must be an integer")
        if value < 1 or value > 10:
            raise serializers.ValidationError("Importance must be between 1 and 10")
        return value
    
    def validate_estimated_hours(self, value):
        """Ensure estimated_hours is positive number."""
        if not isinstance(value, (int, float)):
            raise serializers.ValidationError("Estimated hours must be a number")
        if value <= 0:
            raise serializers.ValidationError("Estimated hours must be positive")
        return value
    
    def validate_dependencies(self, value):
        """Ensure dependencies is a list."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Dependencies must be a list")
        return value


class AnalyzeTasksRequestSerializer(serializers.Serializer):
    """
    Validates incoming request to POST /api/tasks/analyze/
    """
    
    tasks = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of task dictionaries to analyze"
    )
    
    strategy = serializers.ChoiceField(
        choices=['smart_balance', 'fastest_wins', 'high_impact', 'deadline_driven'],
        default='smart_balance',
        help_text="Sorting strategy to use"
    )


class AnalyzeTasksResponseSerializer(serializers.Serializer):
    """
    Formats response from POST /api/tasks/analyze/
    
    Defines structure of each scored task in response.
    """
    
    id = serializers.IntegerField()
    title = serializers.CharField()
    due_date = serializers.CharField()
    importance = serializers.IntegerField()
    estimated_hours = serializers.FloatField()
    priority_score = serializers.IntegerField()
    urgency = serializers.IntegerField()
    importance_score = serializers.IntegerField()
    effort = serializers.IntegerField()
    dependencies_count = serializers.IntegerField()
    explanation = serializers.CharField()
    priority_level = serializers.CharField()


class SuggestTasksResponseSerializer(serializers.Serializer):
    """
    Formats response from GET/POST /api/tasks/suggest/
    
    Defines structure of each suggestion in response.
    """
    
    title = serializers.CharField()
    reason = serializers.CharField()
    priority = serializers.CharField()
    due_date = serializers.CharField()
    priority_score = serializers.IntegerField()
