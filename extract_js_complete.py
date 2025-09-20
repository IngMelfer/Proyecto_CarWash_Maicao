#!/usr/bin/env python3
import re
import os

def extract_and_validate_js(html_file):
    """Extrae todo el JavaScript del HTML y lo valida línea por línea"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer todo el JavaScript entre <script> tags
    js_blocks = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    
    all_js = ""
    for i, block in enumerate(js_blocks):
        all_js += f"\n// === BLOQUE {i+1} ===\n"
        all_js += block
        all_js += f"\n// === FIN BLOQUE {i+1} ===\n"
    
    # Guardar JavaScript extraído
    with open('extracted_complete.js', 'w', encoding='utf-8') as f:
        f.write(all_js)
    
    print(f"JavaScript extraído y guardado en 'extracted_complete.js'")
    
    # Buscar patrones problemáticos específicos
    lines = all_js.split('\n')
    errors = []
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith('//'):
            continue
            
        # Buscar paréntesis no balanceados en líneas con funciones
        if ('(' in line and ')' in line and 
            ('function' in line or 'addEventListener' in line or '=>' in line)):
            
            # Contar paréntesis considerando strings y template literals
            in_string = False
            in_template = False
            string_char = None
            paren_count = 0
            bracket_count = 0
            
            for j, char in enumerate(line):
                if char == '`' and (j == 0 or line[j-1] != '\\'):
                    in_template = not in_template
                elif not in_template and char in ['"', "'"] and (j == 0 or line[j-1] != '\\'):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                        string_char = None
                elif not in_string and not in_template:
                    if char == '(':
                        paren_count += 1
                    elif char == ')':
                        paren_count -= 1
                    elif char == '{':
                        bracket_count += 1
                    elif char == '}':
                        bracket_count -= 1
            
            if paren_count != 0:
                errors.append(f"Línea {i}: Paréntesis desbalanceados ({paren_count}) - {line_stripped}")
        
        # Buscar template literals problemáticos
        if '${' in line and '`' in line:
            # Contar backticks
            backtick_count = line.count('`')
            if backtick_count % 2 != 0:
                errors.append(f"Línea {i}: Template literal no cerrado - {line_stripped}")
        
        # Buscar operadores ternarios problemáticos
        if '?' in line and ':' in line:
            # Verificar si hay operadores ternarios mal formateados
            ternary_pattern = r'\?\s*[^:]*:'
            if re.search(ternary_pattern, line):
                # Verificar si hay problemas con quotes
                if line.count('"') % 2 != 0 or line.count("'") % 2 != 0:
                    errors.append(f"Línea {i}: Posible problema con operador ternario y quotes - {line_stripped}")
        
        # Buscar funciones con argumentos mal cerrados
        if re.search(r'\w+\([^)]*$', line) and not line.endswith('{'):
            errors.append(f"Línea {i}: Función con argumentos no cerrados - {line_stripped}")
    
    return errors

def find_specific_syntax_error(html_file):
    """Busca el error específico 'missing ) after argument list'"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrones que comúnmente causan este error
    problematic_patterns = [
        r'querySelector\([^)]*"[^"]*"[^)]*\)',  # querySelector con quotes problemáticas
        r'addEventListener\([^)]*,\s*function\([^)]*\)\s*{[^}]*$',  # addEventListener mal cerrado
        r'\$\{[^}]*\?\s*[^:]*:[^}]*\}',  # Operadores ternarios en template literals
        r'`[^`]*\$\{[^}]*`[^`]*`[^}]*\}',  # Template literals anidados
        r'\([^)]*,\s*\)',  # Comas finales en argumentos
    ]
    
    errors = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        for pattern in problematic_patterns:
            if re.search(pattern, line):
                errors.append(f"Línea {i}: Patrón problemático detectado - {line.strip()}")
    
    return errors

if __name__ == "__main__":
    html_file = "templates/reservas/reservar_turno.html"
    
    if os.path.exists(html_file):
        print("=== EXTRAYENDO Y VALIDANDO JAVASCRIPT ===")
        js_errors = extract_and_validate_js(html_file)
        
        print("\n=== BUSCANDO PATRONES PROBLEMÁTICOS ===")
        pattern_errors = find_specific_syntax_error(html_file)
        
        all_errors = js_errors + pattern_errors
        
        if all_errors:
            print(f"\n=== SE ENCONTRARON {len(all_errors)} POSIBLES ERRORES ===")
            for error in all_errors[:20]:  # Mostrar los primeros 20
                print(error)
        else:
            print("\n=== NO SE ENCONTRARON ERRORES OBVIOS ===")
            
        print(f"\nRevisa el archivo 'extracted_complete.js' para análisis manual")
    else:
        print(f"Archivo {html_file} no encontrado")