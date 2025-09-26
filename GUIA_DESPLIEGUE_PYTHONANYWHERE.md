# 🚀 Guía de Despliegue en PythonAnywhere

## Flujo GitHub → PythonAnywhere

Esta guía está optimizada para tu flujo de trabajo específico: **GitHub → PythonAnywhere**.

---

## 📋 Prerrequisitos

### En PythonAnywhere:
- [ ] Cuenta activa en PythonAnywhere
- [ ] Entorno virtual creado: `carwash_env`
- [ ] Acceso a consola Bash
- [ ] Base de datos MySQL configurada

### En GitHub:
- [ ] Repositorio con el código actualizado
- [ ] Archivos de configuración incluidos

---

## 🔧 Configuración Inicial (Solo la primera vez)

### 1. Crear Entorno Virtual
```bash
# En la consola de PythonAnywhere
mkvirtualenv --python=/usr/bin/python3.10 carwash_env
```

### 2. Clonar Repositorio
```bash
cd ~
git clone https://github.com/tu-usuario/Proyecto_CarWash_Maicao.git
cd Proyecto_CarWash_Maicao
```

### 3. Configurar Variables de Entorno
```bash
# Copiar archivo de configuración
cp .env.pythonanywhere .env

# Editar con tus valores reales
nano .env
```

**Valores importantes a configurar en `.env`:**
```bash
SECRET_KEY=tu_clave_secreta_unica_y_segura
DEBUG=False
ALLOWED_HOSTS=tu_usuario.pythonanywhere.com,localhost,127.0.0.1
PYTHONANYWHERE_USERNAME=tu_usuario
DB_NAME=tu_usuario$autolavados
DB_USER=tu_usuario
DB_PASSWORD=tu_password_mysql
DB_HOST=tu_usuario.mysql.pythonanywhere-services.com
```

### 4. Configurar Base de Datos MySQL
```bash
# Activar entorno virtual
workon carwash_env

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate --noinput

# Crear superusuario
python manage.py createsuperuser
```

### 5. Configurar Aplicación Web
1. Ve al panel de PythonAnywhere → **Web**
2. Crea nueva aplicación web
3. Selecciona **Manual configuration** → **Python 3.10**
4. Configura el archivo WSGI usando `wsgi_pythonanywhere.py`

### 6. Configurar Archivos Estáticos
```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

En el panel Web de PythonAnywhere:
- **Static files URL**: `/static/`
- **Static files directory**: `/home/tu_usuario/Proyecto_CarWash_Maicao/staticfiles/`

---

## 🔄 Proceso de Despliegue (Tu flujo actual)

### Comandos que ejecutas:
```bash
cd ~/Proyecto_CarWash_Maicao 
git fetch origin 
git checkout -B main origin/main 
git reset --hard origin/main 
git clean -fd 
workon carwash_env 
pip install -r requirements.txt   # si cambió 
python manage.py migrate --noinput 
python manage.py collectstatic --noinput
```

### Script automatizado (opcional):
```bash
# Usar el script incluido en el proyecto
bash deploy_pythonanywhere.sh
```

### Después del despliegue:
1. **Recargar aplicación web** en el panel de PythonAnywhere
2. **Verificar logs** si hay errores
3. **Probar funcionalidad** en tu dominio

---

## 📁 Estructura de Archivos en PythonAnywhere

```
/home/tu_usuario/
├── Proyecto_CarWash_Maicao/          # Tu proyecto
│   ├── .env                          # Variables de entorno (NO en GitHub)
│   ├── .env.pythonanywhere          # Plantilla de configuración
│   ├── wsgi_pythonanywhere.py       # Configuración WSGI
│   ├── settings_production.py       # Settings de producción
│   ├── deploy_pythonanywhere.sh     # Script de despliegue
│   ├── requirements.txt             # Dependencias
│   ├── manage.py
│   ├── autolavados_plataforma/
│   ├── autenticacion/
│   ├── reservas/
│   ├── empleados/
│   ├── clientes/
│   ├── notificaciones/
│   ├── static/
│   ├── templates/
│   └── staticfiles/                 # Archivos estáticos recolectados
└── .virtualenvs/
    └── carwash_env/                 # Entorno virtual
```

---

## 🔍 Verificación Post-Despliegue

### 1. Verificar Aplicación Web
- [ ] Aplicación carga sin errores
- [ ] CSS y JavaScript funcionan
- [ ] Formularios responden correctamente

### 2. Verificar Base de Datos
```bash
# Probar conexión
python manage.py check --database default

# Verificar migraciones
python manage.py showmigrations
```

### 3. Verificar Logs
```bash
# Ver logs de error
tail -f /var/log/tu_usuario.pythonanywhere.com.error.log

# Ver logs de acceso
tail -f /var/log/tu_usuario.pythonanywhere.com.access.log
```

---

## 🚨 Solución de Problemas Comunes

### Error: "DisallowedHost"
**Solución:** Verificar `ALLOWED_HOSTS` en `.env`
```bash
ALLOWED_HOSTS=tu_usuario.pythonanywhere.com,localhost,127.0.0.1
```

### Error: "No module named 'django'"
**Solución:** Activar entorno virtual
```bash
workon carwash_env
```

### Error: Base de datos
**Solución:** Verificar configuración MySQL en `.env`
```bash
DB_HOST=tu_usuario.mysql.pythonanywhere-services.com
DB_NAME=tu_usuario$autolavados
```

### Archivos estáticos no cargan
**Solución:** 
1. Ejecutar `python manage.py collectstatic --noinput`
2. Verificar configuración en panel Web
3. Recargar aplicación

### Error 500
**Solución:**
1. Revisar logs de error
2. Verificar archivo `.env`
3. Comprobar permisos de archivos

---

## 📝 Checklist de Despliegue

### Antes de cada despliegue:
- [ ] Código probado localmente
- [ ] Cambios commitados y pusheados a GitHub
- [ ] Variables de entorno actualizadas si es necesario

### Durante el despliegue:
- [ ] Ejecutar comandos de actualización
- [ ] Verificar que no hay errores en la consola
- [ ] Recargar aplicación web

### Después del despliegue:
- [ ] Probar funcionalidades principales
- [ ] Verificar que no hay errores 500
- [ ] Comprobar logs si hay warnings

---

## 🔐 Seguridad

### Variables Sensibles:
- **NUNCA** subas el archivo `.env` a GitHub
- Usa claves secretas únicas y seguras
- Mantén `DEBUG=False` en producción
- Configura `ALLOWED_HOSTS` correctamente

### Backup:
- Realiza backups regulares de la base de datos
- Mantén copias de seguridad del archivo `.env`
- Documenta cambios importantes

---

## 📞 Soporte

### Recursos Útiles:
- [Documentación PythonAnywhere](https://help.pythonanywhere.com/)
- [Documentación Django](https://docs.djangoproject.com/)
- Logs de la aplicación en PythonAnywhere

### Comandos de Diagnóstico:
```bash
# Verificar configuración Django
python manage.py check

# Ver configuración actual
python manage.py diffsettings

# Probar conexión DB
python manage.py dbshell
```

---

## 🎉 ¡Listo!

Tu aplicación CarWash está ahora desplegada en PythonAnywhere siguiendo tu flujo de trabajo preferido: **GitHub → PythonAnywhere**.

**URL de tu aplicación:** `https://tu_usuario.pythonanywhere.com`

---

*Guía optimizada para el flujo GitHub → PythonAnywhere*