#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from reservas.models import HorarioDisponible, Reserva

def test_horarios_largos():
    """
    Prueba que los horarios largos (más de 8 horas) permitan reservas mientras estén activos
    """
    print("=== PRUEBA: Horarios Largos (Nocturnos) ===")
    
    # Simular la hora actual (22:53)
    fecha_actual = datetime.strptime('2025-09-17', '%Y-%m-%d').date()
    hora_actual = datetime.strptime('22:53:00', '%H:%M:%S').time()
    now_local = datetime.combine(fecha_actual, hora_actual)
    
    print(f"Fecha: {fecha_actual}")
    print(f"Hora actual simulada: {hora_actual}")
    
    # Obtener horarios de la base de datos
    horarios_bd = HorarioDisponible.objects.filter(
        fecha=fecha_actual,
        disponible=True
    ).order_by('hora_inicio')
    
    print(f"\nHorarios en la base de datos: {horarios_bd.count()}")
    
    horarios_procesados = []
    
    for horario_bd in horarios_bd:
        print(f"\n--- Procesando Horario: {horario_bd.hora_inicio} a {horario_bd.hora_fin} ---")
        print(f"Capacidad: {horario_bd.capacidad}")
        
        # Aplicar la nueva lógica
        # 1. ¿Ya terminó?
        if hora_actual >= horario_bd.hora_fin:
            print(f"❌ TERMINADO: {hora_actual} >= {horario_bd.hora_fin}")
            continue
        
        # 2. Verificar si es horario largo
        duracion_horario = datetime.combine(fecha_actual, horario_bd.hora_fin) - datetime.combine(fecha_actual, horario_bd.hora_inicio)
        es_horario_largo = duracion_horario.total_seconds() > 8 * 3600  # 8 horas
        
        print(f"📏 Duración: {duracion_horario} ({'LARGO' if es_horario_largo else 'CORTO'})")
        
        if es_horario_largo:
            # Para horarios largos, verificar tiempo restante
            tiempo_restante = datetime.combine(fecha_actual, horario_bd.hora_fin) - datetime.combine(fecha_actual, hora_actual)
            print(f"⏰ Tiempo restante: {tiempo_restante}")
            
            if tiempo_restante.total_seconds() < 30 * 60:  # Menos de 30 minutos restantes
                print(f"❌ POCO TIEMPO RESTANTE: {tiempo_restante} < 30 minutos")
                continue
            else:
                print(f"✅ SUFICIENTE TIEMPO RESTANTE: {tiempo_restante} >= 30 minutos")
        else:
            # Para horarios cortos, lógica original
            if hora_actual >= horario_bd.hora_inicio:
                print(f"❌ YA COMENZÓ: {hora_actual} >= {horario_bd.hora_inicio}")
                continue
            
            hora_minima = (now_local + timedelta(minutes=30)).time()
            if horario_bd.hora_inicio < hora_minima:
                print(f"❌ SIN MARGEN: {horario_bd.hora_inicio} < {hora_minima}")
                continue
        
        # 3. Contar reservas
        reservas_count = Reserva.objects.filter(
            fecha_hora__date=fecha_actual,
            fecha_hora__time__gte=horario_bd.hora_inicio,
            fecha_hora__time__lt=horario_bd.hora_fin,
            estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
        ).count()
        
        bahias_disponibles = max(0, horario_bd.capacidad - reservas_count)
        print(f"📊 Reservas existentes: {reservas_count}")
        print(f"📊 Bahías disponibles: {bahias_disponibles}")
        
        if bahias_disponibles > 0:
            print("✅ HORARIO DISPONIBLE - Se mostrará al usuario")
            horarios_procesados.append({
                'hora_inicio': horario_bd.hora_inicio.strftime('%H:%M'),
                'hora_fin': horario_bd.hora_fin.strftime('%H:%M'),
                'disponible': True,
                'bahias_disponibles': bahias_disponibles,
                'bahias_totales': horario_bd.capacidad
            })
        else:
            print("❌ SIN BAHÍAS DISPONIBLES")
    
    print("\n=== RESULTADO FINAL ===")
    print(f"Horarios que se mostrarán al usuario: {len(horarios_procesados)}")
    for h in horarios_procesados:
        print(f"  - {h['hora_inicio']} a {h['hora_fin']} ({h['bahias_disponibles']}/{h['bahias_totales']} bahías)")
    
    print("\n=== Fin de la prueba ===")

if __name__ == '__main__':
    test_horarios_largos()