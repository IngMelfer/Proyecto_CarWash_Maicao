#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, date, time, timedelta

# Configurar Django
sys.path.append('c:\\Proyectos_2025\\autolavados-plataforma')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from reservas.models import HorarioDisponible, Reserva
from django.utils import timezone

def test_logica_corregida():
    hoy = date.today()
    now_local = datetime.now()
    
    print(f"=== TEST LÓGICA CORREGIDA ({hoy}) ===")
    print(f"Hora actual: {now_local.strftime('%H:%M:%S')}")
    print()
    
    # Obtener horarios disponibles
    horarios_bd = HorarioDisponible.objects.filter(
        fecha=hoy,
        disponible=True
    ).order_by('hora_inicio')
    
    print(f"Horarios en BD para hoy: {horarios_bd.count()}")
    
    horarios = []
    
    for horario_bd in horarios_bd:
        print(f"\n--- Procesando horario: {horario_bd.hora_inicio} - {horario_bd.hora_fin} ---")
        
        # Aplicar la nueva lógica
        if hoy == now_local.date():
            hora_actual = now_local.time()
            print(f"Hora actual: {hora_actual}")
            print(f"Hora inicio horario: {horario_bd.hora_inicio}")
            print(f"Hora fin horario: {horario_bd.hora_fin}")
            
            # Si el horario ya terminó, no incluirlo
            if hora_actual >= horario_bd.hora_fin:
                print("❌ Horario ya terminó - NO incluir")
                continue
            
            # Si el horario aún no ha comenzado, verificar que tenga al menos 30 minutos de margen
            if hora_actual < horario_bd.hora_inicio:
                hora_minima = (now_local + timedelta(minutes=30)).time()
                print(f"Hora mínima requerida: {hora_minima}")
                if horario_bd.hora_inicio < hora_minima:
                    print("❌ Horario muy próximo (menos de 30 min) - NO incluir")
                    continue
                else:
                    print("✅ Horario futuro con margen suficiente - INCLUIR")
            else:
                print("✅ Horario activo ahora - INCLUIR")
        
        # Contar reservas existentes
        reservas_count = Reserva.objects.filter(
            fecha_hora__date=hoy,
            fecha_hora__time__gte=horario_bd.hora_inicio,
            fecha_hora__time__lt=horario_bd.hora_fin,
            estado__in=['PE', 'CO', 'EP']  # PENDIENTE, CONFIRMADA, EN_PROCESO
        ).count()
        
        print(f"Reservas existentes: {reservas_count}")
        print(f"Capacidad del horario: {horario_bd.capacidad}")
        
        # Verificar disponibilidad
        bahias_disponibles = max(0, horario_bd.capacidad - reservas_count)
        print(f"Bahías disponibles: {bahias_disponibles}")
        
        horario_info = {
            'hora_inicio': horario_bd.hora_inicio.strftime('%H:%M'),
            'hora_fin': horario_bd.hora_fin.strftime('%H:%M'),
            'disponible': bahias_disponibles > 0,
            'bahias_disponibles': bahias_disponibles,
            'bahias_totales': horario_bd.capacidad
        }
        
        horarios.append(horario_info)
        print("Resultado: {}".format('✅ DISPONIBLE' if horario_info['disponible'] else '❌ NO DISPONIBLE'))
    
    print("\n=== RESULTADO FINAL ===")
    print(f"Total horarios procesados: {len(horarios)}")
    
    if not horarios:
        print("❌ No hay horarios disponibles para esta fecha")
        return False
    
    horarios_disponibles_count = sum(1 for h in horarios if h['disponible'])
    print(f"Horarios con disponibilidad: {horarios_disponibles_count}")
    
    if horarios_disponibles_count == 0:
        print("❌ No hay horarios con bahías disponibles")
        return False
    
    print("✅ HAY HORARIOS DISPONIBLES:")
    for horario in horarios:
        if horario['disponible']:
            print(f"  - {horario['hora_inicio']} - {horario['hora_fin']}: {horario['bahias_disponibles']}/{horario['bahias_totales']} bahías")
    
    return True

if __name__ == "__main__":
    test_logica_corregida()