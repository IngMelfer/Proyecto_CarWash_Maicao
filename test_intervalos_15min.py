#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from reservas.models import HorarioDisponible, Reserva, Servicio

def test_intervalos_15_minutos():
    """
    Prueba que los horarios se generen cada 15 minutos desde la hora actual + 30 min
    """
    print("=== PRUEBA: Intervalos de 15 Minutos ===")
    
    # Simular la hora actual (22:53)
    fecha_actual = datetime.strptime('2025-09-17', '%Y-%m-%d').date()
    hora_actual = datetime.strptime('22:53:00', '%H:%M:%S').time()
    now_local = datetime.combine(fecha_actual, hora_actual)
    
    print(f"Fecha: {fecha_actual}")
    print(f"Hora actual simulada: {hora_actual}")
    
    # Obtener un servicio de ejemplo
    servicio = Servicio.objects.first()
    if not servicio:
        print("❌ No hay servicios en la base de datos")
        return
    
    duracion_servicio = servicio.duracion_minutos
    print(f"Servicio: {servicio.nombre} (duración: {duracion_servicio} min)")
    
    # Obtener horarios de la base de datos
    horarios_bd = HorarioDisponible.objects.filter(
        fecha=fecha_actual,
        disponible=True
    ).order_by('hora_inicio')
    
    print(f"\nHorarios base en la BD: {horarios_bd.count()}")
    
    horarios_generados = []
    
    for horario_bd in horarios_bd:
        print(f"\n--- Procesando Horario Base: {horario_bd.hora_inicio} a {horario_bd.hora_fin} ---")
        print(f"Capacidad: {horario_bd.capacidad}")
        
        # Determinar la hora de inicio para generar intervalos
        if fecha_actual == now_local.date():
            # Para el día actual, empezar desde la hora actual + 30 minutos
            hora_minima = (now_local + timedelta(minutes=30)).time()
            print(f"Hora mínima (actual + 30 min): {hora_minima}")
            
            # Si la hora mínima es después del fin del horario, saltar este horario
            if hora_minima >= horario_bd.hora_fin:
                print(f"❌ HORARIO TERMINADO: {hora_minima} >= {horario_bd.hora_fin}")
                continue
            
            # Usar la hora más tardía entre el inicio del horario y la hora mínima
            if hora_minima > horario_bd.hora_inicio:
                hora_inicio_intervalo = hora_minima
            else:
                hora_inicio_intervalo = horario_bd.hora_inicio
        else:
            # Para fechas futuras, usar la hora de inicio del horario
            hora_inicio_intervalo = horario_bd.hora_inicio
        
        print(f"Hora de inicio para intervalos: {hora_inicio_intervalo}")
        
        # Redondear la hora de inicio al próximo intervalo de 15 minutos
        dt_inicio = datetime.combine(fecha_actual, hora_inicio_intervalo)
        minutos = dt_inicio.minute
        # Redondear hacia arriba al próximo múltiplo de 15
        minutos_redondeados = ((minutos + 14) // 15) * 15
        if minutos_redondeados >= 60:
            dt_inicio = dt_inicio.replace(minute=0) + timedelta(hours=1)
        else:
            dt_inicio = dt_inicio.replace(minute=minutos_redondeados)
        
        print(f"Hora redondeada a 15 min: {dt_inicio.time()}")
        
        # Generar intervalos de 15 minutos
        hora_actual_intervalo = dt_inicio.time()
        contador_intervalos = 0
        
        while hora_actual_intervalo < horario_bd.hora_fin:
            # Calcular la hora de fin del servicio
            dt_fin_servicio = datetime.combine(fecha_actual, hora_actual_intervalo) + timedelta(minutes=duracion_servicio)
            hora_fin_servicio = dt_fin_servicio.time()
            
            print(f"\n  🕐 Intervalo {contador_intervalos + 1}: {hora_actual_intervalo} - {hora_fin_servicio}")
            
            # Verificar que el servicio termine antes del cierre del horario
            if hora_fin_servicio <= horario_bd.hora_fin:
                # Contar reservas existentes para este intervalo específico
                reservas_count = Reserva.objects.filter(
                    fecha_hora__date=fecha_actual,
                    fecha_hora__time=hora_actual_intervalo,
                    estado__in=['PE', 'CO', 'EP']  # PENDIENTE, CONFIRMADA, EN_PROCESO
                ).count()
                
                # Verificar disponibilidad basada en la capacidad del horario
                bahias_disponibles = max(0, horario_bd.capacidad - reservas_count)
                
                print(f"    📊 Reservas: {reservas_count}, Bahías disponibles: {bahias_disponibles}")
                
                if bahias_disponibles > 0:
                    print("    ✅ DISPONIBLE")
                    horarios_generados.append({
                        'hora_inicio': hora_actual_intervalo.strftime('%H:%M'),
                        'hora_fin': hora_fin_servicio.strftime('%H:%M'),
                        'disponible': True,
                        'bahias_disponibles': bahias_disponibles,
                        'bahias_totales': horario_bd.capacidad
                    })
                else:
                    print("    ❌ SIN BAHÍAS")
                
                contador_intervalos += 1
            else:
                print(f"    ❌ SERVICIO NO CABE: {hora_fin_servicio} > {horario_bd.hora_fin}")
            
            # Avanzar al siguiente intervalo de 15 minutos
            dt_siguiente = datetime.combine(fecha_actual, hora_actual_intervalo) + timedelta(minutes=15)
            hora_actual_intervalo = dt_siguiente.time()
        
        print(f"Total intervalos generados para este horario: {contador_intervalos}")
    
    print("\n=== RESULTADO FINAL ===")
    print(f"Horarios específicos generados: {len(horarios_generados)}")
    
    if horarios_generados:
        print("\nHorarios disponibles:")
        for i, h in enumerate(horarios_generados, 1):
            print(f"  {i}. {h['hora_inicio']} - {h['hora_fin']} ({h['bahias_disponibles']}/{h['bahias_totales']} bahías)")
    else:
        print("❌ No se generaron horarios disponibles")
    
    print("\n=== Fin de la prueba ===")

if __name__ == '__main__':
    test_intervalos_15_minutos()