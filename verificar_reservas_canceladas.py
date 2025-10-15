#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from reservas.models import Reserva
from datetime import date

def verificar_reservas():
    print("=== VERIFICACIÓN DE RESERVAS ===")
    print(f"Total reservas: {Reserva.objects.count()}")
    print(f"Reservas de hoy: {Reserva.objects.filter(fecha_hora__date=date.today()).count()}")
    
    print("\n=== RESERVAS POR ESTADO (TODAS) ===")
    for estado_code, estado_name in Reserva.ESTADO_CHOICES:
        count = Reserva.objects.filter(estado=estado_code).count()
        print(f"{estado_name} ({estado_code}): {count}")
    
    print("\n=== RESERVAS DE HOY POR ESTADO ===")
    for estado_code, estado_name in Reserva.ESTADO_CHOICES:
        count = Reserva.objects.filter(fecha_hora__date=date.today(), estado=estado_code).count()
        print(f"{estado_name} ({estado_code}): {count}")
    
    # Verificar específicamente las canceladas
    canceladas_total = Reserva.objects.filter(estado=Reserva.CANCELADA).count()
    canceladas_hoy = Reserva.objects.filter(fecha_hora__date=date.today(), estado=Reserva.CANCELADA).count()
    
    print(f"\n=== RESUMEN CANCELADAS ===")
    print(f"Total reservas canceladas: {canceladas_total}")
    print(f"Reservas canceladas hoy: {canceladas_hoy}")
    
    if canceladas_total == 0:
        print("\n⚠️  NO HAY RESERVAS CANCELADAS EN LA BASE DE DATOS")
        print("Esto significa que la tarjeta 'Cancelados' mostrará 0")
    else:
        print(f"\n✅ Hay {canceladas_total} reservas canceladas en total")
        print(f"✅ Hay {canceladas_hoy} reservas canceladas hoy")

if __name__ == "__main__":
    verificar_reservas()