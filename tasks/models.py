from django.db import models
from datetime import date

class Task(models.Model):
    """
    Task model to store task information in database.
    
    Fields:
    - title: Name of the task
    - due_date: When the task is due
    - importance: Rating from 1-10 (how critical is it?)
    - estimated_hours: How long the task will take
    - dependencies: JSON list of task IDs this task depends on
    - created_at: When the task was created
    """
    
    title = models.CharField(
        max_length=255,
        help_text="Title of the task"
    )
    
    due_date = models.DateField(
        help_text="Date when task is due"
    )
    
    importance = models.IntegerField(
        default=5,
        help_text="Importance rating from 1-10"
    )
    
    estimated_hours = models.FloatField(
        default=2,
        help_text="Estimated hours to complete"
    )
    
    dependencies = models.JSONField(
        default=list,
        blank=True,
        help_text="List of task IDs this task depends on"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this task was created"
    )
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
