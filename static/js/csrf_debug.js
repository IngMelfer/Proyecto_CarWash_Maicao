// Script de diagnóstico y corrección para problemas CSRF

// Función para mostrar todas las cookies disponibles
function mostrarCookies() {
    console.log('=== Diagnóstico de Cookies CSRF ===');
    console.log('Todas las cookies disponibles:');
    
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        cookies.forEach((cookie, index) => {
            console.log(`${index + 1}. ${cookie.trim()}`);
        });
    } else {
        console.log('No hay cookies disponibles');
    }
    
    // Verificar específicamente la cookie CSRF
    const csrfCookie = getCookie('csrftoken');
    console.log('\nEstado de la cookie CSRF:');
    console.log(csrfCookie ? `Cookie CSRF encontrada: ${csrfCookie.substring(0, 10)}...` : 'Cookie CSRF NO encontrada');
    
    // Verificar la configuración SameSite
    console.log('\nVerificación de configuración SameSite:');
    console.log('SameSite=Lax en settings.py: ' + (document.cookie.includes('SameSite=Lax') ? 'Sí' : 'No'));
    
    // Verificar si estamos en un iframe (posible problema de cookies de terceros)
    console.log('\nVerificación de iframe:');
    console.log('La página está en un iframe: ' + (window.self !== window.top ? 'Sí' : 'No'));
    
    return csrfCookie !== null;
}

// Función para verificar los tokens CSRF en los formularios
function verificarFormularios() {
    console.log('\n=== Verificación de Formularios ===');
    const forms = document.querySelectorAll('form');
    
    console.log(`Total de formularios encontrados: ${forms.length}`);
    
    forms.forEach((form, index) => {
        const method = form.method.toUpperCase();
        const action = form.action;
        const csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
        
        console.log(`\nFormulario #${index + 1}:`);
        console.log(`- Método: ${method}`);
        console.log(`- Acción: ${action}`);
        console.log(`- Token CSRF: ${csrfInput ? 'Presente' : 'AUSENTE'}`);
        
        if (method === 'POST' && !csrfInput) {
            console.error(`⚠️ ADVERTENCIA: Formulario POST sin token CSRF: ${action}`);
        }
    });
}

// Función para regenerar el token CSRF
async function regenerarTokenCSRF() {
    console.log('Intentando regenerar token CSRF...');
    try {
        // Hacer una solicitud GET a la vista de diagnóstico CSRF
        const response = await fetch('/reservas/csrf-diagnostico/', {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            console.log('Solicitud para regenerar token CSRF completada');
            // Verificar si ahora tenemos la cookie
            setTimeout(() => {
                const tenemosCookie = mostrarCookies();
                console.log('Después de regenerar, cookie CSRF:', tenemosCookie ? 'Presente' : 'Aún ausente');
                
                // Si tenemos la cookie, actualizar los formularios
                if (tenemosCookie) {
                    actualizarFormulariosCSRF();
                }
            }, 500); // Pequeño retraso para asegurar que la cookie se haya establecido
            return true;
        } else {
            console.error('Error al regenerar token CSRF:', response.status);
            return false;
        }
    } catch (error) {
        console.error('Error de red al regenerar token CSRF:', error);
        return false;
    }
}

// Función para actualizar los tokens CSRF en todos los formularios
function actualizarFormulariosCSRF() {
    const csrftoken = getCookie('csrftoken');
    if (!csrftoken) {
        console.error('No se puede actualizar formularios: Token CSRF no disponible');
        return false;
    }
    
    // Actualizar todos los formularios POST
    const forms = document.querySelectorAll('form[method="post"]');
    let actualizados = 0;
    
    forms.forEach(form => {
        let tokenInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
        
        // Si no existe el campo, crearlo
        if (!tokenInput) {
            tokenInput = document.createElement('input');
            tokenInput.type = 'hidden';
            tokenInput.name = 'csrfmiddlewaretoken';
            form.prepend(tokenInput);
        }
        
        // Actualizar el valor del token
        tokenInput.value = csrftoken;
        actualizados++;
    });
    
    console.log(`Formularios actualizados con nuevo token CSRF: ${actualizados}`);
    return true;
}

// Función para configurar AJAX con el token CSRF
function configurarAJAXConCSRF() {
    // Para jQuery (si está disponible)
    if (typeof $ !== 'undefined') {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain) {
                    const csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        console.log('jQuery AJAX configurado con token CSRF');
    }
    
    // Para Fetch API (interceptar solicitudes)
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        // Solo para solicitudes que no sean GET, HEAD, etc.
        if (options.method && !['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(options.method.toUpperCase())) {
            if (!options.headers) {
                options.headers = {};
            }
            
            // Si headers es un objeto Headers, usamos set
            if (options.headers instanceof Headers) {
                if (!options.headers.has('X-CSRFToken')) {
                    const csrftoken = getCookie('csrftoken');
                    options.headers.set('X-CSRFToken', csrftoken);
                }
            } 
            // Si es un objeto plano
            else {
                if (!options.headers['X-CSRFToken']) {
                    const csrftoken = getCookie('csrftoken');
                    options.headers['X-CSRFToken'] = csrftoken;
                }
            }
            
            // Asegurar que se envían las credenciales
            if (options.credentials === undefined) {
                options.credentials = 'same-origin';
            }
        }
        return originalFetch(url, options);
    };
    console.log('Fetch API configurada con token CSRF');
}

// Función principal para inicializar el diagnóstico CSRF
async function inicializarDiagnosticoCSRF() {
    console.log('Iniciando diagnóstico CSRF...');
    
    // Verificar si tenemos la cookie CSRF
    const tenemosCookie = mostrarCookies();
    verificarFormularios();
    
    // Si no tenemos la cookie, intentar regenerarla
    if (!tenemosCookie) {
        console.warn('Cookie CSRF no encontrada, intentando regenerar...');
        await regenerarTokenCSRF();
    } else {
        // Si tenemos la cookie, actualizar los formularios por si acaso
        actualizarFormulariosCSRF();
    }
    
    // Configurar AJAX con el token CSRF
    configurarAJAXConCSRF();
    
    console.log('\nDiagnóstico CSRF completado.');
}

// Ejecutar diagnóstico cuando la página esté cargada
document.addEventListener('DOMContentLoaded', inicializarDiagnosticoCSRF);

// Función auxiliar para obtener cookies (copia de csrf.js)
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

// Exportar funciones para uso externo
window.csrfDebug = {
    mostrarCookies,
    verificarFormularios,
    regenerarTokenCSRF,
    actualizarFormulariosCSRF,
    inicializarDiagnosticoCSRF
};