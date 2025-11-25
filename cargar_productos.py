import json
import os

from producto import (
    Producto, ProductoSiSi, ProductoRotunda,
    ProductoSierramora
)

def clase_segun_marca(marca):
    if not marca:
        return Producto

    # Normalizar
    marca_normalizada = (
        marca.lower()
             .replace(" ", "")
             .replace("-", "")
             .strip()
    )

    if marca_normalizada == "sisi":
        return ProductoSiSi

    if marca_normalizada == "rotunda":
        return ProductoRotunda

    if marca_normalizada == "sierramora":
        return ProductoSierramora

    return Producto


def producto_a_dict(producto):
    """Convierte cualquier producto a un diccionario serializable."""
    return {
        "nombre": producto.nombre,
        "precio": producto.precio,
        "link": producto.link,
        "imagen": producto.imagen,
        "marca": getattr(producto, "marca", "Desconocida"),
    }

def normalizar_precio(valor):
    """
    Convierte el precio a int sin decimales.
    Sirve si viene '1290', 1290, 1290.0, '1290.00', '$1.290', etc.
    """
    if valor is None:
        return 0

    # Convertir a string para limpiar
    texto = str(valor)

    # Sacar símbolos raros
    texto = (
        texto.replace("$", "")
             .replace(".", "")
             .replace(",", "")
             .strip()
    )

    try:
        return int(texto)
    except:
        return 0


def cargar_todos_los_productos(carpeta_data):
    productos_totales = []

    for archivo in os.listdir(carpeta_data):
        if archivo.endswith(".json"):
            ruta = os.path.join(carpeta_data, archivo)

            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)

            for item in datos:
                marca = item.get("marca", "Desconocida")
                ClaseProd = clase_segun_marca(marca)

                producto = ClaseProd(
                    nombre=item.get("nombre", "Sin nombre"),
                    precio=normalizar_precio(item.get("precio", 0)),
                    link=item.get("link") or item.get("url", ""),
                    imagen=item.get("imagen", ""),
                    marca=marca
                )

                productos_totales.append(producto)

    return productos_totales


def exportar_todos_los_productos_json(carpeta_data, archivo_salida="productos_unificados.json"):
    productos = cargar_todos_los_productos(carpeta_data)

    lista_dicts = [producto_a_dict(p) for p in productos]

    with open(archivo_salida, "w", encoding="utf-8") as f:
        json.dump(lista_dicts, f, ensure_ascii=False, indent=4)

    print(f"✔ Archivo JSON generado: {archivo_salida}")
    print(f"📦 Cantidad total de productos: {len(lista_dicts)}")

    return lista_dicts


if __name__ == "__main__":

    carpeta = os.path.join(os.path.dirname(__file__), "data")
    print("📁 Buscando JSON en:", carpeta)

    productos_json = exportar_todos_los_productos_json(carpeta)
