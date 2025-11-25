from flask import Flask, render_template, request
import os

from cargar_productos import cargar_todos_los_productos
from buscar_por_imagen import buscar_por_imagen_phash

from analisis_productos import (
    productos_por_marca,
    precio_promedio_por_marca,
    top_5_productos_mas_caros
)

# Cargar todos los productos al iniciar
CARPETA_DATA = os.path.join(os.path.dirname(__file__), "data")
PRODUCTOS = cargar_todos_los_productos(CARPETA_DATA)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    resultados = None
    imagen_subida = None

    if request.method == "POST":
        archivo = request.files.get("imagen")
        if archivo:
            ruta_local = os.path.join("static", "img", "input.jpg")
            archivo.save(ruta_local)
            imagen_subida = ruta_local

            # Ejecutar búsqueda
            resultados_raw = buscar_por_imagen_phash(
                ruta_local,
                PRODUCTOS,
                topn=6,
                force_rebuild=False # cachear prods
            )

            for score, prod in resultados_raw:
                print(">>", prod.nombre, "precio:", prod.precio, "raw:", getattr(prod, "precio_raw", None))


            # Convertir resultados a formato fácil de mostrar
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


    return render_template("index.html", resultados=resultados, imagen_subida=imagen_subida)


@app.route("/analisis")
def analisis():
    conteo_marcas = productos_por_marca(PRODUCTOS)
    promedios = precio_promedio_por_marca(PRODUCTOS)
    top_5 = top_5_productos_mas_caros(PRODUCTOS)

    return render_template(
        "analisis.html",
        conteo_marcas=conteo_marcas,
        promedios=promedios,
        top_5=top_5
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)

