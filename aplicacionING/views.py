from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import ProjectFolder, ChangeHistory, ActivityFolder
from .forms import ProjectFolderForm, ActivityFolderForm, RegistroForm,RoleForm
from .models import Role, ProjectFolder, ActivityFolder
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

from datetime import date, datetime


def custom_logout_view(request):
    logout(request)
    return redirect('login')  

@user_passes_test(lambda u: u.is_superuser)
def ver_usuarios(request):
    users = User.objects.all()
    roles = Group.objects.all()  # Obtener todos los grupos como roles
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        selected_role_id = request.POST.get(f"roles_{user_id}")
        if user_id and selected_role_id:
            user = User.objects.get(id=user_id)
            role = Group.objects.get(id=selected_role_id)
            
            # Elimina todos los grupos previos del usuario y asigna el nuevo
            user.groups.clear()
            user.groups.add(role)
        return redirect('ver_usuarios')
    return render(request, 'ver_usuarios.html', {'users': users, 'roles': roles})


@login_required
def ver_permisos(request):
    permisos_generales = {
        'Administrador': ["Crear", "Editar", "Eliminar", "Ver historial"],
        'Miembro del equipo': ["Editar"],
        'Usuario externo': ["Ver"]
    }
    
    request.user.refresh_from_db()

    # Determina el rol actual del usuario
    if request.user.is_superuser:
        rol = 'Administrador'
    elif request.user.groups.filter(name='Miembro del equipo').exists():
        rol = 'Miembro del equipo'
    else:
        rol = 'Usuario externo'
    
    # Obtiene los permisos generales en función del rol del usuario
    permisos_usuario = permisos_generales.get(rol, [])

    return render(request, 'ver_permisos.html', {'permisos_usuario': permisos_usuario, 'rol': rol})
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



@login_required
def home(request):
    es_miembro_equipo = request.user.groups.filter(name="Miembro del Equipo").exists() if request.user.is_authenticated else False
    context = {
        'es_miembro_equipo': es_miembro_equipo
    }
    return render(request, 'home.html', context)

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
    
    return redirect('proyecto_detalle', proyecto_id=proyecto_id)

@login_required
def create_project_folder(request):
    if request.method == 'POST':
        form = ProjectFolderForm(request.POST)
        if form.is_valid():
            project = form.save()
            

            ChangeHistory.objects.create(
                project = project,
                change_description = f"Se creó el proyecto {project.name}"
            )
            return redirect('list_project_folders')
    else:
        form = ProjectFolderForm()
    return render(request, 'create_project_folder.html', {'form': form})

@login_required
def list_project_folders(request):
    projects = ProjectFolder.objects.all()
    if not projects:
        message = "Aun no tienes proyectos"
        return render(request, 'carpetas.html', {'message': message})
    return render(request, 'carpetas.html', {'projects': projects})


@login_required
def create_project(request):
    if not request.user.is_superuser:
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
  
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Verifica si el usuario seleccionó la opción de administrador
            is_admin = request.POST.get('is_admin')
            if is_admin:
                user.is_superuser = True  # Esto convierte al usuario en superusuario
            user.save()
            
            # Asigna el rol correspondiente
            if is_admin:
                admin_role = Role.objects.get(name="Administrador")
                user.role_set.add(admin_role)
                messages.success(request, 'Te has registrado como administrador.')
            else:
                external_role = Role.objects.get(name="Usuario Externo")
                user.role_set.add(external_role)
                messages.success(request, 'Registro exitoso. Bienvenido a CatNest.')

            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroForm()
    return render(request, 'registration/registro.html', {'form': form})


@login_required
def change_history(request):
    history = ChangeHistory.objects.all().order_by('-change_date')
    return render(request, 'change_history.html', {'history': history})

@login_required
def OpenProject(request, project_id):
    project = get_object_or_404(ProjectFolder, id=project_id)
    # Verificar si el usuario es miembro del equipo o superusuario
    es_miembro_equipo = request.user.groups.filter(name="Miembro del Equipo").exists() or request.user.is_superuser
    
    return render(request, 'OpenProject.html', {'project': project, 'es_miembro_equipo': es_miembro_equipo})

@login_required
def DeleteProject(request, project_id):
    project = get_object_or_404(ProjectFolder, id=project_id)
    
    if request.method == 'POST':
        project_name = project.name
        print(f"Intentando eliminar el proyecto: {project_name}")  # Mensaje de depuración
        
        ChangeHistory.objects.create(
            project=project,
            change_description=f'Se eliminó el proyecto {project_name}'
        )

        project.activities.all().delete()
        # Eliminar el proyecto
        project.delete()
        
        print(f"Proyecto {project_name} eliminado de la base de datos.")  # Confirmación en consola
        messages.success(request, f'El proyecto "{project_name}" ha sido eliminado exitosamente.')

        return redirect('home')
    
    # Si la solicitud no es POST, simplemente redirige
    return redirect('home')

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
def delete_activity(request, activity_id, project_id):
    activity = get_object_or_404(ActivityFolder, id=activity_id)

    if request.method == 'POST':
        activity.delete()
        return redirect('OpenProject', project_id=project_id)
    

def delete_activity(request, activity_id, project_id):
    activity = get_object_or_404(ActivityFolder, id=activity_id)

    if request.method == 'POST':
        activity.delete()
        return redirect('OpenProject', project_id=project_id)
    
def ver_historial(request):
    historial = ChangeHistory.objects.filter(project__owner=request.user).order_by('-change_date')
    return render(request, 'change_history.html', {'change_history': change_history})


def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="registered_users.csv"'

    writer = csv.writer(response)

    writer.writerow(['Usuario','Rol', 'Email', 'Date Joined'])

    users = User.objects.all()
    for user in users:
        # Determina el rol actual del usuario
        if request.user.is_superuser:
            rol = 'Administrador'
        elif request.user.groups.filter(name='Miembro del equipo').exists():
            rol = 'Miembro del equipo'
        else:
            rol = 'Usuario externo'

        date_joined = user.date_joined.strftime('%Y-%m-%d %H:%M')
        writer.writerow([user.username, rol, user.email, date_joined])

    return response

def eliminar_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('ver_usuarios') 

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

def delete_role(request, role_id):
    # Obtener el rol a eliminar y luego eliminarlo
    role = get_object_or_404(Role, id=role_id)
    role.delete()
    return redirect('administrar_roles')  # Redirige de nuevo a la página de administración de roles

def delete_permission(request, role_id, permission_id):
    # Obtener el rol y el permiso
    role = get_object_or_404(Role, id=role_id)
    permission = get_object_or_404(Permission, id=permission_id)
    # Remover el permiso del rol (sin eliminar el permiso de la base de datos)
    role.permissions.remove(permission)
    return redirect('administrar_roles')  # Redirige de nuevo a la página de administración de roles


def OpenProject(request, project_id):
    project = get_object_or_404(ProjectFolder, id=project_id)
    today = date.today()

    # Obtener todas las actividades relacionadas con el proyecto
    activities = project.activities.filter(parent=None)
    
    # Separar actividades en 'atrasadas' y 'por entregar'
    atrasadas = activities.filter(due_date__lt=today)
    por_entregar = activities.filter(due_date__gte=today)
    
    # Verificación de si el usuario tiene permisos para modificar
    es_miembro_equipo = request.user.is_superuser or request.user.groups.filter(name="Miembro del Equipo").exists()
    
    # Manejar la creación de una sub-actividad
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        
        parent_activity = ActivityFolder.objects.get(id=parent_id) if parent_id else None
        new_activity = ActivityFolder(
            project=project,
            parent=parent_activity,
            name=name,
            description=description,
            due_date=due_date
        )
        new_activity.save()
        return redirect('OpenProject', project_id=project_id)

    return render(request, 'OpenProject.html', {
        'project': project,
        'today': today,
        'atrasadas': atrasadas,
        'por_entregar': por_entregar,
        'es_miembro_equipo': es_miembro_equipo
    })


@login_required
def delete_activity(request, project_id, activity_id):
    activity = get_object_or_404(ActivityFolder, id=activity_id)

    if request.method == 'POST':
        activity.delete()
        return redirect('OpenProject', project_id=project_id)
    return redirect('OpenProject', project_id=project_id)

