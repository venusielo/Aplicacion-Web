from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import ProjectFolder, ChangeHistory, ActivityFolder
from .forms import ProjectFolderForm, ActivityFolderForm, RegistroForm,RoleForm,TaskForm
from .models import Role, ProjectFolder, ActivityFolder, Task
from django.contrib.auth.models import Permission,User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth import logout

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

import csv
from django.http import HttpResponse
from django.contrib.auth.models import User

from django.utils.timezone import now


###################################################################################################### VENTANA PARA INICIAR SESION
def custom_logout_view(request):
    logout(request)
    return redirect('login')  

def init_roles():
    roles = ["Administrador", "Colaborador", "Usuario Externo"]
    for role_name in roles:
        Group.objects.get_or_create(name=role_name)

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # Obtén los valores de las casillas
            is_admin = request.POST.get('is_admin')
            is_collaborator = request.POST.get('is_collaborator')

            # Guarda el usuario primero antes de asignar roles
            user.save()

            # Asigna el rol según la selección del usuario
            if is_admin:
                user.is_superuser = True
                admin_group = Group.objects.get(name="Administrador")
                user.groups.add(admin_group)
                messages.success(request, 'Te has registrado como administrador.')
            elif is_collaborator:
                collaborator_group = Group.objects.get(name="Colaborador")
                user.groups.add(collaborator_group)
                messages.success(request, 'Te has registrado como colaborador.')
            else:
                external_group = Group.objects.get(name="Usuario Externo")
                user.groups.add(external_group)
                messages.success(request, 'Registro exitoso. Bienvenido a CatNest.')

            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroForm()
    return render(request, 'registration/registro.html', {'form': form})


@login_required
def home(request):
    es_admin = request.user.groups.filter(name="Administrador").exists()
    es_colaborador = request.user.groups.filter(name="Colaborador").exists()
    
    context = {
        'es_admin': es_admin,
        'es_colaborador': es_colaborador
    }
    return render(request, 'home.html', context)


@login_required
def ver_permisos(request):
    # Define los permisos para cada rol
    permisos_generales = {
        'Administrador': ["Crear", "Editar", "Eliminar", "Ver historial"],
        'Colaborador': ["Editar", "Ver historial"],
        'Usuario externo': ["Ver"]
    }
    
    request.user.refresh_from_db()
    
    # Determina el rol actual del usuario usando el modelo `Role`
    roles_usuario = request.user.groups.all()
    
    # Por defecto, asignamos el rol a "Usuario externo"
    rol = "Usuario externo"
    
    if request.user.is_superuser:
        rol = "Administrador"
    elif roles_usuario.filter(name="Colaborador").exists():
        rol = "Colaborador"
    elif roles_usuario.filter(name="Administrador").exists():
        rol = "Administrador"

    # Obtiene los permisos según el rol del usuario
    permisos_usuario = permisos_generales.get(rol, [])

    return render(request, 'ver_permisos.html', {
        'permisos_usuario': permisos_usuario,
        'rol': rol
    })



###################################################################################################### CREAR PROYECTOS.
@login_required
def create_project_folder(request):
    if request.method == 'POST':
        form = ProjectFolderForm(request.POST)
        if form.is_valid():
            project = form.save()
            

            ChangeHistory.objects.create(
                project = project,
                change_description = f"Proyecto {project.name} creado"
            )
            return redirect('list_project_folders')
    else:
        form = ProjectFolderForm()
    return render(request, 'create_project_folder.html', {'form': form})


@login_required
def create_project(request):
    if not request.user.groups.filter(name="Administrador").exists():
        messages.warning(request, 'Se requieren permisos de administrador para crear un proyecto.')
        return redirect('home')

    if request.method == 'POST':
        form = ProjectFolderForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user  # Asigna el usuario actual como propietario
            project.save()

            ChangeHistory.objects.create(
                project=project,
                change_description="Proyecto creado"
            )

            messages.success(request, 'Proyecto creado exitosamente.')
            return redirect('home')
    else:
        form = ProjectFolderForm()

    return render(request, 'CreateProject.html', {'form': form})



###################################################################################################### VER PROYECTOS.
@login_required
def list_project_folders(request):
    projects = ProjectFolder.objects.all()
    if not projects:
        message = "Aun no tienes proyectos"
        return render(request, 'carpetas.html', {'message': message})
    return render(request, 'carpetas.html', {'projects': projects})



