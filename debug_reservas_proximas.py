# -*- coding: utf-8 -*-
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "autolavados_plataforma.settings")
django.setup()

from autenticacion.models import Usuario
from reservas.models import Reserva
from clientes.models import Cliente
from django.template.loader import render_to_string
from django.utils import timezone

# Obtener un usuario cliente
try:
    user = Usuario.objects.filter(cliente__isnull=False).first()
    if user:
        cliente = user.cliente
        print(f"Usuario encontrado: {user.username}")
        
        # Obtener reservas próximas
        proximas = Reserva.objects.filter(
            cliente=cliente,
            fecha_hora__gte=timezone.now(),
            estado__in=["PE", "CO"]
        ).order_by("fecha_hora")
        
        print(f"Reservas próximas encontradas: {proximas.count()}")
        
        for reserva in proximas:
            print(f"- ID: {reserva.id}, Servicio: {reserva.servicio.nombre}, Estado: {reserva.estado}")
            print(f"  Fecha: {reserva.fecha_hora}")
            print(f"  Bahía: {reserva.bahia}")
            print(f"  Inicio servicio: {reserva.inicio_servicio}")
            print("---")
            
    else:
        print("No se encontró ningún usuario con cliente asociado")
        
except Exception as e:
    print(f"Error: {e}")