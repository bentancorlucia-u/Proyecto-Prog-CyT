import json
import os

# Importamos las clases de productos según marca
from producto import (
    Producto, ProductoSiSi, ProductoRotunda,
    ProductoSierramora
)

# ==========================================================
#     ELEGIR CLASE DE PRODUCTO SEGÚN LA MARCA
# ==========================================================
def clase_segun_marca(marca):
    """
    Devuelve la clase de producto correspondiente a una marca.
    Esto permite aplicar POO: cada marca puede tener lógica propia.
    Si no se reconoce la marca, se usa la clase base Producto.
    """

    if not marca:
        return Producto

    # Normalizar la marca para evitar errores por formato distinto
    marca_normalizada = (
        marca.lower()
             .replace(" ", "")
             .replace("-", "")
             .strip()
    )

    # Clasificación por marca exacta
    if marca_normalizada == "sisi":
        return ProductoSiSi

    if marca_normalizada == "rotunda":
        return ProductoRotunda

    if marca_normalizada == "sierramora":
        return ProductoSierramora

    # Si no matchea ninguna, devolvemos la clase base
    return Producto


# ==========================================================
#      CONVERSIÓN OBJETO → DICCIONARIO SERIALIZABLE
# ==========================================================
def producto_a_dict(producto):
    """
    Convierte un objeto Producto o derivados a un diccionario listo para JSON.
    Se usa en exportación o debugging.
    """
    return {
        "nombre": producto.nombre,
        "precio": producto.precio,
        "link": producto.link,
        "imagen": producto.imagen,
        "marca": getattr(producto, "marca", "Desconocida"),
    }


# ==========================================================
#       NORMALIZAR PRECIO LEÍDO DESDE JSON / SCRAPING
# ==========================================================
def normalizar_precio(valor):
    """
    Convierte cualquier precio a un entero.
    Admite formatos como:
    '1290', 1290, 1290.0, '1290.00', '$1.290', '1,290', etc.
    """

    if valor is None:
        return 0

    # Lo convertimos a string para poder limpiar caracteres
    texto = str(valor)

    # Eliminamos símbolos de formato
    texto = (
        texto.replace("$", "")
             .replace(".", "")
             .replace(",", "")
             .strip()
    )

    try:
        return int(texto)
    except:
        return 0   # Si falla, devolvemos 0 en vez de romper el flujo


# ==========================================================
#      CARGAR TODOS LOS PRODUCTOS DESDE JSONS LOCALES
# ==========================================================
def cargar_todos_los_productos(carpeta_data):
    """
    Recorre la carpeta_data, busca archivos .json y carga
    todos los productos dentro de ellos.

    - Cada JSON contiene productos de una tienda/marca.
    - Aquí aplicamos la clase adecuada según la marca.
    - Limpia el precio y completa campos faltantes.
    """

    productos_totales = []

    for archivo in os.listdir(carpeta_data):
        if archivo.endswith(".json"):
            ruta = os.path.join(carpeta_data, archivo)

            # Abrimos el JSON
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)

            # Creamos objetos Producto (o subclases)
            for item in datos:
                marca = item.get("marca", "Desconocida")
                ClaseProd = clase_segun_marca(marca)

                # Instanciamos el producto con sus datos
                producto = ClaseProd(
                    nombre=item.get("nombre", "Sin nombre"),
                    precio=normalizar_precio(item.get("precio", 0)),
                    link=item.get("link") or item.get("url", ""),  # fallback por si el campo se llama distinto
                    imagen=item.get("imagen", ""),
                    marca=marca
                )

                productos_totales.append(producto)

    return productos_totales


# ==========================================================
#      EXPORTAR TODOS LOS PRODUCTOS A UN SOLO JSON
# ==========================================================
def exportar_todos_los_productos_json(carpeta_data, archivo_salida="productos_unificados.json"):
    """
    Carga todos los productos desde la carpeta data y los
    exporta unificados en un solo JSON.

    Útil para debugging, backups o análisis fuera del sistema.
    """

    productos = cargar_todos_los_productos(carpeta_data)

    # Convertimos cada producto a diccionario JSON-friendly
    lista_dicts = [producto_a_dict(p) for p in productos]

    # Guardamos el JSON final
    with open(archivo_salida, "w", encoding="utf-8") as f:
        json.dump(lista_dicts, f, ensure_ascii=False, indent=4)

    print(f"✔ Archivo JSON generado: {archivo_salida}")
    print(f"📦 Cantidad total de productos: {len(lista_dicts)}")

    return lista_dicts


# ==========================================================
#      EJECUCIÓN DIRECTA DEL SCRIPT (modo herramienta)
# ==========================================================
if __name__ == "__main__":

    # Calcula automáticamente la ruta /data junto al archivo
    carpeta = os.path.join(os.path.dirname(__file__), "data")
    print("📁 Buscando JSON en:", carpeta)

    # Genera un JSON unificado cuando se ejecuta desde terminal
    productos_json = exportar_todos_los_productos_json(carpeta)