@login_required
def OpenProject(request, project_id):
    project = get_object_or_404(ProjectFolder, id=project_id)
    today = now().date() 

     # Obtener todas las actividades principales relacionadas con el proyecto
    activities = project.activities.filter(parent=None)

    # Filtrar actividades según las condiciones especificadas
    atrasadas = [
        activity for activity in activities if activity.due_date < today and not all(task.completed for task in activity.tasks.all())
    ]
    por_entregar = [
        activity for activity in activities if activity.due_date >= today and not all(task.completed for task in activity.tasks.all())
    ]
    completadas = [
        activity for activity in activities if all(task.completed for task in activity.tasks.all())
    ]

    # Manejar la creación de una sub-actividad o marcar tareas como completadas
    if request.method == 'POST':
        if 'parent_id' in request.POST:  # Sub-actividad
            parent_id = request.POST.get('parent_id')
            name = request.POST.get('name')
            description = request.POST.get('description')
            due_date = request.POST.get('due_date')
            assigned_to_id = request.POST.get('assigned_to')

            parent_activity = ActivityFolder.objects.get(id=parent_id) if parent_id else None
            assigned_to = User.objects.get(id=assigned_to_id) if assigned_to_id else None

            ActivityFolder.objects.create(
                project=project,
                parent=parent_activity,
                name=name,
                description=description,
                due_date=due_date,
                assigned_to=assigned_to
            )
        elif 'mark_complete' in request.POST:  # Marcar tarea como completada
            task_id = request.POST.get('task_id')
            task = Task.objects.get(id=task_id)
            task.completed = True
            task.save()

        return redirect('OpenProject', project_id=project_id)

    return render(request, 'OpenProject.html', {
        'project': project,
        'atrasadas': atrasadas,
        'por_entregar': por_entregar,
        'completadas': completadas,
        'users': User.objects.all(),  # Para asignar usuarios
        'today': today,
    })


@login_required
def mark_task_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.completed = not task.completed
        task.save()

        # Verificar si todas las tareas de la actividad están completas
        activity = task.activity
        if all(t.completed for t in activity.tasks.all()):
            activity.completed = True
            activity.save()

        return redirect('OpenProject', project_id=activity.project.id)


@login_required
def modificar_proyecto(request, proyecto_id):
    project = get_object_or_404(ProjectFolder, id=proyecto_id)
    if request.method == "POST":
        project.name = request.POST.get('name')
        project.description = request.POST.get('description')
        project.save()

        ChangeHistory.objects.create(
            project=project,
            change_description="El proyecto fue modificado"
        )
    
    return redirect('OpenProject', project_id=proyecto_id)


@csrf_exempt
def update_project(request, project_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = ProjectFolder.objects.get(id=project_id)
        project.name = data.get('name', project.name)
        project.description = data.get('description', project.description)
        project.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
def DeleteProject(request, project_id):
    if not request.user.is_superuser:
        messages.warning(request, 'Se requieren permisos de administrador para eliminar un proyecto.')
        return redirect('home')

    project = get_object_or_404(ProjectFolder, id=project_id)
    
    if request.method == 'POST':
        project_name = project.name

        ChangeHistory.objects.create(
            project=project,
            change_description=f'Proyecto {project_name} eliminado'
        )

        project.activities.all().delete()
        project.delete()

        messages.success(request, f'El proyecto "{project_name}" ha sido eliminado exitosamente.')

        return redirect('home')
    
    return redirect('home')

############################################# OPCIONES DENTRO DEL PROYECTO.
@login_required
def create_activity_folder(request, project_id):
    project = get_object_or_404(ProjectFolder, id=project_id)

    if request.method == 'POST':
        form = ActivityFolderForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.project = project
            activity.save()

            ChangeHistory.objects.create(
                project=project,
                activity=activity,
                change_description=f"Actividad '{activity.name}' creada en el proyecto '{project.name}'"
            )

            return redirect('OpenProject', project_id=project_id)
        else:
            print(form.errors)
    else:
        form = ActivityFolderForm(initial={'project': project})

    return render(request, 'create_activity.html', {'form': form, 'project': project})



@login_required
def open_activity(request, activity_id):
    activity = get_object_or_404(ActivityFolder, id=activity_id)
    return render(request, 'create_activity.html', {'activity': activity})

@login_required
def delete_activity(request, project_id, activity_id):
    activity = get_object_or_404(ActivityFolder, id=activity_id)

    if request.method == 'POST':
        activity.delete()
        return redirect('OpenProject', project_id=project_id)
    return redirect('OpenProject', project_id=project_id)

###################################################################################################### HISTORIAL DE CAMBIOS.
@login_required
def change_history(request):
    history = ChangeHistory.objects.all().order_by('-change_date')
    return render(request, 'change_history.html', {'history': history})


def ver_historial(request):
    historial = ChangeHistory.objects.filter(project__owner=request.user).order_by('-change_date')
    return render(request, 'change_history.html', {'change_history': change_history})



###################################################################################################### VER USUARIOS REGISTRADOS.
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=["Administrador", "Colaborador"]).exists())
def ver_usuarios(request):
    # Inicializa los roles al cargar la página
    init_roles()

    users = User.objects.all()
    roles = Group.objects.all()

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        selected_role_id = request.POST.get(f"roles_{user_id}")

        if user_id and selected_role_id:
            try:
                user = User.objects.get(id=user_id)
                role = Group.objects.get(id=selected_role_id)

                # Limpia los grupos previos del usuario y asigna el nuevo
                user.groups.clear()
                user.groups.add(role)
                user.save()

                messages.success(request, f'Rol actualizado para el usuario {user.username}')
            except User.DoesNotExist:
                messages.error(request, 'Usuario no encontrado.')
            except Group.DoesNotExist:
                messages.error(request, 'Rol no encontrado.')

        return redirect('ver_usuarios')

    return render(request, 'ver_usuarios.html', {'users': users, 'roles': roles})



