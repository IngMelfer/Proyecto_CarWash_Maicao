from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from clientes.models import Cliente

class ClienteValidarDirectView(View):
    """Vista directa para validar un cliente sin requisitos de autenticación"""
    template_name = 'reservas/cliente_validar.html'
    
    def get(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        return render(request, self.template_name, {'cliente': cliente})
    
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        # Validar el usuario asociado al cliente
        if hasattr(cliente, 'usuario'):
            usuario = cliente.usuario
            usuario.is_verified = True
            usuario.save(update_fields=['is_verified'])
            messages.success(request, f'Cliente {cliente.nombre} {cliente.apellido} validado exitosamente')
        else:
            messages.error(request, f'El cliente {cliente.nombre} {cliente.apellido} no tiene un usuario asociado')
        # Redirigir a la lista de clientes usando la URL completa
        return redirect('/reservas/clientes/')