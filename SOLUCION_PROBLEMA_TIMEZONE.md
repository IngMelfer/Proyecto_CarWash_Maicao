# Solución al Problema de Timezone en MySQL con Django

## Problema

Se presentaba el siguiente error al acceder al dashboard de administración:

```
ValueError: MySQL backend does not support timezone-aware datetimes when USE_TZ is False.
```

Este error ocurría en la ruta `/reservas/dashboard-admin/` y estaba relacionado con la forma en que Django manejaba las fechas con zonas horarias cuando la configuración `USE_TZ` estaba desactivada.

## Causa

El problema se originaba por una incompatibilidad entre:

1. La configuración `USE_TZ = False` en `settings.py` (que desactiva el soporte de zonas horarias en Django)
2. El uso de funciones como `timezone.make_aware()` en `views_admin.py` que intentaban crear objetos datetime con información de zona horaria
3. MySQL no soporta datetimes con zona horaria cuando `USE_TZ` está desactivado

## Solución Implementada

Se realizaron los siguientes cambios:

### 1. Modificación en `views_admin.py`

Se eliminaron las llamadas a `timezone.make_aware()` y se reemplazaron por la creación directa de objetos datetime sin información de zona horaria:

```python
# Antes
hoy = timezone.now().date()
manana = hoy + timezone.timedelta(days=1)
reservas_pendientes = Reserva.objects.filter(
    fecha_hora__gte=timezone.make_aware(timezone.datetime.combine(hoy, timezone.datetime.min.time())),
    fecha_hora__lt=timezone.make_aware(timezone.datetime.combine(manana, timezone.datetime.min.time())),
    estado=Reserva.CONFIRMADA
).count()

# Después
hoy = timezone.now().date()
manana = hoy + timezone.timedelta(days=1)

# Crear objetos datetime sin zona horaria ya que USE_TZ=False
inicio_dia = timezone.datetime.combine(hoy, timezone.datetime.min.time())
fin_dia = timezone.datetime.combine(manana, timezone.datetime.min.time())

reservas_pendientes = Reserva.objects.filter(
    fecha_hora__gte=inicio_dia,
    fecha_hora__lt=fin_dia,
    estado=Reserva.CONFIRMADA
).count()
```

Este cambio se aplicó en dos lugares del archivo `views_admin.py` donde se realizaban consultas similares.

## Recomendaciones

1. **Consistencia en el manejo de fechas**: Mantener un enfoque consistente en toda la aplicación. Si `USE_TZ=False`, no usar funciones que creen datetimes con zona horaria.

2. **Documentación**: Añadir comentarios en el código para explicar el manejo de fechas y evitar futuros errores.

3. **Middleware de zona horaria**: El proyecto ya cuenta con un middleware (`TimezoneMiddleware`) que configura MySQL para usar UTC (`+00:00`). Esto es importante para mantener consistencia entre Django y MySQL.

4. **Migración de datos**: Si se cambia la configuración de zona horaria en el futuro, será necesario migrar los datos existentes para asegurar que las fechas se interpreten correctamente.

## Verificación

Después de implementar estos cambios, el dashboard de administración carga correctamente sin errores relacionados con zonas horarias.