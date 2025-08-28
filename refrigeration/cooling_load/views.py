from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView
from .models import ColdStorageProject
from django.urls import reverse_lazy


class ProjectCreateView(CreateView):
    model = ColdStorageProject
    fields = [
        'name', 'storage_type', 'length', 'width', 'height',
        'outdoor_temp', 'outdoor_humidity', 'indoor_temp', 'indoor_humidity',
        'insulation_type', 'insulation_thickness', 'product_mass',
        'daily_product_input', 'number_of_workers', 'working_hours',
        'lighting_power', 'fan_power', 'door_openings'
    ]
    template_name = 'cooling_load/project_form.html'

    def form_valid(self, form):
        project = form.save()
        return redirect('project_result', pk=project.pk)

    def form_invalid(self, form):
        print("Form errors:", form.errors)
        return super().form_invalid(form)


class ProjectListView(ListView):
    model = ColdStorageProject
    template_name = 'cooling_load/project_list.html'
    context_object_name = 'projects'


def project_result(request, pk):
    try:
        project = ColdStorageProject.objects.get(pk=pk)
    except ColdStorageProject.DoesNotExist:
        return redirect('project_create')

    # Calculate transmission load
    area = 2 * (project.length * project.width + project.length * project.height + project.width * project.height)
    u_value = 0.4
    temp_diff = project.outdoor_temp - project.indoor_temp
    transmission_load = area * u_value * temp_diff

    # Calculate product load
    product_load = project.daily_product_input * 3.5 / 24

    # Calculate internal load
    people_load = project.number_of_workers * 120 * (project.working_hours / 24)
    lighting_load = project.lighting_power
    fan_load = project.fan_power
    internal_load = people_load + lighting_load + fan_load

    # Calculate infiltration load
    volume = project.length * project.width * project.height
    infiltration_load = volume * 0.5 * 1.2 * 1.0 * temp_diff / 3600

    # Calculate respiration load
    respiration_load = project.product_mass * 0.02

    # Total calculations
    total_load = transmission_load + product_load + internal_load + infiltration_load + respiration_load
    design_load = total_load * 1.15

    context = {
        'project': project,
        'transmission_load': transmission_load,
        'product_load': product_load,
        'internal_load': internal_load,
        'infiltration_load': infiltration_load,
        'respiration_load': respiration_load,
        'total_load': total_load,
        'design_load': design_load
    }
    return render(request, 'cooling_load/project_result.html', context)
