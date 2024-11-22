from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Permission, User


class Role(models.Model):
    name = models.CharField(max_length=50)
    permissions = models.ManyToManyField(Permission, blank=True)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name


class ProjectFolder(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        self.activities.all().delete()
        super(ProjectFolder, self).delete(*args, **kwargs)

class ActivityFolder(models.Model):
    project = models.ForeignKey(ProjectFolder, on_delete=models.CASCADE, related_name='activities')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subactivities')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_activities') ###
    
    def __str__(self):
        return self.name

    def is_completed(self):
         return all(task.completed for task in self.tasks.all())
    
    def completed_tasks_count(self):
         return self.tasks.filter(completed=True).count()

    def pending_tasks_count(self):
         return self.tasks.filter(completed=False).count()



    
class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    activity = models.ForeignKey(ActivityFolder, on_delete=models.CASCADE, related_name='tasks')
    completed = models.BooleanField(default=False)
    def __str__(self):
        return self.name



    
class ChangeHistory(models.Model):
    project = models.ForeignKey(ProjectFolder, null=True, blank=True, on_delete=models.SET_NULL)
    activity = models.ForeignKey(ActivityFolder, null=True, blank=True, on_delete=models.SET_NULL)
    change_description = models.CharField(max_length=255)
    change_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='change_histories')

    def __str__(self):
        return f"{self.change_description} - {self.change_date}"
