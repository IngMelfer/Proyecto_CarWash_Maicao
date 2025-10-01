#!/usr/bin/env python3
"""
Script rápido para limpiar configuración HSTS del navegador
Soluciona el error: net::ERR_SSL_PROTOCOL_ERROR
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def clear_chrome_hsts():
    """Limpia la configuración HSTS de Chrome"""
    print("🔧 Limpiando configuración HSTS de Chrome...")
    
    # Rutas comunes de Chrome en Windows
    chrome_paths = [
        os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\TransportSecurity"),
        os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1\\TransportSecurity"),
    ]
    
    removed = False
    for path in chrome_paths:
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"✅ Eliminado: {path}")
                removed = True
            except Exception as e:
                print(f"⚠️  No se pudo eliminar {path}: {e}")
    
    if not removed:
        print("ℹ️  No se encontraron archivos HSTS para eliminar")
    
    return removed

def clear_edge_hsts():
    """Limpia la configuración HSTS de Edge"""
    print("🔧 Limpiando configuración HSTS de Edge...")
    
    edge_paths = [
        os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\TransportSecurity"),
    ]
    
    removed = False
    for path in edge_paths:
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"✅ Eliminado: {path}")
                removed = True
            except Exception as e:
                print(f"⚠️  No se pudo eliminar {path}: {e}")
    
    if not removed:
        print("ℹ️  No se encontraron archivos HSTS de Edge para eliminar")
    
    return removed

def check_django_server():
    """Verifica si el servidor Django está ejecutándose"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        return True
    except:
        return False

def main():
    print("🚀 Script de limpieza rápida HSTS")
    print("=" * 50)
    
    # Limpiar HSTS
    chrome_cleared = clear_chrome_hsts()
    edge_cleared = clear_edge_hsts()
    
    print("\n📋 INSTRUCCIONES RÁPIDAS:")
    print("1. Cierra TODOS los navegadores")
    print("2. Abre el navegador en modo incógnito")
    print("3. Usa esta URL: http://127.0.0.1:8000/notificaciones/api/contador/")
    print("   ⚠️  IMPORTANTE: Usa HTTP, NO HTTPS")
    
    # Verificar servidor Django
    print("\n🔍 Verificando servidor Django...")
    if check_django_server():
        print("✅ Servidor Django ejecutándose correctamente en HTTP")
    else:
        print("❌ Servidor Django no responde. Asegúrate de que esté ejecutándose.")
    
    print("\n🎯 SOLUCIÓN RÁPIDA:")
    print("• URL correcta: http://127.0.0.1:8000/notificaciones/api/contador/")
    print("• Si persiste el error, usa modo incógnito")
    print("• Borra caché del navegador (Ctrl+Shift+Del)")
    
    if chrome_cleared or edge_cleared:
        print("\n✅ Configuración HSTS limpiada. Reinicia el navegador.")
    else:
        print("\n💡 Usa modo incógnito para evitar problemas de caché.")

if __name__ == "__main__":
    main()