from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Empleado, RegistroTiempo, Calificacion, Incentivo
from autenticacion.models import Usuario
from reservas.models import Servicio
from clientes.models import Cliente
import datetime

Usuario = get_user_model()

class EmpleadoModelTest(TestCase):
    def setUp(self):
        # Crear usuario para empleado
        self.usuario = Usuario.objects.create_user(
            email='empleado@test.com',
            password='password123',
            rol=Usuario.ROL_EMPLEADO
        )
        
        # Crear empleado
        self.empleado = Empleado.objects.create(
            usuario=self.usuario,
            nombre='Juan',
            apellido='Pérez',
            tipo_documento='CC',
            numero_documento='1234567890',
            telefono='3001234567',
            direccion='Calle 123',
            ciudad='Bogotá',
            fecha_nacimiento=datetime.date(1990, 1, 1),
            cargo='Lavador',
            fecha_contratacion=datetime.date.today()
        )
    
    def test_empleado_creation(self):
        self.assertEqual(self.empleado.nombre, 'Juan')
        self.assertEqual(self.empleado.apellido, 'Pérez')
        self.assertEqual(self.empleado.usuario, self.usuario)
        self.assertTrue(self.empleado.activo)
    
    def test_empleado_str(self):
        self.assertEqual(str(self.empleado), 'Juan Pérez')
    
    def test_calificacion_promedio(self):
        # Sin calificaciones
        self.assertEqual(self.empleado.calificacion_promedio(), 0)
        
        # Crear cliente para calificaciones
        usuario_cliente = Usuario.objects.create_user(
            email='cliente@test.com',
            password='password123',
            rol=Usuario.ROL_CLIENTE
        )
        
        cliente = Cliente.objects.create(
            usuario=usuario_cliente,
            nombre='Cliente',
            apellido='Test',
            tipo_documento='CC',
            numero_documento='0987654321',
            email='cliente@test.com'
        )
        
        # Crear servicio para calificaciones
        servicio = Servicio.objects.create(
            nombre='Lavado Básico',
            descripcion='Lavado exterior del vehículo',
            precio=30000,
            duracion=30
        )
        
        # Crear calificaciones
        Calificacion.objects.create(
            empleado=self.empleado,
            cliente=cliente,
            servicio=servicio,
            puntuacion=4,
            comentario='Buen servicio'
        )
        
        Calificacion.objects.create(
            empleado=self.empleado,
            cliente=cliente,
            servicio=servicio,
            puntuacion=5,
            comentario='Excelente servicio'
        )
        
        # Verificar promedio
        self.assertEqual(self.empleado.calificacion_promedio(), 4.5)

class RegistroTiempoModelTest(TestCase):
    def setUp(self):
        # Crear usuario para empleado
        self.usuario = Usuario.objects.create_user(
            email='empleado@test.com',
            password='password123',
            rol=Usuario.ROL_EMPLEADO
        )
        
        # Crear empleado
        self.empleado = Empleado.objects.create(
            usuario=self.usuario,
            nombre='Juan',
            apellido='Pérez',
            tipo_documento='CC',
            numero_documento='1234567890',
            cargo='Lavador'
        )
        
        # Crear servicio
        self.servicio = Servicio.objects.create(
            nombre='Lavado Básico',
            descripcion='Lavado exterior del vehículo',
            precio=30000,
            duracion=30
        )
        
        # Crear registros de tiempo
        self.inicio_servicio = RegistroTiempo.objects.create(
            empleado=self.empleado,
            tipo_registro='inicio_servicio',
            servicio=self.servicio,
            fecha_hora=timezone.now() - datetime.timedelta(hours=1)
        )
    
    def test_registro_tiempo_creation(self):
        self.assertEqual(self.inicio_servicio.empleado, self.empleado)
        self.assertEqual(self.inicio_servicio.tipo_registro, 'inicio_servicio')
        self.assertEqual(self.inicio_servicio.servicio, self.servicio)
    
    def test_registro_tiempo_duracion(self):
        # Crear registro de fin de servicio
        fin_servicio = RegistroTiempo.objects.create(
            empleado=self.empleado,
            tipo_registro='fin_servicio',
            servicio=self.servicio,
            fecha_hora=timezone.now()
        )
        
        # Verificar que la duración se calcula correctamente
        self.assertIsNotNone(fin_servicio.duracion)
        self.assertTrue(fin_servicio.duracion.total_seconds() > 0)

class EmpleadoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Crear usuario administrador
        self.admin_user = Usuario.objects.create_user(
            email='admin@test.com',
            password='password123',
            rol=Usuario.ROL_ADMINISTRADOR,
            is_staff=True
        )
        
        # Crear usuario empleado
        self.empleado_user = Usuario.objects.create_user(
            email='empleado@test.com',
            password='password123',
            rol=Usuario.ROL_EMPLEADO
        )
        
        # Crear empleado
        self.empleado = Empleado.objects.create(
            usuario=self.empleado_user,
            nombre='Juan',
            apellido='Pérez',
            tipo_documento='CC',
            numero_documento='1234567890',
            cargo='Lavador'
        )
    
    def test_empleado_list_view(self):
        # Login como administrador
        self.client.login(email='admin@test.com', password='password123')
        
        # Acceder a la vista de lista de empleados
        response = self.client.get(reverse('empleados:empleado_list'))
        
        # Verificar que la respuesta es exitosa
        self.assertEqual(response.status_code, 200)
        
        # Verificar que el empleado está en el contexto
        self.assertIn(self.empleado, response.context['empleado_list'])
    
    def test_empleado_detail_view(self):
        # Login como administrador
        self.client.login(email='admin@test.com', password='password123')
        
        # Acceder a la vista de detalle del empleado
        response = self.client.get(reverse('empleados:empleado_detail', args=[self.empleado.id]))
        
        # Verificar que la respuesta es exitosa
        self.assertEqual(response.status_code, 200)
        
        # Verificar que el empleado está en el contexto
        self.assertEqual(response.context['empleado'], self.empleado)
    
    def test_registro_tiempo_view(self):
        # Login como empleado
        self.client.login(email='empleado@test.com', password='password123')
        
        # Acceder a la vista de registro de tiempo
        response = self.client.get(reverse('empleados:registro_tiempo'))
        
        # Verificar que la respuesta es exitosa
        self.assertEqual(response.status_code, 200)
        
        # Verificar que el formulario está en el contexto
        self.assertIn('form', response.context)

class EmpleadoAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Crear usuario administrador
        self.admin_user = Usuario.objects.create_user(
            email='admin@test.com',
            password='password123',
            rol=Usuario.ROL_ADMINISTRADOR,
            is_staff=True
        )
        
        # Crear usuario empleado
        self.empleado_user = Usuario.objects.create_user(
            email='empleado@test.com',
            password='password123',
            rol=Usuario.ROL_EMPLEADO
        )
        
        # Crear empleado
        self.empleado = Empleado.objects.create(
            usuario=self.empleado_user,
            nombre='Juan',
            apellido='Pérez',
            tipo_documento='CC',
            numero_documento='1234567890',
            cargo='Lavador'
        )
    
    def test_empleado_api_list(self):
        # Login como administrador
        self.client.login(email='admin@test.com', password='password123')
        
        # Acceder a la API de lista de empleados
        response = self.client.get(reverse('empleados:api_empleados'))
        
        # Verificar que la respuesta es exitosa
        self.assertEqual(response.status_code, 200)
        
        # Verificar que la respuesta contiene datos
        self.assertTrue(len(response.json()) > 0)
    
    def test_empleado_api_detail(self):
        # Login como administrador
        self.client.login(email='admin@test.com', password='password123')
        
        # Acceder a la API de detalle del empleado
        response = self.client.get(reverse('empleados:api_empleado_detail', args=[self.empleado.id]))
        
        # Verificar que la respuesta es exitosa
        self.assertEqual(response.status_code, 200)
        
        # Verificar que la respuesta contiene los datos del empleado
        self.assertEqual(response.json()['id'], self.empleado.id)
        self.assertEqual(response.json()['nombre'], self.empleado.nombre)
        self.assertEqual(response.json()['apellido'], self.empleado.apellido)
