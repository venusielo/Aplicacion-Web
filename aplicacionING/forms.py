import datetime
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import ProjectFolder, ActivityFolder
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from .models import Role , Task
from .models import Task



class RoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Role
        fields = ['name', 'permissions']

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Usuario')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    error_messages = {
        'invalid_login': _(
            "Usuario o contraseña incorrectos. Por favor, intenta nuevamente."
        ),
        'inactive': _("Esta cuenta está inactiva."),
    }

class ProjectFolderForm(forms.ModelForm):
    name = forms.CharField(label='Nombre')
    description = forms.CharField(label='Descripcion')
    class Meta:
        model = ProjectFolder
        fields = ['name', 'description']

class ActivityFolderForm(forms.ModelForm):
    name = forms.CharField(label='Nombre')
    description = forms.CharField(label='Descripcion')
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
        label='Fecha de entrega'
    )
    assigned_to = forms.ModelChoiceField(   ####
        queryset=User.objects.all(),
        required=False,
        label="Asignado a",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ActivityFolder
        fields = ['name', 'description', 'due_date', 'assigned_to'] ###
        widgets = {
            'due_date': forms.DateInput(attrs={'type':'date'})
        }

class TaskForm(forms.ModelForm):
    name = forms.CharField(label='Nombre')
    description = forms.CharField(label='Descripcion')
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
        label='Fecha de Inicio'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
        label='Fecha de final'
    )
    class Meta:
        model = Task
        fields = ['name', 'description', 'start_date', 'end_date',]

class RegistroForm(forms.ModelForm):
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
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ProjectFolderForm(forms.ModelForm):
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
