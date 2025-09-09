#!/bin/bash

# Script para actualizar la aplicación en PythonAnywhere
# Este script debe ejecutarse en la consola de PythonAnywhere

# 1. Navegar al directorio del proyecto
cd ~/Proyecto_CarWash_Maicao

# 2. Actualizar el código desde GitHub
git pull origin main

# 3. Activar el entorno virtual
workon autolavados-env

# 4. Instalar o actualizar dependencias
pip install -r requirements.txt

# 5. Realizar migraciones
python manage.py migrate

# 6. Recolectar archivos estáticos
python manage.py collectstatic --noinput

# 7. Recargar la aplicación web
touch /var/www/IngMelfer_pythonanywhere_com_wsgi.py

echo "Actualización completada. La aplicación debería estar funcionando con los cambios más recientes."