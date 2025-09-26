# 📋 GUÍA DE REQUIREMENTS PARA DESPLIEGUE EN PRODUCCIÓN

## 📁 Archivos de Requirements Disponibles

### 1. `requirements.txt` - **RECOMENDADO PARA PRODUCCIÓN**
- ✅ **Archivo principal optimizado para producción**
- ✅ Incluye todas las dependencias necesarias organizadas por categorías
- ✅ Comentarios explicativos para cada sección
- ✅ Dependencias opcionales comentadas (AWS S3, Sentry)
- ✅ Excluye dependencias de desarrollo y testing

### 2. `requirements_minimal.txt` - **ULTRA BÁSICO**
- ⚡ Solo las dependencias absolutamente esenciales
- 🎯 Ideal para entornos con limitaciones de espacio/memoria
- 📦 Instalación más rápida
- ⚠️ No incluye funcionalidades avanzadas (reportes, análisis)

### 3. `requirements_freeze.txt` - **DESARROLLO**
- 🔧 Snapshot completo del entorno de desarrollo
- ❌ NO usar en producción (incluye dependencias innecesarias)
- 📊 Útil para debugging y comparación

## 🚀 Instrucciones de Despliegue

### Para Producción (RECOMENDADO):
```bash
pip install -r requirements.txt
```

### Para Entorno Mínimo:
```bash
pip install -r requirements_minimal.txt
```

## 📋 Dependencias Principales Incluidas

### 🔧 Framework Base
- **Django 4.2.11** - Framework web principal
- **djangorestframework 3.14.0** - API REST
- **django-cors-headers 4.3.1** - CORS para API

### 🗄️ Base de Datos
- **mysqlclient 2.2.7** - Conector MySQL principal
- **PyMySQL 1.1.0** - Conector MySQL alternativo
- **mysql-connector-python 9.4.0** - Conector oficial MySQL

### 🌐 Servidor Web
- **gunicorn 21.2.0** - Servidor WSGI para producción
- **whitenoise 6.5.0** - Servir archivos estáticos

### 🔐 Seguridad
- **cryptography 45.0.7** - Funciones criptográficas
- **python-dotenv 1.0.0** - Variables de entorno

### 📊 Funcionalidades Avanzadas
- **reportlab 4.4.3** - Generación de PDFs
- **qrcode 8.2** - Códigos QR
- **pandas 2.3.0** - Análisis de datos
- **openpyxl 3.1.5** - Archivos Excel
- **Pillow 11.3.0** - Procesamiento de imágenes

## 🔧 Configuración por Plataforma

### Railway / Heroku
```bash
# Usar requirements.txt directamente
pip install -r requirements.txt
```

### PythonAnywhere
```bash
# Usar requirements_minimal.txt si hay problemas de instalación
pip install -r requirements_minimal.txt
```

### VPS/Servidor Dedicado
```bash
# Usar requirements.txt completo
pip install -r requirements.txt
```

## ⚠️ Dependencias Excluidas de Producción

Las siguientes dependencias están **EXCLUIDAS** del requirements.txt de producción:

- `selenium` - Solo para testing automatizado
- `webdriver-manager` - Solo para testing
- `beautifulsoup4` - Solo para scraping/testing
- `Flask` - Framework alternativo no usado
- `pyinstaller` - Solo para crear ejecutables
- `ngrok/pyngrok` - Solo para desarrollo local

## 🔄 Actualización de Requirements

### Para actualizar requirements.txt:
1. Instalar nueva dependencia: `pip install nueva-dependencia`
2. Agregar manualmente a `requirements.txt` con versión específica
3. Probar instalación: `pip install -r requirements.txt --dry-run`

### Para generar nuevo freeze:
```bash
pip freeze > requirements_freeze.txt
```

## 🧪 Verificación de Instalación

### Probar instalación sin instalar:
```bash
pip install -r requirements.txt --dry-run
```

### Verificar dependencias instaladas:
```bash
pip list
```

### Verificar que Django funciona:
```bash
python manage.py check
```

## 📝 Notas Importantes

1. **Versiones Fijas**: Todas las dependencias tienen versiones específicas para evitar conflictos
2. **Compatibilidad**: Probado con Python 3.11+ y Django 4.2.11
3. **Seguridad**: Versiones actualizadas sin vulnerabilidades conocidas
4. **Optimización**: Excluye dependencias innecesarias para reducir tamaño

## 🆘 Solución de Problemas

### Error de instalación de mysqlclient:
```bash
# En Ubuntu/Debian:
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential

# En CentOS/RHEL:
sudo yum install python3-devel mysql-devel gcc

# En Windows:
# Usar mysqlclient precompilado o PyMySQL como alternativa
```

### Error de memoria en instalación:
```bash
# Usar requirements_minimal.txt
pip install -r requirements_minimal.txt
```

### Verificar compatibilidad:
```bash
# Verificar versión de Python
python --version

# Verificar pip
pip --version

# Actualizar pip si es necesario
pip install --upgrade pip
```

---

## ✅ Checklist de Despliegue

- [ ] Usar `requirements.txt` para producción completa
- [ ] O usar `requirements_minimal.txt` para instalación básica
- [ ] Verificar instalación con `--dry-run`
- [ ] Ejecutar `python manage.py check`
- [ ] Configurar variables de entorno (.env)
- [ ] Ejecutar migraciones: `python manage.py migrate`
- [ ] Recopilar archivos estáticos: `python manage.py collectstatic`
- [ ] Probar servidor: `gunicorn autolavados_plataforma.wsgi:application`