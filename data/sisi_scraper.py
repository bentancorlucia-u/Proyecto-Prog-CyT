# sisi_products_limit.py
# Requisitos:
# pip install selenium webdriver-manager beautifulsoup4

import json
import time
import re
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# -------- CONFIG --------
BASE_LISTING = "https://www.sisi.com.uy/mujer"
HEADLESS = True                 # False si querés ver el navegador
SCROLL_ROUNDS = 6               # scroll en la página de listado
SCROLL_WAIT = 2.0
PER_PRODUCT_WAIT = 1.5          # espera mínima después de abrir cada producto
OUTPUT_JSON = "sisi_products.json"
MAX_PRODUCTS = 50               # <-- límite: cambiá esto al número de productos que querés
# ------------------------

def setup_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def scroll_listing(driver, rounds=6, pause=2.0):
    last_h = driver.execute_script("return document.body.scrollHeight")
    for _ in range(rounds):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_h = driver.execute_script("return document.body.scrollHeight")
        if new_h == last_h:
            break
        last_h = new_h

def extract_listing_links(driver):
    """Extrae links y filtra sólo URLs de producto (heurística con '/catalogo/')."""
    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = []
    for a in soup.select("a[href]"):
        href = a.get("href")
        if not href:
            continue
        # normalizar
        if not href.startswith("http"):
            href_full = urljoin("https://sisi.com.uy", href)
        else:
            href_full = href
        # filtro fuerte: contendrá '/catalogo/' y terminará con _<digits> o con patrón de producto
        if "/catalogo/" in href_full and re.search(r"_\d+$", href_full):
            if href_full not in links:
                links.append(href_full)
    return links

def pick_best_image(soup):
    """Devuelve URL de imagen en alta resolución si encuentra."""
    # 1) meta og:image
    meta_img = soup.select_one("meta[property='og:image']")
    if meta_img and meta_img.get("content"):
        img = meta_img["content"].strip()
        if img and "/promociones/" not in img:
            return normalize_img_url(img)

    # 2) buscar imágenes con patrón high-res (800x1200, 1024-1024, original)
    imgs = soup.select("img")
    best = None
    for img_tag in imgs:
        src = img_tag.get("data-im") or img_tag.get("data-src") or img_tag.get("src") or ""
        if not src:
            continue
        candidate = normalize_img_url(src)
        # evitar imágenes promocionales
        if "/promociones/" in candidate:
            continue
        if any(p in candidate for p in ["/800x1200/", "/800x", "/1024-1024/", "/original/", "/1024x1024/", "/800x1200"]):
            return candidate
        # fallback: imagen dentro /catalogo/
        if "/catalogo/" in candidate:
            best = candidate
    if best:
        return best
    # 3) último recurso: la primera img que no sea promoción
    for img_tag in imgs:
        src = img_tag.get("data-im") or img_tag.get("data-src") or img_tag.get("src") or ""
        if not src:
            continue
        candidate = normalize_img_url(src)
        if "/promociones/" in candidate:
            continue
        return candidate
    return None

def normalize_img_url(src):
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("/"):
        return "https://sisi.com.uy" + src
    return src

def parse_product_page(driver, url):
    driver.get(url)
    time.sleep(PER_PRODUCT_WAIT)  # esperar cargar JS e imágenes
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Nombre: preferir h1, luego og:title, luego title
    nombre = None
    h1 = soup.select_one("h1")
    if h1 and h1.get_text(strip=True):
        nombre = h1.get_text(strip=True)
    if not nombre:
        meta = soup.select_one("meta[property='og:title']")
        if meta and meta.get("content"):
            nombre = meta.get("content").strip()
    if not nombre:
        title_tag = soup.select_one("title")
        if title_tag:
            nombre = title_tag.get_text(strip=True)

    # Precio: buscar montos
    precio = None
    # forma 1: strong.precio.venta span.monto
    p = soup.select_one("strong.precio.venta span.monto")
    if p:
        precio = p.get_text(strip=True)
    if not precio:
        p = soup.select_one("span.monto")
        if p:
            precio = p.get_text(strip=True)
    if not precio:
        p = soup.select_one(".product-price, .price--final, .productPrice")
        if p:
            precio = p.get_text(strip=True)

    # Imagen buena
    imagen = pick_best_image(soup)

    return {
        "nombre": nombre or "Sin nombre",
        "precio": (f"${precio}" if precio and not str(precio).strip().startswith("$") else precio) if precio else None,
        "imagen": imagen,
        "url": url
    }

def main():
    driver = setup_driver(headless=HEADLESS)
    try:
        driver.get(BASE_LISTING)
        time.sleep(2)
        scroll_listing(driver, rounds=SCROLL_ROUNDS, pause=SCROLL_WAIT)
        links = extract_listing_links(driver)
        # aplicar límite y mantener únicos
        unique_links = []
        for l in links:
            if l not in unique_links:
                unique_links.append(l)
            if len(unique_links) >= MAX_PRODUCTS:
                break

        resultados = []
        total = len(unique_links)
        for idx, link in enumerate(unique_links, start=1):
            # progreso simple
            print(f"Procesando {idx}/{total} → {link}", end="\r", flush=True)
            try:
                item = parse_product_page(driver, link)
                resultados.append(item)
            except Exception as e:
                # no detener todo por un error en un producto
                # opcional: loggear en un archivo
                pass

        # guardar JSON al final
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Guardados {len(resultados)} productos en {OUTPUT_JSON}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
