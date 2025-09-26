# Configuración de Cámaras IP en PythonAnywhere

## Introducción

Esta guía explica cómo configurar cámaras IP en el sistema de lavado de carros cuando está desplegado en PythonAnywhere. La configuración permite monitorear las bahías de lavado en tiempo real.

## Requisitos Previos

- Cuenta en PythonAnywhere (gratuita o de pago)
- Cámara IP compatible (IP Webcam, DroidCam, Iriun, RTSP, etc.)
- Router con capacidad de reenvío de puertos (para producción)
- Conocimientos básicos de configuración de red

## Tipos de Cámaras Soportadas

### 1. IP Webcam (Android)
- **App recomendada**: IP Webcam
- **Puerto por defecto**: 8080
- **URL típica**: `http://IP:8080/video`

### 2. DroidCam (Android/iOS)
- **App recomendada**: DroidCam
- **Puerto por defecto**: 4747
- **URL típica**: `http://IP:4747/video`

### 3. Iriun Webcam
- **Puerto por defecto**: 9090
- **URL típica**: `http://IP:9090`

### 4. RTSP (Cámaras profesionales)
- **Protocolo**: RTSP
- **URL típica**: `rtsp://IP:554/stream`

### 5. HTTP/HTTPS (Cámaras genéricas)
- **Protocolo**: HTTP/HTTPS
- **URL personalizable**

## Configuración Paso a Paso

### Paso 1: Configuración Local (Desarrollo)

1. **Instalar la app de cámara** en su dispositivo móvil
2. **Conectar el dispositivo** a la misma red WiFi que su computadora
3. **Obtener la IP local** del dispositivo (generalmente 192.168.x.x)
4. **Configurar en el sistema**:
   - Marcar "Tiene cámara": ✓
   - Seleccionar tipo de cámara
   - Ingresar IP local (ej: `192.168.1.100:8080`)
   - Dejar "Configuración de producción" sin marcar

### Paso 2: Configuración de Producción (PythonAnywhere)

#### 2.1 Configuración del Router

1. **Acceder al panel de administración** del router (generalmente 192.168.1.1)
2. **Configurar reenvío de puertos**:
   - Puerto interno: Puerto de la cámara (ej: 8080)
   - Puerto externo: Puerto público (ej: 8080 o diferente)
   - IP destino: IP local de la cámara
   - Protocolo: TCP

#### 2.2 Obtener IP Pública

1. **Verificar IP pública** en sitios como whatismyipaddress.com
2. **Configurar DNS dinámico** (opcional, recomendado para IPs dinámicas)

#### 2.3 Configuración en el Sistema

1. **Marcar "Configuración de producción"**: ✓
2. **Configurar campos de producción**:
   - **IP Pública**: Su IP pública o dominio DNS
   - **Puerto Externo**: Puerto configurado en el router
   - **Usuario/Contraseña**: Si la cámara requiere autenticación
   - **Usar SSL**: Solo si la cámara soporta HTTPS

### Paso 3: Prueba de Conectividad

1. **Usar el botón "Probar Conectividad"** en el formulario de bahías
2. **Verificar el resultado**:
   - ✅ Verde: Conexión exitosa
   - ❌ Rojo: Error de conexión
3. **Revisar la URL generada** para verificar que sea correcta

## Limitaciones de PythonAnywhere

### Cuentas Gratuitas
- **Solo HTTP/HTTPS**: No se permiten conexiones RTSP
- **Puertos limitados**: Solo puertos estándar (80, 443, 8080, etc.)
- **Sin conexiones salientes**: Limitadas a ciertos servicios

### Cuentas de Pago
- **Más flexibilidad**: Acceso a más puertos
- **Mejor rendimiento**: Menos restricciones de ancho de banda

## Solución de Problemas

### Error: "No se pudo conectar a la cámara"
1. **Verificar que la cámara esté encendida**
2. **Comprobar la configuración de red**
3. **Revisar el reenvío de puertos** en el router
4. **Verificar firewall** del dispositivo y router

### Error: "Tiempo de espera agotado"
1. **Verificar la velocidad de internet**
2. **Comprobar la estabilidad de la conexión**
3. **Revisar la configuración del puerto**

### Error: "La cámara respondió con código XXX"
- **Código 401**: Credenciales incorrectas
- **Código 404**: URL incorrecta
- **Código 403**: Acceso denegado

## Configuraciones Recomendadas por Tipo

### Para Desarrollo Local
```
Tiene cámara: ✓
Tipo: IP Webcam
IP Cámara: 192.168.1.100:8080
Configuración de producción: ✗
```

### Para Producción en PythonAnywhere
```
Tiene cámara: ✓
Tipo: IP Webcam
IP Cámara: 192.168.1.100:8080
Configuración de producción: ✓
IP Pública: 203.0.113.1
Puerto Externo: 8080
Usuario: admin (si es necesario)
Contraseña: password (si es necesario)
Usar SSL: ✗ (a menos que la cámara lo soporte)
```

## Seguridad

### Recomendaciones
1. **Cambiar credenciales por defecto** de la cámara
2. **Usar contraseñas fuertes**
3. **Configurar SSL** cuando sea posible
4. **Limitar acceso por IP** en el router
5. **Actualizar firmware** de la cámara regularmente

### Consideraciones de Red
- **No exponer puertos innecesarios**
- **Usar VPN** cuando sea posible
- **Monitorear accesos** regularmente

## Ejemplos de URLs Generadas

### IP Webcam Local
```
http://192.168.1.100:8080/video
```

### IP Webcam Producción
```
http://203.0.113.1:8080/video
```

### RTSP con Autenticación
```
rtsp://admin:password@203.0.113.1:554/stream
```

### HTTPS con SSL
```
https://admin:password@203.0.113.1:8443/video
```

## Soporte

Para problemas específicos:
1. **Revisar logs** del sistema
2. **Verificar configuración** paso a paso
3. **Probar conectividad** desde diferentes ubicaciones
4. **Contactar soporte técnico** si persisten los problemas

---

**Nota**: Esta documentación asume conocimientos básicos de redes y configuración de routers. Para configuraciones más complejas, consulte con un técnico en redes.