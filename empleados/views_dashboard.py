from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from .models import Empleado, Calificacion, Incentivo
from .forms import EmpleadoPerfilForm
from reservas.models import Reserva
from .forms import EmpleadoPerfilForm


@login_required
def dashboard_lavador(request):
    """
    Vista principal del dashboard para empleados lavadores.
    Muestra estadísticas, resumen de actividad y accesos rápidos.
    """
    try:
        empleado = request.user.empleado
        if not empleado.es_lavador():
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('home')
    except Empleado.DoesNotExist:
        messages.error(request, 'No se encontró información de empleado para tu usuario.')
        return redirect('home')
    
    # Fechas para filtros
    hoy = timezone.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)
    
    # Estadísticas generales
    reservas_hoy = empleado.reservas_asignadas.filter(
        fecha_hora__date=hoy,
        estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
    ).count()
    
    reservas_semana = empleado.reservas_asignadas.filter(
        fecha_hora__date__gte=inicio_semana,
        estado=Reserva.COMPLETADA
    ).count()
    
    reservas_mes = empleado.reservas_asignadas.filter(
        fecha_hora__date__gte=inicio_mes,
        estado=Reserva.COMPLETADA
    ).count()
    
    # Calificación promedio
    promedio_calificacion = empleado.promedio_calificacion()
    total_calificaciones = empleado.calificaciones.count()
    
    # Próximas reservas (hoy y mañana)
    proximas_reservas = empleado.reservas_asignadas.filter(
        fecha_hora__gte=timezone.now(),
        fecha_hora__date__lte=hoy + timedelta(days=1),
        estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
    ).order_by('fecha_hora')[:5]
    
    # Incentivos recientes
    incentivos_recientes = empleado.incentivos.all()[:3]
    total_incentivos_mes = empleado.incentivos.filter(
        fecha_otorgado__gte=inicio_mes
    ).aggregate(total=Sum('monto'))['total'] or Decimal('0')
    
    # Distribución de estados de reservas (últimos 30 días)
    fecha_30_dias = hoy - timedelta(days=30)
    estados_reservas = empleado.reservas_asignadas.filter(
        fecha_hora__date__gte=fecha_30_dias
    ).values('estado').annotate(
        count=Count('id')
    ).order_by('estado')
    
    # Preparar datos para gráficos
    estados_data = {
        'labels': [dict(Reserva.ESTADO_CHOICES).get(item['estado'], item['estado']) for item in estados_reservas],
        'data': [item['count'] for item in estados_reservas]
    }
    
    # Rendimiento semanal (últimas 4 semanas)
    rendimiento_semanal = []
    for i in range(4):
        inicio_semana_i = inicio_semana - timedelta(weeks=i)
        fin_semana_i = inicio_semana_i + timedelta(days=6)
        servicios_semana = empleado.reservas_asignadas.filter(
            fecha_hora__date__gte=inicio_semana_i,
            fecha_hora__date__lte=fin_semana_i,
            estado=Reserva.COMPLETADA
        ).count()
        rendimiento_semanal.append({
            'semana': f"Sem {4-i}",
            'servicios': servicios_semana
        })
    
    context = {
        'empleado': empleado,
        'reservas_hoy': reservas_hoy,
        'reservas_semana': reservas_semana,
        'reservas_mes': reservas_mes,
        'promedio_calificacion': promedio_calificacion,
        'total_calificaciones': total_calificaciones,
        'proximas_reservas': proximas_reservas,
        'incentivos_recientes': incentivos_recientes,
        'total_incentivos_mes': total_incentivos_mes,
        'estados_data': json.dumps(estados_data),
        'rendimiento_semanal': json.dumps(rendimiento_semanal),
    }
    
    return render(request, 'empleados/dashboard_lavador.html', context)


@login_required
def perfil_empleado(request):
    """
    Vista para mostrar y editar el perfil del empleado.
    """
    try:
        empleado = request.user.empleado
        if not empleado.es_lavador():
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('home')
    except Empleado.DoesNotExist:
        messages.error(request, 'No se encontró información de empleado para tu usuario.')
        return redirect('home')
    
    if request.method == 'POST':
        form = EmpleadoPerfilForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil_empleado')
    else:
        form = EmpleadoPerfilForm(instance=empleado)
    
    context = {
        'empleado': empleado,
        'form': form,
    }
    
    return render(request, 'empleados/perfil_empleado.html', context)


