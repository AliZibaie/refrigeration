from django.contrib import admin
from .models import Refrigerant, Calculation

@admin.register(Refrigerant)
class RefrigerantAdmin(admin.ModelAdmin):
    list_display = ['name', 'coolprop_name']
    search_fields = ['name', 'coolprop_name']

@admin.register(Calculation)
class CalculationAdmin(admin.ModelAdmin):
    list_display = ['name', 'refrigerant', 't_evap', 't_cond', 'cop_ideal', 'cop_actual', 'created_at']
    list_filter = ['refrigerant', 'created_at']
    search_fields = ['name']
    readonly_fields = ['cop_ideal', 'cop_actual', 'created_at']
