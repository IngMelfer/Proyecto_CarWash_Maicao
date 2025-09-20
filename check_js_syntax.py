#!/usr/bin/env python3
import re
import sys

def extract_and_check_js_syntax(html_file):
    """
    Extrae JavaScript del HTML y busca errores de sintaxis específicos
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar bloques de script
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL)
    
    all_js = ""
    for script in scripts:
        all_js += script + "\n"
    
    # Buscar patrones problemáticos específicos
    problems = []
    
    # 1. Buscar paréntesis desbalanceados en addEventListener
    lines = all_js.split('\n')
    for i, line in enumerate(lines, 1):
        if 'addEventListener' in line:
            # Contar paréntesis en la línea
            open_parens = line.count('(')
            close_parens = line.count(')')
            if open_parens != close_parens:
                problems.append(f"Línea {i}: Paréntesis desbalanceados en addEventListener: {line.strip()}")
    
    # 2. Buscar template literals mal cerrados
    template_literal_pattern = r'`[^`]*$'
    for i, line in enumerate(lines, 1):
        if re.search(template_literal_pattern, line):
            problems.append(f"Línea {i}: Template literal posiblemente mal cerrado: {line.strip()}")
    
    # 3. Buscar funciones mal cerradas
    function_pattern = r'function\s*\([^)]*\)\s*\{'
    brace_count = 0
    in_function = False
    
    for i, line in enumerate(lines, 1):
        if re.search(function_pattern, line):
            in_function = True
            brace_count = 0
        
        if in_function:
            brace_count += line.count('{') - line.count('}')
            if brace_count < 0:
                problems.append(f"Línea {i}: Llaves desbalanceadas: {line.strip()}")
    
    # 4. Buscar código Django template mezclado
    django_pattern = r'\{%.*?%\}'
    for i, line in enumerate(lines, 1):
        if re.search(django_pattern, line):
            problems.append(f"Línea {i}: Código Django template en JavaScript: {line.strip()}")
    
    # 5. Buscar variables Django sin procesar
    django_var_pattern = r'\{\{.*?\}\}'
    for i, line in enumerate(lines, 1):
        if re.search(django_var_pattern, line):
            problems.append(f"Línea {i}: Variable Django en JavaScript: {line.strip()}")
    
    return problems, all_js

if __name__ == "__main__":
    html_file = "templates/reservas/reservar_turno.html"
    
    problems, js_content = extract_and_check_js_syntax(html_file)
    
    if problems:
        print("PROBLEMAS ENCONTRADOS:")
        for problem in problems:
            print(f"  - {problem}")
    else:
        print("No se encontraron problemas de sintaxis obvios.")
    
    # Guardar el JavaScript extraído para revisión manual
    with open('js_extracted_clean.js', 'w', encoding='utf-8') as f:
        # Remover código Django template para crear JS válido
        clean_js = re.sub(r'\{%.*?%\}', '// Django template code removed', js_content, flags=re.DOTALL)
        clean_js = re.sub(r'\{\{.*?\}\}', '0', clean_js)  # Reemplazar variables con valores dummy
        f.write(clean_js)
    
    print(f"\nJavaScript limpio guardado en 'js_extracted_clean.js'")