def eliminar_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('ver_usuarios') 


def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="registered_users.csv"'

    writer = csv.writer(response)
    writer.writerow(['Usuario', 'Rol', 'Correo', 'Fecha de registro'])

    users = User.objects.all()
    for user in users:
        # Obtenemos el rol del usuario.
        roles_usuario = user.groups.all()
        
        if user.is_superuser or roles_usuario.filter(name="Administrador").exists():
            rol = "Administrador"
        elif roles_usuario.filter(name="Colaborador").exists():
            rol = "Colaborador"
        else:
            rol = "Usuario Externo"


        # Formatear la fecha de creación del usuario
        date_joined = user.date_joined.strftime('%Y-%m-%d %H:%M')
        
        # Escribir la fila en el archivo CSV
        writer.writerow([user.username, rol, user.email, date_joined])

    return response



###################################################################################################### ADMINISTRAR ROLES.
def administrar_roles(request):
    # Obtener todos los roles de la base de datos
    roles = Role.objects.all()
    # Pasar los roles al template
    context = {'roles': roles}
    return render(request, 'administrar_roles.html', context)

def add_role(request):
    if request.method == 'POST':
        new_role = Role(name=request.POST['role_name'])
        print("Role name:", new_role)  # Depuración
        if new_role:
            Role.objects.create(name=new_role)
    return redirect('administrar_roles')

from django.contrib.contenttypes.models import ContentType


@user_passes_test(lambda u: u.is_superuser)
def crear_rol(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ver_roles')
    else:
        form = RoleForm()
    return render(request, 'crear_rol.html', {'form': form})


def delete_role(request, role_id):
    # Obtener el rol a eliminar y luego eliminarlo
    role = get_object_or_404(Role, id=role_id)
    role.delete()
    return redirect('administrar_roles')  # Redirige de nuevo a la página de administración de roles

def add_permission(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    if request.method == 'POST':
        # Obtener el nombre del permiso desde el formulario
        permission_name = request.POST.get('permission_name')
        
        if permission_name:
            # Intentar obtener un permiso existente
            content_type = ContentType.objects.get_for_model(Role)
            permission, created = Permission.objects.get_or_create(
                codename=permission_name.lower().replace(" ", "_"),
                name=permission_name,
                content_type=content_type
            )
            # Añadir el permiso al rol
            role.permissions.add(permission)
        
    return redirect('administrar_roles')

def delete_permission(request, role_id, permission_id):
    # Obtener el rol y el permiso
    role = get_object_or_404(Role, id=role_id)
    permission = get_object_or_404(Permission, id=permission_id)
    # Remover el permiso del rol (sin eliminar el permiso de la base de datos)
    role.permissions.remove(permission)
    return redirect('administrar_roles')  # Para permanecer en la pagina


###################################################################################################### 

from django.http import HttpResponseRedirect

@login_required
def mark_task_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.completed = not task.completed
        task.save()
        # Verificar si todas las tareas de la actividad están completadas
        if task.activity.is_completed():
            task.activity.completed = True  # Mover la actividad a "completadas"
            task.activity.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def create_task(request, activity_id):
    activity = get_object_or_404(ActivityFolder, id=activity_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.activity = activity
            task.save()
            messages.success(request, "Tarea creada exitosamente.")
            return redirect('OpenProject', project_id=activity.project.id)
    else:
        form = TaskForm()
    return render(request, 'create_task.html', {'form': form, 'activity': activity})

