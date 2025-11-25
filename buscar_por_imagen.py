"""
buscar_por_imagen.py

Implementación simple de búsqueda por imagen basada en perceptual hash (phash).
Funciona así:
- Descarga (cuando es necesario) las imágenes de los productos.
- Calcula el phash de cada imagen y lo cachea en /tmp/product_image_phashes.json
- Calcula phash de la imagen de consulta y devuelve los productos con menor Hamming distance.

Dependencias: pillow, imagehash, requests
"""
import os, json, tempfile
from PIL import Image
import imagehash
import requests
from io import BytesIO

CACHE_FILE = os.path.join(tempfile.gettempdir(), "product_image_phashes.json")

def descargar_imagen(url, timeout=8):
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return Image.open(BytesIO(r.content)).convert('RGB')
    except Exception:
        return None

def obtener_phash_de_imagen_local(path):
    try:
        img = Image.open(path).convert('RGB')
        return imagehash.phash(img)
    except Exception:
        return None

def build_phash_index(productos, force_rebuild=False):
    # productos: lista de objetos con atributo 'imagen' (url) y 'link' etc.
    if os.path.exists(CACHE_FILE) and not force_rebuild:
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            if isinstance(cache, dict):
                return cache
        except Exception:
            pass

    index = {}
    for p in productos:
        url = getattr(p, "imagen", "") or ""
        if not url:
            continue
        try:
            img = descargar_imagen(url)
            if img is None:
                continue
            ph = str(imagehash.phash(img))
            index.setdefault(ph, []).append({
                "nombre": p.nombre,
                "precio": p.precio,
                "marca": p.marca,
                "link": getattr(p, "link", ""),
                "imagen": url
            })
        except Exception:
            continue

    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return index

def hamming_distance(hash1, hash2):
    try:
        i1 = int(str(hash1), 16)
        i2 = int(str(hash2), 16)
        x = i1 ^ i2
        return bin(x).count('1')
    except Exception:
        return 999

def buscar_por_imagen_phash(ruta_imagen, productos, topn=5, force_rebuild=False):
    """
    Devuelve lista de (score, producto_obj) ordenada (más cercano primero).
    score normalizado: 1 - (dist / 64) -> entre 0 y 1 (1 = idéntico)
    """
    index = build_phash_index(productos, force_rebuild=force_rebuild)
    if not index:
        print("No hay imágenes indexadas. Asegurate de tener conexión y que los productos tengan URLs de imagen.")
        return []

    ph_query = obtener_phash_de_imagen_local(ruta_imagen)
    if ph_query is None:
        print("No se pudo calcular phash de la imagen de consulta.")
        return []

    results = []
    for ph, items in index.items():
        dist = hamming_distance(str(ph_query), ph)
        for it in items:
            class P:
                def __init__(self,d):
                    self.nombre=d.get('nombre'); self.precio=d.get('precio'); self.marca=d.get('marca'); self.link=d.get('link'); self.imagen=d.get('imagen')
                def mostrar_info(self): return f"{self.nombre} - ${self.precio} - {self.marca}"
            results.append((dist, P(it)))
    results.sort(key=lambda x: x[0])
    normalized = [ (1 - (r[0]/64), r[1]) for r in results[:topn] ]
    return normalized

if __name__ == '__main__':
    print("Este módulo expone buscar_por_imagen_phash(ruta_imagen, productos, topn)")
