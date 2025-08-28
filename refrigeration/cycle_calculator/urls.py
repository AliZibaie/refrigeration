from django.urls import path
from . import views

app_name = 'cycle_calculator'

urlpatterns = [
    path('', views.calculate, name='calculate'),
]
