# Horizonte — demo local en Python

## Iniciar

Desde esta carpeta:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Abrir **http://127.0.0.1:5000/**. Flask sirve las plantillas y los recursos;
Apache/XAMPP no ejecuta esta aplicación. Para detenerla: `Ctrl + C`.

La recarga automática de Python y de las plantillas está activada. Después de
guardar un cambio, actualiza el navegador con `F5`. Los recursos de esta demo
se sirven sin almacenamiento en caché. El navegador no se actualiza por sí solo.

## Archivos

- `app.py`: rutas, validación del formulario y configuración de logos.
- `storage.py`: escritura de visitante y referencia en un TXT.
- `templates/base.html`: estructura compartida.
- `templates/index.html`: formulario y carrusel.
- `templates/gracias.html`: agradecimiento después de guardar.
- `static/css/styles.css`: estilos.
- `static/js/demo.js`: carrusel y contador visual de 30 segundos.
- `static/img/logos/`: imágenes reemplazables.

## Cambiar logos

Copia tus imágenes de demostración a `static/img/logos/` con estos nombres:

- `logo-principal.png`: panel de escritorio.
- `logo-secundario.png`: formulario móvil y agradecimiento.

También se aceptan las extensiones `.webp`, `.jpg`, `.jpeg` y `.svg`.
No cambies la extensión de una imagen para convertirla: conserva su formato real.
Al actualizar la página se detecta el archivo automáticamente; los PNG tienen
prioridad sobre WebP, JPG, JPEG y los SVG de ejemplo, en ese orden.
Las URLs incluyen la fecha de modificación para actualizar la imagen en caché.

Si prefieres otro nombre base, puedes editar la configuración de `app.py`:

```python
LOGO_PRINCIPAL="img/logos/logo-principal.svg",
LOGO_SECUNDARIO="img/logos/logo-secundario.svg",
```

Los atributos `src` de las plantillas reciben las imágenes detectadas.
Ajusta también el texto `alt` en las plantillas para describir tu marca.
En móvil se muestra directamente el formulario debajo del contador.

## Datos de prueba

El formulario acepta únicamente un alias de visitante (máximo 60 caracteres)
y una referencia inventada (máximo 40). Al pulsar **Continuar**, guarda y
redirige a `/gracias`; actualizar esa página no vuelve a enviar el formulario.
La casilla animada es decorativa y el contador se detiene al llegar a cero.

El TXT se crea al recibir el primer envío válido en:

```text
%LOCALAPPDATA%\HorizonteDemo\datos_prueba.txt
```

Se almacena fuera de `htdocs` para que Apache no lo publique. Python imprime
la ruta exacta al arrancar. Cada línea es un objeto JSON de texto legible:

```json
{"visitante": "Visitante de prueba", "referencia": "DEMO-001"}
```

El archivo es texto plano, sin cifrado, destinado a datos ficticios.
El backend valida tamaños y campos, escapa los valores al mostrar errores y
comprueba un token de formulario. No guarda IP, navegador ni la casilla animada.

## Comprobaciones

```powershell
python -m unittest discover -s tests -v
```

Las pruebas usan una carpeta temporal y no escriben en el TXT de la aplicación.
