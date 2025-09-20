// JavaScript para manejar submenús desplegables en Bootstrap 5
document.addEventListener('DOMContentLoaded', function() {
    // Manejar clics en elementos del submenú
    const dropdownSubmenus = document.querySelectorAll('.dropdown-submenu');
    
    dropdownSubmenus.forEach(function(submenu) {
        const dropdownToggle = submenu.querySelector('.dropdown-toggle');
        const dropdownMenu = submenu.querySelector('.dropdown-menu');
        
        if (dropdownToggle && dropdownMenu) {
            // Prevenir que el clic cierre el menú principal
            dropdownToggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Toggle del submenú
                if (dropdownMenu.style.display === 'block') {
                    dropdownMenu.style.display = 'none';
                } else {
                    // Cerrar otros submenús abiertos
                    document.querySelectorAll('.dropdown-submenu .dropdown-menu').forEach(function(menu) {
                        if (menu !== dropdownMenu) {
                            menu.style.display = 'none';
                        }
                    });
                    
                    dropdownMenu.style.display = 'block';
                }
            });
            
            // Manejar hover para escritorio
            if (window.innerWidth > 767) {
                submenu.addEventListener('mouseenter', function() {
                    dropdownMenu.style.display = 'block';
                });
                
                submenu.addEventListener('mouseleave', function() {
                    dropdownMenu.style.display = 'none';
                });
            }
        }
    });
    
    // Cerrar submenús cuando se hace clic fuera
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown-submenu')) {
            document.querySelectorAll('.dropdown-submenu .dropdown-menu').forEach(function(menu) {
                menu.style.display = 'none';
            });
        }
    });
    
    // Ajustar comportamiento en dispositivos móviles
    function handleResponsive() {
        const isMobile = window.innerWidth <= 767;
        
        dropdownSubmenus.forEach(function(submenu) {
            const dropdownMenu = submenu.querySelector('.dropdown-menu');
            if (dropdownMenu) {
                if (isMobile) {
                    dropdownMenu.style.position = 'static';
                    dropdownMenu.style.float = 'none';
                    dropdownMenu.style.width = 'auto';
                    dropdownMenu.style.marginTop = '0';
                    dropdownMenu.style.backgroundColor = 'transparent';
                    dropdownMenu.style.border = '0';
                    dropdownMenu.style.boxShadow = 'none';
                } else {
                    dropdownMenu.style.position = '';
                    dropdownMenu.style.float = '';
                    dropdownMenu.style.width = '';
                    dropdownMenu.style.marginTop = '';
                    dropdownMenu.style.backgroundColor = '';
                    dropdownMenu.style.border = '';
                    dropdownMenu.style.boxShadow = '';
                }
            }
        });
    }
    
    // Ejecutar al cargar y al redimensionar
    handleResponsive();
    window.addEventListener('resize', handleResponsive);
});