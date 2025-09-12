# Guía de Contribución - Premium Car Detailing

## Introducción

Gracias por considerar contribuir a la Plataforma Integral para Autolavados - Premium Car Detailing. Este documento proporciona las pautas y los procesos para contribuir efectivamente al proyecto.

## Flujo de Trabajo con Git

### Ramas

Utilizamos el siguiente esquema de ramas:

- `main`: Rama principal que contiene código estable y listo para producción.
- `develop`: Rama de desarrollo donde se integran las nuevas características.
- `feature/nombre-caracteristica`: Ramas para desarrollar nuevas características.
- `bugfix/nombre-bug`: Ramas para corregir errores.
- `hotfix/nombre-hotfix`: Ramas para correcciones urgentes en producción.

### Proceso de Contribución

1. **Fork y Clone**:
   - Haz un fork del repositorio a tu cuenta de GitHub.
   - Clona tu fork localmente: `git clone https://github.com/TU_USUARIO/Proyecto_CarWash_Maicao.git`

2. **Crea una Rama**:
   - Crea una rama para tu contribución: `git checkout -b feature/tu-caracteristica`

3. **Desarrolla tu Contribución**:
   - Implementa los cambios siguiendo las convenciones de código.
   - Asegúrate de incluir pruebas para nuevas características.

4. **Commit y Push**:
   - Haz commits con mensajes descriptivos: `git commit -m "Añadir: descripción concisa del cambio"`
   - Sube tus cambios: `git push origin feature/tu-caracteristica`

5. **Pull Request**:
   - Crea un Pull Request desde tu rama hacia la rama `develop` del repositorio principal.
   - Describe claramente los cambios realizados y su propósito.

## Convenciones de Código

### Python/Django

- Sigue la guía de estilo [PEP 8](https://www.python.org/dev/peps/pep-0008/).
- Utiliza nombres descriptivos para variables, funciones y clases.
- Documenta el código con docstrings siguiendo el formato de [Google Style Python Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).
- Mantén las funciones pequeñas y con una única responsabilidad.

### HTML/CSS/JavaScript

- Utiliza 2 espacios para la indentación en HTML y CSS.
- Sigue las convenciones de [BEM](http://getbem.com/) para nombrar clases CSS.
- Para JavaScript, sigue la guía de estilo [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript).

## Pruebas

- Todas las nuevas características deben incluir pruebas unitarias.
- Las correcciones de errores deben incluir pruebas que demuestren que el error ha sido solucionado.
- Ejecuta todas las pruebas antes de enviar un Pull Request: `python manage.py test`

## Revisión de Código

- Todos los Pull Requests serán revisados por al menos un miembro del equipo.
- Los comentarios de revisión deben ser constructivos y claros.
- Los Pull Requests deben abordar todos los comentarios antes de ser fusionados.

## Informar Problemas

Si encuentras un error o tienes una sugerencia de mejora:

1. Verifica que el problema no haya sido reportado anteriormente.
2. Crea un nuevo issue con una descripción clara del problema.
3. Incluye pasos para reproducir el error, si es aplicable.
4. Añade capturas de pantalla o registros si es posible.

## Contacto

Si tienes preguntas sobre el proceso de contribución, puedes contactar al equipo de desarrollo a través de los issues de GitHub.

¡Gracias por contribuir a mejorar Premium Car Detailing!