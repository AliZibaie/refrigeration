from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('result/<uuid:pk>/', views.project_result, name='project_result'),
]
