from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import ProjectFolder, ChangeHistory, ActivityFolder
from .forms import ProjectFolderForm, ActivityFolderForm, RegistroForm,RoleForm
from .models import Role
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser)
def ver_usuarios(request):
    users = User.objects.all()
    roles = Role.objects.all()
    user_roles = {user: user.role_set.all() for user in users}
    return render(request, 'ver_usuarios.html', {'user_roles': user_roles})


@login_required
def ver_permisos(request):
    user_permissions = request.user.get_all_permissions()
    return render(request, 'ver_permisos.html', {'user_permissions': user_permissions})

@user_passes_test(lambda u: u.is_superuser)
def crear_rol(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ver_roles')
    else:
        form = RoleForm()
    return render(request, 'Crear_rol.html', {'form': form})


@login_required  # Requiere que el usuario esté autenticado
def home(request):
    return render(request, 'home.html')

def modificar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(ProjectFolder, id=proyecto_id)
    if request.method == "POST":
        
        proyecto.name = request.POST.get('name')
        proyecto.description = request.POST.get('description')
        proyecto.save()
        
        
        ChangeHistory.objects.create(
            project=proyecto,
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

             return redirect('home')
    else:
        form = ProjectFolderForm()  

    return render(request, 'CreateProject.html', {'form': form})     


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.is_superuser:
                messages.success(request, 'Te has registrado como administrador.')
            else:
                messages.success(request, 'Registro exitoso. Bienvenido a CatNest.')
            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroForm()
    return render(request, 'registration/registro.html', {'form': form})


def change_history(request):
    history = ChangeHistory.objects.all().order_by('-change_date')
    return render(request, 'change_history.html', {'history': history})
# @login_required  # Requiere que el usuario esté autenticado

def OpenProject(request, project_id):
    project = get_object_or_404(ProjectFolder, id = project_id)
    return render(request, 'OpenProject.html', {'project' : project})

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
