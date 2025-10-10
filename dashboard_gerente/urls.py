from django.urls import path
from . import views

app_name = 'dashboard_gerente'

urlpatterns = [
    path('', views.DashboardGerenteView.as_view(), name='dashboard'),
    path('kpis/', views.KPIListCreateView.as_view(), name='kpis'),
    path('kpis/<int:pk>/editar/', views.KPIUpdateView.as_view(), name='kpi_editar'),
    path('kpis/<int:pk>/eliminar/', views.KPIDeleteView.as_view(), name='kpi_eliminar'),
    path('kpis/<int:pk>/toggle/', views.KPIToggleActivoView.as_view(), name='kpi_toggle_activo'),
    path('indicadores/', views.IndicadoresView.as_view(), name='indicadores'),
]