@login_required
def servicios_asignados(request):
    """
    Vista para mostrar los servicios asignados al empleado con filtros.
    """
    try:
        empleado = request.user.empleado
        if not empleado.es_lavador():
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('home')
    except Empleado.DoesNotExist:
        messages.error(request, 'No se encontró información de empleado para tu usuario.')
        return redirect('home')
    
    # Filtros
    estado_filtro = request.GET.get('estado', 'todos')
    fecha_filtro = request.GET.get('fecha', 'hoy')
    
    # Base queryset
    reservas = empleado.reservas_asignadas.all()
    
    # Aplicar filtro de estado
    if estado_filtro == 'pendientes':
        reservas = reservas.filter(estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO])
    elif estado_filtro == 'completadas':
        reservas = reservas.filter(estado=Reserva.COMPLETADA)
    elif estado_filtro == 'canceladas':
        reservas = reservas.filter(estado=Reserva.CANCELADA)
    
    # Aplicar filtro de fecha
    hoy = timezone.now().date()
    if fecha_filtro == 'hoy':
        reservas = reservas.filter(fecha_hora__date=hoy)
    elif fecha_filtro == 'semana':
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        reservas = reservas.filter(fecha_hora__date__gte=inicio_semana)
    elif fecha_filtro == 'mes':
        inicio_mes = hoy.replace(day=1)
        reservas = reservas.filter(fecha_hora__date__gte=inicio_mes)
    
    reservas = reservas.order_by('-fecha_hora')
    
    # Estadísticas para la vista
    total_reservas = reservas.count()
    pendientes = reservas.filter(estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]).count()
    completadas = reservas.filter(estado=Reserva.COMPLETADA).count()
    canceladas = reservas.filter(estado=Reserva.CANCELADA).count()
    
    context = {
        'empleado': empleado,
        'reservas': reservas,
        'estado_filtro': estado_filtro,
        'fecha_filtro': fecha_filtro,
        'total_reservas': total_reservas,
        'pendientes': pendientes,
        'completadas': completadas,
        'canceladas': canceladas,
    }
    
    return render(request, 'empleados/servicios_asignados.html', context)


@login_required
def calificaciones_empleado(request):
    """
    Vista para mostrar las calificaciones y reseñas del empleado.
    """
    try:
        empleado = request.user.empleado
        if not empleado.es_lavador():
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('home')
    except Empleado.DoesNotExist:
        messages.error(request, 'No se encontró información de empleado para tu usuario.')
        return redirect('home')
    
    # Obtener calificaciones
    calificaciones = empleado.calificaciones.all().order_by('-fecha_calificacion')
    
    # Estadísticas de calificaciones
    total_calificaciones = calificaciones.count()
    promedio_calificacion = empleado.promedio_calificacion()
    
    # Distribución por puntuación
    distribucion = calificaciones.values('puntuacion').annotate(
        count=Count('id')
    ).order_by('puntuacion')
    
    # Calificaciones por mes (últimos 6 meses)
    hoy = timezone.now().date()
    calificaciones_mensuales = []
    for i in range(6):
        mes = hoy.replace(day=1) - timedelta(days=30*i)
        mes_siguiente = (mes.replace(day=28) + timedelta(days=4)).replace(day=1)
        count = calificaciones.filter(
            fecha_calificacion__date__gte=mes,
            fecha_calificacion__date__lt=mes_siguiente
        ).count()
        promedio = calificaciones.filter(
            fecha_calificacion__date__gte=mes,
            fecha_calificacion__date__lt=mes_siguiente
        ).aggregate(promedio=Avg('puntuacion'))['promedio'] or 0
        
        calificaciones_mensuales.append({
            'mes': mes.strftime('%b %Y'),
            'count': count,
            'promedio': round(float(promedio), 1) if promedio else 0
        })
    
    calificaciones_mensuales.reverse()
    
    context = {
        'empleado': empleado,
        'calificaciones': calificaciones,
        'total_calificaciones': total_calificaciones,
        'promedio_calificacion': promedio_calificacion,
        'distribucion': distribucion,
        'calificaciones_mensuales': json.dumps(calificaciones_mensuales),
    }
    
    return render(request, 'empleados/calificaciones_empleado.html', context)


