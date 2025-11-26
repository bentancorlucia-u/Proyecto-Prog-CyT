# Importamos Flask y funciones útiles para renderizar templates y manejar formularios
from flask import Flask, render_template, request
import os

# Importamos nuestras funciones internas para cargar productos y buscar por imagen
from cargar_productos import cargar_todos_los_productos
from buscar_por_imagen import buscar_por_imagen_phash

# Importamos funciones para el análisis estadístico de los productos
from analisis_productos import (
    productos_por_marca,
    precio_promedio_por_marca,
    top_5_productos_mas_caros
)

# ================================
#   CARGA INICIAL DE PRODUCTOS
# ================================

# Armamos la ruta hacia la carpeta /data dentro del proyecto
CARPETA_DATA = os.path.join(os.path.dirname(__file__), "data")

# Cargamos todos los productos al iniciar el servidor (solo una vez)
# Esto evita recargar JSONs cada vez que alguien entra al sitio
PRODUCTOS = cargar_todos_los_productos(CARPETA_DATA)

# Instanciamos la app Flask
app = Flask(__name__)


# ================================
#            RUTA PRINCIPAL
# ================================
@app.route("/", methods=["GET", "POST"])
def index():
    resultados = None
    imagen_subida = None

    # Si el usuario envió una imagen mediante POST...
    if request.method == "POST":
        archivo = request.files.get("imagen")

        # Validamos que efectivamente exista un archivo
        if archivo:
            # Ruta donde guardamos la imagen subida por el usuario
            ruta_local = os.path.join("static", "img", "input.jpg")
            archivo.save(ruta_local)
            imagen_subida = ruta_local

            # Ejecutar la búsqueda usando perceptual hash (pHash)
            resultados_raw = buscar_por_imagen_phash(
                ruta_local,
                PRODUCTOS,
                topn=6,             # cantidad de resultados a traer
                force_rebuild=False  # evitar recalcular hashes si ya existen
            )

            # Log para consola: mostramos nombres y precios obtenidos
            for score, prod in resultados_raw:
                print(">>", prod.nombre, "precio:", prod.precio, "raw:", getattr(prod, "precio_raw", None))

            # Convertimos los resultados a un diccionario para pasarlos fácilmente al template
            resultados = [
                {
                    "score": round(score, 3),
                    "nombre": prod.nombre,
                    "precio": prod.precio,
                    "marca": prod.marca,
                    "link": prod.link,
                    "imagen": prod.imagen,
                }
                for score, prod in resultados_raw
            ]

    # Renderizamos la página principal con los resultados (o vacío si es GET)
    return render_template("index.html", resultados=resultados, imagen_subida=imagen_subida)


# ================================
#         PÁGINA DE ANÁLISIS
# ================================
@app.route("/analisis")
def analisis():
    # Cálculo de datos estadísticos del catálogo completo
    conteo_marcas = productos_por_marca(PRODUCTOS)
    promedios = precio_promedio_por_marca(PRODUCTOS)
    top_5 = top_5_productos_mas_caros(PRODUCTOS)

    # Renderizamos el panel de análisis
    return render_template(
        "analisis.html",
        conteo_marcas=conteo_marcas,
        promedios=promedios,
        top_5=top_5
    )


# ================================
#     EJECUCIÓN DEL SERVIDOR
# ================================
if __name__ == "__main__":
    # host="0.0.0.0" permite acceder desde otras máquinas en la red (útil para demos)
    app.run(debug=True, host="0.0.0.0", port=8080)
