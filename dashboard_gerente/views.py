from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg, Sum, Min, Max, Q
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
import json
from autenticacion.mixins import GerenteRequiredMixin
from reservas.models import Reserva, Servicio, Bahia, DisponibilidadHoraria
from clientes.models import Cliente
from empleados.models import Empleado, Calificacion
from .models import KPIConfiguracion
from .forms import KPIConfiguracionForm
from django.urls import reverse
from django.shortcuts import get_object_or_404


class DashboardGerenteView(LoginRequiredMixin, GerenteRequiredMixin, View):
    def get(self, request):
        try:
            now = timezone.now()
            hoy = now.date()
            inicio_semana = hoy - timezone.timedelta(days=hoy.weekday())
            inicio_mes = hoy.replace(day=1)
            # Filtros GET para periodo y agrupación
            fi = request.GET.get('fi')
            ff = request.GET.get('ff')
            group_by = request.GET.get('group_by', 'day')  # day|week|fortnight|month
            segment = request.GET.get('segment')
            # Periodo por defecto
            start = now - timezone.timedelta(days=30)
            end = now
            segment_label = 'Últimos 30 días'
            # Segmentadores tienen prioridad
            if segment == 'last7':
                start = now - timezone.timedelta(days=7)
                segment_label = 'Últimos 7 días'
            elif segment == 'last30':
                start = now - timezone.timedelta(days=30)
                segment_label = 'Últimos 30 días'
            elif segment == 'this_month':
                start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                segment_label = 'Este mes'
            elif segment == 'last_month':
                month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                prev_end = month_start - timezone.timedelta(seconds=1)
                start = prev_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end = prev_end
                segment_label = 'Mes anterior'
            else:
                # Rango personalizado por fi/ff si se suministran (admite YYYY-MM-DD o datetime ISO)
                if fi:
                    try:
                        if len(fi) == 10:
                            start_date = timezone.datetime.fromisoformat(fi).date()
                            start = timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time()))
                        else:
                            start = timezone.datetime.fromisoformat(fi)
                            if timezone.is_naive(start):
                                start = timezone.make_aware(start)
                    except Exception:
                        pass
                if ff:
                    try:
                        if len(ff) == 10:
                            end_date = timezone.datetime.fromisoformat(ff).date()
                            # usar fin del día
                            end = timezone.make_aware(timezone.datetime.combine(end_date, timezone.datetime.max.time()))
                        else:
                            end = timezone.datetime.fromisoformat(ff)
                            if timezone.is_naive(end):
                                end = timezone.make_aware(end)
                    except Exception:
                        pass
                # Asegurar que el rango sea válido
                if end < start:
                    start, end = end, start
                segment_label = f"{start.date().isoformat()} — {end.date().isoformat()}"

            # Ingresos
            ingresos_total = Reserva.objects.filter(estado=Reserva.COMPLETADA).aggregate(total=Sum('precio_final'))['total'] or 0
            ingresos_mes = Reserva.objects.filter(estado=Reserva.COMPLETADA, fecha_hora__date__gte=inicio_mes).aggregate(total=Sum('precio_final'))['total'] or 0
            descuentos_mes = Reserva.objects.filter(fecha_hora__date__gte=inicio_mes).aggregate(total=Sum('descuento_aplicado'))['total'] or 0
            ticket_promedio = Reserva.objects.filter(estado=Reserva.COMPLETADA).aggregate(avg=Avg('precio_final'))['avg'] or 0

            # Ingresos últimos 30 días (línea)
            # Agrupador según group_by
            if group_by == 'week':
                trunc = TruncWeek('fecha_hora')
                periodo_key = 'semana'
            elif group_by == 'fortnight':
                trunc = TruncWeek('fecha_hora')  # base semanal, combinaremos cada 2
                periodo_key = 'semana'
            elif group_by == 'month':
                trunc = TruncMonth('fecha_hora')
                periodo_key = 'mes'
            else:
                trunc = TruncDate('fecha_hora')
                periodo_key = 'dia'

            group_by_label = {'day': 'Día', 'week': 'Semana', 'fortnight': 'Quincenal', 'month': 'Mes'}.get(group_by, 'Día')

            ingresos_qs = (
                Reserva.objects
                .filter(estado=Reserva.COMPLETADA, fecha_hora__gte=start, fecha_hora__lte=end)
                .annotate(periodo=trunc)
                .values('periodo')
                .annotate(total=Sum('precio_final'))
                .order_by('periodo')
            )
            ingresos_labels_raw = [str(item['periodo']) for item in ingresos_qs]
            ingresos_data_raw = [float(item['total'] or 0) for item in ingresos_qs]

            # Agrupación quincenal: combinar cada 2 semanas consecutivas
            if group_by == 'fortnight':
                ingresos_labels = []
                ingresos_data = []
                for i in range(0, len(ingresos_labels_raw), 2):
                    label = ingresos_labels_raw[i]
                    if i+1 < len(ingresos_labels_raw):
                        label = f"{ingresos_labels_raw[i]} / {ingresos_labels_raw[i+1]}"
                    ingresos_labels.append(label)
                    total = ingresos_data_raw[i] + (ingresos_data_raw[i+1] if i+1 < len(ingresos_data_raw) else 0)
                    ingresos_data.append(total)
            else:
                ingresos_labels = ingresos_labels_raw
                ingresos_data = ingresos_data_raw

            # Reservas por estado (dona)
            reservas_por_estado = (
                Reserva.objects
                .filter(fecha_hora__gte=start, fecha_hora__lte=end)
                .values('estado')
                .annotate(total=Count('id'))
            )
            estado_labels = [item['estado'] for item in reservas_por_estado]
            estado_data = [item['total'] for item in reservas_por_estado]

            # Servicios top por cantidad y por ingresos (barras)
            servicios_stats = (
                Reserva.objects.filter(estado=Reserva.COMPLETADA, fecha_hora__gte=start, fecha_hora__lte=end)
                .values('servicio__nombre')
                .annotate(cantidad=Count('id'), ingresos=Sum('precio_final'))
                .order_by('-cantidad')[:10]
            )
            servicios_labels = [item['servicio__nombre'] or 'N/A' for item in servicios_stats]
            servicios_cantidad = [item['cantidad'] for item in servicios_stats]
            servicios_ingresos = [float(item['ingresos'] or 0) for item in servicios_stats]

            # Clientes
            total_clientes = Cliente.objects.count()
            nuevos_7 = Cliente.objects.filter(fecha_registro__gte=now - timezone.timedelta(days=7)).count()
            activos_30 = Cliente.objects.filter(reservas__estado=Reserva.COMPLETADA, reservas__fecha_hora__gte=start, reservas__fecha_hora__lte=end).distinct().count()

            # Empleados
            empleados_activos = Empleado.objects.filter(activo=True, rol=Empleado.ROL_LAVADOR).count()
            calificacion_promedio = Calificacion.objects.aggregate(avg=Avg('puntuacion'))['avg'] or 0
            top_lavadores = (
                Empleado.objects
                .filter(rol=Empleado.ROL_LAVADOR, activo=True)
                .annotate(
                    completadas=Count(
                        'reservas_asignadas',
                        filter=Q(
                            reservas_asignadas__estado=Reserva.COMPLETADA,
                            reservas_asignadas__fecha_hora__gte=start,
                            reservas_asignadas__fecha_hora__lte=end
                        )
                    )
                )
                .order_by('-completadas')[:5]
            )
            lavadores_labels = [e.nombre_completo() if hasattr(e, 'nombre_completo') else str(e) for e in top_lavadores]
            lavadores_data = [e.completadas or 0 for e in top_lavadores]

            # Ranking por valoración promedio (★) en el período
            top_lavadores_val = (
                Empleado.objects
                .filter(rol=Empleado.ROL_LAVADOR, activo=True)
                .annotate(
                    rating=Avg(
                        'calificaciones__puntuacion',
                        filter=Q(
                            calificaciones__fecha_calificacion__gte=start,
                            calificaciones__fecha_calificacion__lte=end
                        )
                    ),
                    completadas=Count(
                        'reservas_asignadas',
                        filter=Q(
                            reservas_asignadas__estado=Reserva.COMPLETADA,
                            reservas_asignadas__fecha_hora__gte=start,
                            reservas_asignadas__fecha_hora__lte=end
                        )
                    )
                )
                .order_by('-rating', '-completadas')[:5]
            )
            lavadores_val_labels = [e.nombre_completo() if hasattr(e, 'nombre_completo') else str(e) for e in top_lavadores_val]
            lavadores_val_data = [round(float(e.rating or 0), 2) for e in top_lavadores_val]

            # Bahías - métricas
            bahias_stats = (
                Reserva.objects
                .filter(estado=Reserva.COMPLETADA, fecha_hora__gte=start, fecha_hora__lte=end)
                .values('bahia__nombre')
                .annotate(
                    servicios=Count('id'),
                    ingresos=Sum('precio_final'),
                    uso_minutos=Sum('servicio__duracion_minutos')
                )
                .order_by('-servicios')
            )
            bahias_labels = [item['bahia__nombre'] or 'Sin bahía' for item in bahias_stats]
            bahias_servicios = [item['servicios'] or 0 for item in bahias_stats]
            bahias_ingresos = [float(item['ingresos'] or 0) for item in bahias_stats]
            bahias_uso_horas = [round((item['uso_minutos'] or 0) / 60, 2) for item in bahias_stats]

            # Conteos de Bahías (disponibles / con cámaras / sin cámaras)
            bahias_total_qs = Bahia.objects.filter(activo=True)
            ocupadas_ids = (
                Reserva.objects
                .filter(
                    bahia__isnull=False,
                    fecha_hora__lte=now,
                    estado__in=[Reserva.CONFIRMADA, Reserva.EN_PROCESO]
                )
                .values_list('bahia_id', flat=True)
                .distinct()
            )
            bahias_disponibles = bahias_total_qs.exclude(id__in=list(ocupadas_ids)).count()
            bahias_con_camara = bahias_total_qs.filter(tiene_camara=True).count()
            bahias_sin_camara = bahias_total_qs.filter(tiene_camara=False).count()

            # Métricas adicionales
            reservas_mes = Reserva.objects.filter(fecha_hora__date__gte=inicio_mes).count()
            cancelaciones_mes = Reserva.objects.filter(estado=Reserva.CANCELADA, fecha_hora__date__gte=inicio_mes).count()
            completadas_hoy = Reserva.objects.filter(estado=Reserva.COMPLETADA, fecha_hora__date=hoy).count()
            total_periodo = Reserva.objects.filter(fecha_hora__gte=start, fecha_hora__lte=end).count()
            cancelaciones_periodo = Reserva.objects.filter(estado=Reserva.CANCELADA, fecha_hora__gte=start, fecha_hora__lte=end).count()
            tasa_cancelacion = round((cancelaciones_periodo / total_periodo) * 100, 2) if total_periodo else 0

            # KPI del segmento seleccionado
            ingresos_segmento = Reserva.objects.filter(
                estado=Reserva.COMPLETADA, fecha_hora__gte=start, fecha_hora__lte=end
            ).aggregate(total=Sum('precio_final'))['total'] or 0
            descuentos_segmento = Reserva.objects.filter(
                fecha_hora__gte=start, fecha_hora__lte=end
            ).aggregate(total=Sum('descuento_aplicado'))['total'] or 0
            ticket_promedio_segmento = Reserva.objects.filter(
                estado=Reserva.COMPLETADA, fecha_hora__gte=start, fecha_hora__lte=end
            ).aggregate(avg=Avg('precio_final'))['avg'] or 0
            ingresos_netos_segmento = (ingresos_segmento or 0) - (descuentos_segmento or 0)
            reservas_segmento = Reserva.objects.filter(
                fecha_hora__gte=start, fecha_hora__lte=end
            ).count()
            cancelaciones_segmento = Reserva.objects.filter(
                estado=Reserva.CANCELADA, fecha_hora__gte=start, fecha_hora__lte=end
            ).count()
            completadas_segmento = Reserva.objects.filter(
                estado=Reserva.COMPLETADA, fecha_hora__gte=start, fecha_hora__lte=end
            ).count()
            pendientes_segmento = Reserva.objects.filter(
                estado=Reserva.PENDIENTE, fecha_hora__gte=start, fecha_hora__lte=end
            ).count()

            # Etiquetas compacta y completa para mostrar en headers con tooltip
            try:
                days = (end.date() - start.date()).days + 1
                # Rango truncado: si es el mismo año, el final sin año; si cambia de año, mostrar ambos años
                if start.year == end.year:
                    compact_range = f"{start.date().isoformat()}…{end.strftime('%m-%d')}"
                else:
                    compact_range = f"{start.date().isoformat()}…{end.date().isoformat()}"
                # Etiqueta por duración para rangos largos
                if days >= 60:
                    months = round(days / 30)
                    segment_label_compact = f"{months} mes" if months == 1 else f"{months} meses"
                elif days >= 14:
                    weeks = round(days / 7)
                    segment_label_compact = f"{weeks} semana" if weeks == 1 else f"{weeks} semanas"
                elif days >= 2:
                    segment_label_compact = f"{days} días"
                else:
                    segment_label_compact = "1 día"
                # Para rangos pequeños/medios usar el truncado por fechas
                if days < 60:
                    segment_label_compact = compact_range
            except Exception:
                segment_label_compact = segment_label
            segment_label_full = f"{start.date().isoformat()} — {end.date().isoformat()}"

            context = {
                'ingresos_total': ingresos_total,
                'ingresos_mes': ingresos_mes,
                'descuentos_mes': descuentos_mes,
                'ticket_promedio': ticket_promedio,
                'estado_labels': json.dumps(estado_labels),
                'estado_data': json.dumps(estado_data),
                'ingresos_labels': json.dumps(ingresos_labels),
                'ingresos_data': json.dumps(ingresos_data),
                'servicios_labels': json.dumps(servicios_labels),
                'servicios_cantidad': json.dumps(servicios_cantidad),
                'servicios_ingresos': json.dumps(servicios_ingresos),
                'total_clientes': total_clientes,
                'nuevos_7': nuevos_7,
                'activos_30': activos_30,
                'empleados_activos': empleados_activos,
                'calificacion_promedio': calificacion_promedio,
                'lavadores_labels': json.dumps(lavadores_labels),
                'lavadores_data': json.dumps(lavadores_data),
                'lavadores_val_labels': json.dumps(lavadores_val_labels),
                'lavadores_val_data': json.dumps(lavadores_val_data),
                # Datos de Bahías
                'bahias_labels': json.dumps(bahias_labels),
                'bahias_servicios': json.dumps(bahias_servicios),
                'bahias_uso_horas': json.dumps(bahias_uso_horas),
                'bahias_ingresos': json.dumps(bahias_ingresos),
                'bahias_disponibles': bahias_disponibles,
                'bahias_con_camara': bahias_con_camara,
                'bahias_sin_camara': bahias_sin_camara,
                'applied_filters': {
                    'fi': start.date().isoformat(),
                    'ff': end.date().isoformat(),
                    'group_by': group_by,
                    'segment': segment or 'custom',
                    'segment_label': segment_label,
                    'segment_label_compact': segment_label_compact,
                    'segment_label_full': segment_label_full,
                },
                # Variables de segmento para usar en plantilla
                'segment_label': segment_label,
                'segment_label_compact': segment_label_compact,
                'segment_label_full': segment_label_full,
                'group_by_label': group_by_label,
                'ingresos_segmento': ingresos_segmento,
                'descuentos_segmento': descuentos_segmento,
                'ingresos_netos_segmento': ingresos_netos_segmento,
                'ticket_promedio_segmento': ticket_promedio_segmento,
                'reservas_segmento': reservas_segmento,
                'cancelaciones_segmento': cancelaciones_segmento,
                'completadas_segmento': completadas_segmento,
                'tasa_cancelacion': tasa_cancelacion,
                'pendientes_segmento': pendientes_segmento,
            }
            return render(request, 'dashboard_gerente/dashboard.html', context)
        except Exception as e:
            messages.error(request, f'Error al cargar el dashboard del gerente: {str(e)}')
            # Evitar redirección que puede causar bucle; renderizar con datos por defecto
            safe_context = {
                'ingresos_total': 0,
                'ingresos_mes': 0,
                'descuentos_mes': 0,
                'ticket_promedio': 0,
                'estado_labels': json.dumps([]),
                'estado_data': json.dumps([]),
                'ingresos_labels': json.dumps([]),
                'ingresos_data': json.dumps([]),
                'servicios_labels': json.dumps([]),
                'servicios_cantidad': json.dumps([]),
                'servicios_ingresos': json.dumps([]),
                'total_clientes': 0,
                'nuevos_7': 0,
                'activos_30': 0,
                'empleados_activos': 0,
                'calificacion_promedio': 0,
                'lavadores_labels': json.dumps([]),
                'lavadores_data': json.dumps([]),
                'lavadores_val_labels': json.dumps([]),
                'lavadores_val_data': json.dumps([]),
                # Datos de Bahías (vacíos)
                'bahias_labels': json.dumps([]),
                'bahias_servicios': json.dumps([]),
                'bahias_uso_horas': json.dumps([]),
                'bahias_ingresos': json.dumps([]),
                'bahias_disponibles': 0,
                'bahias_con_camara': 0,
                'bahias_sin_camara': 0,
                # Valores por defecto para variables del segmento
                'segment_label': 'Sin datos',
                'ingresos_segmento': 0,
                'descuentos_segmento': 0,
                'ticket_promedio_segmento': 0,
                'reservas_segmento': 0,
                'cancelaciones_segmento': 0,
                'completadas_segmento': 0,
                'tasa_cancelacion': 0,
            }
            return render(request, 'dashboard_gerente/dashboard.html', safe_context, status=200)


