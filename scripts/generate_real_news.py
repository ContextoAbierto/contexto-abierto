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
    # Perfil Formal
    """Redacta un artículo periodístico completo en español basado en los hechos que se indican a continuación. 
- Mantén únicamente hechos verificables.
- Evita opiniones, adjetivos emocionales, ideología o referencia al medio.
- Escribe formal, profesional y coherente.
- Amplía la noticia aportando contexto histórico, social o institucional.
- Explica posibles consecuencias de los hechos sin especular.
- Longitud mínima: 450-600 palabras.
- Introducción, desarrollo y conclusión diferenciados.
Hechos disponibles:
\"\"\"{texto}\"\"\"""",

    # Perfil Directo
    """Redacta un artículo periodístico en español basado en los hechos que se presentan a continuación.
- Mantén únicamente hechos verificables.
- Estilo conciso, directo y claro.
- Evita opiniones, ideología o referencia al medio.
- Amplía la noticia si hace falta.
- Longitud mínima: 400-500 palabras.
- Organiza en párrafos con introducción, hechos principales y cierre.
Hechos disponibles:
\"\"\"{texto}\"\"\"""",

    # Perfil Explicativo
    """Redacta un artículo periodístico explicativo en español basado en los hechos indicados a continuación.
- Mantén únicamente hechos verificables.
- Explica con detalle y aporta contexto social, institucional o histórico.
- Describe posibles consecuencias o escenarios futuros de forma neutral.
- No menciones ideología ni el medio original.
- Estilo claro, coherente y profesional.
- Longitud mínima: 500-700 palabras.
- Organiza en: contexto inicial, desarrollo de hechos, repercusiones y conclusión final.
Hechos disponibles:
\"\"\"{texto}\"\"\""""
]

news_index = {}

# =============================
# FUNCIONES AUXILIARES
# =============================

def limpiar_texto(texto):
    texto = re.sub(r'<[^>]+>', '', texto)
    texto = texto.replace('\n', ' ').strip()
    return texto

def texto_base_minimo(texto):
    if len(texto) < 300:
        texto += (
            " La información disponible hasta el momento es limitada. "
            "El suceso se enmarca dentro de un contexto más amplio relacionado "
            "con decisiones recientes, reacciones institucionales y posibles "
            "implicaciones a corto y medio plazo."
        )
    return texto

def reinterpretar_con_ia(texto):
    prompt_base = random.choice(PROMPTS)
    prompt = prompt_base.replace("{texto}", texto)

    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 800, "temperature": 0.4}
    }

    try:
        response = requests.post(HF_API_URL, headers=HEADERS, json=payload, timeout=90)
        if response.status_code == 200:
            return response.json()[0]["generated_text"]
        else:
            return texto
    except Exception:
        return texto

def crear_articulo(seccion, categoria, titulo, resumen, enlace):
    fecha = datetime.now().strftime("%Y-%m-%d")
    ruta = f"public/noticias/{seccion}/{categoria}"
    os.makedirs(ruta, exist_ok=True)

    filename = f"{fecha}-{titulo[:60].replace(' ', '_').replace('/', '_')}.html"
    archivo = f"{ruta}/{filename}"

    texto_limpio = limpiar_texto(resumen)
    texto_limpio = texto_base_minimo(texto_limpio)
    texto_final = reinterpretar_con_ia(texto_limpio)

    parrafos = "".join(f"<p>{p}</p>" for p in texto_final.split("\n") if p.strip())

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{titulo}</title>
</head>
<body>
<h1>{titulo}</h1>

{parrafos}

<hr>
<p><strong>Fuente original:</strong>
<a href="{enlace}" target="_blank" rel="noopener">Consultar noticia original</a>
</p>

<p><em>Artículo generado automáticamente el {fecha}</em></p>
</body>
</html>
"""

    with open(archivo, "w", encoding="utf-8") as f:
        f.write(html)

    news_index.setdefault(seccion, {}).setdefault(categoria, []).append(
        f"noticias/{seccion}/{categoria}/{filename}"
    )

# =============================
# PROCESO PRINCIPAL
# =============================

def main():
    for seccion, categorias in FEEDS.items():
        for categoria, urls in categorias.items():
            for url in urls:
                feed = feedparser.parse(url)
                for entry in feed.entries[:1]:  # Control gratuito: 1 noticia por feed
                    resumen = entry.get("summary", "") or entry.get("description", "")
                    titulo = entry.get("title", "Sin título")
                    
                    # Si la noticia está en inglés, la IA la traducirá al español
                    crear_articulo(
                        seccion,
                        categoria,
                        titulo,
                        resumen,
                        entry.link
                    )

    os.makedirs("public/data", exist_ok=True)
    with open("public/data/news_index.json", "w", encoding="utf-8") as f:
        json.dump(news_index, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
