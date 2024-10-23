from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CarpetaForm
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistroForm

# @login_required  # Requiere que el usuario esté autenticado
def home(request):
    return render(request, 'home.html')

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

# @login_required  # Requiere que el usuario esté autenticado
def crear_carpeta(request):
    if request.method == 'POST':
        form = CarpetaForm(request.POST)
        if form.is_valid():
            form.save()  # Guardar la nueva carpeta
            return redirect('home')  # Redirigir a la página principal
    else:
        form = CarpetaForm()
    
    return render(request, 'crear_carpeta.html', {'form': form})


