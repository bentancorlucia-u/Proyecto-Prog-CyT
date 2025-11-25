# Proyecto de Búsqueda y Análisis de Productos

Aplicación web en Flask que permite buscar productos por similitud de imagen y visualizar estadísticas básicas sobre el catálogo cargado desde archivos JSON. Incluye scripts utilitarios para procesar y analizar los datos.

## Requisitos
- Python 3.10+
- Dependencias listadas en `requirements.txt` (incluye Flask, Pillow, imagehash, requests).

## Instalación
1. Crear y activar un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\\Scripts\\activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución de la aplicación web
1. Asegúrate de tener los archivos de datos JSON en la carpeta `data/` (ya incluida en el repositorio).
2. Inicia el servidor Flask:
   ```bash
   python app.py
   ```
3. Accede en el navegador a `http://localhost:8080` para usar la búsqueda por imagen o a `http://localhost:8080/analisis` para ver estadísticas de las marcas y productos.

### Funcionalidades principales
- **Búsqueda por imagen**: sube una imagen y se calculan perceptual hashes (`phash`) para encontrar los productos más similares. Las coincidencias incluyen nombre, precio, marca, enlace e imagen de referencia.
- **Panel de análisis**: muestra conteo de productos por marca, precio promedio por marca y los 5 productos más caros.

## Scripts útiles
- `cargar_productos.py`: combina los JSON en `data/`, normaliza precios y genera objetos de producto. Ejecuta `python cargar_productos.py` para exportar un archivo unificado `productos_unificados.json`.
- `analisis_productos.py`: corre análisis en consola (totales por marca, promedios y errores de datos). Ejecuta `python analisis_productos.py`.

## Notas sobre las imágenes
- Las búsquedas por imagen descargan las imágenes de los productos y guardan hashes en caché en el archivo temporal del sistema (`/tmp/product_image_phashes.json`). Usa el flag `force_rebuild=True` en `buscar_por_imagen_phash` si necesitas regenerar el índice.

## Estructura del proyecto
- `app.py`: servidor Flask y rutas web.
- `producto.py`: clases que representan los productos y sus variantes por marca.
- `buscar_por_imagen.py`: lógica de hashing perceptual e indexado de imágenes.
- `analisis_productos.py`: utilidades de análisis de datos.
- `cargar_productos.py`: carga y normalización de productos desde JSON.
- `templates/` y `static/`: recursos para la interfaz web.

