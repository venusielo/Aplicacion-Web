from django.urls import path
from django.contrib.auth.views import LoginView
from .views import home, crear_carpeta

urlpatterns = [
    path('', home, name='home'),
    path('crear_carpeta/', crear_carpeta, name='crear_carpeta'),
]
