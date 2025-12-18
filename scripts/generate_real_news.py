import feedparser
import requests
import os
import json
import re
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
    prompt = f"""
Redacta un artículo periodístico completo en español a partir de los hechos descritos.

Instrucciones editoriales obligatorias:
- Mantén exclusivamente hechos verificables.
- No incluyas opiniones explícitas.
- No utilices lenguaje emocional ni calificativos ideológicos.
- Reordena la información para mejorar la claridad.
- Aporta contexto institucional, social o histórico cuando sea relevante.
- Explica posibles implicaciones sin hacer juicios.
- No menciones el medio original ni la fuente dentro del texto.
- No indiques ningún tipo de perspectiva política.
- Estilo: periodismo informativo profesional.

Estructura sugerida:
1. Contexto general del suceso.
2. Hechos principales confirmados.
3. Reacciones institucionales o datos relevantes.
4. Situación actual y posibles escenarios futuros.

Extensión mínima: 450 palabras.

Hechos disponibles:
\"\"\"{texto}\"\"\"
"""
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 700,
            "temperature": 0.4
        }
    }

    try:
        response = requests.post(
            HF_API_URL,
            headers=HEADERS,
            json=payload,
            timeout=90
        )

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
                for entry in feed.entries[:1]:  # 1 noticia por feed (control gratis)
                    resumen = entry.get("summary", "")
                    crear_articulo(
                        seccion,
                        categoria,
                        entry.title,
                        resumen,
                        entry.link
                    )

    os.makedirs("public/data", exist_ok=True)
    with open("public/data/news_index.json", "w", encoding="utf-8") as f:
        json.dump(news_index, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
