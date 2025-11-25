import os
import sys

# --- Ajuste para asegurar que podamos importar cargar_productos.py ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cargar_productos import cargar_todos_los_productos


# ============================================================
#           FUNCIONES DE PROCESAMIENTO Y ANÁLISIS
# ============================================================

def productos_por_marca(lista_productos):
    """Devuelve un diccionario con la cantidad de productos por marca."""
    conteo = {}
    for p in lista_productos:
        marca = p.marca or "Desconocida"
        conteo[marca] = conteo.get(marca, 0) + 1
    return conteo


def precio_promedio_por_marca(lista_productos):
    """Calcula el precio promedio de cada marca."""
    totales = {}
    cantidades = {}

    for p in lista_productos:
        marca = p.marca
        totales[marca] = totales.get(marca, 0) + p.precio
        cantidades[marca] = cantidades.get(marca, 0) + 1

    promedios = {marca: round(totales[marca] / cantidades[marca], 2) for marca in totales}
    return promedios


def top_5_productos_mas_caros(lista_productos):
    """Devuelve los 5 productos más caros."""
    return sorted(lista_productos, key=lambda x: x.precio, reverse=True)[:5]


def productos_con_errores(lista_productos):
    """Detecta productos con errores comunes."""
    errores = []
    for p in lista_productos:
        if p.precio == 0 or p.nombre == "" or p.link == "":
            errores.append(p)
    return errores


# ============================================================
#                        PROGRAMA PRINCIPAL
# ============================================================

if __name__ == "__main__":
    carpeta_data = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

    print(f"📁 Leyendo archivos desde: {carpeta_data}")

    productos = cargar_todos_los_productos(carpeta_data)

    print(f"📦 Total productos cargados: {len(productos)}\n")

    # ---------- 🔍 Análisis 1: Productos por marca ----------
    print("📊 Cantidad de productos por marca:")
    marcas = productos_por_marca(productos)
    for marca, cantidad in marcas.items():
        print(f"   • {marca}: {cantidad} productos")

    print("\n---------------------------------------------\n")

    # ---------- 🔍 Análisis 2: Precio promedio por marca ----------
    print("💲 Precio promedio por marca:")
    promedios = precio_promedio_por_marca(productos)
    for marca, prom in promedios.items():
        print(f"   • {marca}: ${prom}")

    print("\n---------------------------------------------\n")

    # ---------- 🔍 Análisis 3: Top 5 productos más caros ----------
    print("🔥 Top 5 productos más caros:")
    for p in top_5_productos_mas_caros(productos):
        print(f"   • {p.nombre} - ${p.precio} ({p.marca})")

    print("\n---------------------------------------------\n")

    # ---------- 🔍 Análisis 4: Productos con errores ----------
    errores = productos_con_errores(productos)

    print("⚠ Productos con posibles errores (precio 0 / sin link / sin nombre):")
    if not errores:
        print("   ✔ No se encontraron errores")
    else:
        for p in errores[:10]:  # Mostrar solo 10
            print(f"   • {p.nombre} - ${p.precio} - {p.marca}")

        print(f"   Total con errores: {len(errores)} productos")


