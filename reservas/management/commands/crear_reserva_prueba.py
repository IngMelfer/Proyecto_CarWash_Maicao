from django.core.management.base import BaseCommand
from django.utils import timezone
from reservas.models import Reserva, Bahia, Servicio, Vehiculo
from clientes.models import Cliente
from datetime import timedelta

class Command(BaseCommand):
    help = 'Crea una reserva de prueba con estado confirmado y fecha pasada para probar el inicio automático de servicios'

    def handle(self, *args, **options):
        # Verificar si hay clientes, vehículos, bahías y servicios disponibles
        if not Cliente.objects.exists():
            self.stdout.write(self.style.ERROR('No hay clientes disponibles. Cree un cliente primero.'))
            return
        
        if not Vehiculo.objects.exists():
            self.stdout.write(self.style.ERROR('No hay vehículos disponibles. Cree un vehículo primero.'))
            return
        
        if not Bahia.objects.exists():
            self.stdout.write(self.style.ERROR('No hay bahías disponibles. Cree una bahía primero.'))
            return
        
        if not Servicio.objects.exists():
            self.stdout.write(self.style.ERROR('No hay servicios disponibles. Cree un servicio primero.'))
            return
        
        # Obtener el primer cliente, vehículo, bahía, servicio y lavador disponibles
        cliente = Cliente.objects.first()
        vehiculo = Vehiculo.objects.filter(cliente=cliente).first() or Vehiculo.objects.first()
        bahia = Bahia.objects.first()
        servicio = Servicio.objects.first()
        
        # Intentar obtener un empleado con cargo de lavador
        from empleados.models import Empleado
        lavador = Empleado.objects.filter(cargo__icontains='lavador').first()
        
        # Crear una reserva con fecha 15 minutos en el pasado y estado confirmado
        fecha_hora = timezone.now() - timedelta(minutes=15)
        
        # Verificar si ya existe una reserva activa para esta bahía
        reserva_activa = Reserva.objects.filter(
            bahia=bahia,
            estado__in=[Reserva.CONFIRMADA, Reserva.EN_PROCESO]
        ).exists()
        
        if reserva_activa:
            self.stdout.write(self.style.ERROR(f'La bahía {bahia.nombre} ya tiene una reserva activa. Elija otra bahía o finalice el servicio actual.'))
            return
        
        # Crear la reserva
        reserva = Reserva.objects.create(
            cliente=cliente,
            vehiculo=vehiculo,
            bahia=bahia,
            servicio=servicio,
            fecha_hora=fecha_hora,
            estado=Reserva.CONFIRMADA,
            notas='Reserva de prueba para inicio automático de servicio',
            lavador=lavador
        )
        
        self.stdout.write(self.style.SUCCESS(f'Reserva creada exitosamente con ID {reserva.id}'))
        self.stdout.write(f'Cliente: {cliente.nombre} {cliente.apellido}')
        self.stdout.write(f'Vehículo: {vehiculo.marca} {vehiculo.modelo} ({vehiculo.placa})')
        self.stdout.write(f'Bahía: {bahia.nombre}')
        self.stdout.write(f'Servicio: {servicio.nombre}')
        self.stdout.write(f'Fecha y hora: {fecha_hora} (15 minutos en el pasado)')
        self.stdout.write(f'Estado: {reserva.get_estado_display()}')
        self.stdout.write(f'Lavador: {reserva.lavador.get_full_name() if reserva.lavador else "No asignado"}')
        self.stdout.write('\nAhora cargue el dashboard para ver si el servicio se inicia automáticamente.')