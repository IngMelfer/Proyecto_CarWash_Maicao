// Funcionalidad para mostrar detalles del lavador en modal
document.addEventListener('DOMContentLoaded', function() {
    // Botones para ver detalles del lavador
    const verDetallesBtns = document.querySelectorAll('.ver-detalles-lavador');
    const lavadorDetallesModal = document.getElementById('lavadorDetallesModal');
    const seleccionarLavadorBtn = document.getElementById('seleccionarLavadorBtn');
    
    // Elementos del modal
    const lavadorDetallesCargando = document.getElementById('lavadorDetallesCargando');
    const lavadorDetallesContenido = document.getElementById('lavadorDetallesContenido');
    const lavadorDetallesError = document.getElementById('lavadorDetallesError');
    const lavadorDetallesErrorMensaje = document.getElementById('lavadorDetallesErrorMensaje');
    
    // Elementos para mostrar información del lavador
    const lavadorFoto = document.getElementById('lavadorFoto');
    const lavadorNombre = document.getElementById('lavadorNombre');
    const lavadorCargo = document.getElementById('lavadorCargo');
    const lavadorCalificacion = document.getElementById('lavadorCalificacion');
    const lavadorExperiencia = document.getElementById('lavadorExperiencia');
    const lavadorTotalCalificaciones = document.getElementById('lavadorTotalCalificaciones');
    const lavadorCalificacionesLista = document.getElementById('lavadorCalificacionesLista');
    
    // Variable para almacenar el ID del lavador seleccionado
    let lavadorSeleccionadoId = null;
    
    // Agregar evento click a los botones de ver detalles
    verDetallesBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const lavadorId = this.dataset.lavadorId;
            cargarDetallesLavador(lavadorId);
        });
    });
    
    // Evento para seleccionar el lavador desde el modal
    if (seleccionarLavadorBtn) {
        seleccionarLavadorBtn.addEventListener('click', function() {
            if (lavadorSeleccionadoId) {
                // Seleccionar el radio button correspondiente
                const radioBtn = document.querySelector(`#lavador${lavadorSeleccionadoId}`);
                if (radioBtn) {
                    radioBtn.checked = true;
                    
                    // Actualizar estilos de la tarjeta
                    const lavadorCards = document.querySelectorAll('.lavador-card');
                    lavadorCards.forEach(card => card.classList.remove('border-primary'));
                    document.querySelector(`.lavador-card[data-lavador-id="${lavadorSeleccionadoId}"]`).classList.add('border-primary');
                    
                    // Actualizar el campo oculto
                    document.querySelector('#lavadorInput').value = lavadorSeleccionadoId;
                    
                    // Cerrar el modal
                    const modalInstance = bootstrap.Modal.getInstance(lavadorDetallesModal);
                    modalInstance.hide();
                }
            }
        });
    }
    
    // Función para cargar los detalles del lavador
    function cargarDetallesLavador(lavadorId) {
        // Guardar el ID del lavador seleccionado
        lavadorSeleccionadoId = lavadorId;
        
        // Mostrar el modal con estado de carga
        lavadorDetallesCargando.style.display = 'block';
        lavadorDetallesContenido.style.display = 'none';
        lavadorDetallesError.style.display = 'none';
        
        // Realizar petición AJAX para obtener los detalles del lavador
        fetch(`/api/lavadores/${lavadorId}/detalles/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Ocultar cargando y mostrar contenido
                lavadorDetallesCargando.style.display = 'none';
                lavadorDetallesContenido.style.display = 'block';
                
                // Mostrar foto del lavador
                if (data.fotografia) {
                    lavadorFoto.innerHTML = `<img src="${data.fotografia}" alt="${data.nombre_completo}" class="rounded-circle" width="100" height="100">`;
                } else {
                    lavadorFoto.innerHTML = `<i class="fas fa-user-circle fa-5x text-secondary"></i>`;
                }
                
                // Mostrar información básica
                lavadorNombre.textContent = data.nombre_completo;
                lavadorCargo.textContent = data.cargo;
                
                // Mostrar calificación con estrellas
                const calificacion = parseFloat(data.promedio_calificacion) || 0;
                let estrellas = '';
                for (let i = 1; i <= 5; i++) {
                    if (i <= Math.floor(calificacion)) {
                        estrellas += '<i class="fas fa-star text-warning"></i>';
                    } else if (i - 0.5 <= calificacion) {
                        estrellas += '<i class="fas fa-star-half-alt text-warning"></i>';
                    } else {
                        estrellas += '<i class="far fa-star text-warning"></i>';
                    }
                }
                lavadorCalificacion.innerHTML = `${estrellas} <span class="ms-1">(${calificacion.toFixed(1)})</span>`;
                
                // Mostrar experiencia y total de calificaciones
                lavadorExperiencia.textContent = data.experiencia || 'No disponible';
                lavadorTotalCalificaciones.textContent = data.total_calificaciones || '0';
                
                // Mostrar últimas calificaciones
                lavadorCalificacionesLista.innerHTML = '';
                if (data.ultimas_calificaciones && data.ultimas_calificaciones.length > 0) {
                    data.ultimas_calificaciones.forEach(calificacion => {
                        // Crear estrellas para esta calificación
                        let estrellasCal = '';
                        for (let i = 1; i <= 5; i++) {
                            if (i <= calificacion.puntuacion) {
                                estrellasCal += '<i class="fas fa-star text-warning"></i>';
                            } else {
                                estrellasCal += '<i class="far fa-star text-warning"></i>';
                            }
                        }
                        
                        // Crear elemento para la calificación
                        const calificacionItem = document.createElement('div');
                        calificacionItem.className = 'mb-3 pb-3 border-bottom';
                        calificacionItem.innerHTML = `
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <div>${estrellasCal}</div>
                                <small class="text-muted">${calificacion.fecha}</small>
                            </div>
                            <p class="mb-0">${calificacion.comentario || 'Sin comentario'}</p>
                        `;
                        lavadorCalificacionesLista.appendChild(calificacionItem);
                    });
                } else {
                    lavadorCalificacionesLista.innerHTML = '<div class="alert alert-info">Este lavador aún no tiene calificaciones.</div>';
                }
            })
            .catch(error => {
                console.error('Error al cargar detalles del lavador:', error);
                lavadorDetallesCargando.style.display = 'none';
                lavadorDetallesError.style.display = 'block';
                lavadorDetallesErrorMensaje.textContent = 'No se pudieron cargar los detalles del lavador. Por favor, inténtalo de nuevo más tarde.';
            });
    }
});