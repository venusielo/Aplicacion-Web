from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import ProjectFolder, ChangeHistory, ActivityFolder
from .forms import ProjectFolderForm, ActivityFolderForm, RegistroForm

@login_required  # Requiere que el usuario esté autenticado
def home(request):
    return render(request, 'home.html')
def modificar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(ProjectFolder, id=proyecto_id)
    if request.method == "POST":
        # Aquí iría el código que modifica los detalles del proyecto
        proyecto.name = request.POST.get('name')
        proyecto.description = request.POST.get('description')
        proyecto.save()
        
        # Registrar el cambio en el historial
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
            
            #registrar el cambio
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
             form.save()
             return redirect('home')
    else:
        form = ProjectFolderForm()  

    return render(request, 'CreateProject.html', {'form': form})     


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('home')
        else:
            return render(request, 'registration/registro.html', {'form': form})
        
    else:
        form = RegistroForm()

    return render(request, 'registration/registro.html', {'form' : form})

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