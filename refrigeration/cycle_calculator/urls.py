from django.urls import path
from .views import CalculationCreateView, CalculationListView, CalculationDetailView

urlpatterns = [
    path('', CalculationCreateView.as_view(), name='calculator'),
    path('calculations/', CalculationListView.as_view(), name='calculation_list'),
    path('calculations/<int:pk>/', CalculationDetailView.as_view(), name='calculation_detail'),
]
