from django.db import migrations, models
import django.db.models.deletion

def migrar_tipos_documento(apps, schema_editor):
    Empleado = apps.get_model('empleados', 'Empleado')
    TipoDocumento = apps.get_model('empleados', 'TipoDocumento')
    
    # Mapeo de códigos antiguos a nuevos modelos
    mapeo_tipos = {
        'CC': TipoDocumento.objects.get(codigo='CC'),
        'PA': TipoDocumento.objects.get(codigo='PA'),
        'CE': TipoDocumento.objects.get(codigo='CE'),
    }
    
    # Actualizar cada empleado con el nuevo tipo de documento
    for empleado in Empleado.objects.all():
        if empleado.tipo_documento_old in mapeo_tipos:
            empleado.tipo_documento = mapeo_tipos[empleado.tipo_documento_old]
            empleado.save(update_fields=['tipo_documento'])

def migrar_cargos(apps, schema_editor):
    Empleado = apps.get_model('empleados', 'Empleado')
    Cargo = apps.get_model('empleados', 'Cargo')
    
    # Mapeo de códigos antiguos a nuevos modelos
    mapeo_cargos = {
        'LAV': Cargo.objects.get(codigo='LAV'),
        'SEC': Cargo.objects.get(codigo='SEC'),
        'SUP': Cargo.objects.get(codigo='SUP'),
        'CAJ': Cargo.objects.get(codigo='CAJ'),
    }
    
    # Actualizar cada empleado con el nuevo cargo
    for empleado in Empleado.objects.all():
        if empleado.cargo_old in mapeo_cargos:
            empleado.cargo = mapeo_cargos[empleado.cargo_old]
            empleado.save(update_fields=['cargo'])

class Migration(migrations.Migration):

    dependencies = [
        ('empleados', '0002_create_tipo_documento_cargo'),
    ]

    operations = [
        # Renombrar campos actuales para preservar los datos
        migrations.RenameField(
            model_name='empleado',
            old_name='tipo_documento',
            new_name='tipo_documento_old',
        ),
        migrations.RenameField(
            model_name='empleado',
            old_name='cargo',
            new_name='cargo_old',
        ),
        
        # Agregar nuevos campos como ForeignKey
        migrations.AddField(
            model_name='empleado',
            name='tipo_documento',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='empleados', to='empleados.tipodocumento', verbose_name='Tipo de Documento'),
        ),
        migrations.AddField(
            model_name='empleado',
            name='cargo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='empleados', to='empleados.cargo', verbose_name='Cargo'),
        ),
        
        # Migrar datos de los campos antiguos a los nuevos
        migrations.RunPython(migrar_tipos_documento),
        migrations.RunPython(migrar_cargos),
        
        # Eliminar campos antiguos
        migrations.RemoveField(
            model_name='empleado',
            name='tipo_documento_old',
        ),
        migrations.RemoveField(
            model_name='empleado',
            name='cargo_old',
        ),
        
        # Hacer los campos obligatorios
        migrations.AlterField(
            model_name='empleado',
            name='tipo_documento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='empleados', to='empleados.tipodocumento', verbose_name='Tipo de Documento'),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='cargo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='empleados', to='empleados.cargo', verbose_name='Cargo'),
        ),
    ]