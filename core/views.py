
from django.shortcuts import render

def navigate_view(request):
    return render(request, 'core/navigate.html') 