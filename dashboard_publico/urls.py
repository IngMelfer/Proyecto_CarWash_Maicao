from django.urls import path
from . import views

app_name = 'dashboard_publico'

urlpatterns = [
    path('', views.dashboard_publico, name='dashboard_publico'),
]