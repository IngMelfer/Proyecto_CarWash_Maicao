/**
 * Script específico para solucionar problemas de CSRF en el formulario de iniciar servicio
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Iniciar Servicio Fix Script cargado');
    
    // Buscar todos los formularios de iniciar servicio
    const formulariosIniciarServicio = document.querySelectorAll('form[action*="iniciar-servicio"]');
    console.log(`Encontrados ${formulariosIniciarServicio.length} formularios de iniciar servicio`);
    
    formulariosIniciarServicio.forEach((form, index) => {
        console.log(`Procesando formulario de iniciar servicio #${index + 1}`);
        
        // Verificar si ya tiene el token CSRF
        let csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
        if (!csrfInput) {
            console.warn(`Formulario #${index + 1} no tiene token CSRF. Añadiendo...`);
            addCSRFTokenToForm(form);
        } else {
            console.log(`Formulario #${index + 1} ya tiene token CSRF: ${csrfInput.value.substring(0, 10)}...`);
        }
        
        // Reemplazar el evento submit del formulario para asegurar que el token CSRF esté presente
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Verificar si tenemos la cookie CSRF
            const csrftoken = getCookie('csrftoken');
            if (!csrftoken) {
                console.error('No se encontró token CSRF. Solicitando nuevo token...');
                fetchCSRFToken().then(() => {
                    // Intentar enviar el formulario de nuevo después de obtener el token
                    setTimeout(() => {
                        submitFormWithCSRF(form);
                    }, 300);
                });
            } else {
                submitFormWithCSRF(form);
            }
        });
    });
});

// Función para obtener cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Función para solicitar un nuevo token CSRF
function fetchCSRFToken() {
    console.log('Solicitando nuevo token CSRF...');
    
    return fetch('/reservas/csrf-diagnostico/', {
        method: 'GET',
        credentials: 'same-origin',  // Importante para que las cookies se envíen/reciban
    })
    .then(response => {
        if (response.ok) {
            console.log('Solicitud de token CSRF exitosa');
            // Verificar si ahora tenemos la cookie
            const newToken = getCookie('csrftoken');
            if (newToken) {
                console.log('Nuevo token CSRF obtenido:', newToken.substring(0, 10) + '...');
                return true;
            } else {
                console.error('No se pudo obtener un nuevo token CSRF');
                return false;
            }
        } else {
            console.error('Error al solicitar token CSRF:', response.status);
            return false;
        }
    })
    .catch(error => {
        console.error('Error de red al solicitar token CSRF:', error);
        return false;
    });
}

// Añadir token CSRF a un formulario
function addCSRFTokenToForm(form) {
    const token = getCookie('csrftoken');
    if (token) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'csrfmiddlewaretoken';
        input.value = token;
        form.prepend(input);
        console.log('Token CSRF añadido al formulario');
        return true;
    } else {
        console.error('No se puede añadir token CSRF al formulario: token no disponible');
        return false;
    }
}

// Enviar formulario con CSRF
function submitFormWithCSRF(form) {
    // Asegurarse de que el formulario tenga el token CSRF actualizado
    let csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
    const currentToken = getCookie('csrftoken');
    
    if (!csrfInput) {
        // Si no existe el input, crearlo
        if (!addCSRFTokenToForm(form)) {
            console.error('No se pudo enviar el formulario: no se pudo añadir el token CSRF');
            return;
        }
    } else if (currentToken && csrfInput.value !== currentToken) {
        // Si el token ha cambiado, actualizarlo
        csrfInput.value = currentToken;
        console.log('Token CSRF actualizado en el formulario');
    }
    
    // Enviar el formulario
    console.log('Enviando formulario con token CSRF...');
    form.submit();
}