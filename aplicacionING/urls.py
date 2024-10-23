from django.urls import path
from django.contrib.auth.views import LoginView
from .import views 
from .views import home

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.list_project_folders, name='list_project_folders'),
    path('projects/create/', views.create_project_folder, name='create_project_folder'),
    path('activities/create/', views.create_activity_folder, name='create_activity_folder'),
    path('change_history/', views.change_history, name='change_history'),
]