@login_required
def incentivos_empleado(request):
    """
    Vista para mostrar los incentivos y bonificaciones del empleado.
    """
    try:
        empleado = request.user.empleado
        if not empleado.es_lavador():
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('home')
    except Empleado.DoesNotExist:
        messages.error(request, 'No se encontró información de empleado para tu usuario.')
        return redirect('home')
    
    # Obtener incentivos
    incentivos = empleado.incentivos.all().order_by('-fecha_otorgado')
    
    # Estadísticas
    total_incentivos = incentivos.aggregate(total=Sum('monto'))['total'] or Decimal('0')
    incentivos_este_año = incentivos.filter(
        fecha_otorgado__year=timezone.now().year
    ).aggregate(total=Sum('monto'))['total'] or Decimal('0')
    
    # Incentivos por mes (último año)
    hoy = timezone.now().date()
    incentivos_mensuales = []
    for i in range(12):
        mes = hoy.replace(day=1) - timedelta(days=30*i)
        mes_siguiente = (mes.replace(day=28) + timedelta(days=4)).replace(day=1)
        total_mes = incentivos.filter(
            fecha_otorgado__gte=mes,
            fecha_otorgado__lt=mes_siguiente
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0')
        
        incentivos_mensuales.append({
            'mes': mes.strftime('%b %Y'),
            'total': float(total_mes)
        })
    
    incentivos_mensuales.reverse()
    
    context = {
        'empleado': empleado,
        'incentivos': incentivos,
        'total_incentivos': total_incentivos,
        'incentivos_este_año': incentivos_este_año,
        'incentivos_mensuales': json.dumps(incentivos_mensuales),
    }
    
    return render(request, 'empleados/incentivos_empleado.html', context)


@login_required
def servicios_empleado(request):
    """Vista para mostrar todos los servicios del empleado con filtros"""
    empleado = get_object_or_404(Empleado, usuario=request.user)
    
    # Obtener servicios del empleado
    servicios = Reserva.objects.filter(lavador=empleado).select_related(
        'cliente', 'servicio', 'vehiculo', 'bahia'
    ).prefetch_related('calificacion_empleado')
    
    # Aplicar filtros
    estado = request.GET.get('estado')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    buscar = request.GET.get('buscar')
    
    if estado:
        servicios = servicios.filter(estado=estado)
    
    if fecha_desde:
        servicios = servicios.filter(fecha_hora__date__gte=fecha_desde)
    
    if fecha_hasta:
        servicios = servicios.filter(fecha_hora__date__lte=fecha_hasta)
    
    if buscar:
        servicios = servicios.filter(
            Q(cliente__nombre__icontains=buscar) |
            Q(cliente__apellido__icontains=buscar) |
            Q(vehiculo__placa__icontains=buscar) |
            Q(servicio__nombre__icontains=buscar)
        )
    
    # Ordenar por fecha más reciente
    servicios = servicios.order_by('-fecha_hora')
    
    # Estadísticas
    estadisticas = {
        'pendientes': servicios.filter(estado__in=['pendiente', 'confirmado']).count(),
        'atendidos': servicios.filter(estado='completado').count(),
        'cancelados': servicios.filter(estado='cancelado').count(),
    }
    
    # Paginación
    paginator = Paginator(servicios, 12)
    page_number = request.GET.get('page')
    servicios_paginados = paginator.get_page(page_number)
    
    context = {
        'empleado': empleado,
        'servicios': servicios_paginados,
        'estadisticas': estadisticas,
        'is_paginated': servicios_paginados.has_other_pages(),
        'page_obj': servicios_paginados,
    }
    
    return render(request, 'empleados/dashboard/servicios.html', context)


@login_required
def calificaciones_empleado(request):
    """Vista para mostrar las calificaciones del empleado"""
    empleado = get_object_or_404(Empleado, usuario=request.user)
    
    # Obtener calificaciones del empleado
    calificaciones = Calificacion.objects.filter(empleado=empleado).select_related(
        'cliente', 'servicio', 'reserva__vehiculo'
    ).order_by('-fecha_creacion')
    
    # Aplicar filtros
    calificacion_filtro = request.GET.get('calificacion')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    buscar = request.GET.get('buscar')
    
    if calificacion_filtro:
        calificaciones = calificaciones.filter(puntuacion=calificacion_filtro)
    
    if fecha_desde:
        calificaciones = calificaciones.filter(fecha_creacion__date__gte=fecha_desde)
    
    if fecha_hasta:
        calificaciones = calificaciones.filter(fecha_creacion__date__lte=fecha_hasta)
    
    if buscar:
        calificaciones = calificaciones.filter(
            Q(cliente__nombre__icontains=buscar) |
            Q(cliente__apellido__icontains=buscar) |
            Q(comentario__icontains=buscar)
        )
    
    # Estadísticas
    estadisticas = {
        'promedio': calificaciones.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0,
        'total': calificaciones.count(),
        'este_mes': calificaciones.filter(
            fecha_creacion__month=timezone.now().month,
            fecha_creacion__year=timezone.now().year
        ).count(),
    }
    
    # Distribución de calificaciones
    distribucion = []
    for i in range(1, 6):
        cantidad = calificaciones.filter(puntuacion=i).count()
        porcentaje = (cantidad / estadisticas['total'] * 100) if estadisticas['total'] > 0 else 0
        distribucion.append({
            'estrellas': i,
            'cantidad': cantidad,
            'porcentaje': porcentaje
        })
    
    # Tendencia mensual (últimos 6 meses)
    tendencia_labels = []
    tendencia_data = []
    for i in range(5, -1, -1):
        fecha = timezone.now() - timedelta(days=30*i)
        mes_nombre = fecha.strftime('%b %Y')
        promedio = calificaciones.filter(
            fecha_creacion__month=fecha.month,
            fecha_creacion__year=fecha.year
        ).aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
        
        tendencia_labels.append(mes_nombre)
        tendencia_data.append(round(promedio, 1))
    
    # Paginación
    paginator = Paginator(calificaciones, 8)
    page_number = request.GET.get('page')
    calificaciones_paginadas = paginator.get_page(page_number)
    
    context = {
        'empleado': empleado,
        'calificaciones': calificaciones_paginadas,
        'estadisticas': estadisticas,
        'distribucion': distribucion,
        'tendencia_labels': tendencia_labels,
        'tendencia_data': tendencia_data,
        'is_paginated': calificaciones_paginadas.has_other_pages(),
        'page_obj': calificaciones_paginadas,
    }
    
    return render(request, 'empleados/dashboard/calificaciones.html', context)


@login_required
def bonificaciones_empleado(request):
    """Vista para mostrar las bonificaciones del empleado"""
    empleado = get_object_or_404(Empleado, usuario=request.user)
    
    # Obtener bonificaciones del empleado
    bonificaciones = Incentivo.objects.filter(empleado=empleado).select_related(
        'servicio_relacionado__servicio'
    ).order_by('-fecha_otorgada')
    
    # Aplicar filtros
    tipo = request.GET.get('tipo')
    mes = request.GET.get('mes')
    ano = request.GET.get('ano')
    monto_min = request.GET.get('monto_min')
    
    if tipo:
        bonificaciones = bonificaciones.filter(tipo_incentivo=tipo)
    
    if mes:
        bonificaciones = bonificaciones.filter(fecha_otorgada__month=mes)
    
    if ano:
        bonificaciones = bonificaciones.filter(fecha_otorgada__year=ano)
    
    if monto_min:
        bonificaciones = bonificaciones.filter(monto__gte=monto_min)
    
    # Resumen financiero
    ahora = timezone.now()
    resumen = {
        'total_mes': bonificaciones.filter(
            fecha_otorgada__month=ahora.month,
            fecha_otorgada__year=ahora.year
        ).aggregate(Sum('monto'))['monto__sum'] or 0,
        'total_ano': bonificaciones.filter(
            fecha_otorgada__year=ahora.year
        ).aggregate(Sum('monto'))['monto__sum'] or 0,
        'total_historico': bonificaciones.aggregate(Sum('monto'))['monto__sum'] or 0,
    }
    
    # Tipos de bonificación
    tipos_bonificacion = []
    tipos_disponibles = [
        ('servicios_completados', 'Servicios Completados', '#28a745'),
        ('calificacion_excelente', 'Calificación Excelente', '#ffc107'),
        ('puntualidad', 'Puntualidad', '#17a2b8'),
        ('meta_mensual', 'Meta Mensual', '#6f42c1'),
        ('cliente_frecuente', 'Cliente Frecuente', '#fd7e14'),
    ]
    
    for tipo_key, tipo_nombre, color in tipos_disponibles:
        total = bonificaciones.filter(tipo_incentivo=tipo_key).aggregate(Sum('monto'))['monto__sum'] or 0
        if total > 0:
            tipos_bonificacion.append({
                'nombre': tipo_nombre,
                'total': total,
                'color': color
            })
    
    # Evolución mensual (últimos 6 meses)
    evolucion_labels = []
    evolucion_data = []
    for i in range(5, -1, -1):
        fecha = timezone.now() - timedelta(days=30*i)
        mes_nombre = fecha.strftime('%b %Y')
        total = bonificaciones.filter(
            fecha_otorgada__month=fecha.month,
            fecha_otorgada__year=fecha.year
        ).aggregate(Sum('monto'))['monto__sum'] or 0
        
        evolucion_labels.append(mes_nombre)
        evolucion_data.append(float(total))
    
    # Metas del mes (simuladas - deberían venir de un modelo de metas)
    metas_mes = [
        {
            'nombre': 'Servicios Completados',
            'descripcion': 'Completar 50 servicios este mes',
            'progreso': 35,
            'objetivo': 50,
            'porcentaje': 70,
            'bonificacion': 100000,
            'completada': False,
            'faltante': 15,
            'color': '#28a745'
        },
        {
            'nombre': 'Calificación Promedio',
            'descripcion': 'Mantener promedio de 4.5 estrellas',
            'progreso': 4.7,
            'objetivo': 4.5,
            'porcentaje': 100,
            'bonificacion': 50000,
            'completada': True,
            'faltante': 0,
            'color': '#ffc107'
        },
        {
            'nombre': 'Puntualidad',
            'descripción': 'Llegar a tiempo al 95% de servicios',
            'progreso': 92,
            'objetivo': 95,
            'porcentaje': 97,
            'bonificacion': 75000,
            'completada': False,
            'faltante': 3,
            'color': '#17a2b8'
        }
    ]
    
    # Datos para gráficos
    tipos_labels = [tipo['nombre'] for tipo in tipos_bonificacion]
    tipos_data = [float(tipo['total']) for tipo in tipos_bonificacion]
    tipos_colors = [tipo['color'] for tipo in tipos_bonificacion]
    
    # Años y meses disponibles para filtros
    anos_disponibles = bonificaciones.dates('fecha_otorgada', 'year', order='DESC')
    meses_disponibles = [
        {'numero': '1', 'nombre': 'Enero'}, {'numero': '2', 'nombre': 'Febrero'},
        {'numero': '3', 'nombre': 'Marzo'}, {'numero': '4', 'nombre': 'Abril'},
        {'numero': '5', 'nombre': 'Mayo'}, {'numero': '6', 'nombre': 'Junio'},
        {'numero': '7', 'nombre': 'Julio'}, {'numero': '8', 'nombre': 'Agosto'},
        {'numero': '9', 'nombre': 'Septiembre'}, {'numero': '10', 'nombre': 'Octubre'},
        {'numero': '11', 'nombre': 'Noviembre'}, {'numero': '12', 'nombre': 'Diciembre'},
    ]
    
    # Paginación
    paginator = Paginator(bonificaciones, 10)
    page_number = request.GET.get('page')
    bonificaciones_paginadas = paginator.get_page(page_number)
    
    context = {
        'empleado': empleado,
        'bonificaciones': bonificaciones_paginadas,
        'resumen': resumen,
        'tipos_bonificacion': tipos_bonificacion,
        'metas_mes': metas_mes,
        'evolucion_labels': evolucion_labels,
        'evolucion_data': evolucion_data,
        'tipos_labels': tipos_labels,
        'tipos_data': tipos_data,
        'tipos_colors': tipos_colors,
        'anos_disponibles': [ano.year for ano in anos_disponibles],
        'meses_disponibles': meses_disponibles,
        'is_paginated': bonificaciones_paginadas.has_other_pages(),
        'page_obj': bonificaciones_paginadas,
    }
    
    return render(request, 'empleados/dashboard/bonificaciones.html', context)


@login_required
def actualizar_disponibilidad(request):
    """API para actualizar la disponibilidad del empleado"""
    if request.method == 'POST':
        empleado = get_object_or_404(Empleado, usuario=request.user)
        disponible = request.POST.get('disponible') == 'true'
        
        empleado.disponible = disponible
        empleado.save()
        
        return JsonResponse({
            'success': True,
            'disponible': empleado.disponible,
            'mensaje': f'Disponibilidad actualizada: {"Disponible" if disponible else "No disponible"}'
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})