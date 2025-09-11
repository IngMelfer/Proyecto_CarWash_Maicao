# Estructura del Proyecto Autolavados-Plataforma

## Visión General

Este documento describe la estructura general del proyecto, sus componentes principales y cómo interactúan entre sí. La plataforma está construida utilizando Django como framework principal, con una arquitectura que separa claramente las diferentes funcionalidades del sistema.

## Estructura de Directorios

```
autolavados-plataforma/
├── autolavados_plataforma/    # Configuración principal del proyecto Django
├── autenticacion/             # App para gestión de usuarios y autenticación
├── clientes/                  # App para gestión de clientes y vehículos
├── notificaciones/            # App para sistema de notificaciones
├── reservas/                  # App principal para gestión de reservas
├── scripts/                   # Scripts de utilidad y tareas programadas
├── static/                    # Archivos estáticos (CSS, JS, imágenes)
├── templates/                 # Plantillas HTML
├── .env.example               # Ejemplo de variables de entorno
├── .env.local                 # Variables de entorno locales (no en control de versiones)
├── manage.py                  # Script de gestión de Django
└── requirements.txt           # Dependencias del proyecto
```

## Componentes Principales

### 1. Aplicaciones Django

#### Autenticación (`autenticacion/`)

Gestiona usuarios, permisos y procesos de autenticación.

**Modelos principales:**
- Extensión del modelo User de Django

**Funcionalidades:**
- Registro de usuarios
- Inicio de sesión
- Recuperación de contraseña
- Gestión de perfiles

#### Clientes (`clientes/`)

Gestiona la información de clientes y sus vehículos.

**Modelos principales:**
- Cliente
- Vehiculo

**Funcionalidades:**
- Registro de clientes
- Gestión de vehículos
- Historial de servicios

#### Notificaciones (`notificaciones/`)

Sistema de notificaciones para mantener informados a los clientes.

**Modelos principales:**
- Notificacion

**Funcionalidades:**
- Creación de notificaciones
- Marcado de notificaciones como leídas
- Envío de notificaciones por correo electrónico

#### Reservas (`reservas/`)

Núcleo del sistema, gestiona todo el proceso de reservas de servicios.

**Modelos principales:**
- Reserva
- HorarioDisponible
- Servicio
- Bahia

**Funcionalidades:**
- Creación y gestión de reservas
- Gestión de horarios disponibles
- Configuración de servicios
- Gestión de bahías (espacios físicos para servicios)

**Comandos personalizados:**
- `cancelar_reservas_sin_pago`: Cancela reservas pendientes sin pago
- `verificar_reservas_vencidas`: Marca como incumplidas las reservas vencidas

### 2. Scripts y Utilidades (`scripts/`)

**Scripts principales:**
- `cancelar_reservas_sin_pago.bat`: Script batch para Windows
- `cancelar_reservas_sin_pago_silencioso.vbs`: Script VBS para ejecución silenciosa en Windows
- `configurar_tarea_pythonanywhere.py`: Configura tareas programadas en PythonAnywhere

**Documentación:**
- `README_CANCELACION_RESERVAS.md`: Documentación del sistema de cancelación
- `README_VERIFICACION_RESERVAS.md`: Documentación del sistema de verificación
- `INSTRUCCIONES_TAREA_PROGRAMADA_DETALLADAS.md`: Guía para configurar tareas en Windows
- `INSTRUCCIONES_PYTHONANYWHERE_DETALLADAS.md`: Guía para configurar tareas en PythonAnywhere

### 3. Configuración del Proyecto (`autolavados_plataforma/`)

**Archivos principales:**
- `settings.py`: Configuración principal de Django
- `urls.py`: Configuración de URLs del proyecto
- `wsgi.py` y `asgi.py`: Configuración para despliegue

### 4. Archivos Estáticos y Plantillas

**Estáticos (`static/`):**
- CSS: Estilos de la aplicación
- JS: Scripts de JavaScript
- Imágenes: Recursos gráficos

**Plantillas (`templates/`):**
- Plantillas base y específicas para cada aplicación

## Flujos de Trabajo Principales

### 1. Proceso de Reserva

1. Cliente selecciona servicio y fecha/hora
2. Sistema verifica disponibilidad
3. Cliente confirma reserva (estado PENDIENTE)
4. Cliente realiza pago
5. Sistema confirma reserva (estado CONFIRMADA)
6. Cliente recibe notificación

### 2. Cancelación Automática de Reservas Sin Pago

1. Tarea programada se ejecuta periódicamente
2. Identifica reservas PENDIENTES sin pago por más del tiempo configurado
3. Cancela estas reservas y libera horarios
4. Notifica a los clientes

### 3. Verificación de Reservas Vencidas

1. Tarea programada se ejecuta periódicamente
2. Identifica reservas cuya fecha/hora ya pasó
3. Marca estas reservas como INCUMPLIDAS
4. Notifica a los clientes

## Interacción entre Componentes

### Modelo de Datos Simplificado

```
Cliente 1:N Vehiculo
Cliente 1:N Reserva
Reserva N:1 Servicio
Reserva N:1 HorarioDisponible
Reserva N:1 Bahia
Cliente 1:N Notificacion
```

### API REST

La plataforma expone una API REST para interactuar con aplicaciones móviles o de terceros:

- `/api/auth/`: Endpoints de autenticación
- `/api/clientes/`: Gestión de clientes y vehículos
- `/api/reservas/`: Gestión de reservas
- `/api/notificaciones/`: Sistema de notificaciones

## Despliegue

El proyecto está configurado para ser desplegado en diferentes entornos:

- **Desarrollo local**: Configuración en `.env.local`
- **Railway**: Configuración en `railway.json`
- **PythonAnywhere**: Scripts específicos para este entorno

## Extensibilidad

El proyecto está diseñado para ser fácilmente extensible:

1. **Nuevos servicios**: Agregar registros en el modelo Servicio
2. **Nuevas funcionalidades**: Crear nuevas aplicaciones Django
3. **Tareas programadas**: Agregar nuevos comandos en `management/commands/`

## Consideraciones de Seguridad

1. **Variables de entorno**: Credenciales y configuraciones sensibles en `.env`
2. **Autenticación API**: Uso de tokens JWT para autenticación
3. **Permisos**: Sistema de permisos basado en roles

## Recursos Adicionales

- [README principal](README.md): Información general del proyecto
- [Guía de despliegue en Railway](GUIA_DESPLIEGUE_RAILWAY.md): Instrucciones para despliegue
- [Documentación de tareas programadas](README_TAREAS_PROGRAMADAS.md): Detalles sobre automatización