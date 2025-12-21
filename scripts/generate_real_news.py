# -*- coding: utf-8 -*-

import feedparser
import requests
import os
import json
import re
import random
from datetime import datetime

# =============================
# CONFIGURACIÓN
# =============================

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

if not HF_API_KEY:
    raise ValueError("HF_API_KEY no está definido en los secrets de GitHub")

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

FEEDS = {
    "espana": {
        "politica": ["https://www.europapress.es/rss/rss.aspx"],
        "economia": ["https://www.eldiario.es/rss/"],
        "deportes": ["https://www.marca.com/rss/futbol/primera-division.xml"]
    },
    "internacional": {
        "politica": ["https://feeds.reuters.com/reuters/worldNews"],
        "economia": ["http://feeds.bbci.co.uk/news/world/rss.xml"],
        "deportes": ["https://www.espn.com/espn/rss/news"]
    }
}

PROMPTS = [
    """Redacta un artículo periodístico completo en español basado en los hechos que se indican a continuación.
Mantén únicamente hechos verificables.
Evita opiniones, ideología o referencias al medio.
Amplía con contexto institucional o histórico.
Longitud mínima: 500 palabras.

Hechos:
\"\"\"{texto}\"\"\""""
]

news_index = {}

# =============================
# FUNCIONES AUXILIARES
# =============================

def limpiar_texto(texto):
    texto = re.sub(r'<[^>]+>', '', texto)
    return texto.replace('\n', ' ').strip()

def texto_base_minimo(texto):
    if len(texto) < 500:
        texto += (
            " Este hecho se produce en un contexto de decisiones institucionales, "
            "reacciones políticas y análisis económicos que continúan desarrollándose."
        )
    return texto

def reinterpretar_con_ia(texto):
    prompt = random.choice(PROMPTS).replace("{texto}", texto)

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 900,
            "temperature": 0.5,
            "return_full_text": False
        }
    }

    try:
        r = requests.post(HF_API_URL, headers=HEADERS, json=payload, timeout=120)
        if r.status_code == 200:
            generado = r.json()[0].get("generated_text", "").strip()
            if len(generado) > 600:
                return generado
    except:
        pass

    return texto

def mejorar_titulo_con_ia(titulo):
    prompt = f"""
Reescribe el siguiente titular periodístico en español.
Máximo 12 palabras. Estilo neutro y profesional.

Titular:
"{titulo}"
"""
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 30, "temperature": 0.3}
    }

    try:
        r = requests.post(HF_API_URL, headers=HEADERS, json=payload, timeout=60)
        if r.status_code == 200:
            return r.json()[0]["generated_text"].strip()
    except:
        pass

    return titulo

# =============================
# CREAR ARTÍCULO HTML
# =============================

def crear_articulo(seccion, categoria, titulo, resumen, enlace):
    fecha_archivo = datetime.now().strftime("%Y-%m-%d")
    fecha_visible = datetime.now().strftime("%d/%m/%Y")

    ruta = f"public/noticias/{seccion}/{categoria}"
    os.makedirs(ruta, exist_ok=True)

    slug = re.sub(r'[^a-zA-Z0-9]+', '-', titulo.lower())[:60]
    archivo = f"{ruta}/{fecha_archivo}-{slug}.html"

    texto = reinterpretar_con_ia(texto_base_minimo(limpiar_texto(resumen)))
    parrafos = "".join(f"<p>{p}</p>" for p in texto.split("\n") if p.strip())

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{titulo}</title>
<link rel="stylesheet" href="/css/style.css">
</head>

<body>

<header class="top-bar">
  <h1><a href="/" style="color:white;text-decoration:none;">Contexto Abierto</a></h1>
  <nav>
    <a href="/">España</a>
    <a href="/">Internacional</a>
    <a href="/" class="humor">Humor</a>
  </nav>
</header>

<main class="container">
<article class="card {seccion}">
  <img src="/img/placeholder.jpg" alt="Imagen noticia">
  <div class="card-content">
    <span class="date">{fecha_visible}</span>
    <h2>{titulo}</h2>
    {parrafos}
    <hr>
    <p class="source">
      <strong>Fuente original:</strong>
      <a href="{enlace}" target="_blank" rel="noopener">Consultar noticia original</a>
    </p>
  </div>
</article>
</main>

<footer>
&copy; Contexto Abierto - Proyecto automatizado
</footer>

</body>
</html>
"""

    with open(archivo, "w", encoding="utf-8") as f:
        f.write(html)

    news_index.setdefault(seccion, {}).setdefault(categoria, []).append(
        f"noticias/{seccion}/{categoria}/{os.path.basename(archivo)}"
    )

# =============================
# PROCESO PRINCIPAL
# =============================

def main():
    for seccion, categorias in FEEDS.items():
        for categoria, urls in categorias.items():
            for url in urls:
                feed = feedparser.parse(url)
                for entry in feed.entries[:1]:
                    titulo = mejorar_titulo_con_ia(entry.get("title", "Sin título"))
                    resumen = entry.get("summary", "") or entry.get("description", "")
                    crear_articulo(seccion, categoria, titulo, resumen, entry.link)

    os.makedirs("public/data", exist_ok=True)
    with open("public/data/news_index.json", "w", encoding="utf-8") as f:
        json.dump(news_index, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
