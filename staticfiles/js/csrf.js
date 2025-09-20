// Función para obtener el token CSRF de las cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // ¿Esta cookie tiene el nombre que buscamos?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Configurar el token CSRF para todas las solicitudes AJAX
const csrftoken = getCookie('csrftoken');

// Configurar jQuery AJAX (si jQuery está presente)
if (typeof $ !== 'undefined') {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}

// Configurar Fetch API para incluir el token CSRF
const originalFetch = window.fetch;
window.fetch = function(url, options) {
    options = options || {};
    options.headers = options.headers || {};
    
    // Agregar el token CSRF a todas las solicitudes
    options.headers['X-CSRFToken'] = csrftoken;
    
    // Agregar el encabezado X-Requested-With para identificar solicitudes AJAX
    options.headers['X-Requested-With'] = 'XMLHttpRequest';
    
    return originalFetch(url, options);
};

// Asegurar que el token CSRF esté disponible en la consola para depuración
console.log('CSRF token configurado para solicitudes AJAX');