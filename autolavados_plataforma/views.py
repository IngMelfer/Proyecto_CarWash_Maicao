from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@login_required(login_url='/autenticacion/login/')
def home_view(request):
    """Vista para la página principal"""
    
    # Si el usuario es un cliente, redirigir al dashboard
    if hasattr(request.user, 'cliente'):
        return redirect('clientes:dashboard')
    
    # Si es administrador u otro tipo de usuario, mostrar la vista normal
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