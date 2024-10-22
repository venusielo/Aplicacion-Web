from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import Carpeta

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