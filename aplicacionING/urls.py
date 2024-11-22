from django.urls import path
from django.contrib.auth.views import LoginView
from .import views
from .views import home
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('home/', views.home, name='home'),
    path('projects/', views.list_project_folders, name='list_project_folders'),
    path('activities/create/', views.create_activity_folder, name='create_activity_folder'),
    path('change_history/', views.change_history, name='change_history'),
    path('CreateProject/', views.create_project, name='CreateProject'),
    path('project/<int:project_id>/', views.OpenProject, name='OpenProject'),
    path('projects/eliminar/<int:project_id>/', views.DeleteProject, name='DeleteProject'),
    path('project/<int:project_id>/create_activity', views.create_activity_folder, name='create_activity'),
    path('project/<int:project_id>/delete_activity/<int:activity_id>/', views.delete_activity, name='delete_activity'),
    path('crear_rol/', views.crear_rol, name='crear_rol'),
    path('ver_permisos/', views.ver_permisos, name='ver_permisos'),
    path('ver_usuarios/', views.ver_usuarios, name='ver_usuarios'),
    path('export-users/', views.export_users_csv, name='export_users_csv'),
    path('update-project/<int:project_id>/', views.update_project, name='update_project'),
    path('eliminar_usuario/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('administrar_roles/', views.administrar_roles, name='administrar_roles'),
    path('add_role/', views.add_role, name='add_role'),  # Para añadir un nuevo rol
    path('add_permission/<int:role_id>/', views.add_permission, name='add_permission'),
    path('delete_role/<int:role_id>/', views.delete_role, name='delete_role'),  # Eliminar un rol
    path('delete_permission/<int:role_id>/<int:permission_id>/', views.delete_permission, name='delete_permission'),  # Eliminar un permiso de un rol
    path('activity/<int:activity_id>/create_task/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/complete/', views.mark_task_complete, name='mark_task_complete'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),


]