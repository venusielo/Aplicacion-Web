from django.db import models

# Create your models here.
from django.db import models

class Carpeta(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre de la carpeta
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    # Puedes agregar otros campos según tus necesidades

    def __str__(self):
        return self.nombre
