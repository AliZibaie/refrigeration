from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cycle_calculator', include('cycle_calculator.urls')),
    path('cooling-load/', include('cooling_load.urls')),
]
