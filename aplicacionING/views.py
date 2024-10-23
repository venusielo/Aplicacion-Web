from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import ProjectFolder, ChangeHistory
from .forms import ProjectFolderForm, ActivityFolderForm, RegistroForm

# @login_required  # Requiere que el usuario esté autenticado
def home(request):
    return render(request, 'home.html')

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

def create_activity_folder(request):
    if request.method == 'POST':
        form = ActivityFolderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_project_folders')  # Redirect to list or project detail
    else:
        form = ActivityFolderForm()
    return render(request, 'create_activity_folder.html', {'form': form})

def list_project_folders(request):
    projects = ProjectFolder.objects.all()
    if not projects:
        message = "Aun no tienes proyectos"
        return render(request, 'carpetas.html', {'message': message})
    return render(request, 'carpetas.html', {'projects': projects})

def create_project(request):
    if request.method == 'POST':
        form = ProjectFolderForm(request.POST)
        if form.is_valid():
             form.save()
             return redirect('carpetas.html')
    else:
        form = ProjectFolderForm()  
    return render(request, 'carpetas.html', {'form': form})     


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