class KPIListCreateView(LoginRequiredMixin, GerenteRequiredMixin, View):
    def get(self, request):
        kpis = KPIConfiguracion.objects.filter(usuario=request.user).order_by('-creado_en')
        form = KPIConfiguracionForm()
        return render(request, 'dashboard_gerente/kpis.html', {
            'kpis': kpis,
            'form': form,
            'form_action_url': reverse('dashboard_gerente:kpis'),
            'editing': False,
        })

    def post(self, request):
        form = KPIConfiguracionForm(request.POST)
        if form.is_valid():
            kpi = form.save(commit=False)
            kpi.usuario = request.user
            kpi.save()
            messages.success(request, 'KPI guardado correctamente.')
            return redirect('dashboard_gerente:kpis')
        kpis = KPIConfiguracion.objects.filter(usuario=request.user).order_by('-creado_en')
        messages.error(request, 'Por favor corrige los errores del formulario.')
        return render(request, 'dashboard_gerente/kpis.html', {
            'kpis': kpis,
            'form': form,
            'form_action_url': reverse('dashboard_gerente:kpis'),
            'editing': False,
        })
class KPIUpdateView(LoginRequiredMixin, GerenteRequiredMixin, View):
    def get(self, request, pk):
        kpi = get_object_or_404(KPIConfiguracion, pk=pk, usuario=request.user)
        form = KPIConfiguracionForm(instance=kpi)
        kpis = KPIConfiguracion.objects.filter(usuario=request.user).order_by('-creado_en')
        return render(request, 'dashboard_gerente/kpis.html', {
            'kpis': kpis,
            'form': form,
            'editing': True,
            'editing_kpi': kpi,
            'form_action_url': reverse('dashboard_gerente:kpi_editar', args=[pk]),
        })

    def post(self, request, pk):
        kpi = get_object_or_404(KPIConfiguracion, pk=pk, usuario=request.user)
        form = KPIConfiguracionForm(request.POST, instance=kpi)
        if form.is_valid():
            form.save()
            messages.success(request, 'KPI actualizado correctamente.')
            return redirect('dashboard_gerente:kpis')
        kpis = KPIConfiguracion.objects.filter(usuario=request.user).order_by('-creado_en')
        messages.error(request, 'Por favor corrige los errores del formulario.')
        return render(request, 'dashboard_gerente/kpis.html', {
            'kpis': kpis,
            'form': form,
            'editing': True,
            'editing_kpi': kpi,
            'form_action_url': reverse('dashboard_gerente:kpi_editar', args=[pk]),
        })


