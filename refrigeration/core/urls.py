from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cycle_calculator.urls')),
path('cooling-load/', include('cooling_load.urls')),
]
