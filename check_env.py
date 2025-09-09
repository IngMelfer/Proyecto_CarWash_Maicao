import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env.local
load_dotenv('.env.local')

# Verificar si USE_MYSQL se está cargando correctamente
use_mysql = os.environ.get('USE_MYSQL', 'No encontrado')
print(f"USE_MYSQL: {use_mysql}")
print(f"USE_MYSQL como booleano: {use_mysql.lower() == 'true'}")

# Verificar otras variables de entorno relacionadas con MySQL
print(f"DB_NAME: {os.environ.get('DB_NAME', 'No encontrado')}")
print(f"DB_USER: {os.environ.get('DB_USER', 'No encontrado')}")
print(f"DB_PASSWORD: {os.environ.get('DB_PASSWORD', 'No encontrado')}")
print(f"DB_HOST: {os.environ.get('DB_HOST', 'No encontrado')}")
print(f"DB_PORT: {os.environ.get('DB_PORT', 'No encontrado')}")