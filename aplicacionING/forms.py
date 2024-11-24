import datetime
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import ProjectFolder, ActivityFolder, Role, Task
from django.contrib.auth.models import User, Permission

######################################################################################################
# FORMULARIOS PARA AUTENTICACIÓN Y REGISTRO DE USUARIOS
######################################################################################################

class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulario de autenticación personalizado para el inicio de sesión de usuarios.
    """
    username = forms.CharField(label='Usuario')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    error_messages = {
        'invalid_login': _(
            "Usuario o contraseña incorrectos. Por favor, intenta nuevamente."
        ),
        'inactive': _( "Esta cuenta está inactiva."),
    }

class RegistroForm(forms.ModelForm):
    """
    Formulario de registro de usuarios con opciones para asignar roles de administrador o colaborador.
    """
    username = forms.CharField(label='Nombre de usuario')
    email = forms.EmailField(label='Correo electrónico')
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirma tu contraseña', widget=forms.PasswordInput)
    is_admin = forms.BooleanField(required=False, label="Registrar como administrador")
    is_collaborator = forms.BooleanField(required=False, label="Registrar como colaborador")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password2(self):
        """
        Verifica que las contraseñas coincidan.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        """
        Guarda al usuario con la contraseña encriptada.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

######################################################################################################
# FORMULARIOS PARA GESTIÓN DE ROLES
######################################################################################################

class RoleForm(forms.ModelForm):
    """
    Formulario para la creación y edición de roles, con la posibilidad de asignar permisos.
    """
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Role
        fields = ['name', 'permissions']

######################################################################################################
# FORMULARIOS PARA GESTIÓN DE PROYECTOS
######################################################################################################

class ProjectFolderForm(forms.ModelForm):
    """
    Formulario para crear y editar proyectos.
    """
    name = forms.CharField(label='Nombre')
    description = forms.CharField(label='Descripcion')
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
        label='Fecha de Inicio'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
        label='Fecha de Término'
    )

    class Meta:
        model = ProjectFolder
        fields = ['name', 'description', 'start_date', 'end_date']

######################################################################################################
# FORMULARIOS PARA GESTIÓN DE ACTIVIDADES
######################################################################################################

class ActivityFolderForm(forms.ModelForm):
    """
    Formulario para crear y editar actividades dentro de un proyecto.
    """
    name = forms.CharField(label='Nombre')
    description = forms.CharField(label='Descripcion')
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
        label='Fecha de entrega'
    )
    assigned_to = forms.ModelChoiceField( 
        queryset=User.objects.all(),
        required=False,
        label="Asignado a",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    priority = forms.ChoiceField(
        choices=ActivityFolder.PRIORITY_CHOICES,
        label="Prioridad",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ActivityFolder
        fields = ['name', 'description', 'due_date', 'assigned_to', 'priority'] 
        widgets = {
            'due_date': forms.DateInput(attrs={'type':'date'})
        }

class EditActivityForm(forms.ModelForm):
    """
    Formulario para editar una actividad, incluyendo su nombre, descripción y fecha de vencimiento.
    """
    name = forms.CharField(label='Nombre')
    description = forms.CharField(label='Descripcion')
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
        label='Fecha de finalización'
    )

    class Meta:
        model = ActivityFolder
        fields = ['name', 'description', 'due_date']

######################################################################################################
# FORMULARIOS PARA GESTIÓN DE TAREAS
######################################################################################################

class TaskForm(forms.ModelForm):
    """
    Formulario para crear y editar tareas dentro de una actividad.
    """
    name = forms.CharField(label='Nombre')
    description = forms.CharField(label='Descripcion')
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
        label='Fecha de Inicio'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
        label='Fecha de finalización'
    )

    class Meta:
        model = Task
        fields = ['name', 'description', 'start_date', 'end_date']
