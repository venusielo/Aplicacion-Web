from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Permission, User

######################################################################################################
# MODELOS PARA GESTIÓN DE ROLES
######################################################################################################

class Role(models.Model):
    """
    Modelo para representar un rol dentro del sistema. Cada rol tiene un nombre y puede tener múltiples permisos.
    """
    name = models.CharField(max_length=50)
    permissions = models.ManyToManyField(Permission, blank=True)  # Permisos asociados al rol
    users = models.ManyToManyField(User, blank=True)  # Usuarios asignados al rol

    def __str__(self):
        return self.name

######################################################################################################
# MODELOS PARA GESTIÓN DE PROYECTOS
######################################################################################################

class ProjectFolder(models.Model):
    """
    Modelo para representar un proyecto. Contiene información básica como nombre, descripción, fechas y el propietario.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación del proyecto
    start_date = models.DateField(null=True, blank=True)  # Fecha de inicio del proyecto
    end_date = models.DateField(null=True, blank=True)  # Fecha de finalización del proyecto
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario propietario del proyecto

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        """
        Sobrescribe el método delete para eliminar todas las actividades asociadas al proyecto antes de eliminar el proyecto.
        """
        self.activities.all().delete()
        super(ProjectFolder, self).delete(*args, **kwargs)

######################################################################################################
# MODELOS PARA GESTIÓN DE ACTIVIDADES
######################################################################################################

class ActivityFolder(models.Model):
    """
    Modelo para representar una actividad dentro de un proyecto. Cada actividad puede tener tareas.
    """
    project = models.ForeignKey(ProjectFolder, on_delete=models.CASCADE, related_name='activities')  # Proyecto al que pertenece la actividad
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subactivities')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)  # Fecha de entrega de la actividad
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación de la actividad
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_activities')  # Usuario asignado
    
    def __str__(self):
        return self.name

    def is_completed(self):
        """
        Verifica si todas las tareas asociadas a la actividad están completadas.
        """
        return all(task.completed for task in self.tasks.all())
    
    def completed_tasks_count(self):
        """
        Cuenta el número de tareas completadas dentro de la actividad.
        """
        return self.tasks.filter(completed=True).count()

    def pending_tasks_count(self):
        """
        Cuenta el número de tareas pendientes dentro de la actividad.
        """
        return self.tasks.filter(completed=False).count()

######################################################################################################
# MODELOS PARA GESTIÓN DE TAREAS
######################################################################################################

class Task(models.Model):
    """
    Modelo para representar una tarea dentro de una actividad.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)  # Fecha de inicio de la tarea
    end_date = models.DateField(null=True, blank=True)  # Fecha de finalización de la tarea
    activity = models.ForeignKey(ActivityFolder, on_delete=models.CASCADE, related_name='tasks')  # Actividad a la que pertenece la tarea
    completed = models.BooleanField(default=False)  # Estado de la tarea

    def __str__(self):
        return self.name

######################################################################################################
# MODELO PARA HISTORIAL DE CAMBIOS
######################################################################################################

class ChangeHistory(models.Model):
    """
    Modelo para registrar el historial de cambios realizados en los proyectos y actividades.
    """
    project = models.ForeignKey(ProjectFolder, null=True, blank=True, on_delete=models.SET_NULL)  # Proyecto relacionado con el cambio
    activity = models.ForeignKey(ActivityFolder, null=True, blank=True, on_delete=models.SET_NULL)  # Actividad relacionada con el cambio
    change_description = models.CharField(max_length=255)  # Descripción del cambio realizado
    change_date = models.DateTimeField(auto_now_add=True)  # Fecha en la que se realizó el cambio
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='change_histories')  # Usuario que realizó el cambio

    def __str__(self):
        return f"{self.change_description} - {self.change_date}"
