from django.db import migrations, models
import django.utils.timezone

def crear_tipos_documento(apps, schema_editor):
    TipoDocumento = apps.get_model('empleados', 'TipoDocumento')
    
    # Crear los tipos de documento predefinidos
    TipoDocumento.objects.create(
        codigo='CC',
        nombre='Cédula de Ciudadanía',
        activo=True,
        fecha_creacion=django.utils.timezone.now(),
        fecha_actualizacion=django.utils.timezone.now()
    )
    
    TipoDocumento.objects.create(
        codigo='PA',
        nombre='Pasaporte',
        activo=True,
        fecha_creacion=django.utils.timezone.now(),
        fecha_actualizacion=django.utils.timezone.now()
    )
    
    TipoDocumento.objects.create(
        codigo='CE',
        nombre='Cédula de Extranjería',
        activo=True,
        fecha_creacion=django.utils.timezone.now(),
        fecha_actualizacion=django.utils.timezone.now()
    )

def crear_cargos(apps, schema_editor):
    Cargo = apps.get_model('empleados', 'Cargo')
    
    # Crear los cargos predefinidos
    Cargo.objects.create(
        codigo='LAV',
        nombre='Lavador',
        descripcion='Encargado de lavar los vehículos',
        activo=True,
        fecha_creacion=django.utils.timezone.now(),
        fecha_actualizacion=django.utils.timezone.now()
    )
    
    Cargo.objects.create(
        codigo='SEC',
        nombre='Secador',
        descripcion='Encargado de secar los vehículos',
        activo=True,
        fecha_creacion=django.utils.timezone.now(),
        fecha_actualizacion=django.utils.timezone.now()
    )
    
    Cargo.objects.create(
        codigo='SUP',
        nombre='Supervisor',
        descripcion='Encargado de supervisar el trabajo de los empleados',
        activo=True,
        fecha_creacion=django.utils.timezone.now(),
        fecha_actualizacion=django.utils.timezone.now()
    )
    
    Cargo.objects.create(
        codigo='CAJ',
        nombre='Cajero',
        descripcion='Encargado de manejar los pagos y la caja',
        activo=True,
        fecha_creacion=django.utils.timezone.now(),
        fecha_actualizacion=django.utils.timezone.now()
    )

class Migration(migrations.Migration):

    dependencies = [
        ('empleados', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoDocumento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=5, unique=True, verbose_name='Código')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Última Actualización')),
            ],
            options={
                'verbose_name': 'Tipo de Documento',
                'verbose_name_plural': 'Tipos de Documento',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Cargo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=5, unique=True, verbose_name='Código')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Última Actualización')),
            ],
            options={
                'verbose_name': 'Cargo',
                'verbose_name_plural': 'Cargos',
                'ordering': ['nombre'],
            },
        ),
        migrations.RunPython(crear_tipos_documento),
        migrations.RunPython(crear_cargos),
    ]