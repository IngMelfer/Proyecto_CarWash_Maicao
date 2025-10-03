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

def test_horarios_sin_pasados():
    """
    Prueba que los horarios que ya comenzaron no se muestren como disponibles
    """
    print("=== PRUEBA: Horarios sin pasados ===")
    
    # Obtener fecha actual
    hoy = datetime.now().date()
    hora_actual = datetime.now().time()
    
    print(f"Fecha actual: {hoy}")
    print(f"Hora actual: {hora_actual}")
    
    # Obtener horarios de hoy
    horarios_hoy = HorarioDisponible.objects.filter(
        fecha=hoy,
        disponible=True
    ).order_by('hora_inicio')
    
    print(f"\nHorarios en la base de datos para hoy: {horarios_hoy.count()}")
    
    for horario in horarios_hoy:
        print(f"  - {horario.hora_inicio} a {horario.hora_fin} (Capacidad: {horario.capacidad})")
        
        # Verificar si el horario ya comenzó
        if hora_actual >= horario.hora_inicio:
            print("    ❌ HORARIO YA COMENZÓ - No debería mostrarse")
        elif hora_actual >= horario.hora_fin:
            print("    ❌ HORARIO YA TERMINÓ - No debería mostrarse")
        else:
            # Verificar margen de 30 minutos
            hora_minima = (datetime.now() + timedelta(minutes=30)).time()
            if horario.hora_inicio < hora_minima:
                print("    ⚠️  HORARIO DENTRO DE 30 MIN - No debería mostrarse")
            else:
                print("    ✅ HORARIO DISPONIBLE - Debería mostrarse")
    
    print("\n=== Fin de la prueba ===")

if __name__ == '__main__':
    test_horarios_sin_pasados()