from django.contrib.auth.models import Permission, ContentType
from aplicacionING.models import Role

# Definir el tipo de contenido para las actividades (asegúrate de que el modelo esté registrado)
content_type = ContentType.objects.get(app_label='aplicacionING', model='activityfolder')  # Ajusta 'activityfolder' si es necesario

# Crear permisos específicos
Permission.objects.get_or_create(codename='crear_actividades', name='Puede crear actividades', content_type=content_type)
Permission.objects.get_or_create(codename='editar_actividades', name='Puede editar actividades', content_type=content_type)
Permission.objects.get_or_create(codename='eliminar_actividades', name='Puede eliminar actividades', content_type=content_type)
Permission.objects.get_or_create(codename='ver_historial', name='Puede ver historial de cambios', content_type=content_type)

# Obtener los permisos creados
crear_actividades = Permission.objects.get(codename='crear_actividades')
editar_actividades = Permission.objects.get(codename='editar_actividades')
eliminar_actividades = Permission.objects.get(codename='eliminar_actividades')
ver_historial = Permission.objects.get(codename='ver_historial')

# Crear roles
admin_role, created = Role.objects.get_or_create(name='Administrador')
equipo_role, created = Role.objects.get_or_create(name='Miembro del Equipo')
externo_role, created = Role.objects.get_or_create(name='Usuario Externo')

# Asignar permisos a los roles
admin_role.permissions.set([crear_actividades, editar_actividades, eliminar_actividades, ver_historial])
equipo_role.permissions.set([crear_actividades, editar_actividades])
externo_role.permissions.set([])

# Guardar roles
admin_role.save()
equipo_role.save()
externo_role.save()
