from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group

@receiver(post_migrate)
def init_roles(sender, **kwargs):
    """Función para crear roles predeterminados si no existen."""
    roles = ["Administrador", "Colaborador", "Usuario Externo"]
    for role_name in roles:
        Group.objects.get_or_create(name=role_name)

