import os
import requests
import feedparser
import base64
from datetime import datetime
import re

# =========================
# CONFIGURACIÓN
# =========================

HF_API_KEY = os.getenv("HF_API_KEY")

TEXT_MODEL = "HuggingFaceH4/zephyr-7b-beta"
IMAGE_MODEL = "stabilityai/stable-diffusion-2"

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

RSS_FEEDS = [
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/espana/portada",
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/internacional/portada",
]

OUTPUT_DIR = "public/noticias/humor"
IMAGE_DIR = f"{OUTPUT_DIR}/images"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# =========================
# UTILIDADES
# =========================

def limpiar_texto(texto):
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()

def fecha_legible():
    return datetime.now().strftime("%d/%m/%Y")

def nombre_archivo(titulo):
    limpio = re.sub(r"[^\w\s-]", "", titulo).strip().lower()
    return limpio.replace(" ", "-")[:60]

# =========================
# IA TEXTO (HUMOR)
# =========================

def generar_humor(texto):
    prompt = f"""
Redacta un artículo de HUMOR y SÁTIRA en español basándote únicamente en los hechos reales siguientes.

Normas:
- No inventes hechos.
- Usa ironía, exageración y tono cómico inteligente.
- Que parezca una columna humorística de prensa.
- No indiques ideología.
- No menciones la fuente dentro del texto.
- Mínimo 500 palabras.
- Introducción, desarrollo y cierre claro.

Hechos reales:
\"\"\"{texto}\"\"\"
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 900,
            "temperature": 0.7
        }
    }

    r = requests.post(
        f"https://api-inference.huggingface.co/models/{TEXT_MODEL}",
        headers=HEADERS,
        json=payload,
        timeout=120
    )

    if r.status_code == 200:
        return r.json()[0]["generated_text"]
    return texto

# =========================
# IA IMAGEN (CARICATURA)
# =========================

def generar_imagen_humor(resumen, titulo):
    prompt = (
        "Ilustración humorística tipo caricatura editorial, estilo cómic, "
        "exagerado y satírico, colores vivos, sobre la siguiente noticia:\n"
        f"{resumen}"
    )

    payload = {
        "inputs": prompt
    }

    r = requests.post(
        f"https://api-inference.huggingface.co/models/{IMAGE_MODEL}",
        headers=HEADERS,
        json=payload,
        timeout=120
    )

    if r.status_code != 200:
        return None

    try:
        image_bytes = base64.b64decode(r.json()["image"])
        filename = f"{nombre_archivo(titulo)}.png"
        path = f"{IMAGE_DIR}/{filename}"

        with open(path, "wb") as f:
            f.write(image_bytes)

        return f"images/{filename}"
    except Exception:
        return None

# =========================
# HTML
# =========================

def guardar_html(titulo, texto, enlace, imagen):
    fecha = fecha_legible()
    archivo = f"{OUTPUT_DIR}/{datetime.now().strftime('%Y-%m-%d')}-{nombre_archivo(titulo)}.html"

    parrafos = "".join(f"<p>{p}</p>" for p in texto.split("\n") if p.strip())
    img_html = f'<img src="{imagen}" style="max-width:100%;margin:20px 0;">' if imagen else ""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{titulo}</title>
</head>
<body>

<h1>{titulo}</h1>

{img_html}

{parrafos}

<hr>
<p><strong>Fuente original:</strong>
<a href="{enlace}" target="_blank" rel="noopener">Ver noticia original</a></p>

<p><em>Artículo generado automáticamente el {fecha}</em></p>

</body>
</html>
"""

    with open(archivo, "w", encoding="utf-8") as f:
        f.write(html)

# =========================
# MAIN
# =========================

def main():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        if not feed.entries:
            continue

        entry = feed.entries[0]

        titulo = entry.title
        resumen = limpiar_texto(entry.get("summary", ""))
        enlace = entry.link

        if len(resumen) < 200:
            continue

        texto_humor = generar_humor(resumen)
        imagen = generar_imagen_humor(resumen, titulo)

        guardar_html(titulo, texto_humor, enlace, imagen)
        break  # solo 1 noticia por ejecución

if __name__ == "__main__":
    main()
