# Proyecto de Búsqueda y Análisis de Productos

Aplicación web en Flask para buscar productos por similitud de imagen y visualizar estadísticas básicas sobre el catálogo cargado desde archivos JSON. Incluye scripts utilitarios para procesar y analizar los datos.

## Requisitos
- Python 3.10+
- Dependencias listadas en `requirements.txt` (Flask, Pillow, imagehash, requests, entre otras)

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
1. Verifica que los archivos de datos JSON estén en la carpeta `data/` (incluida en el repositorio).
2. Inicia el servidor Flask:
   ```bash
   python app.py
   ```
3. Accede con el navegador a:
   - `http://localhost:8080` para la búsqueda por imagen.
   - `http://localhost:8080/analisis` para ver estadísticas de marcas y productos.

### Funcionalidades principales
- **Búsqueda por imagen**: sube una imagen y se calculan perceptual hashes (`phash`) para encontrar los productos más similares. Las coincidencias muestran nombre, precio, marca, enlace e imagen de referencia.
- **Panel de análisis**: visualiza conteo de productos por marca, precio promedio por marca y los cinco productos más caros.

## Scripts útiles
- `cargar_productos.py`: combina los JSON en `data/`, normaliza precios y genera objetos de producto. Ejecuta `python cargar_productos.py` para exportar el archivo unificado `productos_unificados.json`.
- `analisis_productos.py`: ejecuta análisis en consola (totales por marca, promedios y validación de datos). Ejecuta `python analisis_productos.py`.

## Notas sobre las imágenes y caché
- Las búsquedas por imagen descargan las imágenes de los productos y guardan los hashes en caché en `/tmp/product_image_phashes.json`.
- Usa el parámetro `force_rebuild=True` en `buscar_por_imagen_phash` si necesitas regenerar el índice de hashes.

## Estructura del proyecto
- `app.py`: servidor Flask y rutas web.
- `producto.py`: clases que representan los productos y sus variantes por marca.
- `buscar_por_imagen.py`: lógica de hashing perceptual e indexado de imágenes.
- `analisis_productos.py`: utilidades de análisis de datos.
- `cargar_productos.py`: carga y normalización de productos desde JSON.
- `templates/` y `static/`: recursos para la interfaz web.
