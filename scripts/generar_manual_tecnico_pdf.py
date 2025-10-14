# -*- coding: utf-8 -*-
"""
Genera un Manual Técnico en PDF para el sistema Autolavados.
Incluye: resumen del sistema, arquitectura, apps, endpoints clave,
configuración de producción (PythonAnywhere) basada en variables .env,
seguridad, despliegue y referencias a diagramas SVG.
"""
import os
import sys
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
)

# Para incrustar SVG
try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF
    SVGLIB_AVAILABLE = True
except Exception:
    SVGLIB_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
DIAGRAMS_DIR = os.path.join(DOCS_DIR, 'diagrams')
OUTPUT_PDF = os.path.join(DOCS_DIR, 'Manual_Tecnico_Autolavados.pdf')

ENV_PATHS = [
    os.path.join(BASE_DIR, '.env'),
    os.path.join(BASE_DIR, '.env.pythonanywhere'),
]


def load_env_vars(paths):
    env = {}
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if '=' in line:
                            k, v = line.split('=', 1)
                            env[k.strip()] = v.strip()
            except Exception:
                continue
    return env

ENV = load_env_vars(ENV_PATHS)

# Estilos
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCenter', parent=styles['Title'], alignment=1))
styles.add(ParagraphStyle(name='H2', parent=styles['Heading2'], spaceBefore=12, spaceAfter=6))
styles.add(ParagraphStyle(name='H3', parent=styles['Heading3'], spaceBefore=8, spaceAfter=4))
styles.add(ParagraphStyle(name='Body', parent=styles['BodyText'], leading=14))
styles.add(ParagraphStyle(name='Mono', parent=styles['BodyText'], fontName='Courier', leading=14))


class SvgFlowable(Flowable):
    def __init__(self, svg_path, width=None, height=None):
        super().__init__()
        self.svg_path = svg_path
        self.width = width
        self.height = height
        self.drawing = None
        if SVGLIB_AVAILABLE and os.path.exists(svg_path):
            try:
                self.drawing = svg2rlg(svg_path)
                if width and height:
                    # Escala proporcional a las dimensiones dadas
                    sx = width / float(self.drawing.width)
                    sy = height / float(self.drawing.height)
                    self.drawing.scale(sx, sy)
                    self.width = width
                    self.height = height
                else:
                    self.width = self.drawing.width
                    self.height = self.drawing.height
            except Exception:
                self.drawing = None
                self.width = width or 500
                self.height = height or 300
        else:
            self.width = width or 500
            self.height = height or 300

    def wrap(self, availWidth, availHeight):
        return min(self.width, availWidth), self.height

    def draw(self):
        if SVGLIB_AVAILABLE and self.drawing is not None:
            renderPDF.draw(self.drawing, self.canv, 0, 0)
        else:
            # Mensaje cuando no se puede dibujar SVG
            self.canv.setStrokeColor(colors.red)
            self.canv.setFillColor(colors.red)
            self.canv.rect(0, 0, self.width, self.height, stroke=1, fill=0)
            self.canv.setFillColor(colors.black)
            self.canv.drawString(10, self.height/2, 'SVG no disponible (instalar svglib)')



def make_section_title(text):
    return Paragraph(text, styles['H2'])


def make_subtitle(text):
    return Paragraph(text, styles['H3'])


def bullet(text):
    return Paragraph(f"• {text}", styles['Body'])



