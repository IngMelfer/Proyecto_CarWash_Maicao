# ✅ CHECKLIST FINAL DE DESPLIEGUE PYTHONANYWHERE

## 🎯 **ESTADO ACTUAL**
✅ Todos los archivos están preparados y listos  
✅ Migraciones completadas  
✅ Requirements.txt actualizado  
⚠️ **PENDIENTE:** Configurar variables de entorno en PythonAnywhere  

---

## 📋 **PASOS FINALES PARA COMPLETAR EL DESPLIEGUE**

### **PASO 1: Subir código a GitHub** 
```bash
git add .
git commit -m "Preparación completa para PythonAnywhere - todos los archivos listos"
git push origin main
```

### **PASO 2: En PythonAnywhere Console**
```bash
# Navegar al directorio del proyecto
cd ~/Proyecto_CarWash_Maicao

# Obtener la última versión desde GitHub
git fetch origin
git checkout -B main origin/main
git reset --hard origin/main
git clean -fd

# Activar entorno virtual
workon carwash_env

# Instalar dependencias actualizadas
pip install -r requirements.txt
```

### **PASO 3: Configurar variables de entorno**
```bash
# Copiar el archivo de configuración
cp .env.pythonanywhere .env

# Editar con tus valores reales
nano .env
```

**VALORES QUE DEBES CAMBIAR EN EL ARCHIVO .env:**
```env
SECRET_KEY=tu-clave-secreta-super-segura-aqui-cambiar-obligatorio
ALLOWED_HOSTS=tu_usuario.pythonanywhere.com,localhost,127.0.0.1
PYTHONANYWHERE_USERNAME=tu_usuario
PYTHONANYWHERE_DOMAIN=tu_usuario.pythonanywhere.com
PROJECT_PATH=/home/tu_usuario/Proyecto_CarWash_Maicao
DB_NAME=tu_usuario$autolavados
DB_USER=tu_usuario
DB_PASSWORD=tu-password-mysql-aqui
```

### **PASO 4: Configurar base de datos MySQL**
```bash
# Ejecutar migraciones
python manage.py migrate --noinput

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### **PASO 5: Configurar archivos estáticos**
```bash
# Ejecutar script de configuración automática
python configurar_estaticos_pythonanywhere.py

# O manualmente:
python manage.py collectstatic --noinput
```

### **PASO 6: Configurar Web App en PythonAnywhere**

#### **6.1 Configuración WSGI:**
- Ve a la pestaña **"Web"** en tu dashboard
- En **"Code"** → **"WSGI configuration file"**
- Reemplaza el contenido con:
```python
# Copiar contenido del archivo wsgi_pythonanywhere.py
```

#### **6.2 Configurar archivos estáticos:**
En la sección **"Static files"** agrega:
- **URL:** `/static/` → **Directory:** `/home/tu_usuario/Proyecto_CarWash_Maicao/staticfiles`
- **URL:** `/media/` → **Directory:** `/home/tu_usuario/Proyecto_CarWash_Maicao/media`

#### **6.3 Configurar variables de entorno:**
En la sección **"Environment variables"** agrega:
- `DJANGO_SETTINGS_MODULE` = `autolavados_plataforma.settings`

### **PASO 7: Verificación final**
```bash
# Ejecutar script de verificación
python verificacion_post_despliegue.py

# Si todo está bien, deberías ver:
# ✅ ESTADO: DESPLIEGUE EXITOSO
```

### **PASO 8: Recargar aplicación**
- En el panel Web de PythonAnywhere, haz clic en **"Reload tu_usuario.pythonanywhere.com"**

---

## 🔍 **VERIFICACIÓN MANUAL**

### **URLs a probar:**
- `https://tu_usuario.pythonanywhere.com/` - Página principal
- `https://tu_usuario.pythonanywhere.com/admin/` - Panel de administración
- `https://tu_usuario.pythonanywhere.com/api/` - API REST

### **Funcionalidades a verificar:**
- ✅ Login de usuarios
- ✅ Creación de reservas
- ✅ Panel de administración
- ✅ Carga de archivos estáticos (CSS/JS)
- ✅ Subida de imágenes

---

## 🚨 **SOLUCIÓN DE PROBLEMAS COMUNES**

### **Error: "DisallowedHost"**
- Verifica que `ALLOWED_HOSTS` en `.env` incluya tu dominio de PythonAnywhere

### **Error: "Database connection failed"**
- Verifica las credenciales de MySQL en `.env`
- Asegúrate de que la base de datos existe en PythonAnywhere

### **CSS/JS no cargan**
- Ejecuta `python manage.py collectstatic --noinput`
- Verifica la configuración de archivos estáticos en el panel Web

### **Error 500**
- Revisa los logs en: `/var/log/tu_usuario.pythonanywhere.com.error.log`
- Verifica que `DEBUG=False` en `.env`

---

## 📞 **SOPORTE**

### **Archivos de log importantes:**
- Error log: `/var/log/tu_usuario.pythonanywhere.com.error.log`
- Server log: `/var/log/tu_usuario.pythonanywhere.com.server.log`

### **Comandos útiles para debugging:**
```bash
# Ver logs en tiempo real
tail -f /var/log/tu_usuario.pythonanywhere.com.error.log

# Verificar configuración Django
python manage.py check

# Verificar migraciones pendientes
python manage.py showmigrations
```

---

## 🎉 **¡DESPLIEGUE COMPLETADO!**

Una vez completados todos los pasos, tu aplicación estará disponible en:
**https://tu_usuario.pythonanywhere.com**

### **Para futuras actualizaciones:**
1. Haz push a GitHub
2. En PythonAnywhere: `git pull origin main`
3. `pip install -r requirements.txt`
4. `python manage.py migrate --noinput`
5. `python manage.py collectstatic --noinput`
6. Recarga la aplicación web

---

**📝 Nota:** Guarda este checklist para futuras referencias y actualizaciones.