// Verificar que jQuery esté disponible antes de ejecutar el código
if (typeof $ !== 'undefined' && typeof $.fn !== 'undefined') {
    $(document).ready(function() {
        // Variables globales para almacenar la información de la reserva
        let reservaData = {
            servicio_id: null,
            servicio_nombre: '',
            fecha: '',
            hora_id: '',
            bahia_id: null,
            bahia_nombre: '',
            lavador_id: null,
            lavador_nombre: '',
            vehiculo_id: null,
            vehiculo_placa: '',
            medio_pago_id: null,
            medio_pago_nombre: '',
            precio: 0
        };
        
        // Hacer reservaData accesible globalmente para sincronización
        window.reservaData = reservaData;

        // Token CSRF para peticiones AJAX
        const csrftoken = $('input[name="csrfmiddlewaretoken"]').val();

        // Configuración para incluir el token CSRF en todas las peticiones AJAX
        if (typeof $.ajaxSetup === 'function') {
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });
        }
    
    // Inicializar el botón nextToStep2 para que funcione con la selección de servicio
    $('#nextToStep2').click(function() {
        // Verificar si se ha seleccionado un servicio
        if (!reservaData.servicio) {
            mostrarError('Por favor, seleccione un servicio antes de continuar.');
            return;
        }
        
        // Cambiar al paso 2
        cambiarPaso(1, 2);
    });

    // Función para mostrar mensajes de error
    function mostrarError(mensaje) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: mensaje,
            confirmButtonText: 'Aceptar'
        });
    }

    // Función para mostrar mensajes de éxito
    function mostrarExito(mensaje) {
        Swal.fire({
            icon: 'success',
            title: 'Éxito',
            text: mensaje,
            confirmButtonText: 'Aceptar'
        });
    }

    // Función para cambiar entre pasos
    function cambiarPaso(pasoActual, pasoSiguiente) {
        // Ocultar paso actual
        $(`#step${pasoActual}`).removeClass('active');
        $(`#step${pasoActual}-indicator`).removeClass('active');
        
        // Mostrar paso siguiente
        $(`#step${pasoSiguiente}`).addClass('active');
        $(`#step${pasoSiguiente}-indicator`).addClass('active');
        
        // Si es el paso 2, cargar horarios disponibles si ya hay fecha seleccionada
        if (pasoSiguiente === 2 && $('#fecha').val()) {
            cargarHorariosDisponibles($('#fecha').val());
        }
    }

    // Paso 1: Selección de servicio
    $(document).on('click', '.seleccionar-servicio', function() {
        const servicioCard = $(this).closest('.servicio-card');
        const servicioId = servicioCard.data('id');
        const servicioPrecio = servicioCard.data('precio');
        const servicioNombre = servicioCard.find('.card-title').text();
        
        // Guardar datos del servicio
        reservaData.servicio = servicioId;
        reservaData.servicio_nombre = servicioNombre;
        reservaData.precio = servicioPrecio;
        
        // Actualizar resumen
        $('#resumen-servicio').text(servicioNombre);
        $('#resumen-precio').text(servicioPrecio);
        
        // Cambiar al paso 2
        cambiarPaso(1, 2);
    });

    // Paso 2: Selección de fecha y hora
    $('#fecha').change(function() {
        const fecha = $(this).val();
        if (fecha) {
            reservaData.fecha = fecha;
            cargarHorariosDisponibles(fecha);
        }
    });

    // Función para cargar horarios disponibles según la fecha
    function cargarHorariosDisponibles(fecha) {
        $.ajax({
            url: '/reservas/api/horarios-disponibles/',
            type: 'POST',
            data: {
                fecha: fecha,
                servicio_id: reservaData.servicio
            },
            success: function(response) {
                if (response.horarios && response.horarios.length > 0) {
                    mostrarHorariosDisponibles(response.horarios);
                } else {
                    $('#horarios-container').html('<div class="alert alert-warning">No hay horarios disponibles para esta fecha.</div>');
                }
            },
            error: function(error) {
                mostrarError('Error al cargar los horarios disponibles. Por favor, intente nuevamente.');
                console.error('Error al cargar horarios:', error);
            }
        });
    }

    // Función para mostrar los horarios disponibles
    function mostrarHorariosDisponibles(horarios) {
        let html = '<h4>Horarios disponibles</h4>';
        html += '<div class="row row-cols-2 row-cols-md-4 g-3">';
        
        horarios.forEach(function(horario) {
            html += `
                <div class="col">
                    <div class="card h-100 horario-card" data-hora="${horario.hora}">
                        <div class="card-body text-center">
                            <h5 class="card-title">${horario.hora_formateada}</h5>
                            <p class="card-text">${horario.bahias_disponibles} bahías disponibles</p>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-primary w-100 seleccionar-horario">Seleccionar</button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        $('#horarios-container').html(html);
    }

    // Selección de horario
    $(document).on('click', '.seleccionar-horario', function() {
        const horarioCard = $(this).closest('.horario-card');
        const hora = horarioCard.data('hora');
        
        // Guardar hora seleccionada
        reservaData.hora = hora;
        
        // Actualizar resumen
        $('#resumen-fecha').text(reservaData.fecha);
        $('#resumen-hora').text(hora);
        
        // Cargar bahías disponibles para esta hora
        cargarBahiasDisponibles(reservaData.fecha, hora);
    });

    // Función para cargar bahías disponibles según fecha y hora
    function cargarBahiasDisponibles(fecha, hora) {
        $.ajax({
            url: '/reservas/api/bahias-disponibles/',
            type: 'POST',
            data: {
                fecha: fecha,
                hora: hora,
                servicio_id: reservaData.servicio
            },
            success: function(response) {
                if (response.bahias && response.bahias.length > 0) {
                    mostrarBahiasDisponibles(response.bahias);
                } else {
                    $('#bahias-container').html('<div class="alert alert-warning">No hay bahías disponibles para este horario.</div>');
                }
            },
            error: function(error) {
                mostrarError('Error al cargar las bahías disponibles. Por favor, intente nuevamente.');
                console.error('Error al cargar bahías:', error);
            }
        });
    }

    // Función para mostrar las bahías disponibles
    function mostrarBahiasDisponibles(bahias) {
        let html = '<h4 class="mt-4">Bahías disponibles</h4>';
        html += '<div class="row row-cols-1 row-cols-md-3 g-3">';
        
        bahias.forEach(function(bahia) {
            html += `
                <div class="col">
                    <div class="card h-100 bahia-card" data-id="${bahia.id}" data-nombre="${bahia.nombre}">
                        <div class="card-body">
                            <h5 class="card-title">${bahia.nombre}</h5>
                            <p class="card-text">${bahia.descripcion || 'Sin descripción'}</p>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-primary w-100 seleccionar-bahia">Seleccionar</button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        $('#bahias-container').html(html);
    }

    // Selección de bahía
    $(document).on('click', '.seleccionar-bahia', function() {
        const bahiaCard = $(this).closest('.bahia-card');
        const bahiaId = bahiaCard.data('id');
        const bahiaNombre = bahiaCard.data('nombre');
        
        // Guardar bahía seleccionada
        reservaData.bahia = bahiaId;
        reservaData.bahia_nombre = bahiaNombre;
        
        // Actualizar resumen
        $('#resumen-bahia').text(bahiaNombre);
        
        // Cargar lavadores disponibles para esta bahía, fecha y hora
        cargarLavadoresDisponibles(reservaData.fecha, reservaData.hora, bahiaId);
    });

    // Función para cargar lavadores disponibles
    function cargarLavadoresDisponibles(fecha, hora, bahiaId) {
        $.ajax({
            url: '/reservas/api/lavadores-disponibles/',
            type: 'POST',
            data: {
                fecha: fecha,
                hora: hora,
                bahia_id: bahiaId
            },
            success: function(response) {
                if (response.lavadores && response.lavadores.length > 0) {
                    mostrarLavadoresDisponibles(response.lavadores);
                } else {
                    $('#lavadores-container').html('<div class="alert alert-warning">No hay lavadores disponibles para este horario y bahía.</div>');
                }
            },
            error: function(error) {
                mostrarError('Error al cargar los lavadores disponibles. Por favor, intente nuevamente.');
                console.error('Error al cargar lavadores:', error);
            }
        });
    }

    // Función para mostrar los lavadores disponibles
    function mostrarLavadoresDisponibles(lavadores) {
        let html = '<h4 class="mt-4">Lavadores disponibles</h4>';
        html += '<div class="row row-cols-1 row-cols-md-3 g-3">';
        
        lavadores.forEach(function(lavador) {
            html += `
                <div class="col">
                    <div class="card h-100 lavador-card" data-id="${lavador.id}" data-nombre="${lavador.nombre}">
                        <div class="card-body">
                            <h5 class="card-title">${lavador.nombre} ${lavador.apellido}</h5>
                            <div class="rating">
                                ${generarEstrellas(lavador.calificacion)}
                            </div>
                            <button class="btn btn-sm btn-outline-info mt-2 ver-detalles-lavador" data-id="${lavador.id}">
                                Ver detalles
                            </button>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-primary w-100 seleccionar-lavador">Seleccionar</button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        $('#lavadores-container').html(html);
        
        // Cambiar al paso 3 después de mostrar los lavadores
        cambiarPaso(2, 3);
    }

    // Función para generar estrellas según calificación
    function generarEstrellas(calificacion) {
        let estrellas = '';
        for (let i = 1; i <= 5; i++) {
            if (i <= calificacion) {
                estrellas += '<i class="fas fa-star text-warning"></i>';
            } else if (i - 0.5 <= calificacion) {
                estrellas += '<i class="fas fa-star-half-alt text-warning"></i>';
            } else {
                estrellas += '<i class="far fa-star text-warning"></i>';
            }
        }
        return estrellas;
    }

    // Ver detalles del lavador
    $(document).on('click', '.ver-detalles-lavador', function() {
        const lavadorId = $(this).data('id');
        
        $.ajax({
            url: `/reservas/api/lavador/${lavadorId}/`,
            type: 'GET',
            success: function(response) {
                if (response.lavador) {
                    mostrarDetallesLavador(response.lavador);
                }
            },
            error: function(error) {
                mostrarError('Error al cargar los detalles del lavador.');
                console.error('Error al cargar detalles del lavador:', error);
            }
        });
    });

    // Función para mostrar detalles del lavador en el modal
    function mostrarDetallesLavador(lavador) {
        $('#modalLavadorTitle').text(`${lavador.nombre} ${lavador.apellido}`);
        
        let contenido = `
            <div class="text-center mb-3">
                <img src="${lavador.foto || '/static/img/default-user.png'}" alt="${lavador.nombre}" class="img-fluid rounded-circle" style="max-width: 150px;">
            </div>
            <div class="rating text-center mb-3">
                ${generarEstrellas(lavador.calificacion)}
                <span class="ms-2">(${lavador.calificacion.toFixed(1)})</span>
            </div>
            <p><strong>Experiencia:</strong> ${lavador.experiencia || 'No especificada'}</p>
            <p><strong>Especialidad:</strong> ${lavador.especialidad || 'No especificada'}</p>
            
            <h5 class="mt-4">Comentarios recientes</h5>
        `;
        
        if (lavador.comentarios && lavador.comentarios.length > 0) {
            lavador.comentarios.forEach(function(comentario) {
                contenido += `
                    <div class="card mb-2">
                        <div class="card-body">
                            <div class="d-flex justify-content-between">
                                <h6 class="card-subtitle mb-2 text-muted">${comentario.cliente}</h6>
                                <div class="rating">
                                    ${generarEstrellas(comentario.calificacion)}
                                </div>
                            </div>
                            <p class="card-text">${comentario.texto}</p>
                            <small class="text-muted">${comentario.fecha}</small>
                        </div>
                    </div>
                `;
            });
        } else {
            contenido += '<p class="text-muted">No hay comentarios disponibles.</p>';
        }
        
        $('#modalLavadorContent').html(contenido);
        $('#modalLavador').modal('show');
    }

    // Selección de lavador
    $(document).on('click', '.seleccionar-lavador', function() {
        const lavadorCard = $(this).closest('.lavador-card');
        const lavadorId = lavadorCard.data('id');
        const lavadorNombre = lavadorCard.data('nombre');
        
        // Guardar lavador seleccionado
        reservaData.lavador = lavadorId;
        reservaData.lavador_nombre = lavadorNombre;
        
        // Actualizar resumen
        $('#resumen-lavador').text(lavadorNombre);
        
        // Cambiar al paso 3 (selección de vehículo)
        cambiarPaso(2, 3);
    });

    // Botones de navegación entre pasos
    $('#backToStep1').click(function() {
        cambiarPaso(2, 1);
    });

    $('#backToStep2').click(function() {
        cambiarPaso(3, 2);
    });

    $('#backToStep3').click(function() {
        cambiarPaso(4, 3);
    });

    $('#backToStep4').click(function() {
        cambiarPaso(5, 4);
    });

    $('#nextToStep3').click(function() {
        // Validar que se haya seleccionado fecha, hora, bahía y lavador
        if (!reservaData.fecha || !reservaData.hora || !reservaData.bahia || !reservaData.lavador) {
            mostrarError('Por favor, seleccione fecha, hora, bahía y lavador antes de continuar.');
            return;
        }
        
        cambiarPaso(2, 3);
    });

    $('#nextToStep4').click(function() {
        // Validar que se haya seleccionado un vehículo
        const vehiculoId = $('#vehiculo').val();
        if (!vehiculoId) {
            mostrarError('Por favor, seleccione un vehículo antes de continuar.');
            return;
        }
        
        // Guardar vehículo seleccionado
        reservaData.vehiculo = vehiculoId;
        const vehiculoText = $('#vehiculo option:selected').text();
        reservaData.vehiculo_nombre = vehiculoText;
        
        // Actualizar resumen
        $('#resumen-vehiculo').text(vehiculoText);
        
        cambiarPaso(3, 4);
    });

    $('#nextToStep5').click(function() {
        // Validar que se haya seleccionado un medio de pago
        if (!reservaData.medio_pago) {
            mostrarError('Por favor, seleccione un medio de pago antes de continuar.');
            return;
        }
        
        cambiarPaso(4, 5);
    });

    // Paso 4: Selección de medio de pago
    $(document).on('click', '.seleccionar-medio-pago', function() {
        const medioPagoCard = $(this).closest('.medio-pago-card');
        const medioPagoId = medioPagoCard.data('id');
        const medioPagoNombre = medioPagoCard.find('.card-title').text();
        
        // Guardar medio de pago seleccionado
        reservaData.medio_pago = medioPagoId;
        reservaData.medio_pago_nombre = medioPagoNombre;
        
        // Actualizar resumen
        $('#resumen-medio-pago').text(medioPagoNombre);
    });

    // Paso 5: Confirmación de reserva
    $('#confirmarReserva').click(function() {
        // Validar que todos los datos necesarios estén completos
        if (!reservaData.servicio || !reservaData.fecha || !reservaData.hora || 
            !reservaData.bahia || !reservaData.lavador || !reservaData.vehiculo || 
            !reservaData.medio_pago) {
            mostrarError('Por favor, complete todos los campos requeridos antes de confirmar la reserva.');
            return;
        }
        
        // Enviar datos de la reserva al servidor
        $.ajax({
            url: '/reservas/api/crear-reserva/',
            type: 'POST',
            data: reservaData,
            success: function(response) {
                if (response.success) {
                    mostrarExito('¡Reserva creada exitosamente!');
                    
                    // Redirigir a la página de comprobante
                    setTimeout(function() {
                        window.location.href = `/reservas/comprobante/${response.reserva_id}/`;
                    }, 2000);
                } else {
                    mostrarError(response.error || 'Error al crear la reserva. Por favor, intente nuevamente.');
                }
            },
            error: function(error) {
                mostrarError('Error al procesar la reserva. Por favor, intente nuevamente.');
                console.error('Error al crear reserva:', error);
            }
        });
    });
    }); // Cierre de $(document).ready
} else {
    console.error('jQuery no está disponible. El formulario de reserva no funcionará correctamente.');
}