class KPIDeleteView(LoginRequiredMixin, GerenteRequiredMixin, View):
    def post(self, request, pk):
        kpi = get_object_or_404(KPIConfiguracion, pk=pk, usuario=request.user)
        kpi.delete()
        messages.success(request, 'KPI eliminado correctamente.')
        return redirect('dashboard_gerente:kpis')


class KPIToggleActivoView(LoginRequiredMixin, GerenteRequiredMixin, View):
    def post(self, request, pk):
        kpi = get_object_or_404(KPIConfiguracion, pk=pk, usuario=request.user)
        kpi.activo = not kpi.activo
        kpi.save(update_fields=['activo'])
        messages.success(request, f'KPI marcado como {"activo" if kpi.activo else "inactivo"}.')
        return redirect('dashboard_gerente:kpis')


class IndicadoresView(LoginRequiredMixin, GerenteRequiredMixin, View):
    def get(self, request):
        try:
            now = timezone.now()
            # Filtros de la UI
            fecha_inicio_str = request.GET.get('fecha_inicio')
            fecha_fin_str = request.GET.get('fecha_fin')
            group_by = request.GET.get('group_by', 'day')  # day|week|month
            estado_override = request.GET.get('estado') or None
            servicio_id = request.GET.get('servicio')
            comparar = request.GET.get('comparar') == 'on'

            # KPIs activos
            kpis = KPIConfiguracion.objects.filter(usuario=request.user, activo=True).order_by('-creado_en')
            default_days = kpis.first().periodo_dias if kpis.exists() else 30
            start = now - timezone.timedelta(days=default_days)
            end = now
            if fecha_inicio_str:
                try:
                    start = timezone.datetime.fromisoformat(fecha_inicio_str)
                    if timezone.is_naive(start):
                        start = timezone.make_aware(start)
                except Exception:
                    pass
            if fecha_fin_str:
                try:
                    end = timezone.datetime.fromisoformat(fecha_fin_str)
                    if timezone.is_naive(end):
                        end = timezone.make_aware(end)
                except Exception:
                    pass

            charts = []
            for kpi in kpis:
                labels, data, cmp_labels, cmp_data = self._compute_series(
                    kpi=kpi,
                    start=start,
                    end=end,
                    group_by=group_by,
                    estado=estado_override,
                    servicio_id=servicio_id,
                    comparar=comparar,
                )
                # Valores para medidor
                actual = float(data[-1]) if data else 0
                min_val = float(min(data)) if data else 0
                max_val = float(max(data)) if data else (actual or 1)
                # Bandera de porcentaje (utilización por duración) y preferencia baja
                is_percent = (
                    kpi.entidad == KPIConfiguracion.Entidad.RESERVAS and
                    kpi.metrica == KPIConfiguracion.Metrica.SUMA and
                    (kpi.campo or '').strip() == 'duracion_minutos'
                )
                prefer_low = ((kpi.estado_filtro or '').lower() in ['cancelada', 'incumplida'])
                # Meta: si es porcentaje y no hay umbral, usar 85%
                meta_val = (
                    float(kpi.umbral_alerta) if getattr(kpi, 'umbral_alerta', None) is not None else (85.0 if is_percent else max_val)
                )
                is_currency = (kpi.entidad == KPIConfiguracion.Entidad.INGRESOS) or ('precio' in (kpi.campo or '').lower())
                charts.append({
                    'id': f'chart_{kpi.id}',
                    'nombre': kpi.nombre,
                    'labels': json.dumps(labels),
                    'data': json.dumps(data),
                    'cmp_labels': json.dumps(cmp_labels),
                    'cmp_data': json.dumps(cmp_data),
                    'entidad': kpi.get_entidad_display(),
                    'metrica': kpi.get_metrica_display(),
                    'periodo': kpi.periodo_dias,
                    'actual': actual,
                    'min': min_val,
                    'max': max_val,
                    'meta': meta_val,
                    'is_currency': is_currency,
                    'is_percent': is_percent,
                    'prefer_low': prefer_low,
                })

            # Opciones dinámicas de estado y servicios
            estado_field = Reserva._meta.get_field('estado')
            estado_choices = [{'value': k, 'label': v} for k, v in getattr(estado_field, 'choices', [])]
            servicios = Servicio.objects.all().order_by('nombre')

            context = {
                'charts': charts,
                'kpis': kpis,
                'servicios': servicios,
                'estado_choices': estado_choices,
                'applied_filters': {
                    'fecha_inicio': start.date().isoformat(),
                    'fecha_fin': end.date().isoformat(),
                    'group_by': group_by,
                    'estado': estado_override or '',
                    'servicio': servicio_id or '',
                    'comparar': comparar,
                }
            }
            return render(request, 'dashboard_gerente/indicadores.html', context)
        except Exception as e:
            messages.error(request, f'Error al cargar Indicadores: {str(e)}')
            servicios = Servicio.objects.all().order_by('nombre')
            return render(request, 'dashboard_gerente/indicadores.html', {'charts': [], 'kpis': [], 'servicios': servicios, 'estado_choices': []}, status=200)

    def _compute_series(self, kpi: KPIConfiguracion, start, end, group_by='day', estado=None, servicio_id=None, comparar=False):
        # Selección de agrupador
        if group_by == 'week':
            trunc = TruncWeek('fecha_hora')
        elif group_by == 'month':
            trunc = TruncMonth('fecha_hora')
        else:
            trunc = TruncDate('fecha_hora')

        if kpi.entidad in ['reservas', 'ingresos']:
            qs = Reserva.objects.filter(fecha_hora__gte=start, fecha_hora__lte=end)
            # Estado del KPI o override
            estado_filtro = estado or kpi.estado_filtro
            if estado_filtro:
                qs = qs.filter(estado=estado_filtro)
            if servicio_id:
                try:
                    qs = qs.filter(servicio_id=int(servicio_id))
                except Exception:
                    pass

            # Agrupación principal
            grouped = qs.annotate(periodo=trunc).values('periodo')
            campo = kpi.campo or 'id'
            metric = kpi.metrica
            if metric == KPIConfiguracion.Metrica.CUENTA:
                agg = grouped.annotate(valor=Count('id')).order_by('periodo')
            elif metric == KPIConfiguracion.Metrica.SUMA:
                agg = grouped.annotate(valor=Sum(campo)).order_by('periodo')
            elif metric == KPIConfiguracion.Metrica.PROMEDIO:
                agg = grouped.annotate(valor=Avg(campo)).order_by('periodo')
            elif metric == KPIConfiguracion.Metrica.MAXIMO:
                agg = grouped.annotate(valor=Max(campo)).order_by('periodo')
            elif metric == KPIConfiguracion.Metrica.MINIMO:
                agg = grouped.annotate(valor=Min(campo)).order_by('periodo')
            else:
                agg = grouped.annotate(valor=Count('id')).order_by('periodo')
            labels = [str(item['periodo']) for item in agg]
            data = [float(item['valor'] or 0) for item in agg]

            cmp_labels, cmp_data = [], []
            if comparar:
                # periodo previo del mismo tamaño
                delta = end - start
                prev_start = start - delta
                prev_end = start
                qs_prev = Reserva.objects.filter(fecha_hora__gte=prev_start, fecha_hora__lte=prev_end)
                if estado_filtro:
                    qs_prev = qs_prev.filter(estado=estado_filtro)
                if servicio_id:
                    try:
                        qs_prev = qs_prev.filter(servicio_id=int(servicio_id))
                    except Exception:
                        pass
                grouped_prev = qs_prev.annotate(periodo=trunc).values('periodo')
                if metric == KPIConfiguracion.Metrica.CUENTA:
                    agg_prev = grouped_prev.annotate(valor=Count('id')).order_by('periodo')
                elif metric == KPIConfiguracion.Metrica.SUMA:
                    agg_prev = grouped_prev.annotate(valor=Sum(campo)).order_by('periodo')
                elif metric == KPIConfiguracion.Metrica.PROMEDIO:
                    agg_prev = grouped_prev.annotate(valor=Avg(campo)).order_by('periodo')
                elif metric == KPIConfiguracion.Metrica.MAXIMO:
                    agg_prev = grouped_prev.annotate(valor=Max(campo)).order_by('periodo')
                elif metric == KPIConfiguracion.Metrica.MINIMO:
                    agg_prev = grouped_prev.annotate(valor=Min(campo)).order_by('periodo')
                else:
                    agg_prev = grouped_prev.annotate(valor=Count('id')).order_by('periodo')
                cmp_labels = [str(item['periodo']) for item in agg_prev]
                cmp_data = [float(item['valor'] or 0) for item in agg_prev]

            return labels, data, cmp_labels, cmp_data
        else:
            # Futuro: implementar soporte para clientes, servicios, empleados.
            return [], [], [], []