# Documentación de la API REST

## Descripción General

La API REST de la Plataforma de Autolavados proporciona acceso programático a las funcionalidades del sistema, permitiendo la integración con aplicaciones móviles, sitios web externos u otros sistemas. Esta API sigue los principios RESTful y utiliza JSON como formato de intercambio de datos.

## Autenticación

La API utiliza autenticación basada en tokens JWT (JSON Web Tokens).

### Obtener Token

```
POST /api/auth/token/
```

**Parámetros de solicitud:**

```json
{
  "username": "usuario",
  "password": "contraseña"
}
```

**Respuesta exitosa:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Refrescar Token

```
POST /api/auth/token/refresh/
```

**Parámetros de solicitud:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Respuesta exitosa:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Uso del Token

Incluya el token en el encabezado de autorización de todas las solicitudes:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Endpoints

### Clientes

#### Listar Clientes

```
GET /api/clientes/
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "nombre": "Juan Pérez",
    "email": "juan@ejemplo.com",
    "telefono": "3001234567",
    "fecha_registro": "2023-01-15T10:30:00Z"
  },
  {...}
]
```

#### Obtener Cliente

```
GET /api/clientes/{id}/
```

**Respuesta:**

```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "email": "juan@ejemplo.com",
  "telefono": "3001234567",
  "fecha_registro": "2023-01-15T10:30:00Z",
  "vehiculos": [
    {
      "id": 1,
      "placa": "ABC123",
      "marca": "Toyota",
      "modelo": "Corolla",
      "año": 2020
    },
    {...}
  ]
}
```

#### Crear Cliente

```
POST /api/clientes/
```

**Parámetros de solicitud:**

```json
{
  "nombre": "María López",
  "email": "maria@ejemplo.com",
  "telefono": "3007654321"
}
```

**Respuesta exitosa:**

```json
{
  "id": 2,
  "nombre": "María López",
  "email": "maria@ejemplo.com",
  "telefono": "3007654321",
  "fecha_registro": "2023-06-20T14:25:00Z"
}
```

### Vehículos

#### Listar Vehículos de un Cliente

```
GET /api/clientes/{cliente_id}/vehiculos/
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "placa": "ABC123",
    "marca": "Toyota",
    "modelo": "Corolla",
    "año": 2020
  },
  {...}
]
```

#### Crear Vehículo

```
POST /api/clientes/{cliente_id}/vehiculos/
```

**Parámetros de solicitud:**

```json
{
  "placa": "XYZ789",
  "marca": "Honda",
  "modelo": "Civic",
  "año": 2021
}
```

### Servicios

#### Listar Servicios

```
GET /api/servicios/
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "nombre": "Lavado Básico",
    "descripcion": "Lavado exterior del vehículo",
    "precio": 15000,
    "duracion_minutos": 30
  },
  {...}
]
```

### Horarios Disponibles

#### Listar Horarios Disponibles

```
GET /api/horarios-disponibles/?fecha=2023-06-21
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "fecha": "2023-06-21",
    "hora_inicio": "09:00:00",
    "hora_fin": "09:30:00",
    "bahia": 1,
    "disponible": true
  },
  {...}
]
```

### Reservas

#### Listar Reservas

```
GET /api/reservas/
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "cliente": 1,
    "vehiculo": 1,
    "servicio": 1,
    "horario": 1,
    "estado": "PENDIENTE",
    "fecha_creacion": "2023-06-20T10:15:00Z",
    "fecha_actualizacion": "2023-06-20T10:15:00Z"
  },
  {...}
]
```

#### Crear Reserva

```
POST /api/reservas/
```

**Parámetros de solicitud:**

```json
{
  "cliente": 1,
  "vehiculo": 1,
  "servicio": 1,
  "horario": 1
}
```

**Respuesta exitosa:**

```json
{
  "id": 2,
  "cliente": 1,
  "vehiculo": 1,
  "servicio": 1,
  "horario": 1,
  "estado": "PENDIENTE",
  "fecha_creacion": "2023-06-20T15:30:00Z",
  "fecha_actualizacion": "2023-06-20T15:30:00Z"
}
```

#### Actualizar Estado de Reserva

```
PATCH /api/reservas/{id}/
```

**Parámetros de solicitud:**

```json
{
  "estado": "CONFIRMADA"
}
```

### Notificaciones

#### Listar Notificaciones del Cliente

```
GET /api/clientes/{cliente_id}/notificaciones/
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "cliente": 1,
    "titulo": "Reserva Confirmada",
    "mensaje": "Su reserva para el 21/06/2023 a las 09:00 ha sido confirmada.",
    "leida": false,
    "fecha_creacion": "2023-06-20T10:20:00Z"
  },
  {...}
]
```

#### Marcar Notificación como Leída

```
PATCH /api/notificaciones/{id}/
```

**Parámetros de solicitud:**

```json
{
  "leida": true
}
```

## Códigos de Estado

- `200 OK`: Solicitud exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Solicitud inválida
- `401 Unauthorized`: Autenticación requerida
- `403 Forbidden`: No tiene permisos para acceder al recurso
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor

## Paginación

Las respuestas que devuelven múltiples elementos están paginadas por defecto. Puede especificar el tamaño de la página y el número de página utilizando los parámetros `page_size` y `page`:

```
GET /api/reservas/?page=2&page_size=10
```

**Respuesta:**

```json
{
  "count": 45,
  "next": "http://api.ejemplo.com/api/reservas/?page=3&page_size=10",
  "previous": "http://api.ejemplo.com/api/reservas/?page=1&page_size=10",
  "results": [
    {...},
    {...}
  ]
}
```

## Filtrado

Muchos endpoints soportan filtrado de resultados. Por ejemplo:

```
GET /api/reservas/?estado=PENDIENTE
```

## Ordenamiento

Puede ordenar los resultados utilizando el parámetro `ordering`:

```
GET /api/reservas/?ordering=-fecha_creacion
```

Use el prefijo `-` para ordenar de forma descendente.

## Manejo de Errores

En caso de error, la API devolverá un objeto JSON con detalles sobre el error:

```json
{
  "error": "Mensaje de error",
  "detail": "Descripción detallada del error",
  "code": "ERROR_CODE"
}
```

## Límites de Tasa

La API tiene límites de tasa para prevenir abusos. Los límites actuales son:

- 100 solicitudes por minuto para usuarios autenticados
- 20 solicitudes por minuto para usuarios no autenticados

Si excede estos límites, recibirá un código de estado `429 Too Many Requests`.

## Versiones de la API

La versión actual de la API es v1. Puede especificar la versión en la URL:

```
/api/v1/reservas/
```

## Soporte

Si tiene problemas o preguntas sobre la API, contacte al equipo de soporte en api-support@ejemplo.com.