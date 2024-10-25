from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import ProjectFolder, ActivityFolder
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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
    due_date= forms.CharField(label="Fecha de Termino")
    class Meta:
        model = ActivityFolder
        fields = ['name', 'description', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type':'date'})
        }

class RegistroForm(forms.ModelForm):
    username = forms.CharField(label='Nombre de usuario')  # Etiqueta personalizada
    email = forms.EmailField(label='Correo electrónico')  # Etiqueta personalizada
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirma tu contraseña', widget=forms.PasswordInput)

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

    
class ProjectForm(forms.ModelForm):
    name = forms.CharField(label='Nombre')
    description = forms.CharField(label='Descripcion')
    class Meta:
            model = ProjectFolder
            fields = ['name', 'description']