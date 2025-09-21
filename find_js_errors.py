import os
import re

def find_js_syntax_errors(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar bloques de script
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL)
    
    errors = []
    for i, script in enumerate(scripts):
        if 'src=' not in script and script.strip():
            lines = script.split('\n')
            for line_num, line in enumerate(lines, 1):
                # Buscar comas seguidas de } o ]
                if re.search(r',\s*[\]\}]', line):
                    errors.append({
                        'file': file_path,
                        'script_block': i + 1,
                        'line': line_num,
                        'content': line.strip()
                    })
    
    return errors

# Buscar en archivos específicos que pueden estar causando el error
target_files = [
    'templates/empleados/dashboard.html',
    'templates/empleados/dashboard/dashboard.html',
    'templates/empleados/dashboard/base_dashboard.html'
]

all_errors = []
for file_path in target_files:
    if os.path.exists(file_path):
        errors = find_js_syntax_errors(file_path)
        all_errors.extend(errors)

if all_errors:
    print('ERRORES DE SINTAXIS ENCONTRADOS:')
    for error in all_errors:
        print(f'Archivo: {error["file"]}')
        print(f'Bloque de script: {error["script_block"]}')
        print(f'Línea: {error["line"]}')
        print(f'Contenido: {error["content"]}')
        print('-' * 50)
else:
    print('No se encontraron errores de sintaxis en los archivos del dashboard.')