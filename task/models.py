from django.db import models

from danbi_edu.const import team_choices


class Task(models.Model):
    create_user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    team = models.CharField(max_length=10, choices=team_choices)
    title = models.CharField(max_length=50)
    content = models.TextField()
    is_complete = models.BooleanField(default=False)
    complete_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class SubTask(models.Model):
    team = models.CharField(max_length=10, choices=team_choices)
    is_complete = models.BooleanField(default=False)
    completed_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    task = models.ForeignKey("task.Task", on_delete=models.CASCADE)