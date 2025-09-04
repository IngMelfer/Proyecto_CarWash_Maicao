from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Reemplazar la vista basada en clase por una vista basada en función
from django.contrib.auth.decorators import login_required

@login_required(login_url='/autenticacion/login/')
def home_view(request):
    """Vista para la página principal"""
    context = {
        'title': 'Plataforma de Autolavados',
        'api_endpoints': [
            {
                'name': 'Autenticación',
                'description': 'Registro, login y gestión de usuarios',
                'method': 'POST',
                'path': '/api/auth/'
            },
            {
                'name': 'Reservas',
                'description': 'Gestión de citas y servicios',
                'method': 'GET/POST',
                'path': '/api/reservas/'
            },
            {
                'name': 'Notificaciones',
                'description': 'Sistema de alertas y mensajes',
                'method': 'GET',
                'path': '/api/notificaciones/'
            },
            {
                'name': 'Clientes',
                'description': 'Gestión de perfiles de clientes',
                'method': 'GET/PUT',
                'path': '/api/clientes/'
            },
            {
                'name': 'Puntos',
                'description': 'Sistema de fidelización',
                'method': 'GET',
                'path': '/api/puntos/'
            },
        ]
    }
    return render(request, 'home.html', context)