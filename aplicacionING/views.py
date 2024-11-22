from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import ProjectFolder, ChangeHistory, ActivityFolder
from .forms import ProjectFolderForm, ActivityFolderForm, RegistroForm,EditActivityForm,TaskForm
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

def create_project_folder(request):
    if request.method == 'POST':
        form = ProjectFolderForm(request.POST)
        if form.is_valid():
            project = form.save()
            

            ChangeHistory.objects.create(
                project = project,
                change_description = f"Proyecto {project.name} creado",
                user=request.user
            )
            return redirect('list_project_folders')
    else:
        form = ProjectFolderForm()
    return render(request, 'create_project_folder.html', {'form': form})



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
                change_description="Proyecto creado",
                user=request.user
            )

            messages.success(request, 'Proyecto creado exitosamente.')
            return redirect('home')
    else:
        form = ProjectFolderForm()

    return render(request, 'CreateProject.html', {'form': form})



###################################################################################################### VER PROYECTOS.

def list_project_folders(request):
    projects = ProjectFolder.objects.all()
    if not projects:
        message = "Aun no tienes proyectos"
        return render(request, 'carpetas.html', {'message': message})
    return render(request, 'carpetas.html', {'projects': projects})




def OpenProject(request, project_id):
    project = get_object_or_404(ProjectFolder, id=project_id)
    today = now().date() 

    # Obtener todas las actividades principales relacionadas con el proyecto
    activities = project.activities.filter(parent=None)

    # Filtrar actividades según las condiciones especificadas
    atrasadas = sorted(
    [
        activity for activity in activities if activity.due_date < today and (
            not activity.tasks.exists() or not all(task.completed for task in activity.tasks.all())
        )
    ],
    key=lambda x: x.due_date
    )

    # Cálculo de días de atraso
    for activity in atrasadas:
        activity.dias_atraso = (today - activity.due_date).days

    completadas = sorted(
    [
        activity for activity in activities if activity.tasks.exists() and all(task.completed for task in activity.tasks.all())
    ],
    key=lambda x: x.due_date
    )

    por_entregar = sorted(
    [
        activity for activity in activities if activity not in completadas and activity.due_date >= today and (
            not activity.tasks.exists() or not all(task.completed for task in activity.tasks.all())
        )
    ],
    key=lambda x: x.due_date
    )
    

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
            # Registro del cambio
            ChangeHistory.objects.create(
                project=project,
                change_description=f"Actividad '{name}' creada",
                user=request.user
            )
        elif 'mark_complete' in request.POST:  # Marcar tarea como completada
            task_id = request.POST.get('task_id')
            task = Task.objects.get(id=task_id)
            task.completed = True
            task.save()
            # Registro del cambio
            ChangeHistory.objects.create(
                project=project,
                change_description=f"Tarea '{task.name}' marcada como completada",
                user=request.user
            )

        return redirect('OpenProject', project_id=project_id)

    return render(request, 'OpenProject.html', {
        'project': project,
        'atrasadas': atrasadas,
        'por_entregar': por_entregar,
        'completadas': completadas,
        'users': User.objects.all(),
        'today': today,
    })



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
def edit_project(request, project_id):
    project = get_object_or_404(ProjectFolder, id=project_id)
    if request.method == 'POST':
        project_name = project.name
        form = ProjectFolderForm(request.POST, instance=project)

        ChangeHistory.objects.create(
            project=project,
            change_description=f'Proyecto {project_name} modificado',
            user=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Proyecto actualizado exitosamente.')
            return redirect('list_project_folders')
    else:
        form = ProjectFolderForm(instance=project)
    return render(request, 'edit_project.html', {'form': form, 'project': project})


def DeleteProject(request, project_id):
    """
    Vista para eliminar un proyecto. Solo los administradores pueden eliminar.
    """
    project = get_object_or_404(ProjectFolder, id=project_id)
    
    if request.method == 'POST':
        project_name = project.name

        # Registrar el cambio en el historial
        ChangeHistory.objects.create(
            project=project,
            change_description=f'Proyecto {project_name} eliminado',
            user=request.user
        )

        # Eliminar el proyecto
        project.delete()

        # Mensaje de éxito
        messages.success(request, f'El proyecto "{project_name}" ha sido eliminado exitosamente.')

        # Redirigir al listado de proyectos
        return redirect('list_project_folders')
    
    # En caso de que no sea un POST, redirige al listado de proyectos
    return redirect('list_project_folders')


############################################# OPCIONES DENTRO DEL PROYECTO.

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
                change_description=f"Actividad '{activity.name}' creada en el proyecto '{project.name}'",
                user=request.user # Aquí asignamos el usuario que realiza el cambio
             )

            return redirect('OpenProject', project_id=project_id)
        else:
            print(form.errors)
    else:
        form = ActivityFolderForm(initial={'project': project})

    return render(request, 'create_activity.html', {'form': form, 'project': project})


