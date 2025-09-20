#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, date, time

# Configurar Django
sys.path.append('c:\\Proyectos_2025\\autolavados-plataforma')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from reservas.models import HorarioDisponible, Reserva, Bahia
from django.utils import timezone

def debug_horarios_hoy():
    hoy = date.today()
    ahora = timezone.now()
    
    print(f"=== DEBUG HORARIOS PARA HOY ({hoy}) ===")
    print(f"Hora actual: {ahora.strftime('%H:%M:%S')}")
    print()
    
    # 1. Verificar horarios disponibles en la BD para hoy
    print("1. HORARIOS DISPONIBLES EN LA BASE DE DATOS:")
    horarios_hoy = HorarioDisponible.objects.filter(fecha=hoy)
    print(f"Total horarios para hoy: {horarios_hoy.count()}")
    
    for horario in horarios_hoy:
        print(f"  - {horario.fecha} | {horario.hora_inicio} - {horario.hora_fin} | Disponible: {horario.disponible} | Capacidad: {horario.capacidad}")
    print()
    
    # 2. Verificar bahías totales
    print("2. BAHÍAS EN EL SISTEMA:")
    bahias = Bahia.objects.all()
    print(f"Total bahías: {bahias.count()}")
    for bahia in bahias:
        print(f"  - ID {bahia.id}: {bahia.nombre} (Activa: {bahia.activo})")
    print()
    
    # 3. Verificar reservas de hoy
    print("3. RESERVAS DE HOY:")
    reservas_hoy = Reserva.objects.filter(fecha_hora__date=hoy)
    print(f"Total reservas hoy: {reservas_hoy.count()}")
    
    for reserva in reservas_hoy:
        bahia_info = f"{reserva.bahia.nombre} (ID: {reserva.bahia.id})" if reserva.bahia else 'Sin asignar'
        print(f"  - {reserva.fecha_hora.strftime('%H:%M')} | Bahía: {bahia_info} | Estado: {reserva.estado}")
    print()
    
    # 4. Verificar reservas activas ahora
    print("4. RESERVAS ACTIVAS AHORA:")
    reservas_activas = Reserva.objects.filter(
        fecha_hora__date=hoy,
        estado__in=['confirmada', 'en_proceso']
    )
    
    bahias_ocupadas = []
    for reserva in reservas_activas:
        hora_inicio = reserva.fecha_hora.time()
        # Asumiendo duración de 1 hora por reserva
        hora_fin_estimada = datetime.combine(hoy, hora_inicio)
        hora_fin_estimada = (hora_fin_estimada + timezone.timedelta(hours=1)).time()
        
        if hora_inicio <= ahora.time() <= hora_fin_estimada:
            bahia_info = f"{reserva.bahia.nombre} (ID: {reserva.bahia.id})" if reserva.bahia else 'Sin asignar'
            bahias_ocupadas.append(reserva.bahia.id if reserva.bahia else None)
            print(f"  - Bahía {bahia_info}: {hora_inicio} - {hora_fin_estimada} (estimado)")
    
    print(f"Bahías ocupadas ahora: {len(bahias_ocupadas)}")
    print(f"Bahías disponibles: {bahias.filter(activo=True).count() - len(bahias_ocupadas)}")
    print()
    
    # 5. Simular la lógica actual de la vista
    print("5. SIMULACIÓN DE LA LÓGICA ACTUAL:")
    
    # Obtener horarios disponibles (lógica actual)
    horarios_disponibles = HorarioDisponible.objects.filter(
        fecha=hoy,
        disponible=True
    )
    
    print(f"Horarios marcados como disponibles: {horarios_disponibles.count()}")
    
    # Filtrar horarios pasados
    horarios_futuros = []
    for horario in horarios_disponibles:
        if horario.hora_inicio > ahora.time():
            horarios_futuros.append(horario)
            print(f"  - Horario futuro: {horario.hora_inicio} - {horario.hora_fin}")
    
    print(f"Horarios futuros disponibles: {len(horarios_futuros)}")
    
    if not horarios_futuros:
        print("❌ PROBLEMA: No hay horarios futuros disponibles")
        print("   Posibles causas:")
        print("   - No hay registros de HorarioDisponible para hoy")
        print("   - Todos los horarios están marcados como no disponibles")
        print("   - Todos los horarios ya pasaron")

if __name__ == "__main__":
    debug_horarios_hoy()