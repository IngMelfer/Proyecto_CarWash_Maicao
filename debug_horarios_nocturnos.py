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

def debug_horarios_nocturnos():
    """
    Debug específico para horarios nocturnos (22:53)
    """
    print("=== DEBUG: Horarios Nocturnos ===")
    
    # Simular la hora actual (22:53)
    fecha_actual = datetime.strptime('2025-09-17', '%Y-%m-%d').date()
    hora_actual = datetime.strptime('22:53:00', '%H:%M:%S').time()
    
    print(f"Fecha: {fecha_actual}")
    print(f"Hora actual simulada: {hora_actual}")
    
    # Obtener horarios de la base de datos
    horarios_bd = HorarioDisponible.objects.filter(
        fecha=fecha_actual,
        disponible=True
    ).order_by('hora_inicio')
    
    print(f"\nHorarios en la base de datos: {horarios_bd.count()}")
    
    for horario in horarios_bd:
        print(f"\n--- Horario: {horario.hora_inicio} a {horario.hora_fin} ---")
        print(f"Capacidad: {horario.capacidad}")
        
        # Verificar condiciones de filtrado
        print("\n🔍 Verificando condiciones:")
        
        # 1. ¿Ya terminó?
        if hora_actual >= horario.hora_fin:
            print(f"❌ TERMINADO: {hora_actual} >= {horario.hora_fin}")
            continue
        else:
            print(f"✅ NO TERMINADO: {hora_actual} < {horario.hora_fin}")
        
        # 2. ¿Ya comenzó?
        if hora_actual >= horario.hora_inicio:
            print(f"❌ YA COMENZÓ: {hora_actual} >= {horario.hora_inicio}")
            continue
        else:
            print(f"✅ AÚN NO COMENZÓ: {hora_actual} < {horario.hora_inicio}")
        
        # 3. ¿Tiene margen de 30 minutos?
        hora_minima = (datetime.combine(fecha_actual, hora_actual) + timedelta(minutes=30)).time()
        if horario.hora_inicio < hora_minima:
            print(f"❌ SIN MARGEN: {horario.hora_inicio} < {hora_minima} (30 min desde ahora)")
            continue
        else:
            print(f"✅ CON MARGEN: {horario.hora_inicio} >= {hora_minima}")
        
        # 4. Contar reservas
        reservas_count = Reserva.objects.filter(
            fecha_hora__date=fecha_actual,
            fecha_hora__time__gte=horario.hora_inicio,
            fecha_hora__time__lt=horario.hora_fin,
            estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
        ).count()
        
        bahias_disponibles = max(0, horario.capacidad - reservas_count)
        print(f"📊 Reservas existentes: {reservas_count}")
        print(f"📊 Bahías disponibles: {bahias_disponibles}")
        
        if bahias_disponibles > 0:
            print("✅ HORARIO DEBERÍA MOSTRARSE")
        else:
            print("❌ SIN BAHÍAS DISPONIBLES")
    
    print("\n=== Fin del debug ===")

if __name__ == '__main__':
    debug_horarios_nocturnos()