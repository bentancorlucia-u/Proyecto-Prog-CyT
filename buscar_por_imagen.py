"""
buscar_por_imagen.py

Implementación simple de búsqueda por similitud de imágenes usando perceptual hash (pHash).
La idea es medir qué tan “parecida” es una imagen a otra comparando sus hashes.

Flujo general:
1. Descarga las imágenes de los productos (si hace falta).
2. Calcula el pHash de cada imagen y lo guarda en un archivo cacheado en /tmp.
3. Calcula el pHash de la imagen subida por el usuario.
4. Compara ambos hashes con distancia de Hamming.
5. Devuelve los productos más similares.

Dependencias:
- pillow (manejo de imágenes)
- imagehash (cálculo del phash)
- requests (descarga de imágenes)
"""

import os, json, tempfile
from PIL import Image
import imagehash
import requests
from io import BytesIO

# Ruta al archivo donde se guardará la caché de pHashes
CACHE_FILE = os.path.join(tempfile.gettempdir(), "product_image_phashes.json")


# ==========================================================
#                    DESCARGA DE IMÁGENES
# ==========================================================
def descargar_imagen(url, timeout=8):
    """
    Descarga una imagen desde una URL y la convierte a RGB.
    Devuelve un objeto PIL.Image o None si falla.
    """
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()  # lanza error si la respuesta no es 200
        return Image.open(BytesIO(r.content)).convert('RGB')
    except Exception:
        return None


# ==========================================================
#                 PHASH DE IMAGEN LOCAL
# ==========================================================
def obtener_phash_de_imagen_local(path):
    """
    Abre una imagen local, la convierte a RGB y calcula su pHash.
    Devuelve un objeto imagehash.phash o None si falla.
    """
    try:
        img = Image.open(path).convert('RGB')
        return imagehash.phash(img)
    except Exception:
        return None


# ==========================================================
#              CONSTRUCCIÓN DEL ÍNDICE pHASH
# ==========================================================
def build_phash_index(productos, force_rebuild=False):
    """
    Construye un índice que mapea:
        { phash_string : [lista de productos con ese phash] }

    - Si ya existe un archivo de caché y no se pide reconstrucción, lo usa.
    - Si no, descarga imágenes, calcula pHash y genera el índice.
    """

    # --- Intentamos usar la caché existente ---
    if os.path.exists(CACHE_FILE) and not force_rebuild:
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            if isinstance(cache, dict):
                return cache
        except Exception:
            pass  # Si falla, recalculamos desde cero

    # --- Construcción desde cero ---
    index = {}
    for p in productos:
        # Obtenemos la URL de la imagen del producto
        url = getattr(p, "imagen", "") or ""
        if not url:
            continue

        try:
            img = descargar_imagen(url)
            if img is None:
                continue

            # Calculamos el pHash y lo guardamos como string hexadecimal
            ph = str(imagehash.phash(img))

            # Guardamos info relevante del producto en el índice
            index.setdefault(ph, []).append({
                "nombre": p.nombre,
                "precio": p.precio,
                "marca": p.marca,
                "link": getattr(p, "link", ""),
                "imagen": url
            })

        except Exception:
            continue

    # --- Guardar caché en /tmp ---
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return index


# ==========================================================
#             DISTANCIA DE HAMMING ENTRE HASHES
# ==========================================================
def hamming_distance(hash1, hash2):
    """
    Calcula la distancia de Hamming entre dos hashes pHash expresados en hexadecimal.
    Cuantos más bits diferentes, mayor la distancia → menos similares.
    """
    try:
        i1 = int(str(hash1), 16)
        i2 = int(str(hash2), 16)

        # XOR obtiene los bits distintos entre ambos hashes
        x = i1 ^ i2

        # Contamos cuántos bits son "1" = diferencia
        return bin(x).count('1')

    except Exception:
        return 999  # valor grande = muy diferente


# ==========================================================
#              BÚSQUEDA PRINCIPAL POR pHASH
# ==========================================================
def buscar_por_imagen_phash(ruta_imagen, productos, topn=5, force_rebuild=False):
    """
    Devuelve lista de (score, producto_obj) ordenada del más similar al menos similar.

    Score normalizado:
        score = 1 - (distancia / 64)
        → 1 = idéntico
        → 0 = completamente diferente
    """

    # Cargamos o reconstruimos el índice
    index = build_phash_index(productos, force_rebuild=force_rebuild)
    if not index:
        print("No hay imágenes indexadas. Asegurate de tener conexión y que los productos tengan URLs de imagen.")
        return []

    # Calculamos el pHash de la imagen del usuario
    ph_query = obtener_phash_de_imagen_local(ruta_imagen)
    if ph_query is None:
        print("No se pudo calcular phash de la imagen de consulta.")
        return []

    results = []

    # Comparamos contra cada hash del índice
    for ph, items in index.items():

        # Distancia de Hamming entre ambas imágenes
        dist = hamming_distance(str(ph_query), ph)

        # Convertimos diccionarios a objetos simples (para mantener uniformidad)
        for it in items:
            class P:
                """Clase interna simple que representa un producto indexado."""
                def __init__(self, d):
                    self.nombre = d.get('nombre')
                    self.precio = d.get('precio')
                    self.marca = d.get('marca')
                    self.link = d.get('link')
                    self.imagen = d.get('imagen')

                def mostrar_info(self):
                    return f"{self.nombre} - ${self.precio} - {self.marca}"

            results.append((dist, P(it)))

    # Ordenamos por menor distancia (mayor similitud)
    results.sort(key=lambda x: x[0])

    # Normalizamos puntajes y devolvemos solo los top N
    normalized = [
        (1 - (r[0] / 64), r[1])  # 64 bits en un phash estándar
        for r in results[:topn]
    ]

    return normalized


# ==========================================================
#               EJECUCIÓN DIRECTA DEL MÓDULO
# ==========================================================
if __name__ == '__main__':
    print("Este módulo expone buscar_por_imagen_phash(ruta_imagen, productos, topn)")

