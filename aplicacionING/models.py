from django.db import models
from django.utils import timezone

class ProjectFolder(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ActivityFolder(models.Model):
    project = models.ForeignKey(ProjectFolder, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class ChangeHistory(models.Model):
    project = models.ForeignKey(ProjectFolder, on_delete=models.CASCADE, related_name='change_history')
    change_description = models.TextField()
    change_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cambio en {self.project.name} - {self.change_date}"
    
