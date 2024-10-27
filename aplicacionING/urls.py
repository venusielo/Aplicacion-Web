from django.urls import path
from django.contrib.auth.views import LoginView
from .import views 
from .views import home

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.list_project_folders, name='list_project_folders'),
    #path('projects/create/', views.create_project_folder, name='create_project_folder'),
    path('activities/create/', views.create_activity_folder, name='create_activity_folder'),
    path('change_history/', views.change_history, name='change_history'),
    path('CreateProject/', views.create_project, name='CreateProject'),
    path('project/<int:project_id>/', views.OpenProject, name='OpenProject'),
    path('projects/eliminar/<int:project_id>/', views.DeleteProject, name='DeleteProject'),
    path('project/<int:project_id>/create_activity', views.create_activity_folder, name='create_activity'),
    path('project/<int:project_id>/delete_activity/<int:activity_id>/', views.delete_activity, name='delete_activity'),
    path('Crear_rol/', views.crear_rol, name='Crear_rol'),
    path('ver_permisos/', views.ver_permisos, name='ver_permisos'),
    path('ver_usuarios/', views.ver_usuarios, name='ver_usuarios'),


]