from django.utils import timezone
import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

# Importar modelos después de configurar Django
from reservas.models import DisponibilidadHoraria

# Crear disponibilidad horaria para todos los días de la semana
def crear_disponibilidad():
    # Eliminar registros existentes para evitar duplicados
    DisponibilidadHoraria.objects.all().delete()
    
    # Crear disponibilidad para cada día de la semana (0=Lunes, 6=Domingo)
    for dia in range(7):
        DisponibilidadHoraria.objects.create(
            dia_semana=dia,
            hora_inicio='06:00',
            hora_fin='18:00',
            capacidad_maxima=5,
            activo=True
        )
        print(f'Creada disponibilidad para día {dia} de 06:00 a 18:00')
    
    # Verificar que se hayan creado los registros
    registros = DisponibilidadHoraria.objects.all()
    print(f'\nTotal de registros creados: {registros.count()}')
    for reg in registros:
        print(f'Día: {reg.get_dia_semana_display()}, Hora inicio: {reg.hora_inicio}, Hora fin: {reg.hora_fin}')

if __name__ == '__main__':
    crear_disponibilidad()