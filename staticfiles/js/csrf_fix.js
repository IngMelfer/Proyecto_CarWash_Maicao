/**
 * Script para solucionar problemas con CSRF en Django
 * Este script verifica y corrige problemas comunes con tokens CSRF
 * Versión mejorada para resolver problemas específicos con IniciarServicioView
 */

// Función principal para inicializar la corrección de CSRF
function inicializarCorreccionCSRF() {
    console.log('CSRF Fix Script cargado');
    
    // Verificar si la cookie CSRF existe
    const csrftoken = getCookie('csrftoken');
    console.log('Estado de cookie CSRF:', csrftoken ? 'Presente' : 'Ausente');
    
    if (!csrftoken) {
        console.warn('Cookie CSRF no encontrada. Solicitando nuevo token...');
        // Solicitar un nuevo token CSRF
        fetchCSRFToken();
    } else {
        console.log('Cookie CSRF encontrada:', csrftoken.substring(0, 10) + '...');
        // Configurar el token para todas las solicitudes AJAX
        setupAjaxCSRF(csrftoken);
    }
    
    // Verificar todos los formularios POST para asegurar que tienen el token CSRF
    checkAllForms();
    
    // Observar cambios en el DOM para corregir formularios dinámicos
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                // Verificar si se agregaron nuevos formularios
                for (let i = 0; i < mutation.addedNodes.length; i++) {
                    const node = mutation.addedNodes[i];
                    if (node.nodeType === 1) { // ELEMENT_NODE
                        // Si el nodo es un formulario
                        if (node.tagName === 'FORM' && node.method.toLowerCase() === 'post') {
                            let tokenInput = node.querySelector('input[name="csrfmiddlewaretoken"]');
                            if (!tokenInput) {
                                tokenInput = document.createElement('input');
                                tokenInput.type = 'hidden';
                                tokenInput.name = 'csrfmiddlewaretoken';
                                tokenInput.value = getCookie('csrftoken');
                                node.prepend(tokenInput);
                                console.log('Se agregó token CSRF a un formulario dinámico');
                            }
                        }
                        // Si el nodo contiene formularios
                        const forms = node.querySelectorAll('form[method="post"]');
                        if (forms.length > 0) {
                            checkAllForms();
                        }
                    }
                }
            }
        });
    });
    
    // Configurar el observador para observar todo el documento
    observer.observe(document.documentElement, {
        childList: true,
        subtree: true
    });
}

// Ejecutar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', inicializarCorreccionCSRF);

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
    
    // Hacer una solicitud GET a una URL que establezca la cookie CSRF
    fetch('/reservas/csrf-diagnostico/', {
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
                // Configurar el token para todas las solicitudes AJAX
                setupAjaxCSRF(newToken);
                // Actualizar todos los formularios con el nuevo token
                updateAllFormTokens(newToken);
            } else {
                console.error('No se pudo obtener un nuevo token CSRF');
            }
        } else {
            console.error('Error al solicitar token CSRF:', response.status);
        }
    })
    .catch(error => {
        console.error('Error de red al solicitar token CSRF:', error);
    });
}

// Configurar el token CSRF para todas las solicitudes AJAX
function setupAjaxCSRF(token) {
    // Para jQuery (si está disponible)
    if (typeof $ !== 'undefined' && typeof $.ajaxSetup === 'function') {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!(/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", token);
                }
            }
        });
        console.log('Token CSRF configurado para jQuery AJAX');
    } else {
        console.log('jQuery no está disponible o no tiene ajaxSetup');
    }
    
    // Para Fetch API
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        options = options || {};
        options.headers = options.headers || {};
        
        // Solo agregar el token para métodos no seguros
        if (options.method && !['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(options.method.toUpperCase())) {
            options.headers['X-CSRFToken'] = token;
        }
        
        // Asegurar que las credenciales se envíen con la solicitud
        if (!options.credentials) {
            options.credentials = 'same-origin';
        }
        
        return originalFetch(url, options);
    };
    console.log('Token CSRF configurado para Fetch API');
}

// Verificar todos los formularios POST para asegurar que tienen el token CSRF
function checkAllForms() {
    const forms = document.querySelectorAll('form[method="post"]');
    console.log(`Verificando ${forms.length} formularios POST...`);
    
    forms.forEach((form, index) => {
        const csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
        if (!csrfInput) {
            console.warn(`Formulario #${index + 1} (${form.action}) no tiene token CSRF. Añadiendo...`);
            addCSRFTokenToForm(form);
        } else {
            console.log(`Formulario #${index + 1} (${form.action}) tiene token CSRF.`);
        }
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
    } else {
        console.error('No se puede añadir token CSRF al formulario: token no disponible');
    }
}

// Actualizar todos los formularios con el nuevo token
function updateAllFormTokens(token) {
    const forms = document.querySelectorAll('form[method="post"]');
    forms.forEach(form => {
        let csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            csrfInput.value = token;
        } else {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrfmiddlewaretoken';
            input.value = token;
            form.prepend(input);
        }
    });
    console.log(`Tokens CSRF actualizados en ${forms.length} formularios`);
}