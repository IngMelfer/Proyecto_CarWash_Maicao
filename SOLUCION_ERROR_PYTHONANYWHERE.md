# 🔧 SOLUCIÓN ERROR PYTHONANYWHERE - KeyError: '__version__'

## 🚨 Problema Identificado
El error `KeyError: '__version__'` indica un problema con la instalación de dependencias en PythonAnywhere, específicamente con paquetes que tienen problemas de compatibilidad con Python 3.13.

## ✅ SOLUCIÓN INMEDIATA

### Paso 1: Usar Requirements Mínimo
En lugar de `requirements.txt`, usa el archivo `requirements_minimal.txt`:

```bash
# En PythonAnywhere Console
cd ~/carwash_maicao
pip install -r requirements_minimal.txt
```

### Paso 2: Si aún hay errores, instalar uno por uno
```bash
# Instalar Django primero
pip install Django==4.2.16

# Instalar base de datos
pip install mysqlclient==2.2.4

# Instalar el resto
pip install python-dotenv==1.0.1
pip install django-cors-headers==4.3.1
pip install qrcode==7.4.2
pip install Pillow==10.4.0
pip install gunicorn==21.2.0
pip install whitenoise==6.6.0
pip install requests==2.31.0
pip install pytz==2024.1
pip install packaging==24.1
```

### Paso 3: Verificar instalación
```bash
python -c "import django; print(django.get_version())"
python -c "import MySQLdb; print('MySQL OK')"
```

## 🔍 CAUSAS DEL ERROR

1. **Versiones incompatibles**: Algunos paquetes no están optimizados para Python 3.13
2. **Dependencias conflictivas**: Paquetes que requieren versiones específicas de setuptools
3. **Problemas de build**: Errores en la compilación de wheels

## 📋 COMANDOS ALTERNATIVOS

### Opción A: Actualizar pip y setuptools
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements_minimal.txt
```

### Opción B: Instalar sin cache
```bash
pip install --no-cache-dir -r requirements_minimal.txt
```

### Opción C: Usar versiones específicas de setuptools
```bash
pip install setuptools==68.0.0
pip install -r requirements_minimal.txt
```

## 🎯 RECOMENDACIÓN FINAL

1. **Usa `requirements_minimal.txt`** - Contiene solo las dependencias esenciales
2. **Instala paso a paso** - Si hay errores, instala paquete por paquete
3. **Verifica cada instalación** - Confirma que cada paquete se instala correctamente

## 📞 SIGUIENTE PASO
Una vez instaladas las dependencias mínimas, continúa con:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## 🔄 ACTUALIZACIÓN FUTURA
Después de que el proyecto funcione, puedes agregar dependencias adicionales una por una:
```bash
pip install djangorestframework==3.14.0
pip install colorama==0.4.6
# etc...
```