def open_activity(request, activity_id):
    activity = get_object_or_404(ActivityFolder, id=activity_id)
    return render(request, 'create_activity.html', {'activity': activity})
def edit_activity(request, project_id, activity_id):
    activity = get_object_or_404(ActivityFolder, id=activity_id)

    if request.method == 'POST':
        form = EditActivityForm(request.POST, instance=activity)
        if form.is_valid():
            old_due_date = activity.due_date  # Guardar la fecha de vencimiento actual antes de actualizar
            activity = form.save()  # Guardar la actividad y actualizar la instancia

            # Comparar si la fecha de vencimiento ha cambiado
            if old_due_date != activity.due_date:
                ChangeHistory.objects.create(
                    project=activity.project,
                    activity=activity,
                    change_description=f"Fecha de vencimiento de la actividad '{activity.name}' cambiada de {old_due_date} a {activity.due_date}",
                    user=request.user
                )

            messages.success(request, f"Actividad '{activity.name}' actualizada exitosamente.")
            return redirect('OpenProject', project_id=project_id)
    else:
        form = EditActivityForm(instance=activity)

    return render(request, 'edit_activity.html', {'form': form, 'activity': activity, 'project_id': project_id})


def delete_activity(request, project_id, activity_id):
    activity = get_object_or_404(ActivityFolder, id=activity_id)

    ChangeHistory.objects.create(
                activity=activity,
                change_description=f"Actividad '{activity.name}' eliminada",
                user=request.user
             )


    if request.method == 'POST':
        activity.delete()
        return redirect('OpenProject', project_id=project_id)
    
    return redirect('OpenProject', project_id=project_id)

###################################################################################################### HISTORIAL DE CAMBIOS.

def change_history(request):
    # Obtener los parámetros de orden y tipo de cambio de la solicitud
    order = request.GET.get('order', 'desc')  # Por defecto, orden descendente
    tipo = request.GET.get('tipo', 'todos')  # Por defecto, todos los tipos de cambios

    # Determinar el tipo de orden
    if order == 'asc':
        history = ChangeHistory.objects.all().order_by('change_date')
    else:
        history = ChangeHistory.objects.all().order_by('-change_date')

    # Filtrar por tipo de cambio si es necesario
    if tipo == 'actividad':
        history = history.filter(change_description__icontains='Actividad')
    elif tipo == 'tarea':
        history = history.filter(change_description__icontains='Tarea')

    
    es_admin = request.user.is_superuser or request.user.groups.filter(name="Administrador").exists()

    # Pasar la orden actual y el tipo al contexto para su uso en el template
    context = {
        'history': history,
        'current_order': order,
        'current_tipo': tipo,
        'es_admin': es_admin
    }
    return render(request, 'change_history.html', context)


@login_required
def delete_history(request):
    if request.method == "POST":
        if request.user.is_superuser or request.user.groups.filter(name="Administrador").exists():  # Verifica permisos
            ChangeHistory.objects.all().delete()
            messages.success(request, "Todo el historial de cambios ha sido eliminado con éxito.")
        else:
            messages.error(request, "No tienes permisos para realizar esta acción.")
    return redirect('change_history')


###################################################################################################### VER USUARIOS REGISTRADOS.

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


###################################################################################################### 

from django.http import HttpResponseRedirect


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



def create_task(request, activity_id):
    activity = get_object_or_404(ActivityFolder, id=activity_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.activity = activity
            task.save()

            # Registro del cambio
            ChangeHistory.objects.create(
                project=activity.project,
                activity=activity,
                change_description=f"Tarea '{task.name}' creada en la actividad '{activity.name}'",
                user=request.user
            )

            messages.success(request, "Tarea creada exitosamente.")
            return redirect('OpenProject', project_id=activity.project.id)
    else:
        form = TaskForm()
    return render(request, 'create_task.html', {'form': form, 'activity': activity})



def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project_id = task.activity.project.id

    if request.method == 'POST':
        task_name = task.name
        task.delete()

        # Registro del cambio
        ChangeHistory.objects.create(
            project=task.activity.project,
            activity=task.activity,
            change_description=f'Tarea "{task_name}" eliminada',
            user=request.user
        )

        messages.success(request, f'Tarea "{task_name}" eliminada exitosamente.')

    return redirect('OpenProject', project_id=project_id)
