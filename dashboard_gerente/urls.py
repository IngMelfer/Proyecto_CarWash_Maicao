from django.urls import path
from . import views

app_name = 'dashboard_gerente'

urlpatterns = [
    path('', views.DashboardGerenteView.as_view(), name='dashboard'),
    path('kpis/', views.KPIListCreateView.as_view(), name='kpis'),
    path('indicadores/', views.IndicadoresView.as_view(), name='indicadores'),
]