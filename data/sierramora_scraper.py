import json
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def scrape_sierramora():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1600, "height": 4000})

        page.goto("https://www.sierramorashop.com/shop", wait_until="domcontentloaded")
        time.sleep(2)

        # Scroll infinito real
        last_height = 0
        same = 0
        while True:
            new_h = page.evaluate("document.body.scrollHeight")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

            if new_h == last_height:
                same += 1
            else:
                same = 0

            if same >= 5:
                break

            last_height = new_h

        # ------------------------------------
        # 🔥 FORZAR CARGA DE TODAS LAS IMÁGENES
        # ------------------------------------
        page.evaluate("""
            const imgs = document.querySelectorAll('img');
            imgs.forEach(img => {
                img.loading = 'eager';
                if (img.dataset?.src) img.src = img.dataset.src;
                if (img.dataset?.srcset) img.srcset = img.dataset.srcset;
            });
        """)
        time.sleep(2)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    productos = []

    for item in soup.select("div.cnt"):
        nombre_tag = item.select_one("div.info a.tit h2")
        precio_tag = item.select_one("div.info strong.precio span.monto")
        link_tag = item.select_one("a.img")

        if not (nombre_tag and precio_tag and link_tag):
            continue

        nombre = nombre_tag.get_text(strip=True)
        precio_raw = precio_tag.get_text(strip=True)

        link = link_tag["href"]
        if not link.startswith("http"):
            link = "https://www.sierramorashop.com" + link

        # EXTRAER CUALQUIER IMG REAL
        img_tag = item.select_one("a.img img")
        img_url = None

        if img_tag:
            src = img_tag.get("src", "")
            if src.startswith("//"):
                src = "https:" + src
            if src:
                img_url = src

        productos.append({
            "nombre": nombre,
            "precio": precio_raw,
            "link": link,
            "imagen": img_url,
            "marca": "Sierra Mora",
        })

    with open("productos_sierramora.json", "w", encoding="utf-8") as f:
        json.dump(productos, f, ensure_ascii=False, indent=2)

    print("✔ Productos scrapeados:", len(productos))
    return productos


if __name__ == "__main__":
    scrape_sierramora()













