from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from dashboard_gerente.models import KPIConfiguracion

class Command(BaseCommand):
    help = "Crea KPIs de ejemplo para visualizar funcionamiento (Reservas e Ingresos)"

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default=None, help='Usuario propietario de los KPIs (por defecto, el primero)')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Usuario '{username}' no existe"))
                return
        else:
            user = User.objects.order_by('id').first()
            if not user:
                self.stderr.write(self.style.ERROR("No hay usuarios en el sistema"))
                return

        ejemplos = [
            # Volumen de reservas por día (Conteo)
            dict(nombre='Volumen Reservas Diario', entidad='reservas', metrica='count', campo='id', estado_filtro='', periodo_dias=30, umbral_alerta=None, activo=True),
            # Ingresos diarios (Suma de precio_final)
            dict(nombre='Ingresos Diarios', entidad='reservas', metrica='sum', campo='precio_final', estado_filtro='completada', periodo_dias=30, umbral_alerta=None, activo=True),
            # Ticket promedio (Promedio de precio_final)
            dict(nombre='Ticket Promedio', entidad='reservas', metrica='avg', campo='precio_final', estado_filtro='completada', periodo_dias=30, umbral_alerta=None, activo=True),
            # Uso de descuentos (Suma)
            dict(nombre='Descuentos Aplicados', entidad='reservas', metrica='sum', campo='descuento_aplicado', estado_filtro='', periodo_dias=30, umbral_alerta=None, activo=True),
        ]

        creados = 0
        for e in ejemplos:
            obj, created = KPIConfiguracion.objects.get_or_create(
                usuario=user,
                nombre=e['nombre'],
                defaults=e,
            )
            if created:
                creados += 1
        self.stdout.write(self.style.SUCCESS(f"KPIs de demo creados: {creados}"))