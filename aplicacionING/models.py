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
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
#class ChangeHistory(models.Model):
#    project = models.ForeignKey(ProjectFolder, on_delete=models.CASCADE, related_name='change_history')
#    change_description = models.TextField()
#    change_date = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return f"Cambio en {self.project.name} - {self.change_date}"

def get_default_user():
    return User.objects.get(username="sistema").id

class ChangeHistory(models.Model):
    project = models.ForeignKey(ProjectFolder, null=True, blank=True, on_delete=models.SET_NULL)
    activity = models.ForeignKey(ActivityFolder, null=True, blank=True, on_delete=models.SET_NULL)
    change_description = models.CharField(max_length=255)
    change_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=get_default_user)

    def __str__(self):
        return f"{self.change_description} - {self.change_date}"    