def build_pdf():
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(DIAGRAMS_DIR, exist_ok=True)

    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
        title='Manual Técnico - Autolavados',
        author='Sistema Autolavados'
    )

    elems = []

    # Portada
    elems.append(Paragraph('Manual Técnico - Plataforma Autolavados', styles['TitleCenter']))
    elems.append(Spacer(1, 12))
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    elems.append(Paragraph(f'Generado: {now}', styles['Body']))
    domain = ENV.get('PYTHONANYWHERE_DOMAIN', 'dominio-pythonanywhere')
    elems.append(Paragraph(f'Dominio producción: https://{domain}', styles['Body']))
    elems.append(Spacer(1, 24))

    # Resumen del sistema
    elems.append(make_section_title('1. Resumen del sistema'))
    elems.append(Paragraph(
        'Plataforma Django para gestión de autolavados: autenticación de usuarios, reservas, notificaciones, dashboards y administración.',
        styles['Body']
    ))
    elems.append(Spacer(1, 12))

    # Arquitectura (SVG)
    elems.append(make_section_title('2. Arquitectura (Producción - PythonAnywhere)'))
    arquitectura_svg = os.path.join(DIAGRAMS_DIR, 'arquitectura.svg')
    elems.append(SvgFlowable(arquitectura_svg, width=500, height=330))
    elems.append(Spacer(1, 12))

    # Aplicaciones
    elems.append(make_section_title('3. Aplicaciones y módulos'))
    apps_table = Table([
        ['App', 'Descripción'],
        ['autenticacion', 'Registro, login, logout, perfil y endpoints de autenticación'],
        ['clientes', 'Gestión de clientes y perfiles'],
        ['reservas', 'Creación, consulta y pago de reservas'],
        ['notificaciones', 'Envío de correos/SMS/push'],
        ['empleados', 'Gestión de personal y tareas'],
        ['dashboard_gerente', 'Panel de administración y métricas'],
        ['dashboard_publico', 'Páginas públicas y marketing'],
    ], colWidths=[140, 360])
    apps_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elems.append(apps_table)
    elems.append(Spacer(1, 12))

    # Endpoints clave
    elems.append(make_section_title('4. Endpoints clave'))
    elems.append(make_subtitle('4.1 Autenticación'))
    elems.append(bullet('POST /api/auth/api/registro/ - Registrar usuario'))
    elems.append(bullet('POST /api/auth/api/login/ - Iniciar sesión y obtener sesión/token'))
    elems.append(bullet('POST /api/auth/api/logout/ - Cerrar sesión'))
    elems.append(bullet('GET /api/auth/api/perfil/ - Ver perfil autenticado'))

    elems.append(make_subtitle('4.2 Reservas'))
    elems.append(bullet('GET /reservas/api/horarios-disponibles/ - Consultar slots disponibles'))
    elems.append(bullet('POST /reservas/api/verificar-placa/ - Verificar placa única del vehículo'))
    elems.append(bullet('POST /reservas/api/crear/ - Crear reserva y voucher'))
    elems.append(bullet('GET /reservas/api/resumen/ - Obtener resumen/estado de reserva'))

    elems.append(make_subtitle('4.3 Notificaciones'))
    elems.append(bullet('POST /notificaciones/api/enviar/ - Enviar notificación a cliente'))
    elems.append(Spacer(1, 12))

    # Configuración producción
    elems.append(make_section_title('5. Configuración de Producción (settings_production.py)'))
    allowed_hosts = ENV.get('ALLOWED_HOSTS', 'autolavados.pythonanywhere.com')
    elems.append(bullet(f'ALLOWED_HOSTS: {allowed_hosts}'))
    elems.append(bullet('DEBUG: false'))
    elems.append(bullet('WhiteNoise para archivos estáticos (collectstatic)'))
    elems.append(bullet('SECRET_KEY y credenciales desde variables de entorno'))
    elems.append(bullet('Base de datos MySQL configurada vía .env'))
    elems.append(Spacer(1, 12))

    # Seguridad
    elems.append(make_section_title('6. Seguridad'))
    elems.append(bullet('CSRF y CORS ajustados al dominio de producción'))
    elems.append(bullet('Gestión de permisos y grupos'))
    elems.append(bullet('Logs y auditoría de eventos críticos'))
    elems.append(Spacer(1, 12))

    # Despliegue
    elems.append(make_section_title('7. Despliegue en PythonAnywhere'))
    elems.append(bullet('Instalar dependencias: pip install -r requirements.txt'))
    elems.append(bullet('Configurar variables en .env.pythonanywhere'))
    elems.append(bullet('Aplicar migraciones: python manage.py migrate --settings=settings_production'))
    elems.append(bullet('Recolectar estáticos: python manage.py collectstatic --noinput --settings=settings_production'))
    elems.append(bullet('Recargar la WebApp desde el panel de PythonAnywhere'))
    elems.append(Spacer(1, 12))

    # Flujo de reservas (SVG)
    elems.append(make_section_title('8. Flujo de Reservas'))
    flujo_svg = os.path.join(DIAGRAMS_DIR, 'flujo_reservas.svg')
    elems.append(SvgFlowable(flujo_svg, width=500, height=330))

    # Final
    elems.append(PageBreak())
    elems.append(make_section_title('9. Mantenimiento y Operación'))
    elems.append(bullet('Backups periódicos de BD y estáticos'))
    elems.append(bullet('Monitoreo de cuotas y logs en PythonAnywhere'))
    elems.append(bullet('Revisión de endpoints y estados de pago'))

    doc.build(elems)
    return OUTPUT_PDF


if __name__ == '__main__':
    pdf_path = build_pdf()
    print(f'Manual técnico PDF generado en: {pdf_path}')