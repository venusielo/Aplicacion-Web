"""
URL configuration for ingenieria_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from aplicacionING.views import home
from aplicacionING.views import registro
from aplicacionING.forms import CustomAuthenticationForm
from django.contrib.auth.forms import AuthenticationForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name= 'home'),
    path('', include('aplicacionING.urls')),
    path('registro/', registro, name='registro'),
    path('login/', LoginView.as_view(template_name='registration/login.html', authentication_form=AuthenticationForm), name='login'),  # Página de login
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # Página para cerrar sesión
]
