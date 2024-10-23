from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import Carpeta
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CarpetaForm(forms.ModelForm):
    class Meta:
        model = Carpeta
        fields = ['nombre']  # Campo que queremos mostrar en el formulario

class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _(
            "Usuario o contraseña incorrectos. Por favor, intenta nuevamente."
        ),
        'inactive': _("Esta cuenta está inactiva."),
    }

class RegistroForm(forms.ModelForm):

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