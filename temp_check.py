from reservas.models import Reserva
from clientes.models import Cliente

cliente = Cliente.objects.first()
print('Cliente:', cliente)

en_proceso = Reserva.objects.filter(cliente=cliente, estado=Reserva.EN_PROCESO).select_related('servicio')
print('Reservas en proceso:', en_proceso.count())

for r in en_proceso:
    print(f'  ID: {r.id}, Estado: {r.estado}, Servicio: {r.servicio.nombre}')