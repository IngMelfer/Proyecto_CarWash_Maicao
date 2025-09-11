from django.urls import path
from .views_validar import ClienteValidarDirectView

urlpatterns = [
    path('', ClienteValidarDirectView.as_view(), name='cliente_validar_alt'),
]