// Script para mejorar la interactividad de los modales
document.addEventListener('DOMContentLoaded', function() {
    // Función para mejorar la interactividad de los modales
    function fixModalInteraction() {
        // Obtener todos los modales
        const modals = document.querySelectorAll('.modal');
        
        // Para cada modal
        modals.forEach(modal => {
            // Forzar que el modal sea interactivo
            modal.style.pointerEvents = 'auto';
            
            // Asegurar que los eventos de mouse funcionen correctamente
            modal.addEventListener('mouseenter', function(e) {
                // Prevenir que el evento se propague a elementos subyacentes
                e.stopPropagation();
                // Forzar que el modal sea interactivo al entrar
                this.style.pointerEvents = 'auto';
                document.body.style.cursor = 'auto';
            });
            
            // Asegurar que el contenido del modal sea interactivo
            const modalContent = modal.querySelector('.modal-content');
            if (modalContent) {
                modalContent.style.pointerEvents = 'auto';
                modalContent.style.cursor = 'auto';
            }
            
            // Asegurar que el diálogo del modal sea interactivo
            const modalDialog = modal.querySelector('.modal-dialog');
            if (modalDialog) {
                modalDialog.style.pointerEvents = 'auto';
                modalDialog.style.cursor = 'auto';
            }
            
            // Asegurar que los botones dentro del modal sean interactivos
            const interactiveElements = modal.querySelectorAll('button, a, .btn, input, select, textarea, .modal-header, .modal-body, .modal-footer');
            interactiveElements.forEach(element => {
                element.style.pointerEvents = 'auto';
                if (element.tagName.toLowerCase() === 'button' || element.tagName.toLowerCase() === 'a' || element.classList.contains('btn')) {
                    element.style.cursor = 'pointer';
                } else {
                    element.style.cursor = 'auto';
                }
                
                // Mejorar la interactividad al pasar el mouse
                element.addEventListener('mouseenter', function(e) {
                    if (element.tagName.toLowerCase() === 'button' || element.tagName.toLowerCase() === 'a' || element.classList.contains('btn')) {
                        this.style.opacity = '0.9';
                    }
                    e.stopPropagation();
                });
                
                element.addEventListener('mouseleave', function(e) {
                    if (element.tagName.toLowerCase() === 'button' || element.tagName.toLowerCase() === 'a' || element.classList.contains('btn')) {
                        this.style.opacity = '1';
                    }
                    e.stopPropagation();
                });
            });
        });
    }
    
    // Ejecutar la función cuando se muestra un modal
    document.body.addEventListener('shown.bs.modal', function() {
        setTimeout(fixModalInteraction, 100); // Pequeño retraso para asegurar que el modal esté completamente cargado
    });
    
    // También ejecutar al cargar la página para modales que ya estén visibles
    fixModalInteraction();
    
    // Ejecutar periódicamente para asegurar que los modales sigan siendo interactivos
    setInterval(fixModalInteraction, 1